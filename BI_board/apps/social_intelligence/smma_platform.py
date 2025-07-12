"""
SMMA Platform - Social Media Marketing Agency tools and client management
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import logging

from .models import SocialAccount, SocialPost, SocialCampaign, SocialReport
from .analytics_engine import social_analytics_engine, SocialAnalysisResult
from .platform_apis import get_platform_api

logger = logging.getLogger(__name__)

@dataclass
class ClientPerformance:
    """Client performance summary for SMMA dashboard"""
    client_name: str
    industry: str
    platforms: List[str]
    total_followers: int
    follower_growth: float
    avg_engagement_rate: float
    monthly_reach: int
    top_performing_content: List[Dict[str, Any]]
    key_insights: List[str]
    recommendations: List[str]
    roi_metrics: Dict[str, float]

@dataclass
class AgencyDashboard:
    """Complete agency dashboard data"""
    total_clients: int
    total_followers_managed: int
    avg_engagement_rate: float
    monthly_revenue: float
    client_performances: List[ClientPerformance]
    industry_benchmarks: Dict[str, Dict[str, float]]
    growth_trends: Dict[str, List[float]]
    alert_summary: Dict[str, int]

class SMMAClientManager:
    """Manage SMMA clients and their social media accounts"""
    
    def __init__(self):
        self.analytics_engine = social_analytics_engine
    
    def analyze_client_performance(self, 
                                 client_accounts: List[SocialAccount],
                                 date_range_days: int = 30) -> ClientPerformance:
        """Comprehensive client performance analysis"""
        
        if not client_accounts:
            raise ValueError("No client accounts provided")
        
        # Get client info from first account
        client_account = client_accounts[0]
        client_name = client_account.user.get_full_name() or client_account.user.username
        industry = client_account.industry
        
        # Aggregate data across all platforms
        all_posts = []
        total_followers = 0
        platforms = []
        
        for account in client_accounts:
            platforms.append(account.platform)
            total_followers += account.followers_count
            
            # Get recent posts
            posts = SocialPost.objects.filter(
                account=account,
                posted_at__gte=datetime.now() - timedelta(days=date_range_days)
            )
            all_posts.extend(posts)
        
        # Calculate follower growth (simplified - would need historical data)
        follower_growth = self._calculate_follower_growth(client_accounts, date_range_days)
        
        # Analyze performance across all platforms
        if all_posts:
            analysis_result = self.analytics_engine.analyze_social_performance(
                client_accounts[0],  # Primary account for industry context
                all_posts
            )
            
            avg_engagement_rate = analysis_result.metrics_summary.get('avg_engagement_rate', 0)
            top_content = analysis_result.top_content[:5]
            key_insights = [insight.title for insight in analysis_result.insights[:5]]
            recommendations = analysis_result.recommendations[:5]
        else:
            avg_engagement_rate = 0
            top_content = []
            key_insights = []
            recommendations = []
        
        # Calculate ROI metrics
        roi_metrics = self._calculate_roi_metrics(client_accounts, all_posts)
        
        # Estimate monthly reach
        monthly_reach = self._estimate_monthly_reach(client_accounts, all_posts)
        
        return ClientPerformance(
            client_name=client_name,
            industry=industry,
            platforms=platforms,
            total_followers=total_followers,
            follower_growth=follower_growth,
            avg_engagement_rate=avg_engagement_rate,
            monthly_reach=monthly_reach,
            top_performing_content=top_content,
            key_insights=key_insights,
            recommendations=recommendations,
            roi_metrics=roi_metrics
        )
    
    def generate_agency_dashboard(self, agency_clients: List[List[SocialAccount]]) -> AgencyDashboard:
        """Generate comprehensive agency dashboard"""
        
        client_performances = []
        total_followers = 0
        total_engagement_rates = []
        
        # Analyze each client
        for client_accounts in agency_clients:
            try:
                performance = self.analyze_client_performance(client_accounts)
                client_performances.append(performance)
                total_followers += performance.total_followers
                total_engagement_rates.append(performance.avg_engagement_rate)
            except Exception as e:
                logger.error(f"Error analyzing client: {e}")
                continue
        
        # Calculate agency-wide metrics
        avg_engagement_rate = sum(total_engagement_rates) / len(total_engagement_rates) if total_engagement_rates else 0
        
        # Calculate monthly revenue (simplified)
        monthly_revenue = self._calculate_agency_revenue(client_performances)
        
        # Get industry benchmarks
        industry_benchmarks = self._get_industry_benchmarks(client_performances)
        
        # Calculate growth trends
        growth_trends = self._calculate_growth_trends(client_performances)
        
        # Generate alert summary
        alert_summary = self._generate_alert_summary(client_performances)
        
        return AgencyDashboard(
            total_clients=len(client_performances),
            total_followers_managed=total_followers,
            avg_engagement_rate=avg_engagement_rate,
            monthly_revenue=monthly_revenue,
            client_performances=client_performances,
            industry_benchmarks=industry_benchmarks,
            growth_trends=growth_trends,
            alert_summary=alert_summary
        )
    
    def generate_client_report(self, 
                             client_accounts: List[SocialAccount],
                             report_type: str = 'monthly',
                             custom_metrics: List[str] = None) -> Dict[str, Any]:
        """Generate comprehensive client report"""
        
        performance = self.analyze_client_performance(client_accounts)
        
        # Get detailed analytics for each platform
        platform_analytics = {}
        for account in client_accounts:
            posts = SocialPost.objects.filter(
                account=account,
                posted_at__gte=datetime.now() - timedelta(days=30)
            )
            
            if posts:
                analysis = self.analytics_engine.analyze_social_performance(account, posts)
                platform_analytics[account.platform] = {
                    'metrics': analysis.metrics_summary,
                    'insights': [insight.title for insight in analysis.insights],
                    'optimal_times': analysis.optimal_posting_times,
                    'top_content': analysis.top_content[:3]
                }
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(performance, platform_analytics)
        
        # Create detailed recommendations
        detailed_recommendations = self._generate_detailed_recommendations(performance, platform_analytics)
        
        # Calculate competitive analysis
        competitive_analysis = self._generate_competitive_analysis(client_accounts)
        
        return {
            'report_type': report_type,
            'client_name': performance.client_name,
            'report_period': f"{datetime.now() - timedelta(days=30)} to {datetime.now()}",
            'executive_summary': executive_summary,
            'performance_overview': {
                'total_followers': performance.total_followers,
                'follower_growth': performance.follower_growth,
                'engagement_rate': performance.avg_engagement_rate,
                'monthly_reach': performance.monthly_reach,
                'roi_metrics': performance.roi_metrics
            },
            'platform_breakdown': platform_analytics,
            'top_performing_content': performance.top_performing_content,
            'key_insights': performance.key_insights,
            'detailed_recommendations': detailed_recommendations,
            'competitive_analysis': competitive_analysis,
            'next_month_strategy': self._generate_next_month_strategy(performance)
        }
    
    def track_campaign_performance(self, campaign: SocialCampaign) -> Dict[str, Any]:
        """Track and analyze campaign performance"""
        
        # Get campaign posts (would need to link posts to campaigns)
        campaign_posts = SocialPost.objects.filter(
            posted_at__gte=campaign.start_date,
            posted_at__lte=campaign.end_date or datetime.now()
        )
        
        # Calculate campaign metrics
        total_impressions = campaign.impressions
        total_reach = campaign.reach
        total_clicks = campaign.clicks
        total_conversions = campaign.conversions
        
        # Calculate performance metrics
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpc = float(campaign.cost_per_click) if campaign.cost_per_click else 0
        cpa = float(campaign.cost_per_conversion) if campaign.cost_per_conversion else 0
        
        # Analyze campaign content performance
        if campaign_posts:
            content_analysis = self._analyze_campaign_content(campaign_posts)
        else:
            content_analysis = {}
        
        return {
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'campaign_type': campaign.campaign_type,
            'status': campaign.status,
            'duration_days': (datetime.now() - campaign.start_date).days,
            'performance_metrics': {
                'impressions': total_impressions,
                'reach': total_reach,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'ctr': round(ctr, 2),
                'conversion_rate': round(conversion_rate, 2),
                'cpc': cpc,
                'cpa': cpa
            },
            'content_analysis': content_analysis,
            'optimization_recommendations': self._generate_campaign_recommendations(campaign, ctr, conversion_rate)
        }
    
    def _calculate_follower_growth(self, accounts: List[SocialAccount], days: int) -> float:
        """Calculate follower growth rate"""
        # Simplified calculation - in reality, would need historical follower data
        total_current = sum(account.followers_count for account in accounts)
        # Assuming 2% monthly growth as baseline
        estimated_previous = total_current * 0.98
        growth_rate = ((total_current - estimated_previous) / estimated_previous) * 100
        return round(growth_rate, 2)
    
    def _calculate_roi_metrics(self, accounts: List[SocialAccount], posts: List[SocialPost]) -> Dict[str, float]:
        """Calculate ROI metrics for client"""
        if not posts:
            return {}
        
        # Simplified ROI calculation
        total_engagement = sum(post.likes_count + post.comments_count + post.shares_count for post in posts)
        total_reach = sum(post.views_count for post in posts if post.views_count)
        
        # Estimate value per engagement (industry-dependent)
        value_per_engagement = 0.50  # $0.50 per engagement
        estimated_value = total_engagement * value_per_engagement
        
        # Estimate cost (simplified)
        estimated_cost = len(posts) * 25  # $25 per post
        
        roi = ((estimated_value - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 0
        
        return {
            'total_engagement': total_engagement,
            'estimated_value': estimated_value,
            'estimated_cost': estimated_cost,
            'roi_percentage': round(roi, 2),
            'cost_per_engagement': round(estimated_cost / total_engagement, 2) if total_engagement > 0 else 0
        }
    
    def _estimate_monthly_reach(self, accounts: List[SocialAccount], posts: List[SocialPost]) -> int:
        """Estimate monthly reach across all platforms"""
        total_followers = sum(account.followers_count for account in accounts)
        
        # Estimate reach as percentage of followers (varies by platform)
        platform_reach_rates = {
            'instagram': 0.15,  # 15% organic reach
            'facebook': 0.05,   # 5% organic reach
            'twitter': 0.20,    # 20% organic reach
            'linkedin': 0.10,   # 10% organic reach
            'tiktok': 0.30,     # 30% organic reach
            'youtube': 0.25     # 25% organic reach
        }
        
        total_reach = 0
        for account in accounts:
            reach_rate = platform_reach_rates.get(account.platform, 0.15)
            account_reach = account.followers_count * reach_rate
            total_reach += account_reach
        
        return int(total_reach)
    
    def _calculate_agency_revenue(self, client_performances: List[ClientPerformance]) -> float:
        """Calculate estimated agency monthly revenue"""
        # Simplified revenue calculation based on client size and performance
        total_revenue = 0
        
        for performance in client_performances:
            # Base pricing tiers
            if performance.total_followers < 10000:
                base_price = 1500  # $1,500/month for small clients
            elif performance.total_followers < 50000:
                base_price = 3000  # $3,000/month for medium clients
            else:
                base_price = 5000  # $5,000/month for large clients
            
            # Performance bonus
            if performance.avg_engagement_rate > 0.05:  # Above 5%
                base_price *= 1.2
            
            # Multi-platform bonus
            if len(performance.platforms) > 2:
                base_price *= 1.1
            
            total_revenue += base_price
        
        return total_revenue
    
    def _get_industry_benchmarks(self, client_performances: List[ClientPerformance]) -> Dict[str, Dict[str, float]]:
        """Get industry benchmarks for comparison"""
        # Group clients by industry
        industries = {}
        for performance in client_performances:
            if performance.industry not in industries:
                industries[performance.industry] = []
            industries[performance.industry].append(performance)
        
        # Calculate benchmarks for each industry
        benchmarks = {}
        for industry, performances in industries.items():
            avg_engagement = sum(p.avg_engagement_rate for p in performances) / len(performances)
            avg_followers = sum(p.total_followers for p in performances) / len(performances)
            avg_growth = sum(p.follower_growth for p in performances) / len(performances)
            
            benchmarks[industry] = {
                'avg_engagement_rate': round(avg_engagement, 4),
                'avg_followers': int(avg_followers),
                'avg_growth_rate': round(avg_growth, 2)
            }
        
        return benchmarks
    
    def _calculate_growth_trends(self, client_performances: List[ClientPerformance]) -> Dict[str, List[float]]:
        """Calculate growth trends (simplified)"""
        # In reality, this would use historical data
        return {
            'follower_growth': [p.follower_growth for p in client_performances],
            'engagement_trends': [p.avg_engagement_rate for p in client_performances]
        }
    
    def _generate_alert_summary(self, client_performances: List[ClientPerformance]) -> Dict[str, int]:
        """Generate summary of alerts and issues"""
        alerts = {
            'low_engagement': 0,
            'declining_growth': 0,
            'content_opportunities': 0,
            'competitor_threats': 0
        }
        
        for performance in client_performances:
            if performance.avg_engagement_rate < 0.02:  # Below 2%
                alerts['low_engagement'] += 1
            
            if performance.follower_growth < 0:  # Declining followers
                alerts['declining_growth'] += 1
            
            if len(performance.recommendations) > 3:  # Many recommendations = opportunities
                alerts['content_opportunities'] += 1
        
        return alerts
    
    def _generate_executive_summary(self, performance: ClientPerformance, platform_analytics: Dict[str, Any]) -> str:
        """Generate executive summary for client report"""
        summary_parts = []
        
        # Overall performance
        if performance.avg_engagement_rate > 0.03:
            summary_parts.append(f"Strong engagement performance at {performance.avg_engagement_rate:.1%}")
        else:
            summary_parts.append(f"Engagement rate of {performance.avg_engagement_rate:.1%} has room for improvement")
        
        # Growth
        if performance.follower_growth > 0:
            summary_parts.append(f"Positive follower growth of {performance.follower_growth:.1f}%")
        else:
            summary_parts.append("Follower growth needs attention")
        
        # Platform performance
        best_platform = max(platform_analytics.keys(), 
                          key=lambda p: platform_analytics[p]['metrics'].get('avg_engagement_rate', 0))
        summary_parts.append(f"{best_platform.title()} is the top-performing platform")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_detailed_recommendations(self, performance: ClientPerformance, platform_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed recommendations with priorities"""
        recommendations = []
        
        # Engagement recommendations
        if performance.avg_engagement_rate < 0.025:
            recommendations.append({
                'priority': 'high',
                'category': 'engagement',
                'title': 'Improve Content Engagement',
                'description': 'Focus on creating more interactive and valuable content',
                'action_items': [
                    'Ask questions in posts to encourage comments',
                    'Share behind-the-scenes content',
                    'Use trending hashtags relevant to your industry'
                ]
            })
        
        # Growth recommendations
        if performance.follower_growth < 1:
            recommendations.append({
                'priority': 'medium',
                'category': 'growth',
                'title': 'Accelerate Follower Growth',
                'description': 'Implement strategies to attract new followers',
                'action_items': [
                    'Collaborate with industry influencers',
                    'Run targeted follower acquisition campaigns',
                    'Cross-promote on other platforms'
                ]
            })
        
        return recommendations
    
    def _generate_competitive_analysis(self, client_accounts: List[SocialAccount]) -> Dict[str, Any]:
        """Generate competitive analysis"""
        # Simplified competitive analysis
        return {
            'market_position': 'Above Average',
            'key_competitors': ['Competitor A', 'Competitor B', 'Competitor C'],
            'competitive_advantages': [
                'Higher engagement rate than industry average',
                'Consistent posting schedule',
                'Strong visual content'
            ],
            'areas_for_improvement': [
                'Increase posting frequency',
                'Expand to additional platforms',
                'Improve hashtag strategy'
            ]
        }
    
    def _generate_next_month_strategy(self, performance: ClientPerformance) -> Dict[str, Any]:
        """Generate strategy for next month"""
        return {
            'content_themes': [
                f'Industry-specific content for {performance.industry}',
                'User-generated content campaigns',
                'Educational and how-to content'
            ],
            'posting_schedule': {
                'frequency': '5-7 posts per week',
                'optimal_times': 'Based on audience analysis',
                'content_mix': '60% educational, 30% promotional, 10% behind-the-scenes'
            },
            'growth_targets': {
                'follower_growth': f'{max(2, performance.follower_growth + 1):.1f}%',
                'engagement_rate': f'{performance.avg_engagement_rate + 0.005:.1%}',
                'reach_increase': '15%'
            }
        }
    
    def _analyze_campaign_content(self, posts: List[SocialPost]) -> Dict[str, Any]:
        """Analyze campaign content performance"""
        if not posts:
            return {}
        
        # Convert to DataFrame for analysis
        posts_data = []
        for post in posts:
            posts_data.append({
                'engagement_rate': post.engagement_rate or 0,
                'content_type': post.content_type,
                'hashtag_count': len(post.hashtags),
                'content_length': len(post.content_text)
            })
        
        df = pd.DataFrame(posts_data)
        
        return {
            'avg_engagement_rate': float(df['engagement_rate'].mean()),
            'best_content_type': df.groupby('content_type')['engagement_rate'].mean().idxmax(),
            'optimal_hashtag_count': df.groupby('hashtag_count')['engagement_rate'].mean().idxmax(),
            'total_posts': len(posts)
        }
    
    def _generate_campaign_recommendations(self, campaign: SocialCampaign, ctr: float, conversion_rate: float) -> List[str]:
        """Generate campaign optimization recommendations"""
        recommendations = []
        
        if ctr < 1.0:  # Below 1% CTR
            recommendations.append('Improve ad creative and copy to increase click-through rate')
        
        if conversion_rate < 2.0:  # Below 2% conversion rate
            recommendations.append('Optimize landing page and conversion funnel')
        
        if campaign.campaign_type == 'awareness' and ctr > 2.0:
            recommendations.append('Consider shifting budget to conversion-focused campaigns')
        
        return recommendations

# Global instance
smma_client_manager = SMMAClientManager()
