"""
Base extractor class and factory function.
All extractors inherit from BaseExtractor.
"""

from abc import ABC, abstractmethod
from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime

from app.models import ExtractedStrategy, PlatformMetrics


class ExtractionResult(BaseModel):
    """Result from content extraction."""
    success: bool
    title: str = ""
    author: str = ""
    published_date: Optional[datetime] = None
    content: str = ""
    comment_content: Optional[str] = None
    platform_metrics: PlatformMetrics = PlatformMetrics()
    extracted_data: ExtractedStrategy = ExtractedStrategy()
    error: Optional[str] = None


class BaseExtractor(ABC):
    """Base class for all content extractors."""
    
    @abstractmethod
    async def extract(self, url: str) -> ExtractionResult:
        """Extract content from URL."""
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Check if URL is valid for this extractor."""
        pass


def get_extractor(source_type: Literal["youtube", "reddit", "article"]):
    """Factory function to get appropriate extractor."""
    from app.extractors.youtube import YouTubeExtractor
    from app.extractors.reddit import RedditExtractor
    from app.extractors.article import ArticleExtractor
    
    extractors = {
        "youtube": YouTubeExtractor(),
        "reddit": RedditExtractor(),
        "article": ArticleExtractor(),
    }
    
    return extractors.get(source_type, ArticleExtractor())
