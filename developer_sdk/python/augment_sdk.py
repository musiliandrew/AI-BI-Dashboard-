"""
Augment Data Intelligence SDK for Python
The easiest way to add industry-specific analytics to your Python applications
"""

import requests
import pandas as pd
import json
import time
import websocket
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import threading

class AugmentAPIError(Exception):
    """Custom exception for Augment API errors"""
    def __init__(self, message: str, status_code: int = 0, details: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}

@dataclass
class AnalysisResult:
    """Result from data analysis"""
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    data_summary: Dict[str, Any]
    industry: str
    confidence_score: float

class AugmentAPI:
    """Main SDK class for Augment Data Intelligence API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.augment.com/v1", timeout: int = 30):
        """
        Initialize the Augment API client
        
        Args:
            api_key: Your Augment API key (format: ak_[tier]_[secret])
            base_url: API base URL (default: production)
            timeout: Request timeout in seconds
        """
        if not api_key or not api_key.startswith('ak_'):
            raise ValueError("Invalid API key format. Expected: ak_[tier]_[secret]")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'Augment-SDK-Python/1.0.0',
            'Content-Type': 'application/json'
        })
    
    def analyze(self, 
                data: Union[pd.DataFrame, List[Dict], str], 
                industry: Optional[str] = None,
                insights: List[str] = None) -> AnalysisResult:
        """
        Analyze data with industry-specific intelligence
        
        Args:
            data: Data to analyze (DataFrame, list of dicts, or CSV string)
            industry: Industry type (automotive, retail, restaurant, etc.)
            insights: Types of insights to generate
            
        Returns:
            AnalysisResult with AI-generated insights and recommendations
        """
        if insights is None:
            insights = ['trends', 'correlations', 'recommendations']
        
        # Prepare data payload
        data_payload = self._prepare_data(data)
        
        payload = {
            'data': data_payload,
            'industry': industry,
            'insight_types': insights,
            'auto_detect_industry': industry is None
        }
        
        response = self._request('POST', '/data/analyze', payload)
        
        return AnalysisResult(
            insights=response['insights'],
            recommendations=response['recommendations'],
            data_summary=response['data_summary'],
            industry=response['detected_industry'] or industry,
            confidence_score=response['confidence_score']
        )
    
    def analyze_file(self, file_path: str, **kwargs) -> AnalysisResult:
        """
        Analyze a file (CSV, Excel, JSON)
        
        Args:
            file_path: Path to the file to analyze
            **kwargs: Additional arguments passed to analyze()
            
        Returns:
            AnalysisResult with insights
        """
        # Read file based on extension
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        return self.analyze(data, **kwargs)
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a data processing pipeline
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Pipeline creation result with pipeline_id
        """
        return self._request('POST', '/pipelines/create', pipeline_config)
    
    def execute_pipeline(self, pipeline_id: str, wait: bool = True, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a pipeline
        
        Args:
            pipeline_id: ID of the pipeline to execute
            wait: Whether to wait for completion
            timeout: Maximum wait time in seconds
            
        Returns:
            Pipeline execution result
        """
        payload = {
            'wait_for_completion': wait,
            'timeout': timeout
        }
        
        return self._request('POST', f'/pipelines/{pipeline_id}/execute', payload)
    
    def get_industry_templates(self, industry: str) -> Dict[str, Any]:
        """
        Get available templates for an industry
        
        Args:
            industry: Industry name
            
        Returns:
            Available templates and configurations
        """
        return self._request('GET', f'/industries/{industry}/templates')
    
    def get_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get usage analytics for your API key
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Usage statistics and analytics
        """
        params = {'days': days}
        return self._request('GET', '/analytics/usage', params=params)
    
    def register_webhook(self, url: str, events: List[str], description: str = "") -> Dict[str, Any]:
        """
        Register a webhook endpoint
        
        Args:
            url: Webhook URL
            events: List of events to listen for
            description: Optional description
            
        Returns:
            Webhook registration result
        """
        payload = {
            'url': url,
            'events': events,
            'description': description
        }
        
        return self._request('POST', '/webhooks/register', payload)
    
    def stream_insights(self, industry: str, events: List[str], callback: callable):
        """
        Stream real-time insights via WebSocket
        
        Args:
            industry: Industry to monitor
            events: Events to listen for
            callback: Function to call with each insight
        """
        ws_url = self.base_url.replace('https://', 'wss://') + '/insights/stream'
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                callback(data)
            except Exception as e:
                print(f"Error processing message: {e}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def on_open(ws):
            config = {
                'industry': industry,
                'events': events,
                'api_key': self.api_key
            }
            ws.send(json.dumps(config))
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_open=on_open
        )
        
        # Run in separate thread
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        return ws
    
    def _prepare_data(self, data: Union[pd.DataFrame, List[Dict], str]) -> Dict[str, Any]:
        """Prepare data for API submission"""
        if isinstance(data, pd.DataFrame):
            return {
                'format': 'json',
                'content': data.to_dict('records')
            }
        elif isinstance(data, list):
            return {
                'format': 'json',
                'content': data
            }
        elif isinstance(data, str):
            return {
                'format': 'csv',
                'content': data
            }
        else:
            return {
                'format': 'json',
                'content': data
            }
    
    def _request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params, timeout=self.timeout)
            elif method == 'PUT':
                response = self.session.put(url, json=data, params=params, timeout=self.timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if not response.ok:
                try:
                    error_data = response.json()
                except:
                    error_data = {}
                
                raise AugmentAPIError(
                    error_data.get('message', f'HTTP {response.status_code}'),
                    response.status_code,
                    error_data
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise AugmentAPIError(f"Network error: {str(e)}", 0, {'original_error': str(e)})

class AugmentHelpers:
    """Helper functions for common industry use cases"""
    
    @staticmethod
    def analyze_automotive_sales(api_key: str, sales_data: pd.DataFrame) -> AnalysisResult:
        """Quick automotive sales analysis"""
        augment = AugmentAPI(api_key)
        return augment.analyze(
            sales_data,
            industry='automotive',
            insights=['sales_velocity', 'inventory_optimization', 'pricing_analysis']
        )
    
    @staticmethod
    def analyze_retail_inventory(api_key: str, inventory_data: pd.DataFrame) -> AnalysisResult:
        """Quick retail inventory analysis"""
        augment = AugmentAPI(api_key)
        return augment.analyze(
            inventory_data,
            industry='retail',
            insights=['demand_forecasting', 'stockout_prediction', 'category_performance']
        )
    
    @staticmethod
    def analyze_restaurant_performance(api_key: str, order_data: pd.DataFrame) -> AnalysisResult:
        """Quick restaurant performance analysis"""
        augment = AugmentAPI(api_key)
        return augment.analyze(
            order_data,
            industry='restaurant',
            insights=['menu_optimization', 'peak_hours', 'customer_preferences']
        )
    
    @staticmethod
    def analyze_fintech_users(api_key: str, user_data: pd.DataFrame) -> AnalysisResult:
        """Quick fintech user behavior analysis"""
        augment = AugmentAPI(api_key)
        return augment.analyze(
            user_data,
            industry='fintech',
            insights=['user_engagement', 'churn_prediction', 'feature_adoption']
        )

# Example usage
if __name__ == "__main__":
    # Initialize API
    augment = AugmentAPI('ak_live_your_secret_key')
    
    # Load sample data
    data = pd.read_csv('sample_data.csv')
    
    # Analyze with auto-detection
    result = augment.analyze(data)
    
    print(f"Detected Industry: {result.industry}")
    print(f"Confidence Score: {result.confidence_score}")
    print(f"Key Insights: {len(result.insights)}")
    
    for insight in result.insights:
        print(f"- {insight['title']}: {insight['description']}")
    
    print(f"\nRecommendations:")
    for rec in result.recommendations:
        print(f"- {rec}")
