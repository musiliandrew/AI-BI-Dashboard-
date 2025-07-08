from django.core.management.base import BaseCommand
from apps.organizations.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Create default subscription plans for the SaaS platform'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'starter',
                'display_name': 'Starter',
                'price_monthly': 0.00,
                'price_yearly': 0.00,
                'max_datasets_per_month': 5,
                'max_dashboards': 1,
                'max_api_calls_per_month': 100,
                'max_users_per_org': 1,
                'has_advanced_analytics': False,
                'has_custom_models': False,
                'has_api_access': False,
                'has_sso': False,
                'has_white_label': False,
            },
            {
                'name': 'professional',
                'display_name': 'Professional',
                'price_monthly': 49.00,
                'price_yearly': 490.00,  # 2 months free
                'max_datasets_per_month': 100,
                'max_dashboards': 10,
                'max_api_calls_per_month': 10000,
                'max_users_per_org': 5,
                'has_advanced_analytics': True,
                'has_custom_models': False,
                'has_api_access': True,
                'has_sso': False,
                'has_white_label': False,
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise',
                'price_monthly': 199.00,
                'price_yearly': 1990.00,  # 2 months free
                'max_datasets_per_month': 999999,  # Unlimited
                'max_dashboards': 999999,  # Unlimited
                'max_api_calls_per_month': 999999,  # Unlimited
                'max_users_per_org': 50,
                'has_advanced_analytics': True,
                'has_custom_models': True,
                'has_api_access': True,
                'has_sso': True,
                'has_white_label': True,
            }
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created subscription plan: {plan.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Subscription plan already exists: {plan.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created/verified all subscription plans!')
        )
