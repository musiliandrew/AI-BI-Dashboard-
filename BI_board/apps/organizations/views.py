from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import stripe
import os

from .models import Organization, OrganizationMembership, SubscriptionPlan, UsageLog, BillingHistory
from .serializers import (
    OrganizationSerializer, OrganizationMembershipSerializer, SubscriptionPlanSerializer,
    UsageLogSerializer, BillingHistorySerializer, OrganizationCreateSerializer
)
from .permissions import IsOrganizationOwnerOrAdmin, IsOrganizationMember

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    @action(detail=True, methods=['get'])
    def usage_analytics(self, request, pk=None):
        """Get detailed usage analytics for the organization"""
        organization = self.get_object()
        
        # Check permission
        if not organization.memberships.filter(user=request.user).exists():
            return Response({'error': 'Not a member of this organization'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Get usage data for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        usage_data = UsageLog.objects.filter(
            organization=organization,
            created_at__gte=thirty_days_ago
        ).values('usage_type').annotate(count=Count('id'))
        
        # Daily usage breakdown
        daily_usage = UsageLog.objects.filter(
            organization=organization,
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        return Response({
            'usage_summary': list(usage_data),
            'daily_usage': list(daily_usage),
            'current_limits': {
                'datasets': {
                    'used': organization.current_month_datasets,
                    'limit': organization.subscription_plan.max_datasets_per_month
                },
                'api_calls': {
                    'used': organization.current_month_api_calls,
                    'limit': organization.subscription_plan.max_api_calls_per_month
                },
                'users': {
                    'used': organization.total_users,
                    'limit': organization.subscription_plan.max_users_per_org
                }
            }
        })

class OrganizationMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]
    
    def get_queryset(self):
        org_id = self.kwargs.get('organization_pk')
        return OrganizationMembership.objects.filter(organization_id=org_id)

class BillingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, organization_id):
        """Get billing information for organization"""
        organization = get_object_or_404(Organization, id=organization_id)
        
        # Check if user is owner or admin
        membership = organization.memberships.filter(user=request.user).first()
        if not membership or not membership.can_manage_billing:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get billing history
        billing_history = BillingHistory.objects.filter(
            organization=organization
        ).order_by('-created_at')[:10]
        
        return Response({
            'organization': OrganizationSerializer(organization).data,
            'billing_history': BillingHistorySerializer(billing_history, many=True).data
        })

class StripeWebhookView(APIView):
    """Handle Stripe webhooks for subscription events"""
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=400)
        
        # Handle the event
        if event['type'] == 'invoice.payment_succeeded':
            self._handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            self._handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            self._handle_subscription_deleted(event['data']['object'])
        
        return Response({'status': 'success'})
    
    def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        try:
            organization = Organization.objects.get(
                stripe_customer_id=invoice['customer']
            )
            
            BillingHistory.objects.create(
                organization=organization,
                stripe_invoice_id=invoice['id'],
                amount=invoice['amount_paid'] / 100,  # Convert from cents
                currency=invoice['currency'].upper(),
                status='paid',
                billing_period_start=datetime.fromtimestamp(invoice['period_start']),
                billing_period_end=datetime.fromtimestamp(invoice['period_end'])
            )
        except Organization.DoesNotExist:
            pass
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription updates"""
        try:
            organization = Organization.objects.get(
                stripe_subscription_id=subscription['id']
            )
            organization.subscription_status = subscription['status']
            organization.save()
        except Organization.DoesNotExist:
            pass
    
    def _handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation"""
        try:
            organization = Organization.objects.get(
                stripe_subscription_id=subscription['id']
            )
            organization.subscription_status = 'canceled'
            organization.save()
        except Organization.DoesNotExist:
            pass

class CreateCheckoutSessionView(APIView):
    """Create Stripe checkout session for subscription"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        organization_id = request.data.get('organization_id')
        plan_name = request.data.get('plan_name')
        
        organization = get_object_or_404(Organization, id=organization_id)
        plan = get_object_or_404(SubscriptionPlan, name=plan_name)
        
        # Check permission
        membership = organization.memberships.filter(user=request.user).first()
        if not membership or not membership.can_manage_billing:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Create or get Stripe customer
            if not organization.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=organization.name,
                    metadata={'organization_id': str(organization.id)}
                )
                organization.stripe_customer_id = customer.id
                organization.save()
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=organization.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan.display_name,
                        },
                        'unit_amount': int(plan.price_monthly * 100),  # Convert to cents
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri('/dashboard?session_id={CHECKOUT_SESSION_ID}'),
                cancel_url=request.build_absolute_uri('/billing'),
                metadata={
                    'organization_id': str(organization.id),
                    'plan_name': plan_name
                }
            )
            
            return Response({'checkout_url': checkout_session.url})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
