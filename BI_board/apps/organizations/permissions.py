from rest_framework import permissions
from .models import OrganizationMembership

class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from URL or request data
        org_id = view.kwargs.get('organization_pk') or request.data.get('organization_id')
        if not org_id:
            return False
        
        return OrganizationMembership.objects.filter(
            organization_id=org_id,
            user=request.user
        ).exists()

class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner or admin of the organization
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        org_id = view.kwargs.get('organization_pk') or request.data.get('organization_id')
        if not org_id:
            return False
        
        membership = OrganizationMembership.objects.filter(
            organization_id=org_id,
            user=request.user
        ).first()
        
        return membership and membership.role in ['owner', 'admin']

class CanManageUsers(permissions.BasePermission):
    """
    Permission to check if user can manage other users in the organization
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        org_id = view.kwargs.get('organization_pk') or request.data.get('organization_id')
        if not org_id:
            return False
        
        membership = OrganizationMembership.objects.filter(
            organization_id=org_id,
            user=request.user
        ).first()
        
        return membership and membership.can_manage_users

class CanManageBilling(permissions.BasePermission):
    """
    Permission to check if user can manage billing for the organization
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        org_id = view.kwargs.get('organization_pk') or request.data.get('organization_id')
        if not org_id:
            return False
        
        membership = OrganizationMembership.objects.filter(
            organization_id=org_id,
            user=request.user
        ).first()
        
        return membership and membership.can_manage_billing

class CanUploadData(permissions.BasePermission):
    """
    Permission to check if user can upload data to the organization
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from user's current context or request
        user_orgs = request.user.organization_memberships.filter(
            can_upload_data=True
        )
        
        return user_orgs.exists()

class CanUseAPI(permissions.BasePermission):
    """
    Permission to check if user can use API features
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has API access in any organization
        user_orgs = request.user.organization_memberships.filter(
            can_use_api=True,
            organization__subscription_plan__has_api_access=True
        )
        
        return user_orgs.exists()

class HasFeatureAccess(permissions.BasePermission):
    """
    Generic permission to check if user's organization has access to specific features
    """
    
    def __init__(self, feature_name):
        self.feature_name = feature_name
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get user's organizations with the required feature
        feature_field = f"has_{self.feature_name}"
        user_orgs = request.user.organization_memberships.filter(
            **{f"organization__subscription_plan__{feature_field}": True}
        )
        
        return user_orgs.exists()

# Specific feature permissions
class HasAdvancedAnalytics(HasFeatureAccess):
    def __init__(self):
        super().__init__('advanced_analytics')

class HasCustomModels(HasFeatureAccess):
    def __init__(self):
        super().__init__('custom_models')

class HasSSO(HasFeatureAccess):
    def __init__(self):
        super().__init__('sso')

class HasWhiteLabel(HasFeatureAccess):
    def __init__(self):
        super().__init__('white_label')
