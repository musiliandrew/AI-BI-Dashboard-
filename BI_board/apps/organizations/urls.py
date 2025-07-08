from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    OrganizationViewSet, OrganizationMembershipViewSet, SubscriptionPlanViewSet,
    BillingView, StripeWebhookView, CreateCheckoutSessionView
)
from .admin_views import (
    AdminDashboardView, AdminOrganizationViewSet, AdminSubscriptionPlanViewSet,
    AdminUsageAnalyticsView, AdminBillingView
)

# Main router
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plans')

# Nested router for organization memberships
organizations_router = routers.NestedDefaultRouter(router, r'organizations', lookup='organization')
organizations_router.register(r'members', OrganizationMembershipViewSet, basename='organization-members')

# Admin routes
admin_router = DefaultRouter()
admin_router.register(r'admin/organizations', AdminOrganizationViewSet, basename='admin-organizations')
admin_router.register(r'admin/subscription-plans', AdminSubscriptionPlanViewSet, basename='admin-subscription-plans')

urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    path('', include(organizations_router.urls)),
    
    # Billing routes
    path('billing/<uuid:organization_id>/', BillingView.as_view(), name='billing'),
    path('billing/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Admin routes
    path('', include(admin_router.urls)),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/usage-analytics/', AdminUsageAnalyticsView.as_view(), name='admin-usage-analytics'),
    path('admin/billing/', AdminBillingView.as_view(), name='admin-billing'),
]
