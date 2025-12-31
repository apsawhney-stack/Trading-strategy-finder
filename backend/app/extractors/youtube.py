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
            # Fetch transcript using instance-based API (v1.2.x)
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            
            # Format transcript to plain text
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_list)
            
            # Extract video metadata (simplified - would need YouTube Data API for full metadata)
            title = f"YouTube Video {video_id}"  # Placeholder - enhance with YouTube Data API
            author = "Unknown"  # Placeholder
            
            # Run LLM extraction
            extracted_data = await extract_strategy_from_text(transcript_text)
            
            # Update title/author from extraction if available
            if extracted_data.trader_name.value:
                author = extracted_data.trader_name.value
            if extracted_data.strategy_name.value:
                title = f"{extracted_data.strategy_name.value} - {author}"
            
            return ExtractionResult(
                success=True,
                title=title,
                author=author,
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
