"""
YouTube Live Search using YouTube Data API v3.
Searches for options trading strategy videos with quality scoring.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.discovery.trusted_channels import TRUSTED_YOUTUBE_CHANNELS, TRUSTED_CHANNEL_BOOST


class YouTubeSearchClient:
    """Client for YouTube Data API v3 search and video statistics."""
    
    def __init__(self, api_key: Optional[str] = None):
        # Get API key from app settings (which loads .env)
        if api_key is None:
            from app.config import get_settings
            settings = get_settings()
            api_key = settings.youtube_api_key
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not set")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        
        # Search parameters based on design doc
        self.max_results = 15
        self.max_video_age_years = 2
        self.max_video_duration_minutes = 60
    
    def _get_published_after(self) -> str:
        """Get ISO 8601 date for max video age filter."""
        cutoff = datetime.now() - timedelta(days=self.max_video_age_years * 365)
        return cutoff.strftime("%Y-%m-%dT00:00:00Z")
    
    def search(self, query: str) -> List[dict]:
        """
        Search YouTube for options trading videos.
        
        Args:
            query: User's search query (e.g., "iron condor SPX")
            
        Returns:
            List of video candidates with quality scores
        """
        try:
            # Step 1: Search for videos
            search_query = f"{query} options trading"
            
            search_response = self.youtube.search().list(
                q=search_query,
                part="snippet",
                type="video",
                maxResults=self.max_results,
                order="relevance",
                publishedAfter=self._get_published_after(),
                relevanceLanguage="en",
                videoCaption="closedCaption",  # Must have captions for extraction
                videoDuration="medium",  # 4-20 minutes (we'll also accept long)
            ).execute()
            
            if not search_response.get("items"):
                return []
            
            # Extract video IDs
            video_ids = [item["id"]["videoId"] for item in search_response["items"]]
            
            # Step 2: Get video statistics
            videos_response = self.youtube.videos().list(
                id=",".join(video_ids),
                part="snippet,statistics,contentDetails"
            ).execute()
            
            # Step 3: Get channel statistics for subscriber counts
            channel_ids = list(set(
                item["snippet"]["channelId"] 
                for item in videos_response.get("items", [])
            ))
            
            channels_response = self.youtube.channels().list(
                id=",".join(channel_ids),
                part="statistics"
            ).execute()
            
            # Build channel stats lookup
            channel_stats = {
                ch["id"]: ch.get("statistics", {})
                for ch in channels_response.get("items", [])
            }
            
            # Step 4: Score and format results
            candidates = []
            for video in videos_response.get("items", []):
                snippet = video["snippet"]
                stats = video.get("statistics", {})
                channel_id = snippet["channelId"]
                
                # Calculate quality score
                score = self._calculate_quality_score(
                    video_stats=stats,
                    channel_stats=channel_stats.get(channel_id, {}),
                    channel_id=channel_id,
                    duration=video.get("contentDetails", {}).get("duration", "")
                )
                
                # Determine quality tier
                if score >= 70:
                    tier = "high"
                elif score >= 40:
                    tier = "medium"
                else:
                    tier = "low"
                
                candidates.append({
                    "url": f"https://www.youtube.com/watch?v={video['id']}",
                    "title": snippet["title"],
                    "author": snippet["channelTitle"],
                    "source_type": "youtube",
                    "quality_tier": tier,
                    "quality_score": score,
                    "quality_signals": self._get_quality_signals(stats, channel_stats.get(channel_id, {})),
                    "metrics": {
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                    },
                    "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "published_at": snippet.get("publishedAt", ""),
                })
            
            # Sort by quality score
            candidates.sort(key=lambda x: x["quality_score"], reverse=True)
            
            return candidates
            
        except HttpError as e:
            if e.resp.status == 403:
                # Quota exceeded or API key issue
                raise Exception("YouTube API quota exceeded or invalid API key")
            raise Exception(f"YouTube API error: {str(e)}")
        except Exception as e:
            raise Exception(f"YouTube search failed: {str(e)}")
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        # Format: PT#H#M#S (e.g., PT1H30M45S, PT15M30S, PT45S)
        import re
        
        hours = 0
        minutes = 0
        seconds = 0
        
        hour_match = re.search(r'(\d+)H', duration)
        if hour_match:
            hours = int(hour_match.group(1))
        
        min_match = re.search(r'(\d+)M', duration)
        if min_match:
            minutes = int(min_match.group(1))
        
        sec_match = re.search(r'(\d+)S', duration)
        if sec_match:
            seconds = int(sec_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _calculate_quality_score(
        self,
        video_stats: dict,
        channel_stats: dict,
        channel_id: str,
        duration: str
    ) -> int:
        """
        Calculate quality score (0-100) based on video and channel metrics.
        """
        score = 0
        
        # View count (0-30 points)
        views = int(video_stats.get("viewCount", 0))
        if views > 100000:
            score += 30
        elif views > 50000:
            score += 25
        elif views > 10000:
            score += 20
        elif views > 5000:
            score += 15
        elif views > 1000:
            score += 10
        
        # Channel subscribers (0-25 points)
        subs = int(channel_stats.get("subscriberCount", 0))
        if subs > 100000:
            score += 25
        elif subs > 50000:
            score += 20
        elif subs > 10000:
            score += 15
        elif subs > 5000:
            score += 10
        
        # Like ratio (0-15 points)
        likes = int(video_stats.get("likeCount", 0))
        # Note: dislikeCount is no longer public, assume good ratio if likes exist
        if likes > 1000:
            score += 15
        elif likes > 500:
            score += 12
        elif likes > 100:
            score += 8
        elif likes > 50:
            score += 5
        
        # Trusted channel boost (0-20 points)
        trusted_ids = list(TRUSTED_YOUTUBE_CHANNELS.values())
        if channel_id in trusted_ids:
            score += TRUSTED_CHANNEL_BOOST
        
        # Video length bonus (0-10 points)
        duration_seconds = self._parse_duration(duration)
        if 8 * 60 <= duration_seconds <= 30 * 60:  # 8-30 minutes - ideal
            score += 10
        elif duration_seconds <= 60 * 60:  # Under 1 hour - acceptable
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def _get_quality_signals(self, video_stats: dict, channel_stats: dict) -> List[str]:
        """Generate human-readable quality signals."""
        signals = []
        
        views = int(video_stats.get("viewCount", 0))
        if views > 10000:
            signals.append(f"{views:,} views")
        
        subs = int(channel_stats.get("subscriberCount", 0))
        if subs > 10000:
            signals.append(f"{subs:,} subscribers")
        
        likes = int(video_stats.get("likeCount", 0))
        if likes > 100:
            signals.append(f"{likes:,} likes")
        
        return signals if signals else ["No quality signals"]


# Singleton instance
_client: Optional[YouTubeSearchClient] = None


def get_youtube_client() -> YouTubeSearchClient:
    """Get or create YouTube search client singleton."""
    global _client
    if _client is None:
        _client = YouTubeSearchClient()
    return _client


async def search_youtube(query: str) -> List[dict]:
    """
    Search YouTube for options trading videos.
    Runs the synchronous Google API in a thread pool.
    
    Args:
        query: User's search query
        
    Returns:
        List of video candidates with quality scores
    """
    import asyncio
    client = get_youtube_client()
    
    # Run synchronous Google API call in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, client.search, query)

