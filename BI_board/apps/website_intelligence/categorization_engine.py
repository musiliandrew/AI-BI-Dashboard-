"""
Website Categorization and Intelligence Engine
Automatically categorize websites and generate industry-specific insights
"""
import requests
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
from collections import Counter

from .models import WebsiteProperty, WebsiteMetrics, WebsitePage, WebsiteInsight
from ..data_ingestion.ai_intelligence import AIInsight

logger = logging.getLogger(__name__)

@dataclass
class WebsiteCategory:
    """Website categorization result"""
    industry: str
    business_type: str
    website_type: str
    confidence: float
    evidence: List[str]
    keywords: List[str]

@dataclass
class WebsiteAnalysisResult:
    """Complete website analysis result"""
    category: WebsiteCategory
    performance_insights: List[AIInsight]
    content_analysis: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    seo_analysis: Dict[str, Any]
    conversion_opportunities: List[Dict[str, Any]]
    recommendations: List[str]

class WebsiteCategorizationEngine:
    """AI-powered website categorization and analysis"""
    
    def __init__(self):
        self.industry_keywords = self._load_industry_keywords()
        self.business_type_patterns = self._load_business_type_patterns()
        self.website_type_indicators = self._load_website_type_indicators()
    
    def analyze_website(self, website_url: str, existing_data: Dict[str, Any] = None) -> WebsiteAnalysisResult:
        """Comprehensive website analysis and categorization"""
        
        logger.info(f"Analyzing website: {website_url}")
        
        # Crawl and analyze website content
        website_data = self._crawl_website(website_url)
        
        # Categorize the website
        category = self._categorize_website(website_data)
        
        # Analyze performance (if metrics available)
        performance_insights = []
        if existing_data and 'metrics' in existing_data:
            performance_insights = self._analyze_performance(existing_data['metrics'], category)
        
        # Content analysis
        content_analysis = self._analyze_content(website_data, category)
        
        # Technical analysis
        technical_analysis = self._analyze_technical_aspects(website_data)
        
        # SEO analysis
        seo_analysis = self._analyze_seo(website_data)
        
        # Conversion opportunities
        conversion_opportunities = self._identify_conversion_opportunities(website_data, category)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            category, content_analysis, technical_analysis, seo_analysis
        )
        
        return WebsiteAnalysisResult(
            category=category,
            performance_insights=performance_insights,
            content_analysis=content_analysis,
            technical_analysis=technical_analysis,
            seo_analysis=seo_analysis,
            conversion_opportunities=conversion_opportunities,
            recommendations=recommendations
        )
    
    def _crawl_website(self, url: str, max_pages: int = 10) -> Dict[str, Any]:
        """Crawl website to gather content and structure data"""
        
        try:
            # Get main page
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; AugmentBot/1.0)'
            })
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            website_data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_description': self._get_meta_description(soup),
                'headings': self._extract_headings(soup),
                'content_text': self._extract_text_content(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup),
                'forms': self._extract_forms(soup),
                'technologies': self._detect_technologies(response.text, dict(response.headers)),
                'page_structure': self._analyze_page_structure(soup),
                'navigation': self._extract_navigation(soup)
            }
            
            # Crawl additional pages
            additional_pages = self._crawl_additional_pages(url, website_data['links'][:max_pages])
            website_data['additional_pages'] = additional_pages
            
            return website_data
            
        except Exception as e:
            logger.error(f"Error crawling website {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def _categorize_website(self, website_data: Dict[str, Any]) -> WebsiteCategory:
        """Categorize website based on content and structure"""
        
        # Combine all text content for analysis
        all_text = ' '.join([
            website_data.get('title', ''),
            website_data.get('meta_description', ''),
            ' '.join(website_data.get('headings', [])),
            website_data.get('content_text', '')[:2000]  # Limit to first 2000 chars
        ]).lower()
        
        # Industry detection
        industry_scores = {}
        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                industry_scores[industry] = score
        
        # Business type detection
        business_type_scores = {}
        for biz_type, patterns in self.business_type_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, all_text))
            if score > 0:
                business_type_scores[biz_type] = score
        
        # Website type detection
        website_type_scores = {}
        for site_type, indicators in self.website_type_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator['type'] == 'content' and indicator['pattern'] in all_text:
                    score += indicator['weight']
                elif indicator['type'] == 'structure':
                    # Check for structural elements
                    if self._check_structural_indicator(website_data, indicator):
                        score += indicator['weight']
            
            if score > 0:
                website_type_scores[site_type] = score
        
        # Determine best matches
        top_industry = max(industry_scores.items(), key=lambda x: x[1]) if industry_scores else ('unknown', 0)
        top_business_type = max(business_type_scores.items(), key=lambda x: x[1]) if business_type_scores else ('unknown', 0)
        top_website_type = max(website_type_scores.items(), key=lambda x: x[1]) if website_type_scores else ('informational', 0)
        
        # Calculate confidence
        total_indicators = len(self.industry_keywords.get(top_industry[0], [])) + \
                          len(self.business_type_patterns.get(top_business_type[0], [])) + \
                          len(self.website_type_indicators.get(top_website_type[0], []))
        
        confidence = min((top_industry[1] + top_business_type[1] + top_website_type[1]) / max(total_indicators, 1), 1.0)
        
        # Generate evidence
        evidence = []
        if top_industry[1] > 0:
            evidence.append(f"Industry keywords found: {top_industry[0]}")
        if top_business_type[1] > 0:
            evidence.append(f"Business type indicators: {top_business_type[0]}")
        if top_website_type[1] > 0:
            evidence.append(f"Website type features: {top_website_type[0]}")
        
        # Extract key keywords
        keywords = self._extract_keywords(all_text)
        
        return WebsiteCategory(
            industry=top_industry[0],
            business_type=top_business_type[0],
            website_type=top_website_type[0],
            confidence=confidence,
            evidence=evidence,
            keywords=keywords
        )
    
    def _analyze_performance(self, metrics_data: Dict[str, Any], category: WebsiteCategory) -> List[AIInsight]:
        """Analyze website performance with industry context"""
        insights = []
        
        # Get industry benchmarks
        benchmarks = self._get_industry_benchmarks(category.industry)
        
        # Bounce rate analysis
        bounce_rate = metrics_data.get('bounce_rate', 0)
        benchmark_bounce = benchmarks.get('avg_bounce_rate', 50)
        
        if bounce_rate > benchmark_bounce * 1.2:  # 20% above benchmark
            insights.append(AIInsight(
                insight_type='performance',
                title='High Bounce Rate Detected',
                description=f"Bounce rate of {bounce_rate:.1f}% is {bounce_rate - benchmark_bounce:.1f}% above industry average",
                confidence=0.9,
                business_impact=self._get_bounce_rate_impact(category.industry),
                data_evidence={'bounce_rate': bounce_rate, 'benchmark': benchmark_bounce},
                visualization_config={'type': 'gauge', 'value': 'bounce_rate', 'benchmark': 'industry_avg'},
                action_items=[
                    'Improve page loading speed',
                    'Enhance content relevance and quality',
                    'Optimize mobile user experience',
                    'Review and improve call-to-action placement'
                ]
            ))
        
        # Conversion rate analysis
        conversion_rate = metrics_data.get('conversion_rate', 0)
        benchmark_conversion = benchmarks.get('avg_conversion_rate', 2.5)
        
        if conversion_rate < benchmark_conversion * 0.8:  # 20% below benchmark
            insights.append(AIInsight(
                insight_type='conversion',
                title='Conversion Rate Below Industry Average',
                description=f"Conversion rate of {conversion_rate:.1f}% is below industry average of {benchmark_conversion:.1f}%",
                confidence=0.85,
                business_impact=self._get_conversion_impact(category.industry, conversion_rate, benchmark_conversion),
                data_evidence={'conversion_rate': conversion_rate, 'benchmark': benchmark_conversion},
                visualization_config={'type': 'bar_chart', 'x': 'metric', 'y': 'value'},
                action_items=[
                    'Optimize conversion funnel',
                    'A/B test call-to-action buttons',
                    'Improve trust signals and testimonials',
                    'Simplify checkout or contact process'
                ]
            ))
        
        return insights
    
    def _analyze_content(self, website_data: Dict[str, Any], category: WebsiteCategory) -> Dict[str, Any]:
        """Analyze website content quality and optimization"""
        
        content_text = website_data.get('content_text', '')
        headings = website_data.get('headings', [])
        
        # Content quality metrics
        word_count = len(content_text.split())
        reading_level = self._calculate_reading_level(content_text)
        keyword_density = self._calculate_keyword_density(content_text, category.keywords)
        
        # Content structure analysis
        heading_structure = self._analyze_heading_structure(headings)
        
        # Industry-specific content analysis
        industry_content_score = self._score_industry_content(content_text, category.industry)
        
        return {
            'word_count': word_count,
            'reading_level': reading_level,
            'keyword_density': keyword_density,
            'heading_structure': heading_structure,
            'industry_content_score': industry_content_score,
            'content_freshness': self._assess_content_freshness(website_data),
            'multimedia_usage': self._analyze_multimedia_usage(website_data)
        }
    
    def _analyze_technical_aspects(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical aspects of the website"""
        
        return {
            'page_speed_indicators': self._assess_page_speed_indicators(website_data),
            'mobile_optimization': self._assess_mobile_optimization(website_data),
            'security_features': self._assess_security_features(website_data),
            'accessibility': self._assess_accessibility(website_data),
            'structured_data': self._detect_structured_data(website_data),
            'technology_stack': website_data.get('technologies', {})
        }
    
    def _analyze_seo(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEO aspects of the website"""
        
        title = website_data.get('title', '')
        meta_description = website_data.get('meta_description', '')
        headings = website_data.get('headings', [])
        
        return {
            'title_optimization': self._analyze_title_tag(title),
            'meta_description_optimization': self._analyze_meta_description(meta_description),
            'heading_optimization': self._analyze_heading_seo(headings),
            'internal_linking': self._analyze_internal_linking(website_data),
            'image_optimization': self._analyze_image_seo(website_data),
            'url_structure': self._analyze_url_structure(website_data)
        }
    
    def _identify_conversion_opportunities(self, website_data: Dict[str, Any], category: WebsiteCategory) -> List[Dict[str, Any]]:
        """Identify conversion optimization opportunities"""
        
        opportunities = []
        
        # Check for contact forms
        forms = website_data.get('forms', [])
        if not forms:
            opportunities.append({
                'type': 'missing_contact_form',
                'priority': 'high',
                'description': 'No contact forms detected - missing lead generation opportunity',
                'recommendation': 'Add contact forms on key pages to capture leads'
            })
        
        # Check for call-to-action buttons
        cta_indicators = ['buy now', 'contact us', 'get quote', 'schedule', 'book now']
        content_text = website_data.get('content_text', '').lower()
        
        cta_count = sum(1 for cta in cta_indicators if cta in content_text)
        if cta_count < 2:
            opportunities.append({
                'type': 'weak_cta_presence',
                'priority': 'medium',
                'description': 'Limited call-to-action elements detected',
                'recommendation': 'Add more prominent and compelling call-to-action buttons'
            })
        
        # Industry-specific opportunities
        if category.industry == 'automotive':
            if 'inventory' not in content_text and 'vehicles' in content_text:
                opportunities.append({
                    'type': 'missing_inventory_link',
                    'priority': 'high',
                    'description': 'Vehicle content found but no clear inventory access',
                    'recommendation': 'Add prominent links to vehicle inventory'
                })
        
        elif category.industry == 'restaurant':
            if 'menu' not in content_text:
                opportunities.append({
                    'type': 'missing_menu',
                    'priority': 'high',
                    'description': 'Restaurant website without accessible menu',
                    'recommendation': 'Add online menu with clear navigation'
                })
        
        return opportunities
    
    def _generate_recommendations(self, category: WebsiteCategory, content_analysis: Dict[str, Any], 
                                technical_analysis: Dict[str, Any], seo_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Content recommendations
        if content_analysis['word_count'] < 300:
            recommendations.append('Increase content length to at least 300 words for better SEO')
        
        if content_analysis['industry_content_score'] < 0.5:
            recommendations.append(f'Add more {category.industry}-specific content and terminology')
        
        # Technical recommendations
        if not technical_analysis['mobile_optimization']['is_mobile_friendly']:
            recommendations.append('Implement responsive design for mobile optimization')
        
        if technical_analysis['page_speed_indicators']['estimated_load_time'] > 3:
            recommendations.append('Optimize page loading speed (target: under 3 seconds)')
        
        # SEO recommendations
        if not seo_analysis['title_optimization']['is_optimized']:
            recommendations.append('Optimize page title tags with relevant keywords')
        
        if not seo_analysis['meta_description_optimization']['is_optimized']:
            recommendations.append('Add compelling meta descriptions to improve click-through rates')
        
        # Industry-specific recommendations
        industry_recs = self._get_industry_specific_recommendations(category.industry)
        recommendations.extend(industry_recs)
        
        return recommendations[:10]  # Limit to top 10
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keywords for categorization"""
        return {
            'automotive': [
                'car', 'auto', 'vehicle', 'dealership', 'sales', 'service', 'parts',
                'financing', 'lease', 'certified', 'inventory', 'trade-in'
            ],
            'restaurant': [
                'restaurant', 'menu', 'food', 'dining', 'cuisine', 'chef', 'reservation',
                'delivery', 'takeout', 'catering', 'bar', 'wine'
            ],
            'retail': [
                'shop', 'store', 'clothing', 'fashion', 'sale', 'discount', 'collection',
                'brand', 'style', 'accessories', 'shoes', 'apparel'
            ],
            'healthcare': [
                'doctor', 'medical', 'health', 'clinic', 'hospital', 'treatment',
                'patient', 'care', 'therapy', 'wellness', 'medicine'
            ],
            'real_estate': [
                'real estate', 'property', 'home', 'house', 'apartment', 'rent',
                'buy', 'sell', 'agent', 'broker', 'listing'
            ],
            'legal': [
                'lawyer', 'attorney', 'legal', 'law', 'court', 'case', 'consultation',
                'litigation', 'contract', 'advice', 'representation'
            ]
        }
    
    def _load_business_type_patterns(self) -> Dict[str, List[str]]:
        """Load business type detection patterns"""
        return {
            'dealership': [r'dealership', r'auto sales', r'car sales'],
            'restaurant': [r'restaurant', r'bistro', r'cafe', r'diner'],
            'retail_store': [r'boutique', r'shop', r'store', r'retail'],
            'clinic': [r'clinic', r'medical center', r'health center'],
            'agency': [r'agency', r'firm', r'company', r'services'],
            'e_commerce': [r'online store', r'shop online', r'e-commerce']
        }
    
    def _load_website_type_indicators(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load website type indicators"""
        return {
            'ecommerce': [
                {'type': 'content', 'pattern': 'add to cart', 'weight': 3},
                {'type': 'content', 'pattern': 'shopping cart', 'weight': 3},
                {'type': 'content', 'pattern': 'checkout', 'weight': 2},
                {'type': 'structure', 'element': 'product_grid', 'weight': 2}
            ],
            'lead_generation': [
                {'type': 'content', 'pattern': 'contact us', 'weight': 2},
                {'type': 'content', 'pattern': 'get quote', 'weight': 3},
                {'type': 'structure', 'element': 'contact_form', 'weight': 3}
            ],
            'informational': [
                {'type': 'content', 'pattern': 'about us', 'weight': 1},
                {'type': 'content', 'pattern': 'blog', 'weight': 2},
                {'type': 'structure', 'element': 'article_content', 'weight': 2}
            ]
        }
    
    def _get_industry_benchmarks(self, industry: str) -> Dict[str, float]:
        """Get industry-specific performance benchmarks"""
        benchmarks = {
            'automotive': {
                'avg_bounce_rate': 45.0,
                'avg_conversion_rate': 2.8,
                'avg_session_duration': 180
            },
            'restaurant': {
                'avg_bounce_rate': 55.0,
                'avg_conversion_rate': 1.5,
                'avg_session_duration': 120
            },
            'retail': {
                'avg_bounce_rate': 40.0,
                'avg_conversion_rate': 3.2,
                'avg_session_duration': 200
            },
            'healthcare': {
                'avg_bounce_rate': 50.0,
                'avg_conversion_rate': 2.0,
                'avg_session_duration': 150
            }
        }
        
        return benchmarks.get(industry, {
            'avg_bounce_rate': 50.0,
            'avg_conversion_rate': 2.5,
            'avg_session_duration': 150
        })
    
    def _extract_keywords(self, text: str, limit: int = 10) -> List[str]:
        """Extract key keywords from text"""
        # Simple keyword extraction (in production, use more sophisticated NLP)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = Counter(words)
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'way', 'she', 'use', 'her', 'now', 'oil', 'sit', 'set'}
        
        filtered_words = {word: freq for word, freq in word_freq.items() if word not in stop_words and len(word) > 3}
        
        return [word for word, freq in sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:limit]]
    
    # Helper methods (simplified implementations)
    def _get_meta_description(self, soup): 
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ''
    
    def _extract_headings(self, soup): 
        return [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    
    def _extract_text_content(self, soup): 
        return soup.get_text()
    
    def _extract_links(self, soup, base_url): 
        return [urljoin(base_url, a.get('href', '')) for a in soup.find_all('a', href=True)]
    
    def _extract_images(self, soup): 
        return [img.get('src', '') for img in soup.find_all('img')]
    
    def _extract_forms(self, soup): 
        return [{'action': form.get('action', ''), 'method': form.get('method', 'get')} for form in soup.find_all('form')]
    
    def _detect_technologies(self, html, headers): 
        return {}  # Simplified
    
    def _analyze_page_structure(self, soup): 
        return {}  # Simplified
    
    def _extract_navigation(self, soup): 
        return []  # Simplified
    
    def _crawl_additional_pages(self, base_url, links): 
        return []  # Simplified
    
    def _check_structural_indicator(self, website_data, indicator): 
        return False  # Simplified
    
    def _calculate_reading_level(self, text): 
        return 8.0  # Simplified
    
    def _calculate_keyword_density(self, text, keywords): 
        return {}  # Simplified
    
    def _analyze_heading_structure(self, headings): 
        return {}  # Simplified
    
    def _score_industry_content(self, text, industry): 
        return 0.5  # Simplified
    
    def _assess_content_freshness(self, website_data): 
        return {}  # Simplified
    
    def _analyze_multimedia_usage(self, website_data): 
        return {}  # Simplified
    
    def _assess_page_speed_indicators(self, website_data): 
        return {'estimated_load_time': 2.5}  # Simplified
    
    def _assess_mobile_optimization(self, website_data): 
        return {'is_mobile_friendly': True}  # Simplified
    
    def _assess_security_features(self, website_data): 
        return {}  # Simplified
    
    def _assess_accessibility(self, website_data): 
        return {}  # Simplified
    
    def _detect_structured_data(self, website_data): 
        return {}  # Simplified
    
    def _analyze_title_tag(self, title): 
        return {'is_optimized': len(title) > 10}  # Simplified
    
    def _analyze_meta_description(self, meta_desc): 
        return {'is_optimized': len(meta_desc) > 50}  # Simplified
    
    def _analyze_heading_seo(self, headings): 
        return {}  # Simplified
    
    def _analyze_internal_linking(self, website_data): 
        return {}  # Simplified
    
    def _analyze_image_seo(self, website_data): 
        return {}  # Simplified
    
    def _analyze_url_structure(self, website_data): 
        return {}  # Simplified
    
    def _get_bounce_rate_impact(self, industry): 
        return f"High bounce rate reduces {industry} lead generation and sales conversions"
    
    def _get_conversion_impact(self, industry, current, benchmark): 
        lost_conversions = (benchmark - current) / 100 * 1000  # Assuming 1000 monthly visitors
        return f"Potential {lost_conversions:.0f} additional monthly conversions with industry-average rates"
    
    def _get_industry_specific_recommendations(self, industry): 
        recs = {
            'automotive': ['Add vehicle inventory showcase', 'Include financing calculator', 'Add customer testimonials'],
            'restaurant': ['Display menu prominently', 'Add online reservation system', 'Include location and hours'],
            'retail': ['Optimize product images', 'Add customer reviews', 'Implement size guides']
        }
        return recs.get(industry, ['Improve user experience', 'Add clear call-to-actions'])

# Global instance
website_categorization_engine = WebsiteCategorizationEngine()
