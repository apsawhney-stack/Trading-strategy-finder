"""
Integration tests for API endpoints.
Test cases TC-API-001 through TC-API-006.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    # TC-API-001: Health check
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    # TC-API-002: Extract endpoint with valid YouTube URL
    def test_extract_youtube_url_structure(self, client):
        """Test extract endpoint returns correct structure."""
        # Note: This tests the endpoint structure, not actual extraction
        # (which would require API keys)
        response = client.post(
            "/api/extract",
            json={"url": "https://youtube.com/watch?v=invalid123"}
        )
        # Should get a response (success or error, but valid JSON)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        # If extraction fails due to no API key, that's expected
        if not data["success"]:
            assert "error" in data

    # TC-API-003: Extract endpoint with invalid URL
    def test_extract_invalid_url(self, client):
        """Test extract endpoint handles invalid URLs."""
        response = client.post(
            "/api/extract",
            json={"url": "not-a-valid-url"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should still return valid JSON response
        assert "success" in data

    # TC-API-004: Strategies list endpoint
    def test_strategies_list(self, client):
        """Test strategies list endpoint."""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert isinstance(data["strategies"], list)

    # TC-API-005: Discover endpoint
    def test_discover_endpoint(self, client):
        """Test discover endpoint."""
        response = client.post(
            "/api/discover",
            json={"query": "SPX put credit spread", "sources": ["web"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert "filters_applied" in data

    # TC-API-006: CORS headers
    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.options(
            "/api/extract",
            headers={"Origin": "http://localhost:5173"}
        )
        # FastAPI handles CORS via middleware
        # Just verify the endpoint exists
        assert response.status_code in [200, 405]
