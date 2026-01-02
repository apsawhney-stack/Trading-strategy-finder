"""
Configuration settings for the application.
Loads from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Get absolute path for database
_BASE_DIR = Path(__file__).parent.parent
_DB_PATH = _BASE_DIR / "strategy_finder.db"


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Keys
    gemini_api_key: str = ""
    youtube_api_key: str = ""  # For YouTube Data API v3 live search
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "StrategyFinder/1.0"
    
    # Database - use absolute path
    database_url: str = f"sqlite+aiosqlite:///{_DB_PATH}"
    
    # Cache
    cache_dir: str = str(_BASE_DIR / "extraction_cache")
    cache_expiry_days: int = 7
    
    # LLM Settings
    gemini_model: str = "gemini-2.5-flash"
    max_transcript_tokens: int = 30000
    chunk_size: int = 5000
    chunk_overlap: int = 500
    
    # Rate Limiting
    max_extractions_per_minute: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
