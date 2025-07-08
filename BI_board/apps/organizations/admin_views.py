from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

from .models import Organization, OrganizationMembership, SubscriptionPlan, UsageLog, BillingHistory
from .serializers import OrganizationSerializer, SubscriptionPlanSerializer

User = get_user_model()

class AdminDashboardView(APIView):
    """
    Admin dashboard with platform-wide analytics
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get date ranges
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Basic metrics
        total_organizations = Organization.objects.count()
        total_users = User.objects.count()
        active_subscriptions = Organization.objects.filter(
            subscription_status='active'
        ).count()
        
        # Revenue metrics
        monthly_revenue = BillingHistory.objects.filter(
            created_at__gte=thirty_days_ago,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Usage metrics
        total_api_calls = UsageLog.objects.filter(
            usage_type='api_call',
            created_at__gte=thirty_days_ago
        ).count()
        
        total_datasets = UsageLog.objects.filter(
            usage_type='dataset_upload',
            created_at__gte=thirty_days_ago
        ).count()
        
        # Subscription breakdown
        subscription_breakdown = Organization.objects.values(
            'subscription_plan__display_name'
        ).annotate(count=Count('id'))
        
        # Growth metrics (last 30 days)
        new_organizations = Organization.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        new_users = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()
        
        # Top organizations by usage
        top_organizations = Organization.objects.annotate(
            api_calls=Count('usage_logs', filter=models.Q(
                usage_logs__usage_type='api_call',
                usage_logs__created_at__gte=thirty_days_ago
            ))
        ).order_by('-api_calls')[:10]
        
        return Response({
            'metrics': {
                'total_organizations': total_organizations,
                'total_users': total_users,
                'active_subscriptions': active_subscriptions,
                'monthly_revenue': float(monthly_revenue),
                'total_api_calls': total_api_calls,
                'total_datasets': total_datasets,
                'new_organizations': new_organizations,
                'new_users': new_users
            },
            'subscription_breakdown': list(subscription_breakdown),
            'top_organizations': OrganizationSerializer(top_organizations, many=True).data
        })

class AdminOrganizationViewSet(viewsets.ModelViewSet):
    """
    Admin interface for managing organizations
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend an organization"""
        organization = self.get_object()
        organization.subscription_status = 'suspended'
        organization.save()
        
        return Response({'message': 'Organization suspended successfully'})
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate a suspended organization"""
        organization = self.get_object()
        organization.subscription_status = 'active'
        organization.save()
        
        return Response({'message': 'Organization reactivated successfully'})
    
    @action(detail=True, methods=['get'])
    def detailed_usage(self, request, pk=None):
        """Get detailed usage analytics for an organization"""
        organization = self.get_object()
        
        # Get usage data for the last 90 days
        ninety_days_ago = timezone.now() - timedelta(days=90)
        
        usage_by_type = UsageLog.objects.filter(
            organization=organization,
            created_at__gte=ninety_days_ago
        ).values('usage_type').annotate(count=Count('id'))
        
        # Daily usage for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_usage = UsageLog.objects.filter(
            organization=organization,
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # User activity
        user_activity = UsageLog.objects.filter(
            organization=organization,
            created_at__gte=thirty_days_ago
        ).values('user__email').annotate(count=Count('id')).order_by('-count')
        
        return Response({
            'usage_by_type': list(usage_by_type),
            'daily_usage': list(daily_usage),
            'user_activity': list(user_activity),
            'current_limits': {
                'datasets': {
                    'used': organization.current_month_datasets,
                    'limit': organization.subscription_plan.max_datasets_per_month
                },
                'api_calls': {
                    'used': organization.current_month_api_calls,
                    'limit': organization.subscription_plan.max_api_calls_per_month
                }
            }
        })

class AdminSubscriptionPlanViewSet(viewsets.ModelViewSet):
    """
    Admin interface for managing subscription plans
    """
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]

class AdminUsageAnalyticsView(APIView):
    """
    Platform-wide usage analytics for admins
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Usage trends
        usage_trends = UsageLog.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day', 'usage_type').annotate(count=Count('id')).order_by('day')
        
        # Top endpoints
        api_usage = UsageLog.objects.filter(
            usage_type='api_call',
            created_at__gte=start_date
        ).values('metadata__endpoint').annotate(count=Count('id')).order_by('-count')[:10]
        
        # Error rates
        error_rates = UsageLog.objects.filter(
            usage_type='api_call',
            created_at__gte=start_date
        ).values('metadata__status_code').annotate(count=Count('id'))
        
        return Response({
            'usage_trends': list(usage_trends),
            'top_endpoints': list(api_usage),
            'error_rates': list(error_rates)
        })

class AdminBillingView(APIView):
    """
    Admin billing and revenue analytics
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Revenue by month
        revenue_by_month = BillingHistory.objects.filter(
            status='paid'
        ).extra(
            select={'month': "date_trunc('month', created_at)"}
        ).values('month').annotate(
            total_revenue=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('month')
        
        # Revenue by plan
        revenue_by_plan = BillingHistory.objects.filter(
            status='paid'
        ).values(
            'organization__subscription_plan__display_name'
        ).annotate(
            total_revenue=Sum('amount'),
            organization_count=Count('organization', distinct=True)
        )
        
        # Failed payments
        failed_payments = BillingHistory.objects.filter(
            status__in=['failed', 'requires_action']
        ).count()
        
        return Response({
            'revenue_by_month': list(revenue_by_month),
            'revenue_by_plan': list(revenue_by_plan),
            'failed_payments': failed_payments
        })
