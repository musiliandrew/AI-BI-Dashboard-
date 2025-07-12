"""
Global Payment Infrastructure Models
Supporting 20+ payment providers across all major markets
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json

class PaymentProvider(models.Model):
    """Payment provider configuration and capabilities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Provider details
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=30)  # gateway, wallet, bank_transfer, etc.
    
    # Regional coverage
    REGIONS = [
        ('north_america', 'North America'),
        ('europe', 'Europe'),
        ('africa', 'Africa'),
        ('asia_pacific', 'Asia Pacific'),
        ('latin_america', 'Latin America'),
        ('oceania', 'Oceania'),
        ('global', 'Global'),
    ]
    primary_region = models.CharField(max_length=20, choices=REGIONS)
    supported_countries = models.JSONField(default=list)  # ISO country codes
    
    # Supported currencies
    supported_currencies = models.JSONField(default=list)  # ISO currency codes
    
    # Capabilities
    supports_subscriptions = models.BooleanField(default=False)
    supports_marketplace = models.BooleanField(default=False)
    supports_mobile_money = models.BooleanField(default=False)
    supports_bank_transfer = models.BooleanField(default=False)
    supports_digital_wallets = models.BooleanField(default=False)
    supports_buy_now_pay_later = models.BooleanField(default=False)
    
    # Fees and limits
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    transaction_fee_fixed = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    min_transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # API configuration
    api_base_url = models.URLField()
    webhook_url_pattern = models.CharField(max_length=200, blank=True)
    requires_3ds = models.BooleanField(default=False)  # 3D Secure
    
    # Status
    is_active = models.BooleanField(default=True)
    is_sandbox = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.display_name} ({self.primary_region})"

class PaymentAccount(models.Model):
    """User's payment account configuration for each provider"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_accounts')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    
    # Account details
    account_name = models.CharField(max_length=200)
    merchant_id = models.CharField(max_length=100, blank=True)
    
    # API credentials (encrypted)
    api_key = models.TextField(blank=True)
    api_secret = models.TextField(blank=True)
    webhook_secret = models.TextField(blank=True)
    
    # Account configuration
    default_currency = models.CharField(max_length=3, default='USD')  # ISO currency code
    auto_capture = models.BooleanField(default=True)
    
    # Business information
    business_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(max_length=50, blank=True)
    business_country = models.CharField(max_length=2, blank=True)  # ISO country code
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, default='pending')
    
    # Limits
    daily_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.display_name}"

class PaymentTransaction(models.Model):
    """Individual payment transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Transaction identification
    transaction_id = models.CharField(max_length=100, unique=True)  # Our internal ID
    provider_transaction_id = models.CharField(max_length=200, blank=True)  # Provider's ID
    
    # Parties
    payment_account = models.ForeignKey(PaymentAccount, on_delete=models.CASCADE, related_name='transactions')
    customer_email = models.EmailField(blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    
    # Transaction details
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Payment'),
        ('one_time', 'One-time Payment'),
        ('refund', 'Refund'),
        ('chargeback', 'Chargeback'),
        ('transfer', 'Transfer'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Amounts
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)  # ISO currency code
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Converted amount
    
    # Fees
    provider_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment method
    payment_method_type = models.CharField(max_length=30, blank=True)  # card, bank_transfer, mobile_money, etc.
    payment_method_details = models.JSONField(default=dict)  # Last 4 digits, bank name, etc.
    
    # Risk and fraud
    risk_score = models.FloatField(null=True, blank=True)  # 0-1
    fraud_check_result = models.CharField(max_length=20, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    subscription_id = models.CharField(max_length=100, blank=True)
    invoice_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['payment_account', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"

class Subscription(models.Model):
    """Recurring subscription management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Subscription identification
    subscription_id = models.CharField(max_length=100, unique=True)
    provider_subscription_id = models.CharField(max_length=200, blank=True)
    
    # Parties
    payment_account = models.ForeignKey(PaymentAccount, on_delete=models.CASCADE, related_name='subscriptions')
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200, blank=True)
    
    # Subscription details
    plan_name = models.CharField(max_length=200)
    plan_id = models.CharField(max_length=100)
    
    # Billing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    
    BILLING_INTERVALS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    billing_interval = models.CharField(max_length=20, choices=BILLING_INTERVALS)
    billing_interval_count = models.IntegerField(default=1)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
        ('paused', 'Paused'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timing
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    next_billing_date = models.DateTimeField()
    
    # Cancellation
    cancel_at_period_end = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=200, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subscription_id} - {self.plan_name}"

class PaymentWebhook(models.Model):
    """Webhook events from payment providers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Webhook details
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    webhook_id = models.CharField(max_length=200, blank=True)  # Provider's webhook ID
    
    # Event details
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField(default=dict)
    
    # Processing
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Related transaction
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Verification
    signature_verified = models.BooleanField(default=False)
    
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['provider', 'received_at']),
            models.Index(fields=['processed', 'received_at']),
        ]

class PaymentAnalytics(models.Model):
    """Daily payment analytics aggregation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Scope
    payment_account = models.ForeignKey(PaymentAccount, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Volume metrics
    total_transactions = models.IntegerField(default=0)
    successful_transactions = models.IntegerField(default=0)
    failed_transactions = models.IntegerField(default=0)
    
    # Revenue metrics
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Performance metrics
    success_rate = models.FloatField(default=0)  # Percentage
    average_transaction_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment method breakdown
    payment_method_breakdown = models.JSONField(default=dict)
    
    # Currency breakdown
    currency_breakdown = models.JSONField(default=dict)
    
    # Subscription metrics
    new_subscriptions = models.IntegerField(default=0)
    cancelled_subscriptions = models.IntegerField(default=0)
    subscription_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['payment_account', 'date']
        indexes = [
            models.Index(fields=['payment_account', 'date']),
        ]

class CurrencyExchangeRate(models.Model):
    """Currency exchange rates for conversion"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    from_currency = models.CharField(max_length=3)  # ISO currency code
    to_currency = models.CharField(max_length=3)    # ISO currency code
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    
    # Source and timing
    source = models.CharField(max_length=50, default='fixer.io')  # Exchange rate API
    date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency', 'date']
        indexes = [
            models.Index(fields=['from_currency', 'to_currency', 'date']),
        ]

class PaymentDispute(models.Model):
    """Payment disputes and chargebacks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Related transaction
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='disputes')
    provider_dispute_id = models.CharField(max_length=200)
    
    # Dispute details
    DISPUTE_TYPES = [
        ('chargeback', 'Chargeback'),
        ('inquiry', 'Inquiry'),
        ('retrieval', 'Retrieval Request'),
        ('fraud', 'Fraud'),
    ]
    dispute_type = models.CharField(max_length=20, choices=DISPUTE_TYPES)
    
    reason = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    
    # Status
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('accepted', 'Accepted'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Evidence
    evidence_submitted = models.BooleanField(default=False)
    evidence_due_date = models.DateTimeField(null=True, blank=True)
    
    # Timing
    disputed_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
