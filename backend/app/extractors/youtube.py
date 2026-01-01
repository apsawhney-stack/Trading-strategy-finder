"""
YouTube transcript extractor.
Extracts video metadata and transcript using youtube-transcript-api.
"""

import re
from typing import Optional
from datetime import datetime

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from app.extractors.base import BaseExtractor, ExtractionResult
from app.models import PlatformMetrics
from app.extractors.llm import extract_strategy_from_text


class YouTubeExtractor(BaseExtractor):
    """Extractor for YouTube video transcripts."""
    
    # Regex patterns for YouTube URLs
    URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL."""
        return self.extract_video_id(url) is not None
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_video_metadata(self, video_id: str) -> dict:
        """Fetch video metadata (title, channel) from YouTube oEmbed API."""
        import aiohttp
        
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(oembed_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "title": data.get("title", f"YouTube Video {video_id}"),
                            "author": data.get("author_name", "Unknown Channel"),
                            "author_url": data.get("author_url", ""),
                        }
        except Exception:
            pass
        
        return {
            "title": f"YouTube Video {video_id}",
            "author": "Unknown Channel",
            "author_url": "",
        }
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract transcript and strategy from YouTube video."""
        
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return ExtractionResult(
                success=False,
                error="Invalid YouTube URL"
            )
        
        try:
            # Fetch real metadata (channel name, video title)
            metadata = await self.get_video_metadata(video_id)
            channel_name = metadata["author"]
            video_title = metadata["title"]
            
            # Fetch transcript using instance-based API (v1.2.x)
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            
            # Format transcript to plain text
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_list)
            
            # Run LLM extraction
            extracted_data = await extract_strategy_from_text(transcript_text)
            
            # Build display title - use strategy name if extracted, else video title
            if extracted_data.strategy_name.value:
                title = extracted_data.strategy_name.value
            else:
                title = video_title
            
            return ExtractionResult(
                success=True,
                title=title,
                author=channel_name,  # Use actual YouTube channel name
                content=transcript_text,
                platform_metrics=PlatformMetrics(),  # Would need YouTube Data API
                extracted_data=extracted_data,
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle common errors
            if "disabled" in error_msg.lower():
                error_msg = "Transcripts are disabled for this video"
            elif "no transcript" in error_msg.lower():
                error_msg = "No transcript available for this video"
            elif "video unavailable" in error_msg.lower():
                error_msg = "Video is unavailable (private, deleted, or restricted)"
            
            return ExtractionResult(
                success=False,
                error=error_msg
            )
