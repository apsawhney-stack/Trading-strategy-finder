"""
Unit tests for Article extractor.
"""

import pytest
from app.extractors.article import ArticleExtractor


class TestArticleExtractor:
    """Test suite for ArticleExtractor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = ArticleExtractor()

    def test_validate_url_https(self):
        """Test validation of HTTPS URLs."""
        assert self.extractor.validate_url("https://example.com/article")
        assert self.extractor.validate_url("https://blog.tastytrade.com/strategy-guide")

    def test_validate_url_http(self):
        """Test validation of HTTP URLs."""
        assert self.extractor.validate_url("http://example.com/article")

    def test_validate_url_invalid(self):
        """Test that invalid URLs are rejected."""
        assert not self.extractor.validate_url("not-a-url")
        assert not self.extractor.validate_url("ftp://files.example.com")
        assert not self.extractor.validate_url("")

    def test_validate_url_youtube_passes(self):
        """YouTube URLs are technically valid HTTP URLs."""
        # Note: The router handles routing to correct extractor
        assert self.extractor.validate_url("https://youtube.com/watch?v=abc")
