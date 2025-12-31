"""
Unit tests for YouTube extractor.
Test cases TC-YT-001 through TC-YT-005.
"""

import pytest
from app.extractors.youtube import YouTubeExtractor


class TestYouTubeExtractor:
    """Test suite for YouTubeExtractor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = YouTubeExtractor()

    # TC-YT-001: Standard YouTube URL
    def test_extract_video_id_standard_url(self):
        """Test video ID extraction from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    # TC-YT-002: Shortened URL
    def test_extract_video_id_shortened_url(self):
        """Test video ID extraction from youtu.be URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    # TC-YT-003: Embed URL
    def test_extract_video_id_embed_url(self):
        """Test video ID extraction from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    # TC-YT-004: URL with additional parameters
    def test_extract_video_id_with_params(self):
        """Test video ID extraction from URL with extra params."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    # TC-YT-005: Invalid URL
    def test_extract_video_id_invalid_url(self):
        """Test that invalid URL returns None."""
        url = "https://example.com/video"
        video_id = self.extractor.extract_video_id(url)
        assert video_id is None

    def test_validate_url_valid(self):
        """Test URL validation for valid YouTube URLs."""
        assert self.extractor.validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert self.extractor.validate_url("https://youtu.be/dQw4w9WgXcQ")

    def test_validate_url_invalid(self):
        """Test URL validation for invalid URLs."""
        assert not self.extractor.validate_url("https://reddit.com/r/options")
        assert not self.extractor.validate_url("not a url")
