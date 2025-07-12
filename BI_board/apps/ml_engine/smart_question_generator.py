"""
Smart Question Generator
Automatically discovers interesting patterns in data and generates clickable questions for users
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .llm_insight_generator import ExplainedInsight

logger = logging.getLogger(__name__)

@dataclass
class SmartQuestion:
    """A smart question generated from data insights"""
    question_id: str
    question_text: str
    question_type: str  # 'trend', 'anomaly', 'comparison', 'opportunity', 'concern'
    priority_score: float  # 0-1
    insight_preview: str
    full_answer: str
    business_impact: str
    data_evidence: Dict[str, Any]
    recommended_actions: List[str]
    urgency_level: str

@dataclass
class QuestionSet:
    """A set of smart questions for a user"""
    questions: List[SmartQuestion]
    executive_summary: str
    total_questions: int
    high_priority_count: int
    generated_at: datetime

class SmartQuestionGenerator:
    """Generates smart, clickable questions from business insights"""
    
    def __init__(self):
        # Question templates for different insight types
        self.question_templates = {
            'revenue_increase': {
                'template': "Why did {period} revenue increase {percentage}?",
                'type': 'opportunity',
                'priority_base': 0.8
            },
            'revenue_decrease': {
                'template': "Why did {period} revenue decrease {percentage}?",
                'type': 'concern',
                'priority_base': 0.9
            },
            'customer_growth': {
                'template': "What's driving the {percentage} customer growth?",
                'type': 'opportunity',
                'priority_base': 0.7
            },
            'anomaly_detected': {
                'template': "What caused the unusual {metric} pattern on {date}?",
                'type': 'anomaly',
                'priority_base': 0.85
            },
            'trend_analysis': {
                'template': "What's behind the {direction} trend in {metric}?",
                'type': 'trend',
                'priority_base': 0.6
            },
            'performance_comparison': {
                'template': "Why is {metric1} outperforming {metric2}?",
                'type': 'comparison',
                'priority_base': 0.65
            },
            'seasonal_pattern': {
                'template': "Why does {metric} peak during {period}?",
                'type': 'trend',
                'priority_base': 0.55
            },
            'efficiency_opportunity': {
                'template': "How can you improve {metric} efficiency?",
                'type': 'opportunity',
                'priority_base': 0.7
            }
        }
        
        # Industry-specific question templates
        self.industry_templates = {
            'restaurant': {
                'food_cost_spike': "Why did food costs increase {percentage} this {period}?",
                'table_turnover': "How can you improve table turnover during {time_period}?",
                'menu_performance': "Which menu items are driving profitability?",
                'peak_hour_analysis': "What's causing the {time} rush patterns?"
            },
            'automotive': {
                'inventory_turnover': "Why is {vehicle_type} inventory moving {speed}?",
                'service_revenue': "What's driving service department performance?",
                'customer_satisfaction': "How can you improve customer satisfaction scores?",
                'seasonal_sales': "Why do {vehicle_type} sales peak in {season}?"
            },
            'retail': {
                'conversion_rate': "What's affecting your {percentage} conversion rate?",
                'inventory_optimization': "Which products should you stock more of?",
                'customer_segments': "Who are your most valuable customer segments?",
                'pricing_strategy': "How is your pricing affecting sales volume?"
            }
        }
    
    def generate_smart_questions(self, explained_insights: List[ExplainedInsight], 
                               business_context: Dict[str, Any] = None,
                               max_questions: int = 8) -> QuestionSet:
        """Generate smart questions from explained insights"""
        
        logger.info(f"Generating smart questions from {len(explained_insights)} insights")
        
        questions = []
        
        # Generate questions from insights
        for insight in explained_insights:
            question = self._create_question_from_insight(insight, business_context)
            if question:
                questions.append(question)
        
        # Add industry-specific questions if applicable
        if business_context and business_context.get('industry'):
            industry_questions = self._generate_industry_questions(business_context)
            questions.extend(industry_questions)
        
        # Sort by priority and limit
        questions.sort(key=lambda q: q.priority_score, reverse=True)
        questions = questions[:max_questions]
        
        # Generate executive summary
        executive_summary = self._generate_question_summary(questions, business_context)
        
        # Count high priority questions
        high_priority_count = sum(1 for q in questions if q.priority_score > 0.7)
        
        return QuestionSet(
            questions=questions,
            executive_summary=executive_summary,
            total_questions=len(questions),
            high_priority_count=high_priority_count,
            generated_at=datetime.now()
        )
    
    def _create_question_from_insight(self, insight: ExplainedInsight, 
                                    business_context: Dict[str, Any] = None) -> Optional[SmartQuestion]:
        """Create a smart question from an explained insight"""
        
        try:
            # Determine question type based on insight
            question_type = self._determine_question_type(insight)
            
            # Generate question text
            question_text = self._generate_question_text(insight, question_type)
            
            # Calculate priority score
            priority_score = self._calculate_question_priority(insight, question_type)
            
            # Create insight preview
            insight_preview = insight.explanation[:100] + "..." if len(insight.explanation) > 100 else insight.explanation
            
            # Generate question ID
            question_id = f"q_{insight.raw_insight.insight_type}_{hash(insight.raw_insight.title) % 10000}"
            
            return SmartQuestion(
                question_id=question_id,
                question_text=question_text,
                question_type=question_type,
                priority_score=priority_score,
                insight_preview=insight_preview,
                full_answer=self._create_full_answer(insight),
                business_impact=insight.business_impact,
                data_evidence=insight.raw_insight.data,
                recommended_actions=insight.recommended_actions,
                urgency_level=insight.urgency_level
            )
            
        except Exception as e:
            logger.error(f"Error creating question from insight: {e}")
            return None
    
    def _determine_question_type(self, insight: ExplainedInsight) -> str:
        """Determine the type of question based on insight characteristics"""
        
        insight_type = insight.raw_insight.insight_type
        urgency = insight.urgency_level
        
        # Map insight types to question types
        type_mapping = {
            'anomaly': 'anomaly',
            'trend': 'trend',
            'prediction': 'opportunity',
            'correlation': 'comparison',
            'statistics': 'trend'
        }
        
        question_type = type_mapping.get(insight_type, 'trend')
        
        # Adjust based on urgency
        if urgency == 'critical':
            question_type = 'concern'
        elif urgency == 'high' and 'increase' in insight.raw_insight.title.lower():
            question_type = 'opportunity'
        
        return question_type
    
    def _generate_question_text(self, insight: ExplainedInsight, question_type: str) -> str:
        """Generate question text based on insight and type"""
        
        title = insight.raw_insight.title
        data = insight.raw_insight.data
        
        # Extract key information from data
        if 'percentage' in str(data) or 'change' in str(data):
            # Look for percentage changes
            for key, value in data.items():
                if isinstance(value, (int, float)) and abs(value) > 1:
                    percentage = f"{abs(value):.1f}%"
                    direction = "increase" if value > 0 else "decrease"
                    return f"Why did {title.lower()} {direction} {percentage}?"
        
        # Default question patterns based on type
        question_patterns = {
            'trend': f"What's driving the trend in {title.lower()}?",
            'anomaly': f"What caused the unusual pattern in {title.lower()}?",
            'opportunity': f"How can you capitalize on {title.lower()}?",
            'concern': f"What's causing the issue with {title.lower()}?",
            'comparison': f"Why is there a difference in {title.lower()}?"
        }
        
        return question_patterns.get(question_type, f"What insights can you gain from {title.lower()}?")
    
    def _calculate_question_priority(self, insight: ExplainedInsight, question_type: str) -> float:
        """Calculate priority score for a question"""
        
        # Base priority from insight confidence
        base_priority = insight.raw_insight.confidence
        
        # Adjust based on urgency
        urgency_multipliers = {
            'critical': 1.2,
            'high': 1.1,
            'medium': 1.0,
            'low': 0.8
        }
        
        urgency_multiplier = urgency_multipliers.get(insight.urgency_level, 1.0)
        
        # Adjust based on question type
        type_multipliers = {
            'concern': 1.15,
            'anomaly': 1.1,
            'opportunity': 1.05,
            'trend': 1.0,
            'comparison': 0.95
        }
        
        type_multiplier = type_multipliers.get(question_type, 1.0)
        
        # Calculate final priority (capped at 1.0)
        priority = min(base_priority * urgency_multiplier * type_multiplier, 1.0)
        
        return priority
    
    def _create_full_answer(self, insight: ExplainedInsight) -> str:
        """Create a comprehensive answer for the question"""
        
        answer_parts = [
            f"**Analysis:** {insight.explanation}",
            f"**Business Impact:** {insight.business_impact}",
            f"**Confidence Level:** {insight.raw_insight.confidence:.1%}",
        ]
        
        if insight.recommended_actions:
            actions_text = "\n".join([f"• {action}" for action in insight.recommended_actions])
            answer_parts.append(f"**Recommended Actions:**\n{actions_text}")
        
        return "\n\n".join(answer_parts)
    
    def _generate_industry_questions(self, business_context: Dict[str, Any]) -> List[SmartQuestion]:
        """Generate industry-specific questions"""
        
        industry = business_context.get('industry')
        questions = []
        
        if industry in self.industry_templates:
            templates = self.industry_templates[industry]
            
            # Generate 1-2 industry-specific questions
            for i, (key, template) in enumerate(list(templates.items())[:2]):
                question_id = f"industry_{industry}_{i}"
                
                questions.append(SmartQuestion(
                    question_id=question_id,
                    question_text=template,
                    question_type='opportunity',
                    priority_score=0.6,
                    insight_preview=f"Industry-specific analysis for {industry} businesses",
                    full_answer=f"This analysis focuses on key {industry} metrics and industry best practices.",
                    business_impact=f"Optimizing {industry}-specific metrics can significantly improve business performance.",
                    data_evidence={'industry': industry, 'analysis_type': key},
                    recommended_actions=[
                        f"Analyze {industry}-specific benchmarks",
                        "Compare with industry standards",
                        "Implement best practices"
                    ],
                    urgency_level='medium'
                ))
        
        return questions
    
    def _generate_question_summary(self, questions: List[SmartQuestion], 
                                 business_context: Dict[str, Any] = None) -> str:
        """Generate executive summary of questions"""
        
        if not questions:
            return "No significant patterns found in your data at this time."
        
        # Count questions by type
        type_counts = {}
        for question in questions:
            type_counts[question.question_type] = type_counts.get(question.question_type, 0) + 1
        
        # Create summary
        summary_parts = []
        
        if type_counts.get('concern', 0) > 0:
            summary_parts.append(f"{type_counts['concern']} area{'s' if type_counts['concern'] > 1 else ''} requiring attention")
        
        if type_counts.get('opportunity', 0) > 0:
            summary_parts.append(f"{type_counts['opportunity']} growth opportunity{'ies' if type_counts['opportunity'] > 1 else 'y'}")
        
        if type_counts.get('anomaly', 0) > 0:
            summary_parts.append(f"{type_counts['anomaly']} unusual pattern{'s' if type_counts['anomaly'] > 1 else ''}")
        
        if not summary_parts:
            summary_parts.append(f"{len(questions)} business insight{'s' if len(questions) > 1 else ''}")
        
        industry = business_context.get('industry', 'business') if business_context else 'business'
        
        return f"I discovered {', '.join(summary_parts)} in your {industry} data. " \
               f"Click any question below for detailed analysis and recommendations."
