"""
Unified Insight Engine
Central hub that connects all analytics engines and generates comprehensive business insights
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .core_ml_engine import MLModelTrainer, AdvancedAnalyticsEngine
from .llm_insight_generator import LLMInsightGenerator, RawInsight, ExplainedInsight, BusinessContextManager
from ..social_intelligence.analytics_engine import SocialAnalyticsEngine
from ..data_pipeline.models import DataSource, DataPipeline

logger = logging.getLogger(__name__)

@dataclass
class ComprehensiveInsightReport:
    """Complete insight report with all analysis results"""
    explained_insights: List[ExplainedInsight]
    recommendations: List[str]
    executive_summary: str
    key_metrics: Dict[str, Any]
    priority_actions: List[str]
    generated_at: datetime
    confidence_score: float

@dataclass
class InsightPriority:
    """Insight priority scoring"""
    urgency_score: float  # 0-1
    business_impact_score: float  # 0-1
    confidence_score: float  # 0-1
    overall_priority: float  # 0-1

class UnifiedInsightEngine:
    """Central engine that orchestrates all analytics and insight generation"""
    
    def __init__(self):
        # Initialize all analytics engines
        self.ml_trainer = MLModelTrainer()
        self.analytics_engine = AdvancedAnalyticsEngine()
        self.social_engine = SocialAnalyticsEngine()
        self.llm_generator = LLMInsightGenerator()
        self.context_manager = BusinessContextManager()
        
        # Insight processing configuration
        self.max_insights_per_report = 10
        self.min_confidence_threshold = 0.6
        
    async def generate_comprehensive_insights(self, user_id: str, 
                                            data_sources: List[str] = None,
                                            industry: str = None) -> ComprehensiveInsightReport:
        """Generate comprehensive insights from all available data sources"""
        
        logger.info(f"Generating comprehensive insights for user {user_id}")
        
        try:
            # 1. Get or infer business context
            business_context = await self._get_business_context(user_id, data_sources, industry)
            
            # 2. Collect data from all sources
            data_collection = await self._collect_all_data(user_id, data_sources)
            
            # 3. Run all analytics engines
            raw_insights = await self._run_all_analytics(data_collection, business_context)
            
            # 4. Filter and prioritize insights
            prioritized_insights = self._prioritize_insights(raw_insights)
            
            # 5. Generate LLM explanations
            explained_insights = await self.llm_generator.explain_insights(
                prioritized_insights, business_context.get('industry', 'general')
            )
            
            # 6. Generate executive summary and recommendations
            executive_summary = await self._generate_executive_summary(explained_insights, business_context)
            recommendations = self._generate_recommendations(explained_insights)
            priority_actions = self._extract_priority_actions(explained_insights)
            
            # 7. Calculate key metrics
            key_metrics = self._calculate_key_metrics(data_collection, explained_insights)
            
            # 8. Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(explained_insights)
            
            return ComprehensiveInsightReport(
                explained_insights=explained_insights,
                recommendations=recommendations,
                executive_summary=executive_summary,
                key_metrics=key_metrics,
                priority_actions=priority_actions,
                generated_at=datetime.now(),
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            return self._create_fallback_report()
    
    async def _get_business_context(self, user_id: str, data_sources: List[str], 
                                  industry: str) -> Dict[str, Any]:
        """Get or infer business context for the user"""
        
        # Get existing context
        context = self.context_manager.get_user_context(user_id)
        
        # Override with provided industry
        if industry:
            context['industry'] = industry
        
        # Infer context from data sources if not set
        if not context.get('industry') or context['industry'] == 'general':
            inferred_context = self.context_manager.infer_context_from_data(data_sources or [])
            context.update(inferred_context)
        
        # Update context
        self.context_manager.update_user_context(user_id, context)
        
        return context
    
    async def _collect_all_data(self, user_id: str, data_sources: List[str]) -> Dict[str, pd.DataFrame]:
        """Collect data from all available sources"""
        
        data_collection = {}
        
        try:
            # TODO: Implement actual data collection from various sources
            # For now, create sample data based on industry
            
            # Sample business data
            data_collection['business_metrics'] = self._create_sample_business_data()
            
            # Sample social media data (if applicable)
            data_collection['social_media'] = self._create_sample_social_data()
            
            # Sample website data (if applicable)
            data_collection['website_analytics'] = self._create_sample_website_data()
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            data_collection = {'sample_data': pd.DataFrame({'value': [1, 2, 3]})}
        
        return data_collection
    
    async def _run_all_analytics(self, data_collection: Dict[str, pd.DataFrame], 
                                business_context: Dict[str, Any]) -> List[RawInsight]:
        """Run all analytics engines and collect insights"""
        
        raw_insights = []
        
        # 1. Run ML analytics
        ml_insights = await self._run_ml_analytics(data_collection, business_context)
        raw_insights.extend(ml_insights)
        
        # 2. Run statistical analytics
        stats_insights = self._run_statistical_analytics(data_collection)
        raw_insights.extend(stats_insights)
        
        # 3. Run social media analytics (if data available)
        if 'social_media' in data_collection:
            social_insights = self._run_social_analytics(data_collection['social_media'])
            raw_insights.extend(social_insights)
        
        return raw_insights
    
    async def _run_ml_analytics(self, data_collection: Dict[str, pd.DataFrame], 
                               business_context: Dict[str, Any]) -> List[RawInsight]:
        """Run ML model analytics"""
        
        insights = []
        
        try:
            # Get main business data
            if 'business_metrics' in data_collection:
                df = data_collection['business_metrics']
                
                # Run trend analysis
                if len(df) > 10:  # Need sufficient data for trends
                    trend_insight = self._analyze_trends(df)
                    if trend_insight:
                        insights.append(trend_insight)
                
                # Run anomaly detection
                anomaly_insight = self._detect_anomalies(df)
                if anomaly_insight:
                    insights.append(anomaly_insight)
                
                # Industry-specific analysis
                industry_insights = self._run_industry_specific_analysis(df, business_context)
                insights.extend(industry_insights)
        
        except Exception as e:
            logger.error(f"Error in ML analytics: {e}")
        
        return insights
    
    def _run_statistical_analytics(self, data_collection: Dict[str, pd.DataFrame]) -> List[RawInsight]:
        """Run statistical analysis"""
        
        insights = []
        
        try:
            for source_name, df in data_collection.items():
                if len(df) > 5:  # Need minimum data for stats
                    
                    # Descriptive statistics
                    stats_result = self.analytics_engine.perform_statistical_analysis(
                        df, 'descriptive_statistics'
                    )
                    
                    if stats_result:
                        insights.append(RawInsight(
                            insight_type='statistics',
                            title=f'Statistical Summary for {source_name}',
                            data=stats_result,
                            confidence=0.9,
                            source='analytics_engine',
                            timestamp=datetime.now()
                        ))
                    
                    # Correlation analysis
                    if len(df.select_dtypes(include=['number']).columns) > 1:
                        corr_result = self.analytics_engine.perform_statistical_analysis(
                            df, 'correlation_analysis'
                        )
                        
                        if corr_result and corr_result.get('strong_correlations'):
                            insights.append(RawInsight(
                                insight_type='correlation',
                                title=f'Strong Correlations in {source_name}',
                                data=corr_result,
                                confidence=0.8,
                                source='analytics_engine',
                                timestamp=datetime.now()
                            ))
        
        except Exception as e:
            logger.error(f"Error in statistical analytics: {e}")
        
        return insights
    
    def _run_social_analytics(self, social_df: pd.DataFrame) -> List[RawInsight]:
        """Run social media analytics"""
        
        insights = []
        
        try:
            # Analyze engagement patterns
            if 'engagement_rate' in social_df.columns:
                avg_engagement = social_df['engagement_rate'].mean()
                
                insights.append(RawInsight(
                    insight_type='social_performance',
                    title='Social Media Engagement Analysis',
                    data={
                        'average_engagement_rate': avg_engagement,
                        'total_posts': len(social_df),
                        'engagement_trend': 'increasing' if social_df['engagement_rate'].iloc[-1] > avg_engagement else 'stable'
                    },
                    confidence=0.85,
                    source='social_engine',
                    timestamp=datetime.now()
                ))
        
        except Exception as e:
            logger.error(f"Error in social analytics: {e}")
        
        return insights
    
    def _prioritize_insights(self, raw_insights: List[RawInsight]) -> List[RawInsight]:
        """Prioritize insights by business impact and confidence"""
        
        # Calculate priority scores
        prioritized = []
        
        for insight in raw_insights:
            priority = self._calculate_insight_priority(insight)
            
            # Only include insights above threshold
            if priority.overall_priority >= self.min_confidence_threshold:
                prioritized.append((insight, priority))
        
        # Sort by priority and return top insights
        prioritized.sort(key=lambda x: x[1].overall_priority, reverse=True)
        
        return [insight for insight, _ in prioritized[:self.max_insights_per_report]]
    
    def _calculate_insight_priority(self, insight: RawInsight) -> InsightPriority:
        """Calculate priority score for an insight"""
        
        # Urgency based on insight type
        urgency_scores = {
            'anomaly': 0.9,
            'trend': 0.7,
            'prediction': 0.6,
            'correlation': 0.5,
            'statistics': 0.4
        }
        
        urgency_score = urgency_scores.get(insight.insight_type, 0.5)
        
        # Business impact based on data significance
        business_impact_score = min(insight.confidence * 1.2, 1.0)
        
        # Confidence score
        confidence_score = insight.confidence
        
        # Overall priority (weighted average)
        overall_priority = (
            urgency_score * 0.4 +
            business_impact_score * 0.4 +
            confidence_score * 0.2
        )
        
        return InsightPriority(
            urgency_score=urgency_score,
            business_impact_score=business_impact_score,
            confidence_score=confidence_score,
            overall_priority=overall_priority
        )
    
    # Helper methods for sample data creation (for testing)
    def _create_sample_business_data(self) -> pd.DataFrame:
        """Create sample business data for testing"""
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        
        return pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(10000, 2000, 90) + np.sin(np.arange(90) * 2 * np.pi / 7) * 1000,
            'customers': np.random.poisson(100, 90),
            'conversion_rate': np.random.normal(0.05, 0.01, 90),
            'avg_order_value': np.random.normal(100, 20, 90)
        })
    
    def _create_sample_social_data(self) -> pd.DataFrame:
        """Create sample social media data for testing"""
        import numpy as np
        
        return pd.DataFrame({
            'post_id': range(50),
            'engagement_rate': np.random.normal(0.05, 0.02, 50),
            'likes': np.random.poisson(100, 50),
            'comments': np.random.poisson(20, 50),
            'shares': np.random.poisson(10, 50)
        })
    
    def _create_sample_website_data(self) -> pd.DataFrame:
        """Create sample website analytics data for testing"""
        import numpy as np
        
        return pd.DataFrame({
            'page_views': np.random.poisson(1000, 30),
            'unique_visitors': np.random.poisson(800, 30),
            'bounce_rate': np.random.normal(0.4, 0.1, 30),
            'session_duration': np.random.normal(180, 60, 30)
        })
    
    def _analyze_trends(self, df: pd.DataFrame) -> Optional[RawInsight]:
        """Analyze trends in business data"""
        try:
            if 'revenue' in df.columns and len(df) > 10:
                # Calculate trend
                x = range(len(df))
                y = df['revenue'].values
                slope, intercept = np.polyfit(x, y, 1)

                # Calculate trend strength
                correlation = np.corrcoef(x, y)[0, 1]

                if abs(correlation) > 0.3:  # Significant trend
                    trend_direction = 'increasing' if slope > 0 else 'decreasing'

                    return RawInsight(
                        insight_type='trend',
                        title=f'Revenue Trend: {trend_direction.title()}',
                        data={
                            'trend_direction': trend_direction,
                            'slope': slope,
                            'correlation': correlation,
                            'current_value': float(df['revenue'].iloc[-1]),
                            'period_change': float(df['revenue'].iloc[-1] - df['revenue'].iloc[0])
                        },
                        confidence=abs(correlation),
                        source='ml_engine',
                        timestamp=datetime.now()
                    )
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")

        return None

    def _detect_anomalies(self, df: pd.DataFrame) -> Optional[RawInsight]:
        """Detect anomalies in business data"""
        try:
            if 'revenue' in df.columns and len(df) > 5:
                revenue = df['revenue']
                Q1 = revenue.quantile(0.25)
                Q3 = revenue.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                anomalies = df[(revenue < lower_bound) | (revenue > upper_bound)]

                if len(anomalies) > 0:
                    return RawInsight(
                        insight_type='anomaly',
                        title=f'Revenue Anomalies Detected',
                        data={
                            'anomaly_count': len(anomalies),
                            'anomaly_percentage': len(anomalies) / len(df) * 100,
                            'anomaly_values': anomalies['revenue'].tolist()[:5],  # Top 5
                            'normal_range': [float(lower_bound), float(upper_bound)]
                        },
                        confidence=0.8,
                        source='ml_engine',
                        timestamp=datetime.now()
                    )
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")

        return None

    def _run_industry_specific_analysis(self, df: pd.DataFrame,
                                      business_context: Dict[str, Any]) -> List[RawInsight]:
        """Run industry-specific analysis"""
        insights = []
        industry = business_context.get('industry', 'general')

        try:
            if industry == 'restaurant' and 'customers' in df.columns:
                # Restaurant-specific: table turnover analysis
                avg_customers = df['customers'].mean()
                peak_customers = df['customers'].max()

                insights.append(RawInsight(
                    insight_type='industry_analysis',
                    title='Restaurant Capacity Analysis',
                    data={
                        'average_daily_customers': float(avg_customers),
                        'peak_customers': float(peak_customers),
                        'capacity_utilization': float(avg_customers / peak_customers),
                        'industry': industry
                    },
                    confidence=0.75,
                    source='ml_engine',
                    timestamp=datetime.now()
                ))

            elif industry == 'retail' and 'conversion_rate' in df.columns:
                # Retail-specific: conversion analysis
                avg_conversion = df['conversion_rate'].mean()

                insights.append(RawInsight(
                    insight_type='industry_analysis',
                    title='Retail Conversion Performance',
                    data={
                        'average_conversion_rate': float(avg_conversion),
                        'conversion_trend': 'improving' if df['conversion_rate'].iloc[-5:].mean() > avg_conversion else 'stable',
                        'industry': industry
                    },
                    confidence=0.8,
                    source='ml_engine',
                    timestamp=datetime.now()
                ))

        except Exception as e:
            logger.error(f"Error in industry-specific analysis: {e}")

        return insights

    async def _generate_executive_summary(self, explained_insights: List[ExplainedInsight],
                                        business_context: Dict[str, Any]) -> str:
        """Generate executive summary of insights"""

        if not explained_insights:
            return "No significant insights found in the current data analysis."

        # Count insights by urgency
        critical_count = sum(1 for i in explained_insights if i.urgency_level == 'critical')
        high_count = sum(1 for i in explained_insights if i.urgency_level == 'high')

        # Create summary
        summary_parts = []

        if critical_count > 0:
            summary_parts.append(f"{critical_count} critical issue{'s' if critical_count > 1 else ''} requiring immediate attention")

        if high_count > 0:
            summary_parts.append(f"{high_count} high-priority insight{'s' if high_count > 1 else ''}")

        if not summary_parts:
            summary_parts.append(f"{len(explained_insights)} business insight{'s' if len(explained_insights) > 1 else ''}")

        industry = business_context.get('industry', 'business')

        return f"Analysis of your {industry} data reveals {', '.join(summary_parts)}. " \
               f"Key opportunities for improvement and growth have been identified with actionable recommendations."

    def _generate_recommendations(self, explained_insights: List[ExplainedInsight]) -> List[str]:
        """Generate top recommendations from insights"""
        all_actions = []

        for insight in explained_insights:
            all_actions.extend(insight.recommended_actions)

        # Remove duplicates and return top 5
        unique_actions = list(dict.fromkeys(all_actions))
        return unique_actions[:5]

    def _extract_priority_actions(self, explained_insights: List[ExplainedInsight]) -> List[str]:
        """Extract priority actions from critical and high-priority insights"""
        priority_actions = []

        for insight in explained_insights:
            if insight.urgency_level in ['critical', 'high']:
                priority_actions.extend(insight.recommended_actions[:2])  # Top 2 actions per insight

        # Remove duplicates and return top 3
        unique_actions = list(dict.fromkeys(priority_actions))
        return unique_actions[:3]

    def _calculate_key_metrics(self, data_collection: Dict[str, pd.DataFrame],
                             explained_insights: List[ExplainedInsight]) -> Dict[str, Any]:
        """Calculate key business metrics"""
        metrics = {}

        try:
            if 'business_metrics' in data_collection:
                df = data_collection['business_metrics']

                if 'revenue' in df.columns:
                    metrics['total_revenue'] = float(df['revenue'].sum())
                    metrics['average_daily_revenue'] = float(df['revenue'].mean())
                    metrics['revenue_growth'] = float((df['revenue'].iloc[-7:].mean() - df['revenue'].iloc[:7].mean()) / df['revenue'].iloc[:7].mean() * 100)

                if 'customers' in df.columns:
                    metrics['total_customers'] = int(df['customers'].sum())
                    metrics['average_daily_customers'] = float(df['customers'].mean())

            # Add insight metrics
            metrics['total_insights'] = len(explained_insights)
            metrics['critical_insights'] = sum(1 for i in explained_insights if i.urgency_level == 'critical')
            metrics['high_priority_insights'] = sum(1 for i in explained_insights if i.urgency_level == 'high')

        except Exception as e:
            logger.error(f"Error calculating key metrics: {e}")

        return metrics

    def _calculate_overall_confidence(self, explained_insights: List[ExplainedInsight]) -> float:
        """Calculate overall confidence score for the report"""
        if not explained_insights:
            return 0.0

        confidence_scores = [insight.raw_insight.confidence for insight in explained_insights]
        return sum(confidence_scores) / len(confidence_scores)

    def _create_fallback_report(self) -> ComprehensiveInsightReport:
        """Create fallback report when analysis fails"""
        return ComprehensiveInsightReport(
            explained_insights=[],
            recommendations=["Review data quality", "Check data sources", "Contact support"],
            executive_summary="Unable to generate insights due to data processing issues.",
            key_metrics={},
            priority_actions=["Check data connections"],
            generated_at=datetime.now(),
            confidence_score=0.0
        )
