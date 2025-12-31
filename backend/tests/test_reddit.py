"""
Unit tests for Reddit extractor.
Test cases TC-RD-001 through TC-RD-005.
"""

import pytest
from app.extractors.reddit import RedditExtractor


class TestRedditExtractor:
    """Test suite for RedditExtractor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = RedditExtractor()

    # TC-RD-001: Standard Reddit post URL
    def test_extract_post_id_standard_url(self):
        """Test post ID extraction from standard Reddit URL."""
        url = "https://www.reddit.com/r/thetagang/comments/abc123/my_strategy_post"
        post_id = self.extractor.extract_post_id(url)
        assert post_id == "abc123"

    # TC-RD-002: Old Reddit URL
    def test_extract_post_id_old_reddit(self):
        """Test post ID extraction from old.reddit.com URL."""
        url = "https://old.reddit.com/r/options/comments/def456/guide_to_spreads"
        post_id = self.extractor.extract_post_id(url)
        assert post_id == "def456"

    # TC-RD-003: Short redd.it URL
    def test_extract_post_id_short_url(self):
        """Test post ID extraction from redd.it short URL."""
        url = "https://redd.it/abc123"
        post_id = self.extractor.extract_post_id(url)
        assert post_id == "abc123"

    # TC-RD-004: URL without trailing slug
    def test_extract_post_id_no_slug(self):
        """Test post ID extraction without trailing title slug."""
        url = "https://www.reddit.com/r/thetagang/comments/xyz789"
        post_id = self.extractor.extract_post_id(url)
        assert post_id == "xyz789"

    # TC-RD-005: Invalid URL
    def test_extract_post_id_invalid_url(self):
        """Test that invalid URL returns None."""
        url = "https://youtube.com/watch?v=abc123"
        post_id = self.extractor.extract_post_id(url)
        assert post_id is None

    def test_validate_url_valid(self):
        """Test URL validation for valid Reddit URLs."""
        assert self.extractor.validate_url("https://www.reddit.com/r/thetagang/comments/abc123")
        assert self.extractor.validate_url("https://redd.it/abc123")

    def test_validate_url_invalid(self):
        """Test URL validation for invalid URLs."""
        assert not self.extractor.validate_url("https://youtube.com/watch?v=abc")
        assert not self.extractor.validate_url("not a url")
