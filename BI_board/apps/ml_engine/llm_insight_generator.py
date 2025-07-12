"""
LLM-Powered Insight Generator
Transforms raw analytics results into natural language business insights
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
try:
    import openai
except ImportError:
    openai = None

from django.conf import settings

logger = logging.getLogger(__name__)

@dataclass
class RawInsight:
    """Raw insight from analytics engines"""
    insight_type: str  # 'trend', 'anomaly', 'prediction', 'correlation'
    title: str
    data: Dict[str, Any]
    confidence: float
    source: str  # 'ml_engine', 'analytics_engine', 'social_engine'
    timestamp: datetime
    business_context: Dict[str, Any] = None

@dataclass
class ExplainedInsight:
    """LLM-explained insight with business context"""
    raw_insight: RawInsight
    explanation: str
    business_impact: str
    recommended_actions: List[str]
    urgency_level: str  # 'critical', 'high', 'medium', 'low'
    potential_value: Optional[float] = None

class LLMInsightGenerator:
    """Generate natural language insights using LLM"""
    
    def __init__(self):
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.demo_mode = not self.openai_api_key or openai is None

        if not self.demo_mode and openai:
            openai.api_key = self.openai_api_key
        
        # Business context templates
        self.industry_contexts = {
            'automotive': {
                'key_metrics': ['vehicle_sales', 'inventory_turnover', 'customer_satisfaction', 'service_revenue'],
                'business_goals': ['increase_sales_velocity', 'optimize_inventory', 'improve_margins', 'enhance_customer_experience'],
                'terminology': ['dealership', 'vehicle', 'trade-in', 'financing', 'service_department']
            },
            'restaurant': {
                'key_metrics': ['daily_revenue', 'food_cost_percentage', 'table_turnover', 'customer_satisfaction'],
                'business_goals': ['increase_revenue', 'control_costs', 'improve_efficiency', 'enhance_experience'],
                'terminology': ['covers', 'food_cost', 'labor_cost', 'table_turns', 'average_check']
            },
            'retail': {
                'key_metrics': ['sales_per_sqft', 'inventory_turnover', 'conversion_rate', 'average_transaction'],
                'business_goals': ['increase_sales', 'optimize_inventory', 'improve_margins', 'enhance_experience'],
                'terminology': ['SKU', 'inventory', 'conversion', 'basket_size', 'foot_traffic']
            }
        }
    
    async def explain_insights(self, raw_insights: List[RawInsight], 
                             industry: str = 'general') -> List[ExplainedInsight]:
        """Convert raw insights into explained business insights"""
        explained_insights = []
        
        for insight in raw_insights:
            try:
                explained = await self._explain_single_insight(insight, industry)
                explained_insights.append(explained)
            except Exception as e:
                logger.error(f"Error explaining insight {insight.title}: {e}")
                # Fallback to basic explanation
                explained_insights.append(self._create_fallback_insight(insight))
        
        return explained_insights
    
    async def _explain_single_insight(self, insight: RawInsight, industry: str) -> ExplainedInsight:
        """Explain a single insight using LLM"""
        
        if self.demo_mode:
            return self._create_demo_explanation(insight, industry)
        
        # Get industry context
        context = self.industry_contexts.get(industry, self.industry_contexts['retail'])
        
        # Create LLM prompt
        prompt = self._create_explanation_prompt(insight, context)
        
        try:
            # Call OpenAI API
            response = await self._call_openai(prompt)
            
            # Parse response
            explanation_data = self._parse_llm_response(response)
            
            return ExplainedInsight(
                raw_insight=insight,
                explanation=explanation_data['explanation'],
                business_impact=explanation_data['business_impact'],
                recommended_actions=explanation_data['recommended_actions'],
                urgency_level=explanation_data['urgency_level'],
                potential_value=explanation_data.get('potential_value')
            )
            
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._create_fallback_insight(insight)
    
    def _create_explanation_prompt(self, insight: RawInsight, context: Dict[str, Any]) -> str:
        """Create LLM prompt for insight explanation"""
        
        prompt = f"""
You are a senior business analyst explaining data insights to a {context.get('industry', 'business')} owner.

INSIGHT DATA:
- Type: {insight.insight_type}
- Title: {insight.title}
- Confidence: {insight.confidence:.1%}
- Source: {insight.source}
- Data: {json.dumps(insight.data, indent=2)}

BUSINESS CONTEXT:
- Industry: {context.get('industry', 'general')}
- Key Metrics: {', '.join(context.get('key_metrics', []))}
- Business Goals: {', '.join(context.get('business_goals', []))}

INSTRUCTIONS:
1. Explain this insight in simple, actionable business language
2. Focus on business impact and what it means for revenue/costs/efficiency
3. Provide 2-3 specific, actionable recommendations
4. Assess urgency level (critical/high/medium/low)
5. Estimate potential business value if possible

RESPONSE FORMAT (JSON):
{{
    "explanation": "Clear business explanation in 2-3 sentences",
    "business_impact": "What this means for the business (revenue, costs, efficiency)",
    "recommended_actions": ["Action 1", "Action 2", "Action 3"],
    "urgency_level": "high/medium/low",
    "potential_value": 12345.67 (optional, estimated dollar impact)
}}

Respond only with valid JSON.
"""
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior business analyst who explains data insights clearly and actionably."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                'explanation': response[:200] + "...",
                'business_impact': "Requires further analysis",
                'recommended_actions': ["Review data", "Investigate further", "Monitor trends"],
                'urgency_level': 'medium'
            }
    
    def _create_demo_explanation(self, insight: RawInsight, industry: str) -> ExplainedInsight:
        """Create demo explanation without LLM API"""
        
        demo_explanations = {
            'trend': {
                'explanation': f"Your {insight.title.lower()} shows a significant trend with {insight.confidence:.1%} confidence. This pattern indicates a clear direction in your business metrics.",
                'business_impact': "This trend could significantly impact your revenue and operational efficiency if the pattern continues.",
                'recommended_actions': [
                    "Monitor this trend closely over the next 2 weeks",
                    "Investigate the root causes driving this pattern",
                    "Adjust business strategy to capitalize on or mitigate this trend"
                ],
                'urgency_level': 'high' if insight.confidence > 0.8 else 'medium'
            },
            'anomaly': {
                'explanation': f"We detected an unusual pattern in {insight.title.lower()} that deviates from normal behavior with {insight.confidence:.1%} confidence.",
                'business_impact': "This anomaly could indicate either an opportunity to capitalize on or a problem that needs immediate attention.",
                'recommended_actions': [
                    "Investigate the cause of this anomaly immediately",
                    "Check if external factors influenced this pattern",
                    "Implement monitoring to catch similar anomalies early"
                ],
                'urgency_level': 'critical' if insight.confidence > 0.9 else 'high'
            },
            'prediction': {
                'explanation': f"Our predictive model forecasts {insight.title.lower()} with {insight.confidence:.1%} accuracy based on current trends.",
                'business_impact': "This prediction can help you make proactive decisions and optimize resource allocation.",
                'recommended_actions': [
                    "Plan resources based on this prediction",
                    "Set up monitoring to track prediction accuracy",
                    "Prepare contingency plans for different scenarios"
                ],
                'urgency_level': 'medium'
            }
        }
        
        template = demo_explanations.get(insight.insight_type, demo_explanations['trend'])
        
        return ExplainedInsight(
            raw_insight=insight,
            explanation=template['explanation'],
            business_impact=template['business_impact'],
            recommended_actions=template['recommended_actions'],
            urgency_level=template['urgency_level'],
            potential_value=None
        )
    
    def _create_fallback_insight(self, insight: RawInsight) -> ExplainedInsight:
        """Create fallback insight when LLM fails"""
        return ExplainedInsight(
            raw_insight=insight,
            explanation=f"Analysis shows {insight.title} with {insight.confidence:.1%} confidence.",
            business_impact="This insight requires further analysis to determine business impact.",
            recommended_actions=["Review the underlying data", "Consult with domain experts", "Monitor for additional patterns"],
            urgency_level='medium'
        )

class BusinessContextManager:
    """Manages business context for better insight generation"""
    
    def __init__(self):
        self.user_contexts = {}
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get business context for a user"""
        return self.user_contexts.get(user_id, {
            'industry': 'general',
            'business_size': 'small',
            'key_goals': ['increase_revenue', 'reduce_costs'],
            'data_sources': []
        })
    
    def update_user_context(self, user_id: str, context: Dict[str, Any]):
        """Update business context for a user"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        
        self.user_contexts[user_id].update(context)
    
    def infer_context_from_data(self, data_sources: List[str]) -> Dict[str, Any]:
        """Infer business context from available data sources"""
        context = {'industry': 'general', 'data_sources': data_sources}
        
        # Infer industry from data sources
        if any('vehicle' in source.lower() or 'automotive' in source.lower() for source in data_sources):
            context['industry'] = 'automotive'
        elif any('restaurant' in source.lower() or 'food' in source.lower() for source in data_sources):
            context['industry'] = 'restaurant'
        elif any('retail' in source.lower() or 'inventory' in source.lower() for source in data_sources):
            context['industry'] = 'retail'
        
        return context
