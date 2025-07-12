"""
User-Specific AI Personalization System
Learns each user's business patterns, preferences, and context for increasingly personalized insights
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class PersonalizationLevel(Enum):
    BASIC = "basic"           # Industry templates only
    ADAPTIVE = "adaptive"     # Learning user patterns
    PERSONALIZED = "personalized"  # Fully customized to user
    EXPERT = "expert"         # Advanced user-specific optimizations

class LearningDimension(Enum):
    BUSINESS_PATTERNS = "business_patterns"
    USER_PREFERENCES = "user_preferences"
    INTERACTION_STYLE = "interaction_style"
    DECISION_CONTEXT = "decision_context"
    PERFORMANCE_GOALS = "performance_goals"

@dataclass
class PersonalizationProfile:
    """Comprehensive user personalization profile"""
    user_id: str
    personalization_level: PersonalizationLevel
    industry: str
    business_context: Dict[str, Any]
    
    # Learning dimensions
    business_patterns: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_style: Dict[str, Any] = field(default_factory=dict)
    decision_context: Dict[str, Any] = field(default_factory=dict)
    performance_goals: Dict[str, Any] = field(default_factory=dict)
    
    # Personalization metrics
    learning_progress: Dict[str, float] = field(default_factory=dict)
    personalization_score: float = 0.0
    user_satisfaction: float = 0.0
    engagement_level: float = 0.0
    
    # Interaction history
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    decision_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Temporal tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None

@dataclass
class PersonalizedInsight:
    """Insight tailored to specific user"""
    insight_id: str
    user_id: str
    base_insight: Dict[str, Any]
    personalization_applied: List[str]
    user_context: Dict[str, Any]
    personalized_explanation: str
    personalized_actions: List[str]
    relevance_score: float
    confidence_score: float
    business_impact_score: float
    created_at: datetime = field(default_factory=datetime.now)

class UserAIPersonalization:
    """AI system that learns and adapts to individual users"""
    
    def __init__(self):
        self.user_profiles = {}  # user_id -> PersonalizationProfile
        self.personalization_models = {}  # user_id -> personalization_model
        self.learning_engines = {}  # dimension -> learning_engine
        
        # Personalization statistics
        self.personalization_stats = {
            'total_users': 0,
            'personalization_levels': {level.value: 0 for level in PersonalizationLevel},
            'average_satisfaction': 0.0,
            'average_engagement': 0.0,
            'learning_effectiveness': 0.0
        }
        
        # Initialize learning engines
        self._initialize_learning_engines()
    
    def _initialize_learning_engines(self):
        """Initialize learning engines for different dimensions"""
        
        self.learning_engines = {
            LearningDimension.BUSINESS_PATTERNS: BusinessPatternLearner(),
            LearningDimension.USER_PREFERENCES: UserPreferenceLearner(),
            LearningDimension.INTERACTION_STYLE: InteractionStyleLearner(),
            LearningDimension.DECISION_CONTEXT: DecisionContextLearner(),
            LearningDimension.PERFORMANCE_GOALS: PerformanceGoalLearner()
        }
    
    async def initialize_user_personalization(self, user_id: str, 
                                            initial_context: Dict[str, Any]) -> PersonalizationProfile:
        """Initialize personalization for a new user"""
        
        # Create initial profile
        profile = PersonalizationProfile(
            user_id=user_id,
            personalization_level=PersonalizationLevel.BASIC,
            industry=initial_context.get('industry', 'general'),
            business_context=initial_context
        )
        
        # Set initial learning progress
        for dimension in LearningDimension:
            profile.learning_progress[dimension.value] = 0.0
        
        # Store profile
        self.user_profiles[user_id] = profile
        
        # Update statistics
        self.personalization_stats['total_users'] += 1
        self.personalization_stats['personalization_levels'][PersonalizationLevel.BASIC.value] += 1
        
        logger.info(f"Initialized personalization for user {user_id} in {profile.industry} industry")
        
        return profile
    
    async def learn_from_interaction(self, user_id: str, interaction_data: Dict[str, Any]):
        """Learn from user interaction"""
        
        profile = await self._get_or_create_profile(user_id, interaction_data)
        
        # Record interaction
        interaction_entry = {
            'timestamp': datetime.now().isoformat(),
            'interaction_type': interaction_data.get('type', 'unknown'),
            'data': interaction_data
        }
        profile.interaction_history.append(interaction_entry)
        profile.last_interaction = datetime.now()
        
        # Apply learning across dimensions
        learning_updates = {}
        
        for dimension, learner in self.learning_engines.items():
            update = await learner.learn_from_interaction(profile, interaction_data)
            if update:
                learning_updates[dimension.value] = update
        
        # Update profile with learning
        await self._apply_learning_updates(profile, learning_updates)
        
        # Update personalization level if warranted
        await self._update_personalization_level(profile)
        
        # Update engagement metrics
        self._update_engagement_metrics(profile, interaction_data)
        
        profile.last_updated = datetime.now()
        
        logger.debug(f"Learned from interaction for user {user_id}: {interaction_data.get('type', 'unknown')}")
    
    async def learn_from_feedback(self, user_id: str, feedback_data: Dict[str, Any]):
        """Learn from user feedback"""
        
        profile = await self._get_or_create_profile(user_id, {})
        
        # Record feedback
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'feedback_type': feedback_data.get('type', 'general'),
            'satisfaction_score': feedback_data.get('satisfaction_score', 0),
            'data': feedback_data
        }
        profile.feedback_history.append(feedback_entry)
        
        # Update user satisfaction
        satisfaction_scores = [f['satisfaction_score'] for f in profile.feedback_history[-10:]]  # Last 10
        profile.user_satisfaction = np.mean(satisfaction_scores)
        
        # Apply feedback learning
        for dimension, learner in self.learning_engines.items():
            await learner.learn_from_feedback(profile, feedback_data)
        
        # Update personalization score
        await self._update_personalization_score(profile)
        
        profile.last_updated = datetime.now()
        
        logger.info(f"Learned from feedback for user {user_id}: satisfaction={feedback_data.get('satisfaction_score', 0)}")
    
    async def learn_from_decision(self, user_id: str, decision_data: Dict[str, Any]):
        """Learn from user business decisions"""
        
        profile = await self._get_or_create_profile(user_id, {})
        
        # Record decision
        decision_entry = {
            'timestamp': datetime.now().isoformat(),
            'decision_type': decision_data.get('type', 'unknown'),
            'context': decision_data.get('context', {}),
            'outcome': decision_data.get('outcome', {}),
            'data': decision_data
        }
        profile.decision_history.append(decision_entry)
        
        # Learn decision patterns
        decision_learner = self.learning_engines[LearningDimension.DECISION_CONTEXT]
        await decision_learner.learn_from_decision(profile, decision_data)
        
        # Update performance goals based on decisions
        goal_learner = self.learning_engines[LearningDimension.PERFORMANCE_GOALS]
        await goal_learner.learn_from_decision(profile, decision_data)
        
        profile.last_updated = datetime.now()
        
        logger.debug(f"Learned from decision for user {user_id}: {decision_data.get('type', 'unknown')}")
    
    async def personalize_insight(self, user_id: str, base_insight: Dict[str, Any]) -> PersonalizedInsight:
        """Personalize an insight for a specific user"""
        
        profile = await self._get_or_create_profile(user_id, {})
        
        # Generate personalized insight
        insight_id = f"insight_{user_id}_{int(datetime.now().timestamp())}"
        
        # Apply personalization layers
        personalization_applied = []
        personalized_explanation = base_insight.get('explanation', '')
        personalized_actions = base_insight.get('actions', [])
        
        # Business pattern personalization
        if profile.business_patterns:
            personalized_explanation = await self._personalize_explanation_for_business(
                personalized_explanation, profile.business_patterns
            )
            personalization_applied.append('business_patterns')
        
        # User preference personalization
        if profile.user_preferences:
            personalized_actions = await self._personalize_actions_for_preferences(
                personalized_actions, profile.user_preferences
            )
            personalization_applied.append('user_preferences')
        
        # Interaction style personalization
        if profile.interaction_style:
            personalized_explanation = await self._personalize_explanation_for_style(
                personalized_explanation, profile.interaction_style
            )
            personalization_applied.append('interaction_style')
        
        # Calculate relevance and confidence scores
        relevance_score = await self._calculate_relevance_score(base_insight, profile)
        confidence_score = base_insight.get('confidence', 0.5)
        business_impact_score = await self._calculate_business_impact_score(base_insight, profile)
        
        # Create personalized insight
        personalized_insight = PersonalizedInsight(
            insight_id=insight_id,
            user_id=user_id,
            base_insight=base_insight,
            personalization_applied=personalization_applied,
            user_context=self._extract_user_context(profile),
            personalized_explanation=personalized_explanation,
            personalized_actions=personalized_actions,
            relevance_score=relevance_score,
            confidence_score=confidence_score,
            business_impact_score=business_impact_score
        )
        
        logger.debug(f"Personalized insight for user {user_id}: {len(personalization_applied)} layers applied")
        
        return personalized_insight
    
    async def get_personalized_recommendations(self, user_id: str, 
                                             context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        
        profile = await self._get_or_create_profile(user_id, context or {})
        
        recommendations = []
        
        # Business pattern recommendations
        if profile.personalization_level in [PersonalizationLevel.ADAPTIVE, PersonalizationLevel.PERSONALIZED, PersonalizationLevel.EXPERT]:
            business_recs = await self._generate_business_pattern_recommendations(profile)
            recommendations.extend(business_recs)
        
        # Performance goal recommendations
        if profile.performance_goals:
            goal_recs = await self._generate_performance_goal_recommendations(profile)
            recommendations.extend(goal_recs)
        
        # Industry-specific recommendations
        industry_recs = await self._generate_industry_recommendations(profile)
        recommendations.extend(industry_recs)
        
        # Sort by relevance and business impact
        recommendations.sort(key=lambda x: x.get('relevance_score', 0) * x.get('business_impact', 0), reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    async def _get_or_create_profile(self, user_id: str, context: Dict[str, Any]) -> PersonalizationProfile:
        """Get existing profile or create new one"""
        
        if user_id not in self.user_profiles:
            await self.initialize_user_personalization(user_id, context)
        
        return self.user_profiles[user_id]
    
    async def _apply_learning_updates(self, profile: PersonalizationProfile, 
                                    learning_updates: Dict[str, Any]):
        """Apply learning updates to user profile"""
        
        for dimension, update in learning_updates.items():
            if dimension == LearningDimension.BUSINESS_PATTERNS.value:
                profile.business_patterns.update(update)
            elif dimension == LearningDimension.USER_PREFERENCES.value:
                profile.user_preferences.update(update)
            elif dimension == LearningDimension.INTERACTION_STYLE.value:
                profile.interaction_style.update(update)
            elif dimension == LearningDimension.DECISION_CONTEXT.value:
                profile.decision_context.update(update)
            elif dimension == LearningDimension.PERFORMANCE_GOALS.value:
                profile.performance_goals.update(update)
            
            # Update learning progress
            current_progress = profile.learning_progress.get(dimension, 0.0)
            profile.learning_progress[dimension] = min(current_progress + 0.1, 1.0)
    
    async def _update_personalization_level(self, profile: PersonalizationProfile):
        """Update user's personalization level based on learning progress"""
        
        avg_progress = np.mean(list(profile.learning_progress.values()))
        
        old_level = profile.personalization_level
        
        if avg_progress >= 0.8:
            profile.personalization_level = PersonalizationLevel.EXPERT
        elif avg_progress >= 0.6:
            profile.personalization_level = PersonalizationLevel.PERSONALIZED
        elif avg_progress >= 0.3:
            profile.personalization_level = PersonalizationLevel.ADAPTIVE
        else:
            profile.personalization_level = PersonalizationLevel.BASIC
        
        # Update statistics if level changed
        if old_level != profile.personalization_level:
            self.personalization_stats['personalization_levels'][old_level.value] -= 1
            self.personalization_stats['personalization_levels'][profile.personalization_level.value] += 1
            
            logger.info(f"User {profile.user_id} advanced to {profile.personalization_level.value} level")
    
    def _update_engagement_metrics(self, profile: PersonalizationProfile, 
                                 interaction_data: Dict[str, Any]):
        """Update user engagement metrics"""
        
        # Simple engagement scoring based on interaction frequency and type
        interaction_type = interaction_data.get('type', 'unknown')
        
        engagement_weights = {
            'question_click': 0.3,
            'insight_view': 0.2,
            'action_taken': 0.5,
            'feedback_provided': 0.4,
            'dashboard_visit': 0.1
        }
        
        engagement_boost = engagement_weights.get(interaction_type, 0.1)
        
        # Update engagement with decay
        current_engagement = profile.engagement_level
        profile.engagement_level = min(current_engagement * 0.95 + engagement_boost, 1.0)
    
    async def _update_personalization_score(self, profile: PersonalizationProfile):
        """Update overall personalization score"""
        
        # Combine learning progress, satisfaction, and engagement
        avg_learning = np.mean(list(profile.learning_progress.values()))
        satisfaction = profile.user_satisfaction / 5.0  # Normalize to 0-1
        engagement = profile.engagement_level
        
        profile.personalization_score = (avg_learning * 0.4 + satisfaction * 0.4 + engagement * 0.2)
    
    def get_user_profile(self, user_id: str) -> Optional[PersonalizationProfile]:
        """Get user personalization profile"""
        return self.user_profiles.get(user_id)
    
    def get_personalization_statistics(self) -> Dict[str, Any]:
        """Get personalization statistics"""
        
        # Update averages
        if self.user_profiles:
            satisfactions = [p.user_satisfaction for p in self.user_profiles.values()]
            engagements = [p.engagement_level for p in self.user_profiles.values()]
            personalizations = [p.personalization_score for p in self.user_profiles.values()]
            
            self.personalization_stats['average_satisfaction'] = np.mean(satisfactions)
            self.personalization_stats['average_engagement'] = np.mean(engagements)
            self.personalization_stats['learning_effectiveness'] = np.mean(personalizations)
        
        return self.personalization_stats.copy()

    # Personalization Helper Methods
    async def _personalize_explanation_for_business(self, explanation: str,
                                                  business_patterns: Dict[str, Any]) -> str:
        """Personalize explanation based on business patterns"""

        # Add business context to explanation
        if 'decision_patterns' in business_patterns:
            patterns = business_patterns['decision_patterns']
            if patterns:
                explanation += f" Based on your typical {list(patterns.keys())[0]} patterns, "
                explanation += "this aligns with your business decision-making style."

        return explanation

    async def _personalize_actions_for_preferences(self, actions: List[str],
                                                 preferences: Dict[str, Any]) -> List[str]:
        """Personalize actions based on user preferences"""

        action_style = preferences.get('action_style', 'specific')
        detail_level = preferences.get('detail_level', 'medium')

        personalized_actions = []

        for action in actions:
            if action_style == 'specific' and detail_level == 'high':
                # Add more specific details
                personalized_actions.append(f"Specifically: {action} (with detailed implementation steps)")
            elif action_style == 'general' and detail_level == 'low':
                # Simplify action
                personalized_actions.append(action.split('.')[0])  # Take first sentence
            else:
                personalized_actions.append(action)

        return personalized_actions

    async def _personalize_explanation_for_style(self, explanation: str,
                                               interaction_style: Dict[str, Any]) -> str:
        """Personalize explanation based on interaction style"""

        engagement_style = interaction_style.get('engagement_style', 'standard')

        if engagement_style == 'interactive':
            # Add interactive elements
            explanation += " Would you like to explore this pattern further?"
        elif engagement_style == 'analytical':
            # Add more analytical context
            explanation += " This analysis is based on statistical significance testing."

        return explanation

    async def _calculate_relevance_score(self, insight: Dict[str, Any],
                                       profile: PersonalizationProfile) -> float:
        """Calculate how relevant an insight is to the user"""

        relevance = 0.5  # Base relevance

        # Industry relevance
        insight_industry = insight.get('industry_context', {})
        if insight_industry.get('industry') == profile.industry:
            relevance += 0.2

        # Business pattern relevance
        insight_patterns = insight.get('patterns', [])
        user_patterns = list(profile.business_patterns.keys())

        pattern_overlap = len(set(insight_patterns) & set(user_patterns))
        if pattern_overlap > 0:
            relevance += 0.2 * (pattern_overlap / max(len(insight_patterns), 1))

        # Performance goal relevance
        insight_goals = insight.get('related_goals', [])
        user_goals = profile.performance_goals.get('primary_goals', [])

        goal_overlap = len(set(insight_goals) & set(user_goals))
        if goal_overlap > 0:
            relevance += 0.1 * (goal_overlap / max(len(insight_goals), 1))

        return min(relevance, 1.0)

    async def _calculate_business_impact_score(self, insight: Dict[str, Any],
                                             profile: PersonalizationProfile) -> float:
        """Calculate potential business impact for the user"""

        base_impact = insight.get('business_impact_score', 0.5)

        # Adjust based on user's business size
        business_size = profile.business_context.get('business_size', 'medium')
        size_multipliers = {'small': 1.2, 'medium': 1.0, 'large': 0.8}

        adjusted_impact = base_impact * size_multipliers.get(business_size, 1.0)

        # Adjust based on user's performance goals
        if profile.performance_goals:
            primary_goals = profile.performance_goals.get('primary_goals', [])
            insight_goals = insight.get('related_goals', [])

            if set(primary_goals) & set(insight_goals):
                adjusted_impact *= 1.3  # Boost if aligned with goals

        return min(adjusted_impact, 1.0)

    def _extract_user_context(self, profile: PersonalizationProfile) -> Dict[str, Any]:
        """Extract relevant user context for personalization"""

        return {
            'industry': profile.industry,
            'personalization_level': profile.personalization_level.value,
            'business_size': profile.business_context.get('business_size', 'unknown'),
            'primary_goals': profile.performance_goals.get('primary_goals', []),
            'engagement_style': profile.interaction_style.get('engagement_style', 'standard'),
            'satisfaction_level': profile.user_satisfaction
        }

    async def _generate_business_pattern_recommendations(self, profile: PersonalizationProfile) -> List[Dict[str, Any]]:
        """Generate recommendations based on business patterns"""

        recommendations = []

        if 'decision_patterns' in profile.business_patterns:
            patterns = profile.business_patterns['decision_patterns']

            for decision_type, pattern_data in patterns.items():
                recommendations.append({
                    'type': 'business_pattern',
                    'title': f"Optimize {decision_type} Decision Process",
                    'description': f"Based on your {decision_type} patterns, consider optimizing timing and context factors.",
                    'relevance_score': 0.8,
                    'business_impact': 0.7,
                    'actions': [
                        f"Review {decision_type} decision timing",
                        "Analyze context factors for better outcomes",
                        "Set up automated alerts for optimal decision windows"
                    ]
                })

        return recommendations

    async def _generate_performance_goal_recommendations(self, profile: PersonalizationProfile) -> List[Dict[str, Any]]:
        """Generate recommendations based on performance goals"""

        recommendations = []

        primary_goals = profile.performance_goals.get('primary_goals', [])

        for goal in primary_goals:
            recommendations.append({
                'type': 'performance_goal',
                'title': f"Accelerate {goal.title()} Achievement",
                'description': f"Personalized strategies to achieve your {goal} objectives faster.",
                'relevance_score': 0.9,
                'business_impact': 0.8,
                'actions': [
                    f"Set up {goal}-specific KPI tracking",
                    f"Implement {goal} optimization strategies",
                    f"Monitor {goal} progress with automated reports"
                ]
            })

        return recommendations

    async def _generate_industry_recommendations(self, profile: PersonalizationProfile) -> List[Dict[str, Any]]:
        """Generate industry-specific recommendations"""

        industry_recommendations = {
            'automotive': [
                {
                    'type': 'industry_specific',
                    'title': 'Optimize Vehicle Inventory Turnover',
                    'description': 'Improve inventory management based on seasonal demand patterns.',
                    'relevance_score': 0.7,
                    'business_impact': 0.8,
                    'actions': ['Analyze seasonal trends', 'Optimize inventory levels', 'Improve forecasting']
                }
            ],
            'restaurant': [
                {
                    'type': 'industry_specific',
                    'title': 'Enhance Customer Experience During Peak Hours',
                    'description': 'Optimize operations for better customer satisfaction during busy periods.',
                    'relevance_score': 0.8,
                    'business_impact': 0.7,
                    'actions': ['Analyze peak hour patterns', 'Optimize staffing', 'Improve table turnover']
                }
            ],
            'retail': [
                {
                    'type': 'industry_specific',
                    'title': 'Improve Customer Segmentation Strategy',
                    'description': 'Enhance targeting and personalization for different customer segments.',
                    'relevance_score': 0.8,
                    'business_impact': 0.9,
                    'actions': ['Refine customer segments', 'Personalize marketing', 'Optimize pricing']
                }
            ]
        }

        return industry_recommendations.get(profile.industry, [])

# Learning Engine Classes

class BaseLearningEngine:
    """Base class for learning engines"""

    async def learn_from_interaction(self, profile: PersonalizationProfile,
                                   interaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn from user interaction"""
        return None

    async def learn_from_feedback(self, profile: PersonalizationProfile,
                                feedback_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn from user feedback"""
        return None

    async def learn_from_decision(self, profile: PersonalizationProfile,
                                decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn from user decision"""
        return None

class BusinessPatternLearner(BaseLearningEngine):
    """Learns user's business patterns and cycles"""

    async def learn_from_interaction(self, profile: PersonalizationProfile,
                                   interaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        # Learn from data viewing patterns
        if interaction_data.get('type') == 'data_view':
            data_type = interaction_data.get('data_type')
            time_of_day = datetime.now().hour

            return {
                'preferred_data_types': {data_type: time_of_day},
                'viewing_patterns': {
                    'peak_hours': [time_of_day],
                    'data_preferences': [data_type]
                }
            }

        return None

    async def learn_from_decision(self, profile: PersonalizationProfile,
                                decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        # Learn business decision patterns
        decision_type = decision_data.get('type')
        context = decision_data.get('context', {})

        return {
            'decision_patterns': {
                decision_type: {
                    'frequency': 1,
                    'context_factors': list(context.keys()),
                    'typical_timing': datetime.now().hour
                }
            }
        }

class UserPreferenceLearner(BaseLearningEngine):
    """Learns user's preferences for insights and actions"""

    async def learn_from_feedback(self, profile: PersonalizationProfile,
                                feedback_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        # Learn from insight preferences
        if 'insight_preferences' in feedback_data:
            preferences = feedback_data['insight_preferences']

            return {
                'insight_types': preferences.get('preferred_types', []),
                'detail_level': preferences.get('detail_level', 'medium'),
                'action_style': preferences.get('action_style', 'specific'),
                'communication_style': preferences.get('communication_style', 'professional')
            }

        return None

class InteractionStyleLearner(BaseLearningEngine):
    """Learns user's interaction and communication style"""

    async def learn_from_interaction(self, profile: PersonalizationProfile,
                                   interaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        interaction_type = interaction_data.get('type')

        # Learn from question clicking patterns
        if interaction_type == 'question_click':
            question_type = interaction_data.get('question_type', 'unknown')

            return {
                'preferred_question_types': [question_type],
                'interaction_frequency': 1,
                'engagement_style': 'interactive'
            }

        # Learn from dashboard usage
        elif interaction_type == 'dashboard_visit':
            duration = interaction_data.get('duration', 0)

            return {
                'session_duration_preference': duration,
                'engagement_depth': 'deep' if duration > 300 else 'quick'
            }

        return None

class DecisionContextLearner(BaseLearningEngine):
    """Learns the context in which user makes decisions"""

    async def learn_from_decision(self, profile: PersonalizationProfile,
                                decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        context = decision_data.get('context', {})
        outcome = decision_data.get('outcome', {})

        return {
            'decision_factors': list(context.keys()),
            'success_patterns': {
                'context': context,
                'outcome_quality': outcome.get('success_score', 0.5)
            },
            'decision_timing': {
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            }
        }

class PerformanceGoalLearner(BaseLearningEngine):
    """Learns user's performance goals and priorities"""

    async def learn_from_feedback(self, profile: PersonalizationProfile,
                                feedback_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        # Learn from goal-related feedback
        if 'performance_goals' in feedback_data:
            goals = feedback_data['performance_goals']

            return {
                'primary_goals': goals.get('primary', []),
                'secondary_goals': goals.get('secondary', []),
                'success_metrics': goals.get('metrics', []),
                'time_horizons': goals.get('time_horizons', {})
            }

        return None

    async def learn_from_decision(self, profile: PersonalizationProfile,
                                decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        # Infer goals from decisions
        decision_type = decision_data.get('type')
        outcome = decision_data.get('outcome', {})

        if decision_type == 'investment':
            return {
                'financial_goals': ['growth', 'roi_optimization'],
                'risk_tolerance': outcome.get('risk_level', 'medium')
            }
        elif decision_type == 'operational':
            return {
                'operational_goals': ['efficiency', 'cost_reduction'],
                'optimization_focus': outcome.get('focus_area', 'general')
            }

        return None
