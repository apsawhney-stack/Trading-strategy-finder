"""
Article/webpage content extractor.
Extracts main content from web pages using BeautifulSoup.
"""

import re
from typing import Optional
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.extractors.base import BaseExtractor, ExtractionResult
from app.models import PlatformMetrics
from app.extractors.llm import extract_strategy_from_text


class ArticleExtractor(BaseExtractor):
    """Extractor for web articles and blog posts."""
    
    # Headers to mimic a real browser
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    # Content selectors to try (in order of priority)
    CONTENT_SELECTORS = [
        "article",
        "main",
        "[role='main']",
        ".post-content",
        ".article-content",
        ".entry-content",
        ".content",
        "#content",
        ".post-body",
        ".blog-post",
    ]
    
    # Elements to remove (noise)
    NOISE_SELECTORS = [
        "nav",
        "header",
        "footer",
        "aside",
        ".sidebar",
        ".comments",
        ".advertisement",
        ".ad",
        "script",
        "style",
        "noscript",
    ]
    
    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid HTTP/HTTPS URL."""
        try:
            result = urlparse(url)
            return result.scheme in ("http", "https") and bool(result.netloc)
        except Exception:
            return False
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Try to extract author from page."""
        # Try common author patterns
        author_selectors = [
            "[rel='author']",
            ".author",
            ".byline",
            "[itemprop='author']",
            "meta[name='author']",
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == "meta":
                    return element.get("content", "Unknown")
                return element.get_text(strip=True)
        
        return "Unknown"
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Try to extract publication date from page."""
        # Try common date patterns
        date_selectors = [
            "time[datetime]",
            "[itemprop='datePublished']",
            "meta[property='article:published_time']",
            ".date",
            ".published",
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get("datetime") or element.get("content") or element.get_text(strip=True)
                try:
                    # Try ISO format
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    pass
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try og:title first
        og_title = soup.select_one("meta[property='og:title']")
        if og_title:
            return og_title.get("content", "")
        
        # Try h1
        h1 = soup.select_one("h1")
        if h1:
            return h1.get_text(strip=True)
        
        # Fall back to title tag
        title = soup.select_one("title")
        if title:
            return title.get_text(strip=True)
        
        return "Unknown Article"
    
    def _clean_content(self, soup: BeautifulSoup) -> str:
        """Extract and clean main content."""
        # Remove noise elements
        for selector in self.NOISE_SELECTORS:
            for element in soup.select(selector):
                element.decompose()
        
        # Try to find main content
        for selector in self.CONTENT_SELECTORS:
            content = soup.select_one(selector)
            if content:
                return content.get_text(separator="\n", strip=True)
        
        # Fall back to body
        body = soup.select_one("body")
        if body:
            return body.get_text(separator="\n", strip=True)
        
        return ""
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract content from article URL."""
        
        if not self.validate_url(url):
            return ExtractionResult(
                success=False,
                error="Invalid URL format"
            )
        
        try:
            # Fetch page
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "lxml")
            
            # Extract metadata
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            date = self._extract_date(soup)
            
            # Extract content
            content = self._clean_content(soup)
            
            if not content or len(content) < 100:
                return ExtractionResult(
                    success=False,
                    error="Could not extract meaningful content from page"
                )
            
            # Run LLM extraction
            extracted_data = await extract_strategy_from_text(content)
            
            return ExtractionResult(
                success=True,
                title=title,
                author=author,
                published_date=date,
                content=content,
                platform_metrics=PlatformMetrics(),
                extracted_data=extracted_data,
            )
            
        except requests.exceptions.Timeout:
            return ExtractionResult(
                success=False,
                error="Request timed out"
            )
        except requests.exceptions.HTTPError as e:
            return ExtractionResult(
                success=False,
                error=f"HTTP error: {e.response.status_code}"
            )
        except Exception as e:
            return ExtractionResult(
                success=False,
                error=f"Failed to extract article: {str(e)}"
            )
