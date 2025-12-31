"""
Reddit post and comment extractor.
Extracts posts and all comments using PRAW.
"""

import re
from typing import Optional
from datetime import datetime

from app.extractors.base import BaseExtractor, ExtractionResult
from app.models import PlatformMetrics
from app.extractors.llm import extract_strategy_from_text
from app.config import get_settings


class RedditExtractor(BaseExtractor):
    """Extractor for Reddit posts and comments."""
    
    # Regex patterns for Reddit URLs
    URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?reddit\.com/r/(\w+)/comments/(\w+)',
        r'(?:https?://)?(?:old\.)?reddit\.com/r/(\w+)/comments/(\w+)',
        r'(?:https?://)?redd\.it/(\w+)',
    ]
    
    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid Reddit URL."""
        return any(re.search(p, url) for p in self.URL_PATTERNS)
    
    def extract_post_id(self, url: str) -> Optional[str]:
        """Extract post ID from Reddit URL."""
        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, url)
            if match:
                # Handle redd.it short links (just ID)
                if "redd.it" in url:
                    return match.group(1)
                # Handle full URLs (subreddit, post_id)
                return match.group(2)
        return None
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract post content and comments from Reddit."""
        
        settings = get_settings()
        
        # Check if Reddit credentials are configured
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            return ExtractionResult(
                success=False,
                error="Reddit API credentials not configured. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
            )
        
        post_id = self.extract_post_id(url)
        if not post_id:
            return ExtractionResult(
                success=False,
                error="Invalid Reddit URL"
            )
        
        try:
            import praw
            
            # Initialize Reddit API client
            reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent,
            )
            
            # Fetch submission
            submission = reddit.submission(id=post_id)
            
            # Get post content
            title = submission.title
            author = str(submission.author) if submission.author else "[deleted]"
            post_body = submission.selftext or ""
            
            # Get all comments
            submission.comments.replace_more(limit=None)  # Expand all comment trees
            comments = []
            
            for comment in submission.comments.list():
                if hasattr(comment, 'body') and comment.body:
                    comment_author = str(comment.author) if comment.author else "[deleted]"
                    comment_score = comment.score if hasattr(comment, 'score') else 0
                    comments.append(f"[{comment_author} | +{comment_score}]: {comment.body}")
            
            comment_content = "\n\n---\n\n".join(comments)
            
            # Combine post + comments for extraction
            full_content = f"# {title}\n\n{post_body}\n\n## Comments\n\n{comment_content}"
            
            # Run LLM extraction
            extracted_data = await extract_strategy_from_text(full_content)
            
            # Get published date
            published_date = datetime.fromtimestamp(submission.created_utc)
            
            return ExtractionResult(
                success=True,
                title=title,
                author=author,
                published_date=published_date,
                content=post_body,
                comment_content=comment_content,
                platform_metrics=PlatformMetrics(
                    upvotes=submission.score,
                    comments=submission.num_comments,
                ),
                extracted_data=extracted_data,
            )
            
        except Exception as e:
            error_msg = str(e)
            
            if "404" in error_msg or "not found" in error_msg.lower():
                error_msg = "Reddit post not found (deleted or private)"
            elif "403" in error_msg:
                error_msg = "Access denied - check Reddit API credentials"
            
            return ExtractionResult(
                success=False,
                error=error_msg
            )
