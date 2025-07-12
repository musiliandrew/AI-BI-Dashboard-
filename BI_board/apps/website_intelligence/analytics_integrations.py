"""
Website Analytics Integrations - Google Analytics, Adobe Analytics, and custom tracking
"""
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, DateRange
)
import re
import urllib.parse

logger = logging.getLogger(__name__)

@dataclass
class WebsiteMetricsData:
    """Standardized website metrics across all platforms"""
    date: datetime
    sessions: int = 0
    users: int = 0
    new_users: int = 0
    pageviews: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    traffic_sources: Dict[str, int] = None
    device_breakdown: Dict[str, int] = None
    top_pages: List[Dict[str, Any]] = None

@dataclass
class PagePerformanceData:
    """Page-level performance data"""
    page_path: str
    page_title: str
    pageviews: int
    unique_pageviews: int
    avg_time_on_page: float
    bounce_rate: float
    exit_rate: float
    conversions: int = 0

class GoogleAnalyticsIntegration:
    """Google Analytics 4 (GA4) integration"""
    
    def __init__(self, property_id: str, credentials_path: str = None):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient.from_service_account_file(credentials_path) if credentials_path else BetaAnalyticsDataClient()
    
    def get_website_metrics(self, start_date: datetime, end_date: datetime) -> WebsiteMetricsData:
        """Get comprehensive website metrics from GA4"""
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionDefaultChannelGroup"),
                Dimension(name="deviceCategory")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="conversions"),
                Metric(name="totalRevenue")
            ],
            date_ranges=[DateRange(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )]
        )
        
        try:
            response = self.client.run_report(request)
            return self._process_ga4_response(response)
        except Exception as e:
            logger.error(f"GA4 API error: {e}")
            return WebsiteMetricsData(date=start_date)
    
    def get_page_performance(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[PagePerformanceData]:
        """Get page-level performance data"""
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle")
            ],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="averageTimeOnPage"),
                Metric(name="bounceRate"),
                Metric(name="exitRate"),
                Metric(name="conversions")
            ],
            date_ranges=[DateRange(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )],
            limit=limit,
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}]
        )
        
        try:
            response = self.client.run_report(request)
            return self._process_page_performance_response(response)
        except Exception as e:
            logger.error(f"GA4 page performance error: {e}")
            return []
    
    def get_traffic_sources(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get traffic source breakdown"""
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )]
        )
        
        try:
            response = self.client.run_report(request)
            traffic_sources = {}
            
            for row in response.rows:
                channel = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                traffic_sources[channel.lower().replace(' ', '_')] = sessions
            
            return traffic_sources
        except Exception as e:
            logger.error(f"GA4 traffic sources error: {e}")
            return {}
    
    def get_conversion_goals(self) -> List[Dict[str, Any]]:
        """Get configured conversion goals"""
        # This would use the GA4 Admin API to get conversion events
        # For now, return common e-commerce events
        return [
            {'name': 'purchase', 'type': 'ecommerce'},
            {'name': 'add_to_cart', 'type': 'engagement'},
            {'name': 'begin_checkout', 'type': 'engagement'},
            {'name': 'contact_form_submit', 'type': 'lead_generation'}
        ]
    
    def _process_ga4_response(self, response) -> WebsiteMetricsData:
        """Process GA4 API response into standardized format"""
        
        # Aggregate metrics across all rows
        total_sessions = 0
        total_users = 0
        total_new_users = 0
        total_pageviews = 0
        total_bounce_rate = 0
        total_duration = 0
        total_conversions = 0
        total_revenue = 0
        
        traffic_sources = {}
        device_breakdown = {}
        
        for row in response.rows:
            sessions = int(row.metric_values[0].value)
            users = int(row.metric_values[1].value)
            new_users = int(row.metric_values[2].value)
            pageviews = int(row.metric_values[3].value)
            bounce_rate = float(row.metric_values[4].value)
            duration = float(row.metric_values[5].value)
            conversions = int(row.metric_values[6].value)
            revenue = float(row.metric_values[7].value)
            
            # Get dimensions
            channel = row.dimension_values[1].value if len(row.dimension_values) > 1 else 'unknown'
            device = row.dimension_values[2].value if len(row.dimension_values) > 2 else 'unknown'
            
            total_sessions += sessions
            total_users += users
            total_new_users += new_users
            total_pageviews += pageviews
            total_conversions += conversions
            total_revenue += revenue
            
            # Aggregate by source and device
            traffic_sources[channel] = traffic_sources.get(channel, 0) + sessions
            device_breakdown[device] = device_breakdown.get(device, 0) + sessions
        
        # Calculate weighted averages
        avg_bounce_rate = total_bounce_rate / len(response.rows) if response.rows else 0
        avg_duration = total_duration / len(response.rows) if response.rows else 0
        conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0
        
        return WebsiteMetricsData(
            date=datetime.now(),
            sessions=total_sessions,
            users=total_users,
            new_users=total_new_users,
            pageviews=total_pageviews,
            bounce_rate=avg_bounce_rate,
            avg_session_duration=avg_duration,
            conversion_rate=conversion_rate,
            revenue=total_revenue,
            traffic_sources=traffic_sources,
            device_breakdown=device_breakdown
        )
    
    def _process_page_performance_response(self, response) -> List[PagePerformanceData]:
        """Process page performance response"""
        pages = []
        
        for row in response.rows:
            page_path = row.dimension_values[0].value
            page_title = row.dimension_values[1].value
            pageviews = int(row.metric_values[0].value)
            avg_time = float(row.metric_values[1].value)
            bounce_rate = float(row.metric_values[2].value)
            exit_rate = float(row.metric_values[3].value)
            conversions = int(row.metric_values[4].value)
            
            pages.append(PagePerformanceData(
                page_path=page_path,
                page_title=page_title,
                pageviews=pageviews,
                unique_pageviews=pageviews,  # GA4 doesn't have unique pageviews
                avg_time_on_page=avg_time,
                bounce_rate=bounce_rate,
                exit_rate=exit_rate,
                conversions=conversions
            ))
        
        return pages

class GoogleSearchConsoleIntegration:
    """Google Search Console integration for SEO data"""
    
    def __init__(self, site_url: str, credentials_path: str = None):
        self.site_url = site_url
        self.credentials_path = credentials_path
    
    def get_search_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get search performance data"""
        # This would use the Search Console API
        # For now, return sample structure
        return {
            'total_clicks': 1250,
            'total_impressions': 45000,
            'average_ctr': 2.78,
            'average_position': 12.5,
            'top_queries': [
                {'query': 'automotive dealership', 'clicks': 150, 'impressions': 2500},
                {'query': 'car sales near me', 'clicks': 120, 'impressions': 3200}
            ],
            'top_pages': [
                {'page': '/inventory', 'clicks': 300, 'impressions': 5000},
                {'page': '/services', 'clicks': 200, 'impressions': 3500}
            ]
        }

class CustomTrackingIntegration:
    """Custom tracking script for detailed user behavior"""
    
    def __init__(self, tracking_id: str):
        self.tracking_id = tracking_id
        self.api_endpoint = "https://api.augment.com/v1/tracking"
    
    def generate_tracking_script(self, website_domain: str) -> str:
        """Generate custom tracking script for website"""
        script = f"""
        <!-- Augment Website Intelligence Tracking -->
        <script>
        (function() {{
            var augmentTracker = {{
                trackingId: '{self.tracking_id}',
                domain: '{website_domain}',
                apiEndpoint: '{self.api_endpoint}',
                
                init: function() {{
                    this.trackPageView();
                    this.setupEventListeners();
                    this.trackUserBehavior();
                }},
                
                trackPageView: function() {{
                    this.sendEvent('page_view', {{
                        page_url: window.location.href,
                        page_title: document.title,
                        referrer: document.referrer,
                        timestamp: new Date().toISOString()
                    }});
                }},
                
                trackEvent: function(eventName, eventData) {{
                    this.sendEvent(eventName, eventData);
                }},
                
                setupEventListeners: function() {{
                    // Track clicks on important elements
                    document.addEventListener('click', function(e) {{
                        var element = e.target;
                        var eventData = {{
                            element_type: element.tagName,
                            element_class: element.className,
                            element_id: element.id,
                            element_text: element.innerText.substring(0, 100),
                            page_url: window.location.href,
                            timestamp: new Date().toISOString()
                        }};
                        
                        // Track specific elements
                        if (element.tagName === 'A') {{
                            augmentTracker.sendEvent('link_click', eventData);
                        }} else if (element.tagName === 'BUTTON' || element.type === 'submit') {{
                            augmentTracker.sendEvent('button_click', eventData);
                        }}
                    }});
                    
                    // Track form submissions
                    document.addEventListener('submit', function(e) {{
                        augmentTracker.sendEvent('form_submit', {{
                            form_id: e.target.id,
                            form_action: e.target.action,
                            page_url: window.location.href,
                            timestamp: new Date().toISOString()
                        }});
                    }});
                    
                    // Track scroll depth
                    var maxScroll = 0;
                    window.addEventListener('scroll', function() {{
                        var scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
                        if (scrollPercent > maxScroll) {{
                            maxScroll = scrollPercent;
                            if (maxScroll % 25 === 0) {{ // Track at 25%, 50%, 75%, 100%
                                augmentTracker.sendEvent('scroll_depth', {{
                                    scroll_percent: maxScroll,
                                    page_url: window.location.href,
                                    timestamp: new Date().toISOString()
                                }});
                            }}
                        }}
                    }});
                }},
                
                trackUserBehavior: function() {{
                    // Track time on page
                    var startTime = new Date().getTime();
                    window.addEventListener('beforeunload', function() {{
                        var timeOnPage = new Date().getTime() - startTime;
                        augmentTracker.sendEvent('time_on_page', {{
                            duration_seconds: Math.round(timeOnPage / 1000),
                            page_url: window.location.href,
                            timestamp: new Date().toISOString()
                        }});
                    }});
                }},
                
                sendEvent: function(eventName, eventData) {{
                    var payload = {{
                        tracking_id: this.trackingId,
                        event_name: eventName,
                        event_data: eventData,
                        user_agent: navigator.userAgent,
                        screen_resolution: screen.width + 'x' + screen.height,
                        viewport_size: window.innerWidth + 'x' + window.innerHeight
                    }};
                    
                    // Send via beacon API if available, otherwise use fetch
                    if (navigator.sendBeacon) {{
                        navigator.sendBeacon(this.apiEndpoint, JSON.stringify(payload));
                    }} else {{
                        fetch(this.apiEndpoint, {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify(payload)
                        }}).catch(function(error) {{
                            console.log('Augment tracking error:', error);
                        }});
                    }}
                }}
            }};
            
            // Initialize tracking when DOM is ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', function() {{
                    augmentTracker.init();
                }});
            }} else {{
                augmentTracker.init();
            }}
            
            // Make tracker available globally
            window.augmentTracker = augmentTracker;
        }})();
        </script>
        """
        return script
    
    def process_tracking_event(self, event_data: Dict[str, Any]) -> bool:
        """Process incoming tracking event"""
        try:
            # Validate and store event data
            required_fields = ['tracking_id', 'event_name', 'event_data']
            if not all(field in event_data for field in required_fields):
                return False
            
            # Store in database (would integrate with WebsiteEvent model)
            logger.info(f"Processed tracking event: {event_data['event_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing tracking event: {e}")
            return False

class WebsiteTechnologyDetector:
    """Detect technologies used on websites"""
    
    def __init__(self):
        self.technology_patterns = self._load_technology_patterns()
    
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze website to detect technologies"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; AugmentBot/1.0)'
            })
            
            html_content = response.text
            headers = dict(response.headers)
            
            detected_technologies = {}
            
            # Analyze HTML content
            detected_technologies.update(self._analyze_html_content(html_content))
            
            # Analyze HTTP headers
            detected_technologies.update(self._analyze_headers(headers))
            
            # Analyze JavaScript libraries
            detected_technologies.update(self._analyze_javascript(html_content))
            
            return {
                'url': url,
                'technologies': detected_technologies,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing website {url}: {e}")
            return {'url': url, 'technologies': {}, 'error': str(e)}
    
    def _load_technology_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load technology detection patterns"""
        return {
            'wordpress': {
                'patterns': [r'wp-content', r'wp-includes', r'/wp-json/'],
                'headers': ['x-powered-by'],
                'category': 'cms'
            },
            'shopify': {
                'patterns': [r'cdn\.shopify\.com', r'Shopify\.theme'],
                'headers': ['server'],
                'category': 'ecommerce'
            },
            'google_analytics': {
                'patterns': [r'google-analytics\.com', r'gtag\(', r'ga\('],
                'category': 'analytics'
            },
            'facebook_pixel': {
                'patterns': [r'connect\.facebook\.net', r'fbq\('],
                'category': 'marketing'
            },
            'stripe': {
                'patterns': [r'js\.stripe\.com', r'Stripe\('],
                'category': 'payment'
            }
        }
    
    def _analyze_html_content(self, html: str) -> Dict[str, Dict[str, Any]]:
        """Analyze HTML content for technology patterns"""
        detected = {}
        
        for tech_name, tech_config in self.technology_patterns.items():
            for pattern in tech_config.get('patterns', []):
                if re.search(pattern, html, re.IGNORECASE):
                    detected[tech_name] = {
                        'category': tech_config.get('category', 'other'),
                        'confidence': 0.8,
                        'detection_method': 'html_pattern'
                    }
                    break
        
        return detected
    
    def _analyze_headers(self, headers: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Analyze HTTP headers for technology indicators"""
        detected = {}
        
        # Common header-based detections
        server_header = headers.get('server', '').lower()
        powered_by = headers.get('x-powered-by', '').lower()
        
        if 'nginx' in server_header:
            detected['nginx'] = {'category': 'web_server', 'confidence': 0.9, 'detection_method': 'header'}
        
        if 'apache' in server_header:
            detected['apache'] = {'category': 'web_server', 'confidence': 0.9, 'detection_method': 'header'}
        
        if 'php' in powered_by:
            detected['php'] = {'category': 'programming_language', 'confidence': 0.9, 'detection_method': 'header'}
        
        return detected
    
    def _analyze_javascript(self, html: str) -> Dict[str, Dict[str, Any]]:
        """Analyze JavaScript libraries and frameworks"""
        detected = {}
        
        # Common JavaScript library patterns
        js_patterns = {
            'jquery': r'jquery',
            'react': r'react',
            'vue': r'vue\.js',
            'angular': r'angular',
            'bootstrap': r'bootstrap'
        }
        
        for lib_name, pattern in js_patterns.items():
            if re.search(pattern, html, re.IGNORECASE):
                detected[lib_name] = {
                    'category': 'javascript_library',
                    'confidence': 0.7,
                    'detection_method': 'javascript_pattern'
                }
        
        return detected

# Factory function to get the right analytics integration
def get_analytics_integration(platform: str, credentials: Dict[str, str]):
    """Factory function to get the appropriate analytics integration"""
    
    if platform == 'google_analytics':
        return GoogleAnalyticsIntegration(
            property_id=credentials.get('property_id'),
            credentials_path=credentials.get('credentials_path')
        )
    elif platform == 'search_console':
        return GoogleSearchConsoleIntegration(
            site_url=credentials.get('site_url'),
            credentials_path=credentials.get('credentials_path')
        )
    elif platform == 'custom_tracking':
        return CustomTrackingIntegration(
            tracking_id=credentials.get('tracking_id')
        )
    else:
        raise ValueError(f"Unsupported analytics platform: {platform}")

# Global instances
technology_detector = WebsiteTechnologyDetector()
