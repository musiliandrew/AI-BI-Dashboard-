"""
Demo AI Engine for testing without OpenAI API
This simulates the AI responses for demonstration purposes
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .models import UserContext, ChatSession, ChatMessage, DataInsight

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

class DemoAIEngine:
    """
    Demo AI engine that simulates intelligent responses
    """
    
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your AI Data Scientist. I can help you understand your data and make better business decisions. What would you like to explore?",
                "Hi there! I'm here to help you unlock insights from your data. What's on your mind today?",
                "Welcome! I'm your personal data analyst. How can I help you grow your business today?"
            ],
            
            'data_question': [
                "Based on your data, I can see some interesting patterns. Let me break down what I found...",
                "Your data tells a compelling story. Here's what stands out to me...",
                "I've analyzed your dataset and discovered several key insights that could impact your business..."
            ],
            
            'analysis_request': [
                "Great idea! Let me run that analysis for you. This will help us understand...",
                "Perfect! I'll analyze that right away. This type of analysis is excellent for...",
                "Absolutely! Running this analysis will give us insights into..."
            ],
            
            'business_advice': [
                "Based on your data patterns, here's what I recommend for your business...",
                "Looking at your metrics, I see opportunities to improve...",
                "Your data suggests some strategic moves that could boost performance..."
            ]
        }
        
        self.suggested_actions = {
            'general': [
                "Analyze sales trends",
                "Find customer segments", 
                "Predict future performance",
                "Identify growth opportunities",
                "Check data quality"
            ],
            'sales': [
                "Run sales forecasting",
                "Analyze seasonal patterns",
                "Compare product performance",
                "Identify top customers"
            ],
            'customers': [
                "Segment customers",
                "Analyze customer lifetime value",
                "Find churn patterns",
                "Identify upsell opportunities"
            ]
        }
        
        self.follow_up_questions = {
            'general': [
                "What's your biggest business challenge right now?",
                "Which metrics are most important to you?",
                "Would you like me to dive deeper into any specific area?",
                "What time period should we focus on?"
            ],
            'sales': [
                "Which products are you most concerned about?",
                "Are there seasonal patterns you've noticed?",
                "What's your target growth rate?",
                "Which sales channels perform best?"
            ],
            'customers': [
                "What defines a valuable customer for you?",
                "Are you seeing customer retention issues?",
                "Which customer segments are most profitable?",
                "How do you currently acquire customers?"
            ]
        }

    def process_message(self, user_message: str, session: ChatSession, user_context: UserContext) -> ChatResponse:
        """
        Process user message and generate demo AI response
        """
        # Detect intent (simplified)
        intent, confidence = self._detect_intent_demo(user_message)
        
        # Generate response based on intent
        if intent == 'greeting':
            return self._handle_greeting_demo(user_message, user_context)
        elif intent == 'data_question':
            return self._handle_data_question_demo(user_message, user_context)
        elif intent == 'analysis_request':
            return self._handle_analysis_request_demo(user_message, user_context)
        elif intent == 'business_advice':
            return self._handle_business_advice_demo(user_message, user_context)
        else:
            return self._handle_general_demo(user_message, user_context)

    def _detect_intent_demo(self, message: str) -> Tuple[str, float]:
        """Demo intent detection"""
        message_lower = message.lower()
        
        # Simple keyword-based intent detection
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            return 'greeting', 0.9
        elif any(word in message_lower for word in ['analyze', 'analysis', 'run', 'forecast', 'predict']):
            return 'analysis_request', 0.8
        elif any(word in message_lower for word in ['data', 'trend', 'pattern', 'insight', 'show']):
            return 'data_question', 0.8
        elif any(word in message_lower for word in ['recommend', 'advice', 'should', 'strategy', 'improve']):
            return 'business_advice', 0.8
        else:
            return 'general', 0.6

    def _handle_greeting_demo(self, message: str, user_context: UserContext) -> ChatResponse:
        """Handle greeting messages"""
        base_message = random.choice(self.responses['greeting'])
        
        # Personalize based on user context
        if user_context.business_type:
            base_message += f" I see you're in the {user_context.business_type} business."
        
        return ChatResponse(
            message=base_message,
            intent='greeting',
            confidence=0.9,
            suggested_actions=self.suggested_actions['general'],
            data_references={},
            follow_up_questions=self.follow_up_questions['general']
        )

    def _handle_data_question_demo(self, message: str, user_context: UserContext) -> ChatResponse:
        """Handle data-related questions"""
        base_message = random.choice(self.responses['data_question'])
        
        # Add some demo insights
        insights = [
            "Your sales have grown 15% over the last quarter",
            "Customer acquisition costs increased by 8% but customer lifetime value is up 12%",
            "Your top 20% of customers generate 60% of revenue",
            "There's a seasonal pattern in your data showing peaks in Q4",
            "Customer retention rate is 85%, which is above industry average"
        ]
        
        selected_insight = random.choice(insights)
        full_message = f"{base_message}\n\n📊 Key Insight: {selected_insight}"
        
        return ChatResponse(
            message=full_message,
            intent='data_question',
            confidence=0.8,
            suggested_actions=self.suggested_actions['general'],
            data_references={'insight': selected_insight},
            follow_up_questions=self.follow_up_questions['general']
        )

    def _handle_analysis_request_demo(self, message: str, user_context: UserContext) -> ChatResponse:
        """Handle analysis requests"""
        message_lower = message.lower()
        
        # Determine analysis type
        if 'sales' in message_lower or 'forecast' in message_lower:
            analysis_type = 'sales_forecasting'
            category = 'sales'
        elif 'customer' in message_lower or 'segment' in message_lower:
            analysis_type = 'customer_segmentation'
            category = 'customers'
        elif 'risk' in message_lower or 'credit' in message_lower:
            analysis_type = 'credit_risk'
            category = 'general'
        else:
            analysis_type = 'descriptive_analytics'
            category = 'general'
        
        base_message = random.choice(self.responses['analysis_request'])
        full_message = f"{base_message} {analysis_type.replace('_', ' ')} analysis."
        
        return ChatResponse(
            message=full_message,
            intent='analysis_request',
            confidence=0.9,
            suggested_actions=self.suggested_actions[category],
            data_references={},
            follow_up_questions=self.follow_up_questions[category],
            requires_analysis=True,
            analysis_type=analysis_type
        )

    def _handle_business_advice_demo(self, message: str, user_context: UserContext) -> ChatResponse:
        """Handle business advice requests"""
        base_message = random.choice(self.responses['business_advice'])
        
        # Generate demo business advice
        advice_options = [
            "Focus on your top 20% of customers - they drive most of your revenue",
            "Consider seasonal marketing campaigns to capitalize on Q4 peaks",
            "Invest in customer retention programs to improve lifetime value",
            "Optimize your pricing strategy based on customer segments",
            "Expand your most profitable product lines"
        ]
        
        selected_advice = random.choice(advice_options)
        full_message = f"{base_message}\n\n💡 Recommendation: {selected_advice}"
        
        return ChatResponse(
            message=full_message,
            intent='business_advice',
            confidence=0.8,
            suggested_actions=[
                "Get detailed implementation plan",
                "Analyze ROI potential",
                "See supporting data",
                "Compare alternatives"
            ],
            data_references={'advice': selected_advice},
            follow_up_questions=[
                "Would you like me to estimate the ROI of this recommendation?",
                "Should I show you the data supporting this advice?",
                "What's your timeline for implementing changes?",
                "Are there any constraints I should consider?"
            ]
        )

    def _handle_general_demo(self, message: str, user_context: UserContext) -> ChatResponse:
        """Handle general queries"""
        responses = [
            "I understand you're asking about your business data. Let me help you explore that.",
            "That's an interesting question! Based on your data, here's what I can tell you...",
            "Great question! Let me analyze that for you and provide some insights."
        ]
        
        return ChatResponse(
            message=random.choice(responses),
            intent='general',
            confidence=0.6,
            suggested_actions=self.suggested_actions['general'],
            data_references={},
            follow_up_questions=self.follow_up_questions['general']
        )

    def generate_proactive_insights(self, user_context: UserContext, recent_analysis) -> List[str]:
        """Generate demo proactive insights"""
        insights = [
            "Your customer acquisition cost has decreased 12% this month - great job!",
            "I noticed unusual activity in your sales data - would you like me to investigate?",
            "Your top customer segment shows signs of increased engagement",
            "There's an opportunity to improve conversion rates in your marketing funnel",
            "Your seasonal patterns suggest now is a good time to launch new products"
        ]
        
        return random.sample(insights, 3)
