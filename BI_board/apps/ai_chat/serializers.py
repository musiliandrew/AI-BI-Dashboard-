from rest_framework import serializers
from .models import UserContext, ChatSession, ChatMessage, DataInsight, AIPersonality

class UserContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContext
        fields = [
            'business_type', 'industry', 'company_size', 'main_goals',
            'communication_style', 'detail_level', 'preferred_insights',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message_type', 'content', 'metadata',
            'intent_detected', 'confidence_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'is_active', 'session_summary',
            'key_insights_discussed', 'created_at', 'updated_at',
            'messages', 'message_count', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_activity(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else obj.updated_at

class DataInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataInsight
        fields = [
            'id', 'insight_type', 'title', 'description',
            'business_impact', 'recommended_actions', 'confidence_level',
            'times_referenced', 'created_at'
        ]
        read_only_fields = ['id', 'times_referenced', 'created_at']

class AIPersonalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPersonality
        fields = [
            'id', 'name', 'description', 'communication_style',
            'expertise_areas', 'proactivity_level', 'explanation_depth',
            'use_business_language', 'is_active'
        ]
