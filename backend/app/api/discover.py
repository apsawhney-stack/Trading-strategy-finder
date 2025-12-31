"""
API router for source discovery endpoints.
Searches YouTube, Reddit, and curated sites for strategy content.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Literal

from app.discovery.search import DiscoveryCandidate, DiscoveryResult, discover_sources as run_discovery

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class DiscoveryRequest(BaseModel):
    """Request to discover sources."""
    query: str
    sources: List[Literal["youtube", "reddit", "web"]] = ["youtube", "reddit"]
    max_results: int = 20


class DiscoveryResponse(BaseModel):
    """Response from discovery endpoint."""
    query: str
    candidates: List[DiscoveryCandidate]
    filters_applied: List[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/discover", response_model=DiscoveryResponse)
async def discover_sources(request: DiscoveryRequest):
    """
    Discover sources for a strategy query.
    
    Searches configured platforms and returns ranked candidates.
    """
    result = await run_discovery(
        query=request.query,
        platforms=request.sources,
        max_results=request.max_results
    )
    
    return DiscoveryResponse(
        query=request.query,
        candidates=result.candidates,
        filters_applied=result.filters_applied
    )

