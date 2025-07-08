from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import uuid

User = get_user_model()

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'), 
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage Limits
    max_datasets_per_month = models.IntegerField(validators=[MinValueValidator(0)])
    max_dashboards = models.IntegerField(validators=[MinValueValidator(0)])
    max_api_calls_per_month = models.IntegerField(validators=[MinValueValidator(0)])
    max_users_per_org = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Features
    has_advanced_analytics = models.BooleanField(default=False)
    has_custom_models = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_sso = models.BooleanField(default=False)
    has_white_label = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscription_plans'
    
    def __str__(self):
        return self.display_name

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    # Subscription Info
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, default='active')
    subscription_start_date = models.DateTimeField(auto_now_add=True)
    subscription_end_date = models.DateTimeField(blank=True, null=True)
    
    # Usage Tracking
    current_month_datasets = models.IntegerField(default=0)
    current_month_api_calls = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    
    # Settings
    settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
    
    def __str__(self):
        return self.name
    
    def is_usage_limit_reached(self, usage_type):
        """Check if organization has reached usage limits"""
        if usage_type == 'datasets':
            return self.current_month_datasets >= self.subscription_plan.max_datasets_per_month
        elif usage_type == 'api_calls':
            return self.current_month_api_calls >= self.subscription_plan.max_api_calls_per_month
        elif usage_type == 'users':
            return self.total_users >= self.subscription_plan.max_users_per_org
        return False

class OrganizationMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Permissions
    can_manage_users = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_create_dashboards = models.BooleanField(default=True)
    can_upload_data = models.BooleanField(default=True)
    can_use_api = models.BooleanField(default=False)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organization_memberships'
        unique_together = ['organization', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

class UsageLog(models.Model):
    USAGE_TYPES = [
        ('dataset_upload', 'Dataset Upload'),
        ('api_call', 'API Call'),
        ('analysis_run', 'Analysis Run'),
        ('dashboard_view', 'Dashboard View'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='usage_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    usage_type = models.CharField(max_length=50, choices=USAGE_TYPES)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)  # Store additional info
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'usage_logs'
        indexes = [
            models.Index(fields=['organization', 'usage_type', 'created_at']),
        ]

class BillingHistory(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='billing_history')
    
    stripe_invoice_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=50)
    
    billing_period_start = models.DateTimeField()
    billing_period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'billing_history'
