from django.db import models
from apps.users.models import Users
from apps.data_ingestion.models import ProcessedData
from apps.analytics.models import AnalysisResults
import uuid

class UserContext(models.Model):
    """Store user's business context and preferences"""
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='ai_context')
    
    # Business Context
    business_type = models.CharField(max_length=100, blank=True)  # e.g., "e-commerce", "restaurant"
    industry = models.CharField(max_length=100, blank=True)  # e.g., "retail", "finance"
    company_size = models.CharField(max_length=50, blank=True)  # e.g., "1-10 employees"
    main_goals = models.JSONField(default=list, blank=True)  # e.g., ["increase sales", "reduce costs"]
    
    # AI Preferences
    communication_style = models.CharField(max_length=50, default='friendly')  # friendly, professional, technical
    detail_level = models.CharField(max_length=50, default='medium')  # brief, medium, detailed
    preferred_insights = models.JSONField(default=list, blank=True)  # types of insights user likes
    
    # Learning Data
    common_questions = models.JSONField(default=list, blank=True)
    interaction_patterns = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_context'

class ChatSession(models.Model):
    """Individual chat sessions with the AI"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='chat_sessions')
    
    # Session Context
    title = models.CharField(max_length=255, blank=True)  # Auto-generated from first message
    dataset_context = models.ForeignKey(ProcessedData, on_delete=models.SET_NULL, null=True, blank=True)
    analysis_context = models.ForeignKey(AnalysisResults, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session State
    is_active = models.BooleanField(default=True)
    session_summary = models.TextField(blank=True)  # AI-generated summary
    key_insights_discussed = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    """Individual messages in a chat session"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('ai', 'AI Response'),
        ('system', 'System Message'),
        ('insight', 'Data Insight'),
        ('visualization', 'Chart/Graph'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    
    # Message Content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store charts, analysis results, etc.
    
    # Context
    triggered_analysis = models.ForeignKey(AnalysisResults, on_delete=models.SET_NULL, null=True, blank=True)
    referenced_data = models.JSONField(default=dict, blank=True)  # Data points referenced
    
    # AI Processing
    intent_detected = models.CharField(max_length=100, blank=True)  # e.g., "ask_about_trends"
    confidence_score = models.FloatField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

class DataInsight(models.Model):
    """Store discovered insights for reuse and learning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Insight Content
    insight_type = models.CharField(max_length=50)  # trend, anomaly, correlation, etc.
    title = models.CharField(max_length=255)
    description = models.TextField()
    business_impact = models.TextField(blank=True)
    recommended_actions = models.JSONField(default=list, blank=True)
    
    # Data Context
    source_analysis = models.ForeignKey(AnalysisResults, on_delete=models.CASCADE)
    data_points = models.JSONField(default=dict, blank=True)  # Specific data supporting insight
    confidence_level = models.FloatField()  # 0.0 to 1.0
    
    # Usage Tracking
    times_referenced = models.IntegerField(default=0)
    user_feedback = models.JSONField(default=dict, blank=True)  # helpful, not_helpful, etc.
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_insights'
        ordering = ['-confidence_level', '-created_at']

class AIPersonality(models.Model):
    """Configure AI personality and behavior"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Personality Traits
    communication_style = models.JSONField(default=dict)  # tone, formality, etc.
    expertise_areas = models.JSONField(default=list)  # sales, marketing, finance, etc.
    response_patterns = models.JSONField(default=dict)  # how to structure responses
    
    # Behavior Settings
    proactivity_level = models.FloatField(default=0.7)  # How often to suggest insights
    explanation_depth = models.CharField(max_length=50, default='medium')
    use_business_language = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_personalities'

class ConversationFlow(models.Model):
    """Define conversation flows for different scenarios"""
    name = models.CharField(max_length=100)
    trigger_conditions = models.JSONField(default=dict)  # When to use this flow
    
    # Flow Definition
    steps = models.JSONField(default=list)  # Conversation steps
    questions_to_ask = models.JSONField(default=list)  # Proactive questions
    insights_to_highlight = models.JSONField(default=list)  # Key insights to mention
    
    # Success Metrics
    completion_rate = models.FloatField(default=0.0)
    user_satisfaction = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_flows'
