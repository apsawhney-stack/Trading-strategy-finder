"""
SQLite database setup with async SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Text, DateTime, Float, JSON, Boolean
from datetime import datetime

from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL logging
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class SourceDB(Base):
    """Database model for Source entities."""
    __tablename__ = "sources"
    
    id = Column(String(64), primary_key=True)
    url = Column(String(2048), unique=True, nullable=False, index=True)
    source_type = Column(String(20), nullable=False)
    title = Column(String(500), nullable=False)
    author = Column(String(200), nullable=False)
    published_date = Column(DateTime, nullable=True)
    
    # Raw content
    transcript_or_content = Column(Text, nullable=False)
    comment_content = Column(Text, nullable=True)
    
    # Platform metrics (stored as JSON)
    platform_metrics = Column(JSON, default=dict)
    market_context = Column(JSON, default=dict)
    
    # Extracted data (stored as JSON)
    extracted_data = Column(JSON, default=dict)
    quality_metrics = Column(JSON, default=dict)
    
    # Scores for quick filtering
    specificity_score = Column(Float, default=0.0, index=True)
    trust_score = Column(Float, default=0.0, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StrategyAggregateDB(Base):
    """Database model for aggregated strategy analysis."""
    __tablename__ = "strategy_aggregates"
    
    id = Column(String(64), primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    
    # Source IDs (stored as JSON list)
    source_ids = Column(JSON, default=list)
    
    # Consensus data (stored as JSON)
    consensus = Column(JSON, default=list)
    controversies = Column(JSON, default=list)
    gaps = Column(JSON, default=list)
    
    # Backtestability (stored as JSON)
    backtestability = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def init_db():
    """Initialize database and create tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
