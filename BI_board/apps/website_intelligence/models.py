"""
Website Intelligence Models - Website analytics and data collection
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class WebsiteProperty(models.Model):
    """Client website properties for tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='website_properties')
    
    # Website info
    domain = models.CharField(max_length=255)
    website_name = models.CharField(max_length=200)
    website_url = models.URLField()
    
    # Business classification
    industry = models.CharField(max_length=50)  # automotive, retail, restaurant, etc.
    business_type = models.CharField(max_length=50, blank=True)  # dealership, e-commerce, etc.
    business_size = models.CharField(max_length=20, blank=True)  # small, medium, large
    
    # Analytics integrations
    google_analytics_id = models.CharField(max_length=50, blank=True)  # GA4 Property ID
    google_analytics_view_id = models.CharField(max_length=50, blank=True)
    search_console_property = models.CharField(max_length=255, blank=True)
    adobe_analytics_suite = models.CharField(max_length=50, blank=True)
    
    # Custom tracking
    tracking_script_installed = models.BooleanField(default=False)
    tracking_script_id = models.CharField(max_length=64, blank=True)
    
    # Website categorization
    WEBSITE_TYPES = [
        ('ecommerce', 'E-commerce Store'),
        ('lead_generation', 'Lead Generation'),
        ('informational', 'Informational/Blog'),
        ('portfolio', 'Portfolio/Showcase'),
        ('booking', 'Booking/Appointment'),
        ('directory', 'Directory/Listing'),
        ('saas', 'SaaS Application'),
        ('marketplace', 'Marketplace'),
    ]
    website_type = models.CharField(max_length=20, choices=WEBSITE_TYPES, blank=True)
    
    # Technology stack (auto-detected)
    cms_platform = models.CharField(max_length=50, blank=True)  # WordPress, Shopify, etc.
    ecommerce_platform = models.CharField(max_length=50, blank=True)  # WooCommerce, Shopify, etc.
    analytics_platforms = models.JSONField(default=list)  # Detected analytics tools
    marketing_tools = models.JSONField(default=list)  # Detected marketing tools
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(max_length=20, default='daily')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'domain']
    
    def __str__(self):
        return f"{self.website_name} ({self.domain})"

class WebsiteMetrics(models.Model):
    """Daily website metrics and performance data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='metrics')
    
    # Date and source
    date = models.DateField()
    data_source = models.CharField(max_length=30, default='google_analytics')  # GA, Adobe, custom
    
    # Traffic metrics
    sessions = models.IntegerField(default=0)
    users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    pageviews = models.IntegerField(default=0)
    unique_pageviews = models.IntegerField(default=0)
    
    # Engagement metrics
    avg_session_duration = models.FloatField(default=0)  # seconds
    bounce_rate = models.FloatField(default=0)  # percentage
    pages_per_session = models.FloatField(default=0)
    
    # Conversion metrics
    goal_completions = models.IntegerField(default=0)
    goal_conversion_rate = models.FloatField(default=0)
    ecommerce_transactions = models.IntegerField(default=0)
    ecommerce_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Traffic sources
    organic_traffic = models.IntegerField(default=0)
    paid_traffic = models.IntegerField(default=0)
    social_traffic = models.IntegerField(default=0)
    direct_traffic = models.IntegerField(default=0)
    referral_traffic = models.IntegerField(default=0)
    email_traffic = models.IntegerField(default=0)
    
    # Device breakdown
    desktop_sessions = models.IntegerField(default=0)
    mobile_sessions = models.IntegerField(default=0)
    tablet_sessions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['website', 'date', 'data_source']
        indexes = [
            models.Index(fields=['website', 'date']),
            models.Index(fields=['date', 'data_source']),
        ]

class WebsitePage(models.Model):
    """Individual page performance tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='pages')
    
    # Page info
    page_path = models.CharField(max_length=500)
    page_title = models.CharField(max_length=200, blank=True)
    page_url = models.URLField()
    
    # Page categorization
    PAGE_TYPES = [
        ('homepage', 'Homepage'),
        ('product', 'Product Page'),
        ('category', 'Category Page'),
        ('blog', 'Blog Post'),
        ('contact', 'Contact Page'),
        ('about', 'About Page'),
        ('checkout', 'Checkout Page'),
        ('landing', 'Landing Page'),
        ('service', 'Service Page'),
        ('other', 'Other'),
    ]
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, default='other')
    
    # Content analysis
    content_category = models.CharField(max_length=50, blank=True)  # Auto-categorized
    keywords = models.JSONField(default=list)  # Extracted keywords
    content_length = models.IntegerField(default=0)  # Word count
    
    # Performance metrics (latest)
    monthly_pageviews = models.IntegerField(default=0)
    monthly_unique_pageviews = models.IntegerField(default=0)
    avg_time_on_page = models.FloatField(default=0)
    bounce_rate = models.FloatField(default=0)
    exit_rate = models.FloatField(default=0)
    
    # SEO metrics
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    h1_tag = models.CharField(max_length=200, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_crawled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['website', 'page_path']

class ConversionGoal(models.Model):
    """Website conversion goals and tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='conversion_goals')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Goal configuration
    GOAL_TYPES = [
        ('destination', 'Destination (Page Visit)'),
        ('duration', 'Duration (Time on Site)'),
        ('pages_per_session', 'Pages per Session'),
        ('event', 'Event (Custom Action)'),
        ('ecommerce', 'E-commerce Transaction'),
    ]
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    
    # Goal parameters
    goal_config = models.JSONField(default=dict)  # Type-specific configuration
    goal_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Performance tracking
    monthly_completions = models.IntegerField(default=0)
    monthly_conversion_rate = models.FloatField(default=0)
    monthly_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WebsiteEvent(models.Model):
    """Custom website events and user interactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    event_name = models.CharField(max_length=100)
    event_category = models.CharField(max_length=50, blank=True)
    event_action = models.CharField(max_length=100, blank=True)
    event_label = models.CharField(max_length=200, blank=True)
    
    # Event data
    event_value = models.FloatField(null=True, blank=True)
    event_parameters = models.JSONField(default=dict)
    
    # Context
    page_path = models.CharField(max_length=500, blank=True)
    user_id = models.CharField(max_length=100, blank=True)  # Anonymous user ID
    session_id = models.CharField(max_length=100, blank=True)
    
    # Device and source
    device_category = models.CharField(max_length=20, blank=True)
    traffic_source = models.CharField(max_length=50, blank=True)
    campaign = models.CharField(max_length=100, blank=True)
    
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['website', 'timestamp']),
            models.Index(fields=['event_name', 'timestamp']),
        ]

class WebsiteInsight(models.Model):
    """AI-generated insights from website data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='insights')
    
    # Insight details
    INSIGHT_TYPES = [
        ('traffic_pattern', 'Traffic Pattern Analysis'),
        ('conversion_optimization', 'Conversion Optimization'),
        ('content_performance', 'Content Performance'),
        ('user_behavior', 'User Behavior Analysis'),
        ('technical_seo', 'Technical SEO'),
        ('mobile_optimization', 'Mobile Optimization'),
        ('page_speed', 'Page Speed Analysis'),
        ('social_integration', 'Social Media Integration'),
    ]
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField()  # 0-1
    
    # Data evidence
    data_points = models.JSONField(default=dict)
    affected_pages = models.JSONField(default=list)
    
    # Recommendations
    action_items = models.JSONField(default=list)
    expected_impact = models.CharField(max_length=200, blank=True)
    priority = models.CharField(max_length=10, default='medium')  # low, medium, high
    
    # Context
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)

class CrossPlatformAttribution(models.Model):
    """Attribution tracking across social media and website"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='attributions')
    
    # Attribution details
    user_journey_id = models.CharField(max_length=100)  # Unique journey identifier
    
    # Social media touchpoint
    social_platform = models.CharField(max_length=20, blank=True)
    social_post_id = models.CharField(max_length=100, blank=True)
    social_campaign = models.CharField(max_length=100, blank=True)
    
    # Website interaction
    landing_page = models.CharField(max_length=500)
    pages_visited = models.JSONField(default=list)
    session_duration = models.FloatField(default=0)
    
    # Conversion
    converted = models.BooleanField(default=False)
    conversion_goal = models.CharField(max_length=100, blank=True)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timing
    social_interaction_time = models.DateTimeField()
    website_visit_time = models.DateTimeField()
    conversion_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['website', 'social_platform']),
            models.Index(fields=['user_journey_id']),
        ]

class WebsiteTechnology(models.Model):
    """Detected website technologies and tools"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='technologies')
    
    # Technology details
    TECH_CATEGORIES = [
        ('cms', 'Content Management System'),
        ('ecommerce', 'E-commerce Platform'),
        ('analytics', 'Analytics Tool'),
        ('marketing', 'Marketing Tool'),
        ('advertising', 'Advertising Platform'),
        ('social', 'Social Media Integration'),
        ('payment', 'Payment Processor'),
        ('security', 'Security Tool'),
        ('performance', 'Performance Tool'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=TECH_CATEGORIES)
    
    technology_name = models.CharField(max_length=100)
    version = models.CharField(max_length=50, blank=True)
    confidence = models.FloatField(default=0)  # Detection confidence 0-1
    
    # Detection details
    detection_method = models.CharField(max_length=50, blank=True)  # headers, scripts, etc.
    evidence = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_detected_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['website', 'technology_name']

class WebsiteAudit(models.Model):
    """Comprehensive website audits and recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(WebsiteProperty, on_delete=models.CASCADE, related_name='audits')
    
    audit_name = models.CharField(max_length=200)
    audit_type = models.CharField(max_length=50)  # seo, performance, conversion, etc.
    
    # Audit results
    overall_score = models.FloatField(default=0)  # 0-100
    category_scores = models.JSONField(default=dict)  # Scores by category
    
    # Findings
    issues_found = models.JSONField(default=list)
    opportunities = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Audit metadata
    audit_config = models.JSONField(default=dict)
    pages_audited = models.IntegerField(default=0)
    audit_duration = models.FloatField(default=0)  # seconds
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
