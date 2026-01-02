"""
YouTube Live Search using YouTube Data API v3.
Searches for options trading strategy videos with quality scoring.
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.discovery.trusted_channels import TRUSTED_YOUTUBE_CHANNELS, TRUSTED_CHANNEL_BOOST


# ============================================================================
# Strategy Keywords Configuration - Used to filter noise from search results
# ============================================================================

STRATEGY_KEYWORDS = {
    # High signal keywords indicate specific, actionable strategy content (+15 points each)
    "high_signal": [
        # DTE patterns
        "dte", "0dte", "0 dte", "1dte", "2dte", "3dte", "5dte", "7 dte", 
        "14 dte", "21 dte", "30 dte", "45 dte", "expiration", "weeklies", "monthlies",
        # Delta patterns
        "delta", "10 delta", "16 delta", "20 delta", "25 delta", "30 delta",
        ".10 delta", ".16 delta", ".20 delta", ".25 delta", ".30 delta", "delta neutral",
        # Strategy structure
        "strike", "strike width", "spread", "condor", "butterfly", "vertical",
        "5 wide", "10 wide", "5 point", "10 point", "narrow spread", "wide spread",
        "credit", "debit", "premium", "atm", "otm", "itm",
        # Entry criteria
        "entry rules", "entry criteria", "when to enter", "setup", "trade setup", "entry signal",
        # Exit/Management
        "profit target", "stop loss", "take profit", "exit rules", "close at",
        "roll", "roll up", "roll down", "roll out", "adjustment", "manage", 
        "manage losers", "defend",
        # Position sizing
        "position size", "risk per trade", "buying power", "account size", 
        "allocation", "max loss", "risk management", "bp usage", "buying power reduction",
        # Backtest/Evidence
        "backtest", "backtested", "historical", "win rate", "success rate", 
        "expectancy", "pnl", "track record",
        # Greeks
        "gamma", "theta decay", "vega", "rho", "iv", "implied volatility", 
        "iv rank", "iv percentile",
    ],
    
    # Medium signal keywords indicate strategy-related content (+8 points each)
    "medium_signal": [
        # Spread strategies
        "put credit spread", "call credit spread", "bull put spread", "bear call spread",
        "bull call spread", "bear put spread", "iron condor", "iron fly", "iron butterfly",
        "calendar spread", "diagonal spread", "broken wing butterfly", "jade lizard",
        "big lizard", "ratio spread", "back spread", "front spread", "skip strike butterfly",
        # Other strategies
        "wheel strategy", "covered call", "cash secured put", "protective put",
        "strangle", "straddle", "pmcc", "poor mans covered call", "zebraspread",
        "naked put", "naked call", "short put", "short call",
        "defined risk", "undefined risk",
        # Greeks
        "theta", "gamma", "vega",
        # Income focus
        "sell premium", "collect premium", "income strategy", "weekly income", 
        "monthly income", "consistent income",
        "weekly options", "monthly options",
        # Underlyings
        "spx", "spy", "qqq", "iwm", "ndx", "rut", "vix",
        "futures options", "/es", "/nq", "emini",
        # Trusted sources
        "tastytrade", "tasty", "option alpha", "tastylive",
        "sky view trading", "smb capital", "inthemoney", "projectoption", "kamikaze cash",
        # Platforms
        "thinkorswim", "tos", "tastyworks", "schwab", "ibkr", "interactive brokers",
    ],
    
    # Noise patterns indicate non-strategy content (-15 points each)
    "noise_patterns": [
        # Personal stories
        "interview", "my journey", "how i started", "my story", "my first",
        "i made", "i lost", "blew up", "account blowup", "day in my life",
        "meet my", "how i became", "success story", "full time trader", "quit my job",
        # Market commentary (not strategy)
        "market update", "market news", "breaking news", "market prediction",
        "stock picks", "earnings play",
        # Reaction/entertainment content
        "reaction", "reacting to", "day in the life", "vlog", "lifestyle",
        # Beginner/educational (too basic)
        "what is a", "what are", "explained simply", "explained in 5 minutes",
        "for beginners", "beginner guide", "basics of", "beginner mistake",
        "simple trick", "one simple", "avoid this", "why you're losing", "stop doing this",
        # Clickbait phrases
        "you won't believe", "secret", "shocking", "this will change your life",
        "must watch", "watch now", "don't miss", "insane", "crazy", "gamechanger",
        # Hype/unrealistic promises
        "millionaire", "get rich", "easy money", "get rich quick", "overnight",
        "100% win rate", "never lose", "guaranteed", "free money", 
        "unlimited profit", "passive income trick",
        # Meme/gambling content
        "meme stock", "wsb", "wallstreetbets", "yolo", "to the moon",
        # Meta content (not focused on strategy)
        "q&a", "ask me anything", "ama", "subscriber question", "community post",
    ],
}

# Minimum content score to include in results (others are filtered out)
MIN_CONTENT_SCORE = -10  # Set negative to be lenient, increase to be stricter


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
                
                # Calculate content score (keyword-based filtering)
                title = snippet.get("title", "")
                description = snippet.get("description", "")
                content_score, content_signals = self._calculate_content_score(title, description)
                
                # Skip videos with very low content score (noise)
                if content_score < MIN_CONTENT_SCORE:
                    continue
                
                # Calculate quality score (metrics-based)
                quality_score = self._calculate_quality_score(
                    video_stats=stats,
                    channel_stats=channel_stats.get(channel_id, {}),
                    channel_id=channel_id,
                    duration=video.get("contentDetails", {}).get("duration", "")
                )
                
                # Combined score: quality + content bonus
                combined_score = quality_score + min(content_score, 20)  # Cap content bonus at 20
                
                # Determine quality tier based on combined score
                if combined_score >= 70:
                    tier = "high"
                elif combined_score >= 40:
                    tier = "medium"
                else:
                    tier = "low"
                
                # Get quality signals and add content signals
                quality_signals = self._get_quality_signals(stats, channel_stats.get(channel_id, {}))
                if content_signals:
                    quality_signals.extend(content_signals)
                
                candidates.append({
                    "url": f"https://www.youtube.com/watch?v={video['id']}",
                    "title": snippet["title"],
                    "author": snippet["channelTitle"],
                    "source_type": "youtube",
                    "quality_tier": tier,
                    "quality_score": combined_score,
                    "content_score": content_score,
                    "quality_signals": quality_signals,
                    "metrics": {
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                    },
                    "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "published_at": snippet.get("publishedAt", ""),
                })
            
            # Sort by combined quality score
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
    
    def _calculate_content_score(self, title: str, description: str) -> tuple[int, List[str]]:
        """
        Calculate content relevance score based on keywords in title/description.
        
        Returns:
            Tuple of (score, signals) where:
            - score: Integer score (can be negative for noise)
            - signals: List of human-readable signals found
        """
        text = f"{title} {description}".lower()
        score = 0
        signals = []
        
        # Check for high signal keywords (+15 each)
        high_signals_found = 0
        for keyword in STRATEGY_KEYWORDS["high_signal"]:
            if keyword.lower() in text:
                score += 15
                high_signals_found += 1
                if high_signals_found <= 2:  # Only add first 2 as signals to avoid clutter
                    signals.append(f"📍 {keyword}")
        
        # Check for medium signal keywords (+8 each)
        medium_signals_found = 0
        for keyword in STRATEGY_KEYWORDS["medium_signal"]:
            if keyword.lower() in text:
                score += 8
                medium_signals_found += 1
                if medium_signals_found <= 2 and high_signals_found == 0:
                    signals.append(f"✓ {keyword}")
        
        # Check for noise patterns (-15 each)
        for pattern in STRATEGY_KEYWORDS["noise_patterns"]:
            if pattern.lower() in text:
                score -= 15
                signals.append(f"⚠️ {pattern}")
        
        return score, signals
    
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

