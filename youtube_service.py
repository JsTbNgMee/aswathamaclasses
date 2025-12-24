"""
YouTube Channel Service
Fetches latest videos from a YouTube channel automatically
"""

import os
import requests
from datetime import datetime
from functools import lru_cache
import time

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY', '')
        self.channel_username = '@ASHWATHAMACLASSES'
        self.initialized = bool(self.api_key)
        self.cache_time = 0
        self.cached_videos = []
        self.cache_duration = 3600  # Cache for 1 hour
    
    def get_channel_id(self):
        """Get channel ID from username"""
        if not self.initialized:
            return None
        
        try:
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'q': self.channel_username,
                'type': 'channel',
                'key': self.api_key,
                'maxResults': 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    return data['items'][0]['snippet']['channelId']
        except Exception as e:
            print(f"⚠️ Error fetching channel ID: {e}")
        
        return None
    
    def get_latest_videos(self, max_results=10):
        """Fetch latest videos from the channel"""
        if not self.initialized:
            return []
        
        # Return cached if still fresh
        if self.cached_videos and (time.time() - self.cache_time) < self.cache_duration:
            return self.cached_videos
        
        try:
            channel_id = self.get_channel_id()
            if not channel_id:
                print("⚠️ Could not find YouTube channel")
                return []
            
            # Get uploads playlist
            url = 'https://www.googleapis.com/youtube/v3/channels'
            params = {
                'part': 'contentDetails',
                'id': channel_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                print("⚠️ Error fetching channel details")
                return []
            
            uploads_playlist_id = response.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            url = 'https://www.googleapis.com/youtube/v3/playlistItems'
            params = {
                'part': 'snippet,contentDetails',
                'playlistId': uploads_playlist_id,
                'key': self.api_key,
                'maxResults': max_results,
                'order': 'date'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                print("⚠️ Error fetching videos")
                return []
            
            videos = []
            for item in response.json().get('items', []):
                snippet = item['snippet']
                video_id = snippet['resourceId']['videoId']
                
                videos.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'description': snippet['description'][:200] + '...' if len(snippet['description']) > 200 else snippet['description'],
                    'thumbnail': snippet['thumbnails']['high']['url'],
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'published_at': snippet['publishedAt'],
                    'embed_url': f'https://www.youtube.com/embed/{video_id}'
                })
            
            # Cache the results
            self.cached_videos = videos
            self.cache_time = time.time()
            
            print(f"✓ Fetched {len(videos)} videos from YouTube channel")
            return videos
        
        except Exception as e:
            print(f"❌ YouTube API error: {e}")
            return []
    
    def is_configured(self):
        """Check if YouTube API is configured"""
        return self.initialized

# Initialize service globally
yt_service = YouTubeService()
