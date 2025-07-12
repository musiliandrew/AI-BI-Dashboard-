"""
Social Media Platform API Integrations
"""
import requests
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SocialMetrics:
    """Standard metrics across all platforms"""
    followers: int = 0
    following: int = 0
    posts: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    engagement_rate: float = 0.0

@dataclass
class PostData:
    """Standard post data structure"""
    platform_id: str
    content: str
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    metrics: SocialMetrics
    posted_at: datetime
    post_url: str = ""

class BasePlatformAPI:
    """Base class for all social media platform APIs"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.rate_limit_remaining = 100
        self.rate_limit_reset = time.time() + 3600
    
    def _handle_rate_limit(self):
        """Handle rate limiting across platforms"""
        if self.rate_limit_remaining <= 1:
            sleep_time = max(0, self.rate_limit_reset - time.time())
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get basic account information"""
        raise NotImplementedError
    
    def get_posts(self, limit: int = 50, since: datetime = None) -> List[PostData]:
        """Get recent posts"""
        raise NotImplementedError
    
    def get_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """Get comments for a specific post"""
        raise NotImplementedError
    
    def search_mentions(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for mentions of brand/keywords"""
        raise NotImplementedError

class InstagramAPI(BasePlatformAPI):
    """Instagram Basic Display API and Instagram Graph API integration"""
    
    def __init__(self, access_token: str):
        super().__init__(access_token)
        self.base_url = "https://graph.instagram.com"
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Instagram account information"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/me"
        params = {
            'fields': 'id,username,account_type,media_count,followers_count,follows_count',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API error: {e}")
            return {}
    
    def get_posts(self, limit: int = 50, since: datetime = None) -> List[PostData]:
        """Get Instagram posts"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/me/media"
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
            'limit': min(limit, 100),  # Instagram limit
            'access_token': self.access_token
        }
        
        if since:
            params['since'] = int(since.timestamp())
        
        posts = []
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('data', []):
                # Extract hashtags and mentions from caption
                caption = item.get('caption', '')
                hashtags = [tag.strip('#') for tag in caption.split() if tag.startswith('#')]
                mentions = [mention.strip('@') for mention in caption.split() if mention.startswith('@')]
                
                post = PostData(
                    platform_id=item['id'],
                    content=caption,
                    media_urls=[item.get('media_url', '')],
                    hashtags=hashtags,
                    mentions=mentions,
                    metrics=SocialMetrics(
                        likes=item.get('like_count', 0),
                        comments=item.get('comments_count', 0)
                    ),
                    posted_at=datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')),
                    post_url=item.get('permalink', '')
                )
                posts.append(post)
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram posts API error: {e}")
            return []
    
    def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Get detailed insights for a specific post"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/{post_id}/insights"
        params = {
            'metric': 'impressions,reach,engagement,saves,profile_visits',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram insights API error: {e}")
            return {}

class TwitterAPI(BasePlatformAPI):
    """Twitter API v2 integration"""
    
    def __init__(self, bearer_token: str):
        super().__init__(bearer_token)
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
    
    def get_account_info(self, username: str) -> Dict[str, Any]:
        """Get Twitter account information"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/users/by/username/{username}"
        params = {
            'user.fields': 'id,name,username,description,public_metrics,verified,location,created_at'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter API error: {e}")
            return {}
    
    def get_posts(self, user_id: str, limit: int = 50, since: datetime = None) -> List[PostData]:
        """Get Twitter tweets"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/users/{user_id}/tweets"
        params = {
            'tweet.fields': 'id,text,created_at,public_metrics,context_annotations,entities',
            'max_results': min(limit, 100),  # Twitter limit
            'exclude': 'retweets,replies'
        }
        
        if since:
            params['start_time'] = since.isoformat()
        
        posts = []
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            for tweet in data.get('data', []):
                # Extract hashtags and mentions
                entities = tweet.get('entities', {})
                hashtags = [tag['tag'] for tag in entities.get('hashtags', [])]
                mentions = [mention['username'] for mention in entities.get('mentions', [])]
                
                metrics = tweet.get('public_metrics', {})
                post = PostData(
                    platform_id=tweet['id'],
                    content=tweet['text'],
                    media_urls=[],  # Would need additional API call for media
                    hashtags=hashtags,
                    mentions=mentions,
                    metrics=SocialMetrics(
                        likes=metrics.get('like_count', 0),
                        comments=metrics.get('reply_count', 0),
                        shares=metrics.get('retweet_count', 0),
                        views=metrics.get('impression_count', 0)
                    ),
                    posted_at=datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00')),
                    post_url=f"https://twitter.com/user/status/{tweet['id']}"
                )
                posts.append(post)
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter posts API error: {e}")
            return []
    
    def search_mentions(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for mentions on Twitter"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/tweets/search/recent"
        params = {
            'query': query,
            'tweet.fields': 'id,text,created_at,public_metrics,author_id,context_annotations',
            'user.fields': 'id,name,username,verified',
            'expansions': 'author_id',
            'max_results': min(limit, 100)
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter search API error: {e}")
            return {}

class FacebookAPI(BasePlatformAPI):
    """Facebook Graph API integration"""
    
    def __init__(self, access_token: str):
        super().__init__(access_token)
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_page_info(self, page_id: str) -> Dict[str, Any]:
        """Get Facebook page information"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/{page_id}"
        params = {
            'fields': 'id,name,username,category,fan_count,followers_count,engagement,verification_status',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API error: {e}")
            return {}
    
    def get_posts(self, page_id: str, limit: int = 50, since: datetime = None) -> List[PostData]:
        """Get Facebook page posts"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/{page_id}/posts"
        params = {
            'fields': 'id,message,created_time,permalink_url,attachments,reactions.summary(true),comments.summary(true),shares',
            'limit': min(limit, 100),
            'access_token': self.access_token
        }
        
        if since:
            params['since'] = int(since.timestamp())
        
        posts = []
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('data', []):
                message = item.get('message', '')
                hashtags = [tag.strip('#') for tag in message.split() if tag.startswith('#')]
                mentions = [mention.strip('@') for mention in message.split() if mention.startswith('@')]
                
                reactions = item.get('reactions', {}).get('summary', {}).get('total_count', 0)
                comments = item.get('comments', {}).get('summary', {}).get('total_count', 0)
                shares = item.get('shares', {}).get('count', 0)
                
                post = PostData(
                    platform_id=item['id'],
                    content=message,
                    media_urls=[],  # Would extract from attachments
                    hashtags=hashtags,
                    mentions=mentions,
                    metrics=SocialMetrics(
                        likes=reactions,
                        comments=comments,
                        shares=shares
                    ),
                    posted_at=datetime.fromisoformat(item['created_time'].replace('Z', '+00:00')),
                    post_url=item.get('permalink_url', '')
                )
                posts.append(post)
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook posts API error: {e}")
            return []

class LinkedInAPI(BasePlatformAPI):
    """LinkedIn API integration"""
    
    def __init__(self, access_token: str):
        super().__init__(access_token)
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_profile_info(self) -> Dict[str, Any]:
        """Get LinkedIn profile information"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/people/~"
        params = {
            'projection': '(id,firstName,lastName,headline,numConnections,numConnectionsRange)'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn API error: {e}")
            return {}

class TikTokAPI(BasePlatformAPI):
    """TikTok Business API integration"""
    
    def __init__(self, access_token: str):
        super().__init__(access_token)
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        self.headers = {
            'Access-Token': access_token,
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get TikTok user information"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/user/info/"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TikTok API error: {e}")
            return {}

class YouTubeAPI(BasePlatformAPI):
    """YouTube Data API integration"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get YouTube channel information"""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics,brandingSettings',
            'id': channel_id,
            'key': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API error: {e}")
            return {}
    
    def get_videos(self, channel_id: str, limit: int = 50) -> List[PostData]:
        """Get YouTube videos"""
        self._handle_rate_limit()
        
        # First get the uploads playlist ID
        channel_info = self.get_channel_info(channel_id)
        if not channel_info.get('items'):
            return []
        
        uploads_playlist = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        url = f"{self.base_url}/playlistItems"
        params = {
            'part': 'snippet',
            'playlistId': uploads_playlist,
            'maxResults': min(limit, 50),
            'key': self.access_token
        }
        
        posts = []
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items', []):
                snippet = item['snippet']
                video_id = snippet['resourceId']['videoId']
                
                # Get video statistics
                stats = self._get_video_statistics(video_id)
                
                post = PostData(
                    platform_id=video_id,
                    content=snippet['title'] + '\n' + snippet.get('description', ''),
                    media_urls=[f"https://www.youtube.com/watch?v={video_id}"],
                    hashtags=[],  # Would extract from description
                    mentions=[],
                    metrics=SocialMetrics(
                        likes=stats.get('likeCount', 0),
                        comments=stats.get('commentCount', 0),
                        views=stats.get('viewCount', 0)
                    ),
                    posted_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                    post_url=f"https://www.youtube.com/watch?v={video_id}"
                )
                posts.append(post)
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube videos API error: {e}")
            return []
    
    def _get_video_statistics(self, video_id: str) -> Dict[str, int]:
        """Get statistics for a specific video"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                stats = data['items'][0]['statistics']
                return {
                    'viewCount': int(stats.get('viewCount', 0)),
                    'likeCount': int(stats.get('likeCount', 0)),
                    'commentCount': int(stats.get('commentCount', 0))
                }
            
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"YouTube statistics API error: {e}")
        
        return {}

# Factory function to get the right API client
def get_platform_api(platform: str, credentials: Dict[str, str]) -> BasePlatformAPI:
    """Factory function to get the appropriate API client"""
    
    api_classes = {
        'instagram': InstagramAPI,
        'twitter': TwitterAPI,
        'facebook': FacebookAPI,
        'linkedin': LinkedInAPI,
        'tiktok': TikTokAPI,
        'youtube': YouTubeAPI,
    }
    
    if platform not in api_classes:
        raise ValueError(f"Unsupported platform: {platform}")
    
    api_class = api_classes[platform]
    
    # Different platforms use different credential keys
    if platform == 'twitter':
        return api_class(credentials.get('bearer_token'))
    elif platform == 'youtube':
        return api_class(credentials.get('api_key'))
    else:
        return api_class(credentials.get('access_token'))
