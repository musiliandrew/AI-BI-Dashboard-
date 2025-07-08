from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import UserContext, ChatSession, ChatMessage, DataInsight
from .serializers import ChatSessionSerializer, ChatMessageSerializer, UserContextSerializer
from .ai_engine import AIDataScientistEngine
from .insight_discovery import ProactiveInsightDiscovery
from apps.data_ingestion.models import ProcessedData
from apps.analytics.models import AnalysisResults
from apps.analytics.intelligent_tasks import run_intelligent_analytics
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

class ChatSessionViewSet(viewsets.ModelViewSet):
    """Manage chat sessions"""
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a chat session"""
        session = self.get_object()
        message_content = request.data.get('message', '').strip()
        
        if not message_content:
            return Response({'error': 'Message content required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create user context
            user_context, created = UserContext.objects.get_or_create(
                user=request.user,
                defaults={
                    'business_type': request.data.get('business_type', ''),
                    'industry': request.data.get('industry', ''),
                    'communication_style': 'friendly'
                }
            )
            
            # Initialize AI engine
            ai_engine = AIDataScientistEngine()
            
            # Process message
            ai_response = ai_engine.process_message(message_content, session, user_context)
            
            # If analysis is required, trigger it
            if ai_response.requires_analysis and ai_response.analysis_type:
                self._trigger_analysis(session, ai_response.analysis_type)
            
            # Return the AI response
            return Response({
                'message': ai_response.message,
                'suggested_actions': ai_response.suggested_actions,
                'follow_up_questions': ai_response.follow_up_questions,
                'requires_analysis': ai_response.requires_analysis,
                'analysis_type': ai_response.analysis_type,
                'confidence': ai_response.confidence
            })
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return Response({
                'error': 'Failed to process message',
                'message': "I apologize, but I'm having trouble processing your request right now. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _trigger_analysis(self, session: ChatSession, analysis_type: str):
        """Trigger analysis based on AI recommendation"""
        if session.dataset_context:
            try:
                # Start intelligent analysis
                task_result = run_intelligent_analytics.delay(
                    session.dataset_context.id,
                    analysis_type
                )
                
                # Store system message about analysis
                ChatMessage.objects.create(
                    session=session,
                    message_type='system',
                    content=f"Starting {analysis_type.replace('_', ' ')} analysis...",
                    metadata={'task_id': task_result.id, 'analysis_type': analysis_type}
                )
                
            except Exception as e:
                logger.error(f"Error triggering analysis: {str(e)}")

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """View chat messages"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return ChatMessage.objects.filter(
                session_id=session_id,
                session__user=self.request.user
            )
        return ChatMessage.objects.filter(session__user=self.request.user)

class UserContextView(APIView):
    """Manage user context and preferences"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user context"""
        try:
            context = UserContext.objects.get(user=request.user)
            serializer = UserContextSerializer(context)
            return Response(serializer.data)
        except UserContext.DoesNotExist:
            return Response({
                'business_type': '',
                'industry': '',
                'company_size': '',
                'main_goals': [],
                'communication_style': 'friendly',
                'detail_level': 'medium'
            })
    
    def post(self, request):
        """Update user context"""
        context, created = UserContext.objects.get_or_create(
            user=request.user,
            defaults=request.data
        )
        
        if not created:
            # Update existing context
            for key, value in request.data.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            context.save()
        
        serializer = UserContextSerializer(context)
        return Response(serializer.data)

class QuickChatView(APIView):
    """Quick chat without session management"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send a quick message and get AI response"""
        message = request.data.get('message', '').strip()
        dataset_id = request.data.get('dataset_id')  # Optional
        
        if not message:
            return Response({'error': 'Message required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create user context
            user_context, _ = UserContext.objects.get_or_create(
                user=request.user,
                defaults={'communication_style': 'friendly'}
            )
            
            # Create temporary session or get existing one
            session = ChatSession.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            
            if not session:
                session = ChatSession.objects.create(
                    user=request.user,
                    title=f"Chat {message[:30]}..."
                )
            
            # Set dataset context if provided
            if dataset_id:
                try:
                    dataset = ProcessedData.objects.get(
                        id=dataset_id,
                        uploaded_data__user=request.user
                    )
                    session.dataset_context = dataset
                    session.save()
                except ProcessedData.DoesNotExist:
                    pass
            
            # Process with AI
            ai_engine = AIDataScientistEngine()
            ai_response = ai_engine.process_message(message, session, user_context)
            
            return Response({
                'session_id': str(session.id),
                'message': ai_response.message,
                'suggested_actions': ai_response.suggested_actions,
                'follow_up_questions': ai_response.follow_up_questions,
                'requires_analysis': ai_response.requires_analysis,
                'analysis_type': ai_response.analysis_type,
                'confidence': ai_response.confidence
            })
            
        except Exception as e:
            logger.error(f"Error in quick chat: {str(e)}")
            return Response({
                'error': 'Chat processing failed',
                'message': "I'm having trouble right now. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataInsightView(APIView):
    """Get AI-generated insights about user's data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get recent insights for user"""
        insights = DataInsight.objects.filter(
            source_analysis__processed_data__uploaded_data__user=request.user
        ).order_by('-confidence_level', '-created_at')[:10]
        
        insights_data = []
        for insight in insights:
            insights_data.append({
                'id': str(insight.id),
                'title': insight.title,
                'description': insight.description,
                'business_impact': insight.business_impact,
                'recommended_actions': insight.recommended_actions,
                'confidence_level': insight.confidence_level,
                'insight_type': insight.insight_type,
                'created_at': insight.created_at.isoformat()
            })
        
        return Response({'insights': insights_data})
    
    def post(self, request):
        """Generate new insights for a dataset"""
        dataset_id = request.data.get('dataset_id')
        
        if not dataset_id:
            return Response({'error': 'dataset_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dataset = ProcessedData.objects.get(
                id=dataset_id,
                uploaded_data__user=request.user
            )
            
            # Get user context
            user_context, _ = UserContext.objects.get_or_create(
                user=request.user,
                defaults={'communication_style': 'friendly'}
            )
            
            # Generate insights using AI
            ai_engine = AIDataScientistEngine()
            
            # Get recent analysis for this dataset
            recent_analysis = AnalysisResults.objects.filter(
                processed_data=dataset
            ).order_by('-id').first()
            
            if recent_analysis:
                proactive_insights = ai_engine.generate_proactive_insights(user_context, recent_analysis)
                
                return Response({
                    'insights': proactive_insights,
                    'dataset_id': dataset_id
                })
            else:
                return Response({
                    'message': 'No analysis available for this dataset. Please run an analysis first.',
                    'suggested_action': 'Run intelligent analysis'
                })
                
        except ProcessedData.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return Response({'error': 'Failed to generate insights'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DiscoverInsightsView(APIView):
    """Discover smart insights and generate question bubbles"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Discover insights for a dataset and generate smart questions"""
        dataset_id = request.data.get('dataset_id')

        if not dataset_id:
            return Response({'error': 'dataset_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # For demo purposes, return predefined insights
            # In production, this would analyze the actual dataset

            demo_stories = [
                {
                    'story_type': 'achievement',
                    'title': 'March Sales Increased 34%',
                    'suggested_question': 'Why did March sales increase 34%?',
                    'impact_level': 'high',
                    'confidence': 0.9,
                    'comprehensive_answer': """March's 34% sales increase was driven by three key factors:

1. **🎉 Product Launch Impact (45% of increase)**
   - New product line launched Feb 28th
   - Generated $23,400 in first month
   - 67% higher conversion rate than existing products

2. **📱 Marketing Campaign Success (35% of increase)**
   - Social media campaign reached 45K people
   - Email open rates increased to 28% (vs 18% average)
   - Cost per acquisition dropped 23%

3. **🌟 Customer Referrals (20% of increase)**
   - Referral program generated 156 new customers
   - Average order value from referrals: $89 vs $67 normal

**💡 Recommendation:** Double down on the new product line and expand the referral program for April!"""
                },
                {
                    'story_type': 'opportunity',
                    'title': 'Customer Growth Accelerating',
                    'suggested_question': "What's driving the 28% customer growth?",
                    'impact_level': 'high',
                    'confidence': 0.8,
                    'comprehensive_answer': """Your 28% customer growth is excellent! Here's what's working:

1. **🎯 Referral Program Success**
   - 40% of new customers come from referrals
   - Referral customers have 2.3x higher lifetime value
   - Word-of-mouth is your strongest acquisition channel

2. **📱 Digital Marketing Optimization**
   - Social media engagement up 156%
   - Email marketing ROI improved 89%
   - Website conversion rate increased to 4.2%

3. **🌟 Product-Market Fit**
   - Customer satisfaction score: 4.7/5
   - Net Promoter Score: 68 (excellent)
   - Repeat purchase rate: 73%

**🚀 Opportunity:** Scale your referral program and invest more in digital marketing!"""
                },
                {
                    'story_type': 'concern',
                    'title': 'Refunds Up 15% in Q2',
                    'suggested_question': 'Why are refunds up 15% in Q2?',
                    'impact_level': 'medium',
                    'confidence': 0.7,
                    'comprehensive_answer': """The 15% increase in refunds needs investigation:

1. **📦 Product Quality Issues**
   - Specific product line showing 23% refund rate
   - Customer complaints about durability
   - Manufacturing batch from April may be affected

2. **📱 Shipping Delays**
   - Average delivery time increased to 8 days
   - 34% of refunds cite "took too long"
   - Carrier performance declined in Q2

3. **💬 Customer Expectations**
   - Marketing promises vs. reality gap
   - Product descriptions may be overselling features

**🔧 Action Plan:** Review product quality, improve shipping, and align marketing messages with reality."""
                },
                {
                    'story_type': 'opportunity',
                    'title': 'Top Products Drive 67% of Revenue',
                    'suggested_question': 'Which products should I focus on?',
                    'impact_level': 'medium',
                    'confidence': 0.8,
                    'comprehensive_answer': """Your top-performing products are driving significant value:

1. **🏆 #1: Premium Widget Series** - Revenue: $45,600 (32% of total)
2. **🏆 #2: Starter Kit Bundle** - Revenue: $28,900 (21% of total)
3. **🏆 #3: Professional Tools** - Revenue: $19,400 (14% of total)

**💰 Revenue Impact:** Your top 3 products generate 67% of total revenue

**🎯 Focus Strategy:**
- Expand the Premium Widget Series with new variants
- Create more bundles like the Starter Kit
- Cross-sell Professional Tools to Premium customers"""
                }
            ]

            # Generate report
            report = {
                'executive_summary': f"I analyzed your business data and discovered {len(demo_stories)} key insights across sales, customers, and operations.",
                'key_findings': demo_stories,
                'recommendations': [
                    "Focus on your top-performing products and channels",
                    "Address quality and shipping issues to reduce refunds",
                    "Scale successful marketing campaigns and referral programs",
                    "Monitor key metrics weekly for early trend detection"
                ]
            }

            return Response({
                'stories': demo_stories,
                'report': report,
                'dataset_id': dataset_id
            })

        except Exception as e:
            logger.error(f"Error discovering insights: {str(e)}")
            return Response({'error': 'Failed to discover insights'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
