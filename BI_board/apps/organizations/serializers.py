from rest_framework import serializers
from .models import Organization, OrganizationMembership, SubscriptionPlan, UsageLog, BillingHistory

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class OrganizationSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'subscription_plan', 'subscription_status',
            'current_month_datasets', 'current_month_api_calls', 'total_users',
            'usage_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'current_month_datasets', 'current_month_api_calls', 'total_users']
    
    def get_usage_percentage(self, obj):
        """Calculate usage percentages for different metrics"""
        plan = obj.subscription_plan
        return {
            'datasets': (obj.current_month_datasets / plan.max_datasets_per_month * 100) if plan.max_datasets_per_month > 0 else 0,
            'api_calls': (obj.current_month_api_calls / plan.max_api_calls_per_month * 100) if plan.max_api_calls_per_month > 0 else 0,
            'users': (obj.total_users / plan.max_users_per_org * 100) if plan.max_users_per_org > 0 else 0,
        }

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role',
            'can_manage_users', 'can_manage_billing', 'can_create_dashboards',
            'can_upload_data', 'can_use_api', 'joined_at'
        ]

class UsageLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UsageLog
        fields = ['id', 'usage_type', 'user_email', 'metadata', 'created_at']

class BillingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingHistory
        fields = '__all__'

class OrganizationCreateSerializer(serializers.ModelSerializer):
    subscription_plan_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'subscription_plan_name']
    
    def create(self, validated_data):
        plan_name = validated_data.pop('subscription_plan_name')
        try:
            plan = SubscriptionPlan.objects.get(name=plan_name)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError(f"Subscription plan '{plan_name}' does not exist")
        
        organization = Organization.objects.create(
            subscription_plan=plan,
            **validated_data
        )
        
        # Create owner membership for the user
        user = self.context['request'].user
        OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role='owner',
            can_manage_users=True,
            can_manage_billing=True,
            can_create_dashboards=True,
            can_upload_data=True,
            can_use_api=True
        )
        
        return organization
