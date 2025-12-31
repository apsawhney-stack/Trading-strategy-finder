"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import Generator

from app.config import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with mock values."""
    return Settings(
        gemini_api_key="test_key",
        reddit_client_id="test_id",
        reddit_client_secret="test_secret",
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest.fixture
def sample_youtube_urls() -> list[str]:
    """Sample YouTube URLs for testing."""
    return [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
    ]


@pytest.fixture
def sample_reddit_urls() -> list[str]:
    """Sample Reddit URLs for testing."""
    return [
        "https://www.reddit.com/r/thetagang/comments/abc123/my_strategy",
        "https://old.reddit.com/r/options/comments/def456/pcs_guide",
        "https://redd.it/abc123",
    ]


@pytest.fixture
def sample_transcript() -> str:
    """Sample transcript for LLM testing."""
    return """
    Today I want to talk about my SPX put credit spread strategy.
    I typically go 30 to 45 days to expiration, targeting the 16 delta strike.
    My profit target is 50% of the credit received.
    For stop loss, I use 100% of the credit, so 2x the credit.
    I roll at 21 DTE if the position is challenged.
    Last year I made about $12,000 starting from $3,200.
    The strategy can fail when there's a gap down overnight.
    """


@pytest.fixture
def sample_extracted_strategy() -> dict:
    """Sample extracted strategy data."""
    return {
        "strategy_name": {"value": "Put Credit Spread", "confidence": 0.95, "interpretation": "explicit"},
        "setup_rules": {
            "underlying": {"value": "SPX", "confidence": 0.9, "interpretation": "explicit"},
            "dte": {"value": 30, "value_range": [30, 45], "confidence": 0.95, "interpretation": "explicit"},
            "delta": {"value": 0.16, "confidence": 0.9, "interpretation": "explicit"},
        },
        "management_rules": {
            "profit_target": {"value": "50%", "confidence": 0.95, "interpretation": "explicit"},
            "stop_loss": {"value": "100% of credit", "confidence": 0.9, "interpretation": "explicit"},
        },
        "failure_analysis": {
            "failure_modes_mentioned": ["gap down overnight"],
            "discusses_losses": True,
            "bias_detected": False,
        },
    }
