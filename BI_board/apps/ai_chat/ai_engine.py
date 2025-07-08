# import openai  # Commented out for now - will need OpenAI API key
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from django.conf import settings
from .models import UserContext, ChatSession, ChatMessage, DataInsight
from apps.analytics.models import AnalysisResults
from apps.analytics.intelligent_analyzer import IntelligentDatasetAnalyzer
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class ChatResponse:
    """Structure for AI chat responses"""
    message: str
    intent: str
    confidence: float
    suggested_actions: List[str]
    data_references: Dict[str, Any]
    follow_up_questions: List[str]
    requires_analysis: bool = False
    analysis_type: Optional[str] = None

class AIDataScientistEngine:
    """
    LLM-powered AI Data Scientist that can chat about data insights
    """
    
    def __init__(self):
        # Check if OpenAI is available
        self.use_openai = hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY

        if self.use_openai:
            # openai.api_key = settings.OPENAI_API_KEY  # Uncomment when OpenAI key is available
            self.model = "gpt-4"  # or "gpt-3.5-turbo" for cost efficiency
        else:
            # Use demo engine for testing
            from .demo_engine import DemoAIEngine
            self.demo_engine = DemoAIEngine()

        self.analyzer = IntelligentDatasetAnalyzer()
        
        # System prompts for different contexts
        self.system_prompts = {
            'data_scientist': """You are an expert data scientist and business analyst working for SMEs. 
            Your role is to help small business owners understand their data and make better decisions.
            
            Key traits:
            - Speak in business language, not technical jargon
            - Always connect insights to business impact
            - Be proactive in suggesting actionable recommendations
            - Ask clarifying questions to understand business context
            - Explain complex concepts simply
            - Focus on ROI and practical outcomes
            
            Available analysis types:
            1. Sales Forecasting - Predict future sales trends
            2. Credit Risk Analysis - Assess customer payment risk
            3. Customer Segmentation - Group customers for targeted marketing
            4. Correlation Analysis - Find relationships in data
            5. Anomaly Detection - Identify unusual patterns
            6. Descriptive Analytics - Comprehensive data overview
            """,
            
            'business_consultant': """You are a business consultant specializing in data-driven insights for SMEs.
            Help business owners understand what their data means for their business strategy.
            
            Focus on:
            - Revenue growth opportunities
            - Cost reduction strategies
            - Customer retention and acquisition
            - Operational efficiency
            - Risk management
            - Market positioning
            """,
            
            'friendly_advisor': """You are a friendly, knowledgeable advisor helping small business owners.
            Make data insights accessible and actionable for non-technical users.
            
            Communication style:
            - Warm and encouraging
            - Use analogies and examples
            - Break down complex ideas
            - Celebrate successes in the data
            - Provide reassurance about challenges
            """
        }

    def process_message(self, user_message: str, session: ChatSession, user_context: UserContext) -> ChatResponse:
        """
        Process user message and generate AI response
        """
        try:
            # Use demo engine if OpenAI is not available
            if not self.use_openai:
                response = self.demo_engine.process_message(user_message, session, user_context)
                self._store_conversation(session, user_message, response, response.intent, response.confidence)
                return response

            # Original OpenAI-based processing
            # Detect intent and extract context
            intent, confidence = self._detect_intent(user_message, session)

            # Get relevant data context
            data_context = self._get_data_context(session, user_context)

            # Generate response based on intent
            if intent == 'ask_about_data':
                response = self._handle_data_question(user_message, data_context, user_context)
            elif intent == 'request_analysis':
                response = self._handle_analysis_request(user_message, data_context, user_context)
            elif intent == 'explain_insight':
                response = self._handle_insight_explanation(user_message, data_context, user_context)
            elif intent == 'business_advice':
                response = self._handle_business_advice(user_message, data_context, user_context)
            elif intent == 'greeting':
                response = self._handle_greeting(user_message, data_context, user_context)
            else:
                response = self._handle_general_query(user_message, data_context, user_context)

            # Store message and response
            self._store_conversation(session, user_message, response, intent, confidence)

            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return ChatResponse(
                message="I apologize, but I encountered an issue processing your request. Could you please try rephrasing your question?",
                intent="error",
                confidence=0.0,
                suggested_actions=["Try asking a different question", "Upload new data"],
                data_references={},
                follow_up_questions=[]
            )

    def _detect_intent(self, message: str, session: ChatSession) -> Tuple[str, float]:
        """Detect user intent using LLM"""
        
        intent_prompt = f"""
        Analyze this user message and determine their intent. Consider the context of a business data analysis conversation.
        
        User message: "{message}"
        
        Possible intents:
        - greeting: User is starting conversation or being polite
        - ask_about_data: User wants to know about their data/results
        - request_analysis: User wants a specific analysis performed
        - explain_insight: User wants explanation of a finding
        - business_advice: User wants business recommendations
        - drill_down: User wants to explore data deeper
        - compare_metrics: User wants to compare different metrics
        - general_query: Other questions
        
        Respond with JSON: {{"intent": "intent_name", "confidence": 0.95}}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": intent_prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('intent', 'general_query'), result.get('confidence', 0.5)
            
        except Exception as e:
            logger.error(f"Intent detection failed: {str(e)}")
            return 'general_query', 0.5

    def _get_data_context(self, session: ChatSession, user_context: UserContext) -> Dict[str, Any]:
        """Get relevant data context for the conversation"""
        context = {
            'user_business': {
                'type': user_context.business_type,
                'industry': user_context.industry,
                'size': user_context.company_size,
                'goals': user_context.main_goals
            },
            'current_dataset': None,
            'recent_insights': [],
            'analysis_results': {}
        }
        
        # Get current dataset context
        if session.dataset_context:
            try:
                df = pd.read_json(session.dataset_context.processed_json)
                context['current_dataset'] = {
                    'shape': df.shape,
                    'columns': df.columns.tolist(),
                    'sample_data': df.head(3).to_dict('records')
                }
            except Exception as e:
                logger.error(f"Error loading dataset context: {str(e)}")
        
        # Get recent analysis results
        if session.analysis_context:
            try:
                factors = json.loads(session.analysis_context.factors) if session.analysis_context.factors else {}
                context['analysis_results'] = factors
            except Exception as e:
                logger.error(f"Error loading analysis context: {str(e)}")
        
        # Get recent insights from this session
        recent_insights = DataInsight.objects.filter(
            source_analysis__processed_data__uploaded_data__user=session.user
        ).order_by('-created_at')[:5]
        
        context['recent_insights'] = [
            {
                'title': insight.title,
                'description': insight.description,
                'business_impact': insight.business_impact,
                'confidence': insight.confidence_level
            }
            for insight in recent_insights
        ]
        
        return context

    def _handle_data_question(self, message: str, data_context: Dict, user_context: UserContext) -> ChatResponse:
        """Handle questions about data"""
        
        system_prompt = self.system_prompts['data_scientist']
        
        prompt = f"""
        {system_prompt}
        
        User Business Context:
        - Business Type: {data_context['user_business']['type']}
        - Industry: {data_context['user_business']['industry']}
        - Goals: {data_context['user_business']['goals']}
        
        Current Dataset:
        {json.dumps(data_context['current_dataset'], indent=2) if data_context['current_dataset'] else "No dataset loaded"}
        
        Recent Analysis Results:
        {json.dumps(data_context['analysis_results'], indent=2) if data_context['analysis_results'] else "No recent analysis"}
        
        User Question: "{message}"
        
        Provide a helpful response that:
        1. Answers their question in business terms
        2. References specific data points when relevant
        3. Suggests actionable next steps
        4. Asks follow-up questions to better help them
        
        Format your response as JSON:
        {{
            "message": "Your response here",
            "suggested_actions": ["action1", "action2"],
            "follow_up_questions": ["question1", "question2"],
            "requires_analysis": false,
            "analysis_type": null
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return ChatResponse(
                message=result.get('message', ''),
                intent='ask_about_data',
                confidence=0.8,
                suggested_actions=result.get('suggested_actions', []),
                data_references=data_context['analysis_results'],
                follow_up_questions=result.get('follow_up_questions', []),
                requires_analysis=result.get('requires_analysis', False),
                analysis_type=result.get('analysis_type')
            )
            
        except Exception as e:
            logger.error(f"Error handling data question: {str(e)}")
            return self._fallback_response(message, data_context)

    def _handle_analysis_request(self, message: str, data_context: Dict, user_context: UserContext) -> ChatResponse:
        """Handle requests for specific analysis"""
        
        prompt = f"""
        The user is requesting an analysis. Based on their message and available data, determine:
        1. What type of analysis they want
        2. Whether it's possible with current data
        3. How to respond helpfully
        
        User message: "{message}"
        Available data: {data_context['current_dataset']}
        
        Analysis types available:
        - sales_forecasting
        - credit_risk
        - customer_segmentation
        - correlation_analysis
        - anomaly_detection
        - descriptive_analytics
        
        Respond with JSON:
        {{
            "message": "Response explaining what you'll do",
            "analysis_type": "recommended_analysis_type",
            "requires_analysis": true,
            "suggested_actions": ["actions"],
            "follow_up_questions": ["questions"]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return ChatResponse(
                message=result.get('message', ''),
                intent='request_analysis',
                confidence=0.9,
                suggested_actions=result.get('suggested_actions', []),
                data_references={},
                follow_up_questions=result.get('follow_up_questions', []),
                requires_analysis=result.get('requires_analysis', True),
                analysis_type=result.get('analysis_type')
            )
            
        except Exception as e:
            logger.error(f"Error handling analysis request: {str(e)}")
            return self._fallback_response(message, data_context)

    def _handle_business_advice(self, message: str, data_context: Dict, user_context: UserContext) -> ChatResponse:
        """Handle business advice requests"""
        
        system_prompt = self.system_prompts['business_consultant']
        
        prompt = f"""
        {system_prompt}
        
        User Business: {data_context['user_business']['type']} in {data_context['user_business']['industry']}
        Business Goals: {data_context['user_business']['goals']}
        
        Recent Insights:
        {json.dumps(data_context['recent_insights'], indent=2)}
        
        User Question: "{message}"
        
        Provide strategic business advice based on their data insights. Focus on:
        - Actionable recommendations
        - ROI potential
        - Implementation steps
        - Risk considerations
        
        Response as JSON with message, suggested_actions, and follow_up_questions.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return ChatResponse(
                message=result.get('message', ''),
                intent='business_advice',
                confidence=0.8,
                suggested_actions=result.get('suggested_actions', []),
                data_references=data_context['recent_insights'],
                follow_up_questions=result.get('follow_up_questions', [])
            )
            
        except Exception as e:
            logger.error(f"Error handling business advice: {str(e)}")
            return self._fallback_response(message, data_context)

    def _handle_greeting(self, message: str, data_context: Dict, user_context: UserContext) -> ChatResponse:
        """Handle greetings and conversation starters"""
        
        business_context = f"I see you're running a {data_context['user_business']['type']} business" if data_context['user_business']['type'] else "I'm here to help with your business data"
        
        dataset_context = ""
        if data_context['current_dataset']:
            dataset_context = f" I can see you have a dataset with {data_context['current_dataset']['shape'][0]} records and {data_context['current_dataset']['shape'][1]} columns loaded."
        
        message = f"Hello! {business_context}.{dataset_context} What would you like to explore about your data today?"
        
        return ChatResponse(
            message=message,
            intent='greeting',
            confidence=0.9,
            suggested_actions=[
                "Ask about trends in your data",
                "Request a specific analysis",
                "Get business recommendations"
            ],
            data_references={},
            follow_up_questions=[
                "What's your biggest business challenge right now?",
                "What metrics are most important to you?",
                "Would you like me to analyze your data for insights?"
            ]
        )

    def _fallback_response(self, message: str, data_context: Dict) -> ChatResponse:
        """Fallback response when other handlers fail"""
        return ChatResponse(
            message="I understand you're asking about your data. Could you help me understand what specific aspect you'd like to explore? I can help with trends, predictions, customer insights, or business recommendations.",
            intent='general_query',
            confidence=0.5,
            suggested_actions=[
                "Ask about specific metrics",
                "Request an analysis",
                "Upload new data"
            ],
            data_references={},
            follow_up_questions=[
                "What's the most important metric for your business?",
                "Are you looking for trends or predictions?",
                "Would you like me to suggest some insights?"
            ]
        )

    def _store_conversation(self, session: ChatSession, user_message: str, ai_response: ChatResponse, intent: str, confidence: float):
        """Store conversation in database"""
        try:
            # Store user message
            ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message,
                intent_detected=intent,
                confidence_score=confidence
            )
            
            # Store AI response
            ChatMessage.objects.create(
                session=session,
                message_type='ai',
                content=ai_response.message,
                metadata={
                    'suggested_actions': ai_response.suggested_actions,
                    'follow_up_questions': ai_response.follow_up_questions,
                    'data_references': ai_response.data_references,
                    'requires_analysis': ai_response.requires_analysis,
                    'analysis_type': ai_response.analysis_type
                },
                intent_detected=ai_response.intent,
                confidence_score=ai_response.confidence
            )
            
            # Update session
            session.updated_at = session.updated_at  # Trigger update
            session.save()
            
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")

    def generate_proactive_insights(self, user_context: UserContext, recent_analysis: AnalysisResults) -> List[str]:
        """Generate proactive insights and suggestions"""

        # Use demo engine if OpenAI is not available
        if not self.use_openai:
            return self.demo_engine.generate_proactive_insights(user_context, recent_analysis)

        prompt = f"""
        Based on this user's business context and recent analysis, generate 3 proactive insights or suggestions.

        Business: {user_context.business_type} in {user_context.industry}
        Goals: {user_context.main_goals}

        Recent Analysis: {recent_analysis.factors if recent_analysis.factors else "No recent analysis"}

        Generate insights that:
        1. Are actionable and specific
        2. Connect to business goals
        3. Suggest next steps

        Return as JSON array: ["insight1", "insight2", "insight3"]
        """

        try:
            # response = openai.ChatCompletion.create(  # Uncomment when OpenAI is available
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=0.7
            # )
            # return json.loads(response.choices[0].message.content)

            # Fallback to demo for now
            return self.demo_engine.generate_proactive_insights(user_context, recent_analysis)

        except Exception as e:
            logger.error(f"Error generating proactive insights: {str(e)}")
            return []
