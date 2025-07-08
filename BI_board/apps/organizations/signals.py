from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.data_ingestion.models import UploadedData
from apps.analytics.models import AnalysisResults
from .models import Organization, OrganizationMembership, UsageLog

User = get_user_model()

@receiver(post_save, sender=UploadedData)
def track_dataset_upload(sender, instance, created, **kwargs):
    """Track when a dataset is uploaded"""
    if created and instance.user:
        # Get user's organization
        membership = OrganizationMembership.objects.filter(user=instance.user).first()
        if membership:
            # Create usage log
            UsageLog.objects.create(
                organization=membership.organization,
                user=instance.user,
                usage_type='dataset_upload',
                metadata={
                    'file_type': instance.file_type,
                    'file_size': getattr(instance.file, 'size', 0)
                }
            )
            
            # Update organization counter
            org = membership.organization
            org.current_month_datasets += 1
            org.save(update_fields=['current_month_datasets'])

@receiver(post_save, sender=AnalysisResults)
def track_analysis_run(sender, instance, created, **kwargs):
    """Track when an analysis is run"""
    if created and instance.processed_data and instance.processed_data.uploaded_data:
        user = instance.processed_data.uploaded_data.user
        if user:
            membership = OrganizationMembership.objects.filter(user=user).first()
            if membership:
                UsageLog.objects.create(
                    organization=membership.organization,
                    user=user,
                    usage_type='analysis_run',
                    metadata={
                        'analysis_type': getattr(instance, 'name', 'unknown'),
                        'processing_time': instance.processing_time
                    }
                )

@receiver(post_save, sender=OrganizationMembership)
def update_organization_user_count(sender, instance, created, **kwargs):
    """Update organization user count when membership changes"""
    if created:
        org = instance.organization
        org.total_users = org.memberships.count()
        org.save(update_fields=['total_users'])

@receiver(post_delete, sender=OrganizationMembership)
def update_organization_user_count_on_delete(sender, instance, **kwargs):
    """Update organization user count when membership is deleted"""
    org = instance.organization
    org.total_users = org.memberships.count()
    org.save(update_fields=['total_users'])

@receiver(post_save, sender=User)
def create_default_organization_for_new_user(sender, instance, created, **kwargs):
    """Create a default organization for new users (optional)"""
    if created:
        # Only create if user doesn't already have an organization
        if not OrganizationMembership.objects.filter(user=instance).exists():
            # Get the starter plan
            from .models import SubscriptionPlan
            try:
                starter_plan = SubscriptionPlan.objects.get(name='starter')
                
                # Create organization
                org = Organization.objects.create(
                    name=f"{instance.username}'s Organization",
                    slug=f"{instance.username}-org",
                    subscription_plan=starter_plan
                )
                
                # Create membership
                OrganizationMembership.objects.create(
                    organization=org,
                    user=instance,
                    role='owner',
                    can_manage_users=True,
                    can_manage_billing=True,
                    can_create_dashboards=True,
                    can_upload_data=True,
                    can_use_api=False  # API access only for paid plans
                )
            except SubscriptionPlan.DoesNotExist:
                pass  # Skip if starter plan doesn't exist
