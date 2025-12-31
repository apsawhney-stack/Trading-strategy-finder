"""
API router for source extraction endpoints.
Handles YouTube, Reddit, and Article URL extraction.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional
import hashlib
from datetime import datetime

from app.models import Source
from app.extractors import get_extractor
from app.scoring import calculate_specificity_score, calculate_trust_score

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ExtractionRequest(BaseModel):
    """Request to extract strategy from URL."""
    url: str


class ExtractionStatus(BaseModel):
    """Extraction progress status."""
    step: Literal[
        "fetching_content",
        "analyzing_structure", 
        "extracting_strategy",
        "calculating_scores",
        "enriching_context",
        "complete",
        "error"
    ]
    message: str
    progress: float  # 0.0 to 1.0


class ExtractionResponse(BaseModel):
    """Response from extraction endpoint."""
    success: bool
    source: Optional[Source] = None
    error: Optional[str] = None


# ============================================================================
# URL Detection
# ============================================================================

def detect_source_type(url: str) -> Literal["youtube", "reddit", "article"]:
    """Detect the source type from URL."""
    url_lower = url.lower()
    
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "reddit.com" in url_lower or "redd.it" in url_lower:
        return "reddit"
    else:
        return "article"


def generate_source_id(url: str) -> str:
    """Generate unique ID from URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/extract", response_model=ExtractionResponse)
async def extract_source(request: ExtractionRequest):
    """
    Extract strategy data from a URL.
    
    Supports:
    - YouTube videos (via transcript)
    - Reddit posts (post + comments)
    - Articles (web scraping)
    """
    try:
        # Detect source type
        source_type = detect_source_type(request.url)
        
        # Get appropriate extractor
        extractor = get_extractor(source_type)
        
        # Extract content
        extraction_result = await extractor.extract(request.url)
        
        if not extraction_result.success:
            return ExtractionResponse(
                success=False,
                error=extraction_result.error
            )
        
        # Calculate scores
        specificity = calculate_specificity_score(extraction_result.extracted_data)
        trust = calculate_trust_score(extraction_result.extracted_data)
        
        # Build Source object
        source = Source(
            id=generate_source_id(request.url),
            url=request.url,
            source_type=source_type,
            title=extraction_result.title,
            author=extraction_result.author,
            published_date=extraction_result.published_date,
            platform_metrics=extraction_result.platform_metrics,
            transcript_or_content=extraction_result.content,
            comment_content=extraction_result.comment_content,
            extracted_data=extraction_result.extracted_data,
            quality_metrics=specificity.with_trust(trust),
        )
        
        return ExtractionResponse(success=True, source=source)
        
    except Exception as e:
        return ExtractionResponse(
            success=False,
            error=f"Extraction failed: {str(e)}"
        )
