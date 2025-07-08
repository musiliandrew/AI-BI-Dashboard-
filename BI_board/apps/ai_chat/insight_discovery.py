import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class DataStory:
    """A story discovered in the data"""
    story_type: str  # trend, anomaly, opportunity, concern, achievement
    title: str
    description: str
    impact_level: str  # high, medium, low
    confidence: float
    data_points: Dict[str, Any]
    suggested_question: str
    comprehensive_answer: str
    business_impact: str
    recommended_actions: List[str]

@dataclass
class InsightReport:
    """Comprehensive insight report"""
    executive_summary: str
    key_findings: List[DataStory]
    opportunities: List[str]
    concerns: List[str]
    recommendations: List[str]
    next_steps: List[str]

class ProactiveInsightDiscovery:
    """
    AI system that automatically discovers stories in data and generates smart questions
    """
    
    def __init__(self):
        self.story_templates = {
            'sales_increase': {
                'question': "Why did {period} sales increase {percentage}?",
                'answer_template': """
{period}'s {percentage} sales increase was driven by several key factors:

{factors}

**💡 Business Impact:** {impact}
**🎯 Recommendation:** {recommendation}
                """,
                'impact_level': 'high'
            },
            
            'sales_decrease': {
                'question': "What caused the {percentage} sales drop in {period}?",
                'answer_template': """
The {percentage} sales decline in {period} appears to be caused by:

{factors}

**⚠️ Business Impact:** {impact}
**🔧 Action Plan:** {recommendation}
                """,
                'impact_level': 'high'
            },
            
            'customer_growth': {
                'question': "What's driving the {percentage} customer growth?",
                'answer_template': """
Your {percentage} customer growth is excellent! Here's what's working:

{factors}

**🚀 Business Impact:** {impact}
**📈 Opportunity:** {recommendation}
                """,
                'impact_level': 'high'
            },
            
            'seasonal_pattern': {
                'question': "What seasonal patterns should I know about?",
                'answer_template': """
I found important seasonal patterns in your business:

{factors}

**📅 Planning Impact:** {impact}
**🎯 Strategy:** {recommendation}
                """,
                'impact_level': 'medium'
            },
            
            'top_performers': {
                'question': "Which {category} are my top performers?",
                'answer_template': """
Your top-performing {category} are driving significant value:

{factors}

**💰 Revenue Impact:** {impact}
**🎯 Focus Strategy:** {recommendation}
                """,
                'impact_level': 'medium'
            },
            
            'anomaly_detection': {
                'question': "What unusual patterns should I investigate?",
                'answer_template': """
I detected some unusual patterns that need attention:

{factors}

**🔍 Investigation Needed:** {impact}
**⚡ Next Steps:** {recommendation}
                """,
                'impact_level': 'medium'
            },
            
            'opportunity_identification': {
                'question': "What growth opportunities am I missing?",
                'answer_template': """
I identified several untapped opportunities:

{factors}

**💡 Potential Value:** {impact}
**🚀 Implementation:** {recommendation}
                """,
                'impact_level': 'high'
            }
        }

    def discover_stories(self, df: pd.DataFrame, analysis_results: Dict[str, Any], business_context: Dict[str, Any]) -> List[DataStory]:
        """
        Automatically discover interesting stories in the data
        """
        stories = []
        
        try:
            # Detect time-based trends
            time_stories = self._detect_time_trends(df, business_context)
            stories.extend(time_stories)
            
            # Detect performance patterns
            performance_stories = self._detect_performance_patterns(df, business_context)
            stories.extend(performance_stories)
            
            # Detect anomalies
            anomaly_stories = self._detect_anomalies(df, business_context)
            stories.extend(anomaly_stories)
            
            # Detect opportunities
            opportunity_stories = self._detect_opportunities(df, analysis_results, business_context)
            stories.extend(opportunity_stories)
            
            # Sort by impact and confidence
            stories.sort(key=lambda x: (x.impact_level == 'high', x.confidence), reverse=True)
            
            return stories[:6]  # Return top 6 stories for better UX
            
        except Exception as e:
            logger.error(f"Error discovering stories: {str(e)}")
            return []

    def _detect_time_trends(self, df: pd.DataFrame, business_context: Dict) -> List[DataStory]:
        """Detect trends over time"""
        stories = []
        
        # Look for date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not date_cols or not numeric_cols:
            return stories
        
        try:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # Group by month and analyze trends
            df['month'] = df[date_col].dt.to_period('M')
            monthly_data = df.groupby('month')[numeric_cols].sum()
            
            if len(monthly_data) >= 3:  # Need at least 3 months
                for col in numeric_cols:
                    if col in ['id', 'customer_id', 'order_id']:  # Skip ID columns
                        continue
                    
                    # Calculate month-over-month changes
                    pct_changes = monthly_data[col].pct_change().dropna()
                    
                    if len(pct_changes) > 0:
                        latest_change = pct_changes.iloc[-1]
                        latest_month = monthly_data.index[-1]
                        
                        if abs(latest_change) > 0.15:  # 15% change threshold
                            if latest_change > 0:
                                story = self._create_sales_increase_story(
                                    col, latest_month, latest_change, monthly_data
                                )
                            else:
                                story = self._create_sales_decrease_story(
                                    col, latest_month, latest_change, monthly_data
                                )
                            
                            if story:
                                stories.append(story)
        
        except Exception as e:
            logger.error(f"Error detecting time trends: {str(e)}")
        
        return stories

    def _create_sales_increase_story(self, metric: str, period: str, change: float, data: pd.DataFrame) -> DataStory:
        """Create a story about sales increase"""
        percentage = f"{change*100:.0f}%"
        
        # Analyze contributing factors
        factors = []
        if len(data) >= 3:
            trend = data[metric].iloc[-3:].pct_change().mean()
            if trend > 0.05:
                factors.append(f"📈 **Consistent Growth Trend**: {metric} has been growing steadily over the last 3 months")
            
            # Check for acceleration
            recent_growth = data[metric].iloc[-2:].pct_change().iloc[-1]
            if recent_growth > change * 0.8:
                factors.append(f"🚀 **Accelerating Growth**: Growth rate is increasing month-over-month")
        
        if not factors:
            factors.append(f"📊 **Strong Performance**: {metric} showed significant improvement in {period}")
        
        template = self.story_templates['sales_increase']
        
        return DataStory(
            story_type='achievement',
            title=f"{metric.title()} Increased {percentage} in {period}",
            description=f"Significant growth in {metric} during {period}",
            impact_level='high',
            confidence=0.9,
            data_points={'metric': metric, 'change': change, 'period': str(period)},
            suggested_question=template['question'].format(period=period, percentage=percentage),
            comprehensive_answer=template['answer_template'].format(
                period=period,
                percentage=percentage,
                factors='\n'.join([f"{i+1}. {factor}" for i, factor in enumerate(factors)]),
                impact=f"This growth represents a significant positive trend for your business",
                recommendation=f"Continue the strategies that drove this growth and consider scaling successful initiatives"
            ),
            business_impact=f"Positive revenue impact from {metric} growth",
            recommended_actions=[
                f"Analyze what drove the {metric} increase",
                "Scale successful strategies",
                "Monitor for sustainability"
            ]
        )

    def _create_sales_decrease_story(self, metric: str, period: str, change: float, data: pd.DataFrame) -> DataStory:
        """Create a story about sales decrease"""
        percentage = f"{abs(change)*100:.0f}%"
        
        # Analyze potential causes
        factors = []
        if len(data) >= 3:
            trend = data[metric].iloc[-3:].pct_change().mean()
            if trend < -0.05:
                factors.append(f"📉 **Declining Trend**: {metric} has been decreasing over multiple months")
            else:
                factors.append(f"📊 **Isolated Decline**: This appears to be a one-time decrease, not a trend")
        
        # Check seasonality
        if len(data) >= 12:
            same_month_last_year = data[metric].iloc[-12] if len(data) >= 12 else None
            if same_month_last_year:
                yoy_change = (data[metric].iloc[-1] - same_month_last_year) / same_month_last_year
                if yoy_change > 0:
                    factors.append(f"📅 **Still Above Last Year**: Despite the monthly decline, {metric} is still {yoy_change*100:.0f}% higher than last year")
        
        template = self.story_templates['sales_decrease']
        
        return DataStory(
            story_type='concern',
            title=f"{metric.title()} Decreased {percentage} in {period}",
            description=f"Notable decline in {metric} during {period}",
            impact_level='high',
            confidence=0.8,
            data_points={'metric': metric, 'change': change, 'period': str(period)},
            suggested_question=template['question'].format(period=period, percentage=percentage),
            comprehensive_answer=template['answer_template'].format(
                percentage=percentage,
                period=period,
                factors='\n'.join([f"{i+1}. {factor}" for i, factor in enumerate(factors)]),
                impact=f"This decline needs investigation to prevent further losses",
                recommendation=f"Investigate root causes and implement corrective measures for {metric}"
            ),
            business_impact=f"Potential revenue impact from {metric} decline",
            recommended_actions=[
                f"Investigate causes of {metric} decrease",
                "Review recent changes in strategy",
                "Implement corrective measures"
            ]
        )

    def _detect_performance_patterns(self, df: pd.DataFrame, business_context: Dict) -> List[DataStory]:
        """Detect top performers and patterns"""
        stories = []
        
        try:
            # Look for categorical columns that might represent products, customers, etc.
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for cat_col in categorical_cols:
                if cat_col in ['id', 'date', 'time']:
                    continue
                
                for num_col in numeric_cols:
                    if num_col in ['id', 'customer_id', 'order_id']:
                        continue
                    
                    # Analyze performance by category
                    performance = df.groupby(cat_col)[num_col].agg(['sum', 'mean', 'count']).sort_values('sum', ascending=False)
                    
                    if len(performance) >= 3:
                        top_performers = performance.head(3)
                        total_value = performance['sum'].sum()
                        top_3_value = top_performers['sum'].sum()
                        top_3_percentage = (top_3_value / total_value) * 100
                        
                        if top_3_percentage > 50:  # Top 3 represent >50% of value
                            story = self._create_top_performers_story(
                                cat_col, num_col, top_performers, top_3_percentage
                            )
                            stories.append(story)
                            break  # Only one story per category
        
        except Exception as e:
            logger.error(f"Error detecting performance patterns: {str(e)}")
        
        return stories

    def _create_top_performers_story(self, category: str, metric: str, top_performers: pd.DataFrame, percentage: float) -> DataStory:
        """Create story about top performers"""
        
        factors = []
        for idx, (name, data) in enumerate(top_performers.iterrows()):
            rank = idx + 1
            value = data['sum']
            factors.append(f"🏆 **#{rank}: {name}** - {metric}: {value:,.0f}")
        
        template = self.story_templates['top_performers']
        
        return DataStory(
            story_type='opportunity',
            title=f"Top {category.title()} Drive {percentage:.0f}% of {metric.title()}",
            description=f"Performance concentration in top {category}",
            impact_level='medium',
            confidence=0.8,
            data_points={'category': category, 'metric': metric, 'percentage': percentage},
            suggested_question=template['question'].format(category=category),
            comprehensive_answer=template['answer_template'].format(
                category=category,
                factors='\n'.join(factors),
                impact=f"Your top 3 {category} generate {percentage:.0f}% of total {metric}",
                recommendation=f"Focus resources on your top-performing {category} and analyze what makes them successful"
            ),
            business_impact=f"High concentration of value in top {category}",
            recommended_actions=[
                f"Analyze success factors of top {category}",
                f"Invest more in top-performing {category}",
                f"Replicate success patterns in other {category}"
            ]
        )

    def _detect_anomalies(self, df: pd.DataFrame, business_context: Dict) -> List[DataStory]:
        """Detect unusual patterns or anomalies"""
        stories = []
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for col in numeric_cols:
                if col in ['id', 'customer_id', 'order_id']:
                    continue
                
                # Simple anomaly detection using IQR
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                anomalies = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                if len(anomalies) > 0 and len(anomalies) < len(df) * 0.1:  # Less than 10% anomalies
                    story = self._create_anomaly_story(col, anomalies, df)
                    if story:
                        stories.append(story)
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
        
        return stories

    def _create_anomaly_story(self, metric: str, anomalies: pd.DataFrame, full_data: pd.DataFrame) -> DataStory:
        """Create story about detected anomalies"""
        
        anomaly_count = len(anomalies)
        total_count = len(full_data)
        percentage = (anomaly_count / total_count) * 100
        
        factors = [
            f"📊 **Anomaly Count**: {anomaly_count} unusual {metric} values ({percentage:.1f}% of data)",
            f"📈 **Range**: Values outside normal range of {full_data[metric].quantile(0.25):.0f} - {full_data[metric].quantile(0.75):.0f}",
            f"🔍 **Investigation**: These outliers may indicate data quality issues or special cases"
        ]
        
        template = self.story_templates['anomaly_detection']
        
        return DataStory(
            story_type='concern',
            title=f"Unusual {metric.title()} Values Detected",
            description=f"Found {anomaly_count} anomalous values in {metric}",
            impact_level='medium',
            confidence=0.7,
            data_points={'metric': metric, 'anomaly_count': anomaly_count, 'percentage': percentage},
            suggested_question=template['question'],
            comprehensive_answer=template['answer_template'].format(
                factors='\n'.join(factors),
                impact=f"These anomalies could indicate data quality issues or special business cases",
                recommendation=f"Review the unusual {metric} values to ensure data accuracy and identify any special cases"
            ),
            business_impact=f"Potential data quality or business process issues",
            recommended_actions=[
                f"Review anomalous {metric} values",
                "Check data collection processes",
                "Identify if anomalies represent real business cases"
            ]
        )

    def _detect_opportunities(self, df: pd.DataFrame, analysis_results: Dict, business_context: Dict) -> List[DataStory]:
        """Detect growth opportunities"""
        stories = []
        
        # This would be enhanced with more sophisticated analysis
        # For now, create a generic opportunity story
        
        opportunity_factors = [
            "📈 **Market Expansion**: Consider expanding to underperforming segments",
            "🎯 **Customer Retention**: Focus on improving customer lifetime value",
            "💡 **Product Innovation**: Analyze customer feedback for new product opportunities"
        ]
        
        template = self.story_templates['opportunity_identification']
        
        story = DataStory(
            story_type='opportunity',
            title="Growth Opportunities Identified",
            description="Potential areas for business growth",
            impact_level='high',
            confidence=0.6,
            data_points={'opportunities': len(opportunity_factors)},
            suggested_question=template['question'],
            comprehensive_answer=template['answer_template'].format(
                factors='\n'.join([f"{i+1}. {factor}" for i, factor in enumerate(opportunity_factors)]),
                impact="These opportunities could significantly impact business growth",
                recommendation="Prioritize opportunities based on resource availability and potential ROI"
            ),
            business_impact="Potential for significant business growth",
            recommended_actions=[
                "Evaluate each opportunity's potential ROI",
                "Develop implementation timeline",
                "Allocate resources to highest-impact opportunities"
            ]
        )
        
        stories.append(story)
        return stories

    def generate_insight_report(self, stories: List[DataStory], business_context: Dict) -> InsightReport:
        """Generate comprehensive insight report"""
        
        # Categorize stories
        achievements = [s for s in stories if s.story_type == 'achievement']
        concerns = [s for s in stories if s.story_type == 'concern']
        opportunities = [s for s in stories if s.story_type == 'opportunity']
        
        # Generate executive summary
        exec_summary = f"""
**📊 Data Analysis Summary**

I analyzed your business data and discovered {len(stories)} key insights:
- {len(achievements)} positive achievements
- {len(concerns)} areas needing attention  
- {len(opportunities)} growth opportunities

**🎯 Key Takeaway:** {stories[0].title if stories else 'Your data shows interesting patterns worth exploring.'}
        """.strip()
        
        # Extract recommendations
        all_recommendations = []
        for story in stories:
            all_recommendations.extend(story.recommended_actions)
        
        # Remove duplicates and prioritize
        unique_recommendations = list(dict.fromkeys(all_recommendations))[:5]
        
        return InsightReport(
            executive_summary=exec_summary,
            key_findings=stories,
            opportunities=[s.title for s in opportunities],
            concerns=[s.title for s in concerns],
            recommendations=unique_recommendations,
            next_steps=[
                "Review and act on high-priority recommendations",
                "Monitor key metrics for changes",
                "Schedule regular data analysis sessions"
            ]
        )
