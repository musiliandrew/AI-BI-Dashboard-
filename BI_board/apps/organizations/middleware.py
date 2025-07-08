from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .models import OrganizationMembership, UsageLog
import json
import time

class UsageTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track API usage and enforce rate limits
    """
    
    def process_request(self, request):
        # Skip tracking for non-API requests
        if not request.path.startswith('/api/') or not request.user.is_authenticated:
            return None
        
        # Get user's organization
        membership = OrganizationMembership.objects.filter(user=request.user).first()
        if not membership:
            return None
        
        organization = membership.organization
        
        # Check rate limits for API calls
        if self._is_rate_limited(organization, request):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Your organization has exceeded the API rate limit for this billing period.'
            }, status=429)
        
        # Store organization in request for later use
        request.organization = organization
        request.organization_membership = membership
        
        return None
    
    def process_response(self, request, response):
        # Track successful API calls
        if (hasattr(request, 'organization') and 
            request.path.startswith('/api/') and 
            200 <= response.status_code < 300):
            
            self._track_usage(request.organization, request.user, 'api_call', {
                'endpoint': request.path,
                'method': request.method,
                'status_code': response.status_code
            })
        
        return response
    
    def _is_rate_limited(self, organization, request):
        """Check if organization has exceeded rate limits"""
        
        # Skip rate limiting for certain endpoints
        skip_endpoints = ['/api/users/me/', '/api/organizations/']
        if any(request.path.startswith(endpoint) for endpoint in skip_endpoints):
            return False
        
        # Check monthly API limit
        if organization.is_usage_limit_reached('api_calls'):
            return True
        
        # Check per-minute rate limit (using Redis cache)
        cache_key = f"rate_limit:{organization.id}:{int(time.time() // 60)}"
        current_requests = cache.get(cache_key, 0)
        
        # Set per-minute limits based on subscription plan
        rate_limits = {
            'starter': 10,      # 10 requests per minute
            'professional': 100, # 100 requests per minute  
            'enterprise': 1000   # 1000 requests per minute
        }
        
        limit = rate_limits.get(organization.subscription_plan.name, 10)
        
        if current_requests >= limit:
            return True
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, timeout=60)
        return False
    
    def _track_usage(self, organization, user, usage_type, metadata=None):
        """Track usage in the database"""
        try:
            UsageLog.objects.create(
                organization=organization,
                user=user,
                usage_type=usage_type,
                metadata=metadata or {}
            )
            
            # Update organization counters
            if usage_type == 'api_call':
                organization.current_month_api_calls += 1
                organization.save(update_fields=['current_month_api_calls'])
                
        except Exception:
            # Don't fail the request if usage tracking fails
            pass

class OrganizationContextMiddleware(MiddlewareMixin):
    """
    Middleware to add organization context to requests
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Get user's primary organization (first one they're a member of)
            membership = OrganizationMembership.objects.filter(
                user=request.user
            ).select_related('organization').first()
            
            if membership:
                request.current_organization = membership.organization
                request.current_membership = membership
            else:
                request.current_organization = None
                request.current_membership = None
        
        return None

class FeatureAccessMiddleware(MiddlewareMixin):
    """
    Middleware to check feature access for specific endpoints
    """
    
    # Map endpoints to required features
    FEATURE_ENDPOINTS = {
        '/api/analytics/advanced/': 'has_advanced_analytics',
        '/api/models/custom/': 'has_custom_models',
        '/api/auth/sso/': 'has_sso',
    }
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        # Check if endpoint requires specific features
        for endpoint, feature in self.FEATURE_ENDPOINTS.items():
            if request.path.startswith(endpoint):
                if not self._has_feature_access(request.user, feature):
                    return JsonResponse({
                        'error': 'Feature not available',
                        'message': 'This feature is not available in your current subscription plan.',
                        'upgrade_required': True
                    }, status=403)
        
        return None
    
    def _has_feature_access(self, user, feature):
        """Check if user has access to a specific feature"""
        return OrganizationMembership.objects.filter(
            user=user,
            **{f"organization__subscription_plan__{feature}": True}
        ).exists()
