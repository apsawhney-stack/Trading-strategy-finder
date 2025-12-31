"""
Unit tests for the sources API endpoints.
Tests CRUD operations for source persistence.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app
from app.db.database import SourceDB, Base, engine


@pytest.fixture
async def test_client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


class TestSourcesAPI:
    """Test suite for /api/sources endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_sources_empty(self, test_client):
        """Test listing sources when database is empty."""
        with patch('app.api.sources.get_db') as mock_get_db:
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            mock_session.execute.return_value = mock_result
            
            async def mock_gen():
                yield mock_session
            mock_get_db.return_value = mock_gen()
            
            response = await test_client.get("/api/sources")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["sources"] == []
    
    @pytest.mark.asyncio
    async def test_get_source_not_found(self, test_client):
        """Test getting a source that doesn't exist."""
        with patch('app.api.sources.get_db') as mock_get_db:
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            async def mock_gen():
                yield mock_session
            mock_get_db.return_value = mock_gen()
            
            response = await test_client.get("/api/sources/nonexistent")
            
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_source_not_found(self, test_client):
        """Test deleting a source that doesn't exist."""
        with patch('app.api.sources.get_db') as mock_get_db:
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            async def mock_gen():
                yield mock_session
            mock_get_db.return_value = mock_gen()
            
            response = await test_client.delete("/api/sources/nonexistent")
            
            assert response.status_code == 404


class TestSourceDBModel:
    """Test the SourceDB model."""
    
    def test_source_db_creation(self):
        """Test creating a SourceDB instance."""
        source = SourceDB(
            id="test123",
            url="https://example.com/video",
            source_type="youtube",
            title="Test Strategy",
            author="Test Author",
            transcript_or_content="Content here",
            extracted_data={"strategy_name": {"value": "Test"}},
            quality_metrics={"specificity_score": 5.0},
            specificity_score=5.0,
            trust_score=4.0,
        )
        
        assert source.id == "test123"
        assert source.source_type == "youtube"
        assert source.specificity_score == 5.0
        assert source.extracted_data["strategy_name"]["value"] == "Test"


class TestSourceConversion:
    """Test conversion between database and Pydantic models."""
    
    def test_source_to_db_basic(self):
        """Test converting a simple Source to SourceDB."""
        from app.api.sources import source_to_db
        from app.models import Source, ExtractedStrategy, QualityMetrics, PlatformMetrics
        
        source = Source(
            id="conv123",
            url="https://youtube.com/watch?v=abc",
            source_type="youtube",
            title="Conversion Test",
            author="Test Author",
            transcript_or_content="Content",
            extracted_data=ExtractedStrategy(),
            quality_metrics=QualityMetrics(specificity_score=6.5, trust_score=5.0),
        )
        
        db_source = source_to_db(source)
        
        assert db_source.id == "conv123"
        assert db_source.url == "https://youtube.com/watch?v=abc"
        assert db_source.specificity_score == 6.5
        assert db_source.trust_score == 5.0
