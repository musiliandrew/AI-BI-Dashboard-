"""
Social Media Intelligence Models
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class SocialAccount(models.Model):
    """Social media account tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    
    # Platform info
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest'),
        ('snapchat', 'Snapchat'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_account_id = models.CharField(max_length=100)  # Platform's internal ID
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True)
    
    # Business info
    industry = models.CharField(max_length=50, blank=True)  # automotive, retail, etc.
    business_type = models.CharField(max_length=50, blank=True)  # dealership, restaurant, etc.
    location = models.CharField(max_length=100, blank=True)
    
    # Account metrics
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    
    # API access
    access_token = models.TextField(blank=True)  # Encrypted
    refresh_token = models.TextField(blank=True)  # Encrypted
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(max_length=20, default='daily')  # hourly, daily, weekly
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['platform', 'platform_account_id']
    
    def __str__(self):
        return f"{self.platform}: @{self.username}"

class SocialPost(models.Model):
    """Individual social media posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, related_name='posts')
    
    # Post identification
    platform_post_id = models.CharField(max_length=100)
    post_url = models.URLField(blank=True)
    
    # Content
    content_text = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, default='post')  # post, story, reel, video, etc.
    media_urls = models.JSONField(default=list)  # Images, videos
    hashtags = models.JSONField(default=list)
    mentions = models.JSONField(default=list)
    
    # Engagement metrics
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    saves_count = models.IntegerField(default=0)
    
    # AI analysis
    sentiment_score = models.FloatField(null=True, blank=True)  # -1 to 1
    engagement_rate = models.FloatField(null=True, blank=True)
    reach_estimate = models.IntegerField(null=True, blank=True)
    
    # Timing
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['account', 'platform_post_id']
        indexes = [
            models.Index(fields=['account', 'posted_at']),
            models.Index(fields=['posted_at', 'engagement_rate']),
        ]

class SocialComment(models.Model):
    """Comments on social media posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name='comments')
    
    platform_comment_id = models.CharField(max_length=100)
    author_username = models.CharField(max_length=100)
    author_display_name = models.CharField(max_length=200, blank=True)
    
    content = models.TextField()
    likes_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    
    # AI analysis
    sentiment_score = models.FloatField(null=True, blank=True)
    is_spam = models.BooleanField(default=False)
    is_customer_service = models.BooleanField(default=False)
    
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class CompetitorAccount(models.Model):
    """Competitor social media accounts for benchmarking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competitor_accounts')
    
    # Competitor info
    platform = models.CharField(max_length=20, choices=SocialAccount.PLATFORM_CHOICES)
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True)
    
    # Business classification
    industry = models.CharField(max_length=50)
    business_type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    estimated_size = models.CharField(max_length=20, blank=True)  # small, medium, large
    
    # Tracking
    is_active = models.BooleanField(default=True)
    last_analyzed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Competitor: {self.platform} @{self.username}"

class SocialCampaign(models.Model):
    """Social media campaigns and their performance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_campaigns')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Campaign details
    CAMPAIGN_TYPES = [
        ('awareness', 'Brand Awareness'),
        ('engagement', 'Engagement'),
        ('traffic', 'Website Traffic'),
        ('leads', 'Lead Generation'),
        ('sales', 'Sales/Conversions'),
        ('app_installs', 'App Installs'),
    ]
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    
    platforms = models.JSONField(default=list)  # Which platforms
    target_audience = models.JSONField(default=dict)  # Demographics, interests
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timeline
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Performance tracking
    impressions = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    cost_per_click = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    cost_per_conversion = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SocialInsight(models.Model):
    """AI-generated insights from social media data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_insights')
    
    # Insight details
    INSIGHT_TYPES = [
        ('content_performance', 'Content Performance'),
        ('audience_analysis', 'Audience Analysis'),
        ('competitor_benchmark', 'Competitor Benchmarking'),
        ('optimal_timing', 'Optimal Posting Times'),
        ('hashtag_analysis', 'Hashtag Performance'),
        ('sentiment_trend', 'Sentiment Trends'),
        ('engagement_pattern', 'Engagement Patterns'),
        ('growth_opportunity', 'Growth Opportunities'),
    ]
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField()  # 0-1
    
    # Data evidence
    data_points = models.JSONField(default=dict)
    visualization_config = models.JSONField(default=dict)
    
    # Recommendations
    action_items = models.JSONField(default=list)
    expected_impact = models.CharField(max_length=200, blank=True)
    
    # Context
    platforms = models.JSONField(default=list)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)

class SocialReport(models.Model):
    """Generated social media reports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_reports')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Report configuration
    REPORT_TYPES = [
        ('performance', 'Performance Report'),
        ('competitor', 'Competitor Analysis'),
        ('campaign', 'Campaign Report'),
        ('audience', 'Audience Insights'),
        ('content', 'Content Analysis'),
        ('roi', 'ROI Analysis'),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    
    platforms = models.JSONField(default=list)
    accounts = models.JSONField(default=list)  # Account IDs
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    # Report data
    metrics = models.JSONField(default=dict)
    insights = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    share_token = models.CharField(max_length=64, blank=True)
    
    # Automation
    is_automated = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    next_generation = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SocialAlert(models.Model):
    """Real-time alerts for social media monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_alerts')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Alert conditions
    ALERT_TYPES = [
        ('mention', 'Brand Mention'),
        ('sentiment_drop', 'Sentiment Drop'),
        ('viral_content', 'Viral Content'),
        ('competitor_activity', 'Competitor Activity'),
        ('engagement_spike', 'Engagement Spike'),
        ('negative_comment', 'Negative Comment'),
        ('crisis_detection', 'Crisis Detection'),
    ]
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    
    conditions = models.JSONField(default=dict)  # Threshold values, keywords, etc.
    platforms = models.JSONField(default=list)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    webhook_url = models.URLField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
