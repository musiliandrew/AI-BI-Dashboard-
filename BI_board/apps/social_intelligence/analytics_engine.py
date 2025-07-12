"""
Social Media Analytics Engine - Industry-specific social intelligence
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from textblob import TextBlob
import re
from collections import Counter

from .models import SocialAccount, SocialPost, SocialInsight
from ..data_ingestion.ai_intelligence import AIInsight

logger = logging.getLogger(__name__)

@dataclass
class SocialAnalysisResult:
    """Result from social media analysis"""
    insights: List[AIInsight]
    metrics_summary: Dict[str, Any]
    competitor_benchmarks: Dict[str, Any]
    recommendations: List[str]
    optimal_posting_times: List[Dict[str, Any]]
    top_content: List[Dict[str, Any]]
    audience_insights: Dict[str, Any]

class SocialAnalyticsEngine:
    """AI-powered social media analytics with industry specialization"""
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.content_categories = self._load_content_categories()
    
    def analyze_social_performance(self, 
                                 account: SocialAccount, 
                                 posts: List[SocialPost],
                                 competitors: List[SocialAccount] = None,
                                 date_range_days: int = 30) -> SocialAnalysisResult:
        """Comprehensive social media performance analysis"""
        
        logger.info(f"Analyzing social performance for {account.platform} @{account.username}")
        
        # Convert to DataFrame for analysis
        posts_df = self._posts_to_dataframe(posts)
        
        # Generate insights
        insights = []
        insights.extend(self._analyze_content_performance(posts_df, account.industry))
        insights.extend(self._analyze_engagement_patterns(posts_df, account.platform))
        insights.extend(self._analyze_audience_behavior(posts_df))
        insights.extend(self._analyze_hashtag_performance(posts_df))
        insights.extend(self._analyze_posting_timing(posts_df))
        
        # Competitor benchmarking
        competitor_benchmarks = {}
        if competitors:
            competitor_benchmarks = self._benchmark_against_competitors(
                posts_df, competitors, account.industry
            )
            insights.extend(self._generate_competitive_insights(competitor_benchmarks))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(insights, account.industry)
        
        # Calculate metrics summary
        metrics_summary = self._calculate_metrics_summary(posts_df, account)
        
        # Find optimal posting times
        optimal_times = self._find_optimal_posting_times(posts_df)
        
        # Identify top content
        top_content = self._identify_top_content(posts_df)
        
        # Audience insights
        audience_insights = self._analyze_audience_insights(posts_df, account)
        
        return SocialAnalysisResult(
            insights=insights,
            metrics_summary=metrics_summary,
            competitor_benchmarks=competitor_benchmarks,
            recommendations=recommendations,
            optimal_posting_times=optimal_times,
            top_content=top_content,
            audience_insights=audience_insights
        )
    
    def _posts_to_dataframe(self, posts: List[SocialPost]) -> pd.DataFrame:
        """Convert posts to pandas DataFrame for analysis"""
        data = []
        for post in posts:
            data.append({
                'post_id': str(post.id),
                'content': post.content_text,
                'posted_at': post.posted_at,
                'likes': post.likes_count,
                'comments': post.comments_count,
                'shares': post.shares_count,
                'views': post.views_count,
                'saves': post.saves_count,
                'hashtags': post.hashtags,
                'mentions': post.mentions,
                'content_type': post.content_type,
                'engagement_rate': post.engagement_rate or 0,
                'sentiment_score': post.sentiment_score,
                'hour': post.posted_at.hour,
                'day_of_week': post.posted_at.weekday(),
                'media_count': len(post.media_urls)
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['total_engagement'] = df['likes'] + df['comments'] + df['shares']
            df['content_length'] = df['content'].str.len()
            df['hashtag_count'] = df['hashtags'].apply(len)
            df['mention_count'] = df['mentions'].apply(len)
        
        return df
    
    def _analyze_content_performance(self, df: pd.DataFrame, industry: str) -> List[AIInsight]:
        """Analyze content performance with industry-specific insights"""
        insights = []
        
        if df.empty:
            return insights
        
        # Content type performance
        if 'content_type' in df.columns:
            type_performance = df.groupby('content_type').agg({
                'total_engagement': 'mean',
                'engagement_rate': 'mean',
                'views': 'mean'
            }).round(2)
            
            best_type = type_performance['engagement_rate'].idxmax()
            best_rate = type_performance.loc[best_type, 'engagement_rate']
            
            insights.append(AIInsight(
                insight_type='content_performance',
                title=f'{best_type.title()} Content Performs Best',
                description=f"{best_type} content has {best_rate:.1%} average engagement rate, outperforming other content types",
                confidence=0.85,
                business_impact=self._get_industry_content_impact(industry, best_type),
                data_evidence={'content_performance': type_performance.to_dict()},
                visualization_config={'type': 'bar_chart', 'x': 'content_type', 'y': 'engagement_rate'},
                action_items=[
                    f'Create more {best_type} content',
                    f'Analyze what makes {best_type} content successful',
                    'Test different variations of top-performing content types'
                ]
            ))
        
        # Content length analysis
        if 'content_length' in df.columns and len(df) > 10:
            # Find optimal content length
            df['length_bucket'] = pd.cut(df['content_length'], 
                                       bins=[0, 50, 100, 200, 500, float('inf')],
                                       labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long'])
            
            length_performance = df.groupby('length_bucket')['engagement_rate'].mean()
            optimal_length = length_performance.idxmax()
            optimal_rate = length_performance.max()
            
            insights.append(AIInsight(
                insight_type='content_performance',
                title=f'{optimal_length} Posts Drive Highest Engagement',
                description=f"{optimal_length} posts achieve {optimal_rate:.1%} average engagement rate",
                confidence=0.8,
                business_impact='Content optimization for better audience engagement',
                data_evidence={'length_performance': length_performance.to_dict()},
                visualization_config={'type': 'line_chart', 'x': 'content_length', 'y': 'engagement_rate'},
                action_items=[
                    f'Focus on creating {optimal_length.lower()} content',
                    'Test content length variations',
                    'Analyze top-performing posts for length patterns'
                ]
            ))
        
        return insights
    
    def _analyze_engagement_patterns(self, df: pd.DataFrame, platform: str) -> List[AIInsight]:
        """Analyze engagement patterns and trends"""
        insights = []
        
        if df.empty or len(df) < 7:
            return insights
        
        # Engagement trend analysis
        df_sorted = df.sort_values('posted_at')
        df_sorted['engagement_ma'] = df_sorted['engagement_rate'].rolling(window=7).mean()
        
        recent_avg = df_sorted['engagement_rate'].tail(7).mean()
        overall_avg = df_sorted['engagement_rate'].mean()
        trend_change = (recent_avg - overall_avg) / overall_avg * 100
        
        if abs(trend_change) > 10:  # Significant change
            trend_direction = "increasing" if trend_change > 0 else "decreasing"
            insights.append(AIInsight(
                insight_type='engagement_pattern',
                title=f'Engagement Rate {trend_direction.title()} by {abs(trend_change):.1f}%',
                description=f"Recent engagement rate ({recent_avg:.1%}) is {trend_direction} compared to overall average ({overall_avg:.1%})",
                confidence=0.9,
                business_impact='Audience engagement trend monitoring',
                data_evidence={'trend_change': trend_change, 'recent_avg': recent_avg, 'overall_avg': overall_avg},
                visualization_config={'type': 'line_chart', 'x': 'posted_at', 'y': 'engagement_rate'},
                action_items=[
                    'Analyze recent content changes' if trend_change < 0 else 'Identify what\'s driving increased engagement',
                    'Adjust content strategy based on trend',
                    'Monitor engagement closely over next week'
                ]
            ))
        
        return insights
    
    def _analyze_hashtag_performance(self, df: pd.DataFrame) -> List[AIInsight]:
        """Analyze hashtag effectiveness"""
        insights = []
        
        if df.empty or 'hashtags' not in df.columns:
            return insights
        
        # Flatten hashtags and calculate performance
        hashtag_data = []
        for _, row in df.iterrows():
            for hashtag in row['hashtags']:
                hashtag_data.append({
                    'hashtag': hashtag.lower(),
                    'engagement_rate': row['engagement_rate'],
                    'total_engagement': row['total_engagement']
                })
        
        if not hashtag_data:
            return insights
        
        hashtag_df = pd.DataFrame(hashtag_data)
        hashtag_performance = hashtag_df.groupby('hashtag').agg({
            'engagement_rate': 'mean',
            'total_engagement': 'mean'
        }).round(3)
        
        # Find top performing hashtags (minimum 2 uses)
        hashtag_counts = hashtag_df['hashtag'].value_counts()
        frequent_hashtags = hashtag_counts[hashtag_counts >= 2].index
        
        if len(frequent_hashtags) > 0:
            top_hashtags = hashtag_performance.loc[frequent_hashtags].nlargest(5, 'engagement_rate')
            
            insights.append(AIInsight(
                insight_type='hashtag_analysis',
                title='Top Performing Hashtags Identified',
                description=f"#{top_hashtags.index[0]} drives highest engagement at {top_hashtags.iloc[0]['engagement_rate']:.1%}",
                confidence=0.8,
                business_impact='Hashtag strategy optimization for better reach',
                data_evidence={'top_hashtags': top_hashtags.to_dict()},
                visualization_config={'type': 'bar_chart', 'x': 'hashtag', 'y': 'engagement_rate'},
                action_items=[
                    f'Use #{top_hashtags.index[0]} more frequently',
                    'Research related high-performing hashtags',
                    'Test hashtag combinations for optimal reach'
                ]
            ))
        
        return insights
    
    def _analyze_posting_timing(self, df: pd.DataFrame) -> List[AIInsight]:
        """Analyze optimal posting times"""
        insights = []
        
        if df.empty or len(df) < 14:
            return insights
        
        # Hour analysis
        hourly_performance = df.groupby('hour')['engagement_rate'].mean()
        best_hour = hourly_performance.idxmax()
        best_hour_rate = hourly_performance.max()
        
        # Day of week analysis
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_performance = df.groupby('day_of_week')['engagement_rate'].mean()
        best_day = daily_performance.idxmax()
        best_day_rate = daily_performance.max()
        
        insights.append(AIInsight(
            insight_type='optimal_timing',
            title=f'Best Posting Time: {best_hour}:00 on {day_names[best_day]}',
            description=f"Posts at {best_hour}:00 on {day_names[best_day]} achieve {best_hour_rate:.1%} engagement rate",
            confidence=0.85,
            business_impact='Timing optimization for maximum audience reach',
            data_evidence={
                'hourly_performance': hourly_performance.to_dict(),
                'daily_performance': daily_performance.to_dict()
            },
            visualization_config={'type': 'heatmap', 'x': 'hour', 'y': 'day_of_week', 'z': 'engagement_rate'},
            action_items=[
                f'Schedule more posts for {best_hour}:00',
                f'Focus on {day_names[best_day]} posting',
                'Test posting times around peak hours'
            ]
        ))
        
        return insights
    
    def _find_optimal_posting_times(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find optimal posting times based on engagement"""
        if df.empty:
            return []
        
        # Group by hour and day of week
        time_performance = df.groupby(['day_of_week', 'hour']).agg({
            'engagement_rate': 'mean',
            'total_engagement': 'mean'
        }).reset_index()
        
        # Get top 5 time slots
        top_times = time_performance.nlargest(5, 'engagement_rate')
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        optimal_times = []
        for _, row in top_times.iterrows():
            optimal_times.append({
                'day': day_names[int(row['day_of_week'])],
                'hour': int(row['hour']),
                'engagement_rate': float(row['engagement_rate']),
                'avg_engagement': float(row['total_engagement'])
            })
        
        return optimal_times
    
    def _identify_top_content(self, df: pd.DataFrame, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify top performing content"""
        if df.empty:
            return []
        
        top_posts = df.nlargest(limit, 'engagement_rate')
        
        top_content = []
        for _, post in top_posts.iterrows():
            top_content.append({
                'post_id': post['post_id'],
                'content_preview': post['content'][:100] + '...' if len(post['content']) > 100 else post['content'],
                'engagement_rate': float(post['engagement_rate']),
                'total_engagement': int(post['total_engagement']),
                'posted_at': post['posted_at'].isoformat(),
                'content_type': post.get('content_type', 'post'),
                'hashtags': post.get('hashtags', [])
            })
        
        return top_content
    
    def _generate_recommendations(self, insights: List[AIInsight], industry: str) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        # Collect action items from insights
        for insight in insights:
            recommendations.extend(insight.action_items)
        
        # Add industry-specific recommendations
        industry_recs = self._get_industry_recommendations(industry)
        recommendations.extend(industry_recs)
        
        # Remove duplicates and return top 10
        unique_recs = list(dict.fromkeys(recommendations))
        return unique_recs[:10]
    
    def _get_industry_content_impact(self, industry: str, content_type: str) -> str:
        """Get industry-specific impact description for content types"""
        impact_map = {
            'automotive': {
                'video': 'Video content showcases vehicles effectively, driving showroom visits',
                'image': 'High-quality vehicle photos increase purchase consideration',
                'carousel': 'Multiple vehicle angles improve customer engagement'
            },
            'restaurant': {
                'video': 'Food videos drive appetite appeal and increase orders',
                'image': 'Food photography directly impacts customer cravings',
                'story': 'Behind-the-scenes content builds brand authenticity'
            },
            'retail': {
                'video': 'Product demonstrations increase purchase confidence',
                'image': 'Product showcases drive website traffic and sales',
                'carousel': 'Multiple product views improve conversion rates'
            }
        }
        
        return impact_map.get(industry, {}).get(content_type, 'Content optimization improves audience engagement')
    
    def _get_industry_recommendations(self, industry: str) -> List[str]:
        """Get industry-specific social media recommendations"""
        recommendations_map = {
            'automotive': [
                'Showcase vehicle features through video content',
                'Share customer testimonials and reviews',
                'Post behind-the-scenes dealership content',
                'Highlight special offers and promotions'
            ],
            'restaurant': [
                'Share high-quality food photography',
                'Post cooking process videos',
                'Feature customer dining experiences',
                'Promote daily specials and events'
            ],
            'retail': [
                'Create product demonstration videos',
                'Share customer styling tips',
                'Highlight new arrivals and collections',
                'Post user-generated content'
            ],
            'healthcare': [
                'Share educational health content',
                'Post patient success stories (with permission)',
                'Highlight team expertise and credentials',
                'Promote health awareness campaigns'
            ]
        }
        
        return recommendations_map.get(industry, [
            'Maintain consistent posting schedule',
            'Engage with audience comments promptly',
            'Use relevant industry hashtags',
            'Share valuable, educational content'
        ])
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry benchmark data"""
        # This would typically come from a database or external service
        return {
            'automotive': {
                'avg_engagement_rate': 0.025,
                'avg_posts_per_week': 5,
                'avg_followers_growth': 0.02
            },
            'restaurant': {
                'avg_engagement_rate': 0.035,
                'avg_posts_per_week': 7,
                'avg_followers_growth': 0.03
            },
            'retail': {
                'avg_engagement_rate': 0.03,
                'avg_posts_per_week': 6,
                'avg_followers_growth': 0.025
            }
        }
    
    def _load_content_categories(self) -> Dict[str, List[str]]:
        """Load content category definitions"""
        return {
            'automotive': ['vehicle_showcase', 'customer_testimonial', 'dealership_tour', 'maintenance_tips'],
            'restaurant': ['food_showcase', 'cooking_process', 'customer_dining', 'chef_spotlight'],
            'retail': ['product_showcase', 'styling_tips', 'new_arrivals', 'customer_photos']
        }
    
    def _calculate_metrics_summary(self, df: pd.DataFrame, account: SocialAccount) -> Dict[str, Any]:
        """Calculate comprehensive metrics summary"""
        if df.empty:
            return {}
        
        return {
            'total_posts': len(df),
            'avg_engagement_rate': float(df['engagement_rate'].mean()),
            'total_likes': int(df['likes'].sum()),
            'total_comments': int(df['comments'].sum()),
            'total_shares': int(df['shares'].sum()),
            'avg_likes_per_post': float(df['likes'].mean()),
            'avg_comments_per_post': float(df['comments'].mean()),
            'best_performing_post': {
                'engagement_rate': float(df['engagement_rate'].max()),
                'content_preview': df.loc[df['engagement_rate'].idxmax(), 'content'][:100]
            },
            'posting_frequency': len(df) / 30,  # posts per day over 30 days
            'follower_count': account.followers_count
        }
    
    def _analyze_audience_behavior(self, df: pd.DataFrame) -> List[AIInsight]:
        """Analyze audience behavior patterns"""
        insights = []
        
        if df.empty:
            return insights
        
        # Comment-to-like ratio analysis
        if 'comments' in df.columns and 'likes' in df.columns:
            df['comment_like_ratio'] = df['comments'] / (df['likes'] + 1)  # +1 to avoid division by zero
            avg_ratio = df['comment_like_ratio'].mean()
            
            if avg_ratio > 0.1:  # High engagement threshold
                insights.append(AIInsight(
                    insight_type='audience_analysis',
                    title='High Audience Engagement Quality',
                    description=f"Comment-to-like ratio of {avg_ratio:.3f} indicates highly engaged audience",
                    confidence=0.8,
                    business_impact='Strong audience relationship and brand loyalty',
                    data_evidence={'comment_like_ratio': avg_ratio},
                    visualization_config={'type': 'scatter_plot', 'x': 'likes', 'y': 'comments'},
                    action_items=[
                        'Continue creating conversation-starting content',
                        'Respond to comments to maintain engagement',
                        'Ask questions in posts to encourage comments'
                    ]
                ))
        
        return insights
    
    def _analyze_audience_insights(self, df: pd.DataFrame, account: SocialAccount) -> Dict[str, Any]:
        """Generate audience insights"""
        if df.empty:
            return {}
        
        return {
            'engagement_quality': {
                'avg_comment_like_ratio': float(df['comments'].sum() / (df['likes'].sum() + 1)),
                'engagement_consistency': float(df['engagement_rate'].std()),
                'audience_responsiveness': float(df['comments'].mean())
            },
            'content_preferences': {
                'preferred_content_length': self._get_preferred_content_length(df),
                'hashtag_engagement': float(df['hashtag_count'].corr(df['engagement_rate'])) if len(df) > 1 else 0,
                'media_preference': self._get_media_preference(df)
            },
            'timing_insights': {
                'most_active_hours': df.groupby('hour')['total_engagement'].sum().nlargest(3).index.tolist(),
                'most_active_days': df.groupby('day_of_week')['total_engagement'].sum().nlargest(3).index.tolist()
            }
        }
    
    def _get_preferred_content_length(self, df: pd.DataFrame) -> str:
        """Determine preferred content length based on engagement"""
        if 'content_length' not in df.columns or len(df) < 5:
            return 'unknown'
        
        df['length_bucket'] = pd.cut(df['content_length'], 
                                   bins=[0, 50, 100, 200, 500, float('inf')],
                                   labels=['very_short', 'short', 'medium', 'long', 'very_long'])
        
        length_performance = df.groupby('length_bucket')['engagement_rate'].mean()
        return str(length_performance.idxmax())
    
    def _get_media_preference(self, df: pd.DataFrame) -> str:
        """Determine audience media preference"""
        if 'media_count' not in df.columns or len(df) < 5:
            return 'unknown'
        
        media_performance = df.groupby('media_count')['engagement_rate'].mean()
        optimal_media_count = media_performance.idxmax()
        
        if optimal_media_count == 0:
            return 'text_only'
        elif optimal_media_count == 1:
            return 'single_media'
        else:
            return 'multiple_media'
    
    def _benchmark_against_competitors(self, df: pd.DataFrame, competitors: List[SocialAccount], industry: str) -> Dict[str, Any]:
        """Benchmark performance against competitors"""
        # This would involve fetching competitor data and comparing metrics
        # For now, return placeholder structure
        return {
            'engagement_rate_percentile': 75,  # User is in 75th percentile
            'posting_frequency_comparison': 'above_average',
            'follower_growth_comparison': 'average',
            'content_performance_vs_competitors': 'above_average'
        }
    
    def _generate_competitive_insights(self, benchmarks: Dict[str, Any]) -> List[AIInsight]:
        """Generate insights based on competitive benchmarking"""
        insights = []
        
        if benchmarks.get('engagement_rate_percentile', 0) > 80:
            insights.append(AIInsight(
                insight_type='competitor_benchmark',
                title='Above-Average Engagement Performance',
                description=f"Your engagement rate ranks in the {benchmarks['engagement_rate_percentile']}th percentile among industry competitors",
                confidence=0.9,
                business_impact='Strong competitive position in social media engagement',
                data_evidence=benchmarks,
                visualization_config={'type': 'gauge', 'value': 'engagement_percentile'},
                action_items=[
                    'Maintain current content strategy',
                    'Analyze what differentiates your top content',
                    'Consider increasing posting frequency to capitalize on engagement'
                ]
            ))
        
        return insights

# Global instance
social_analytics_engine = SocialAnalyticsEngine()
