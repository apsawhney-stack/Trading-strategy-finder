"""
API router for strategy endpoints.
Handles aggregation, consensus, and strategy management.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from app.db import get_db, SourceDB, StrategyAggregateDB
from app.models import Source

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class StrategyListResponse(BaseModel):
    """List of strategy aggregates."""
    strategies: List[dict]


class StrategyDetailResponse(BaseModel):
    """Detailed strategy with sources."""
    strategy: dict
    sources: List[Source]


class SynthesizeRequest(BaseModel):
    """Request to synthesize strategy from sources."""
    source_ids: List[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/strategies", response_model=StrategyListResponse)
async def list_strategies(db: AsyncSession = Depends(get_db)):
    """List all strategy aggregates."""
    result = await db.execute(
        select(StrategyAggregateDB).order_by(StrategyAggregateDB.updated_at.desc())
    )
    strategies = result.scalars().all()
    
    return StrategyListResponse(
        strategies=[
            {
                "id": s.id,
                "name": s.name,
                "source_count": len(s.source_ids),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in strategies
        ]
    )


@router.get("/strategies/{strategy_id}", response_model=StrategyDetailResponse)
async def get_strategy(strategy_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed strategy with all sources."""
    # Get strategy
    result = await db.execute(
        select(StrategyAggregateDB).where(StrategyAggregateDB.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Get sources
    source_result = await db.execute(
        select(SourceDB).where(SourceDB.id.in_(strategy.source_ids))
    )
    sources = source_result.scalars().all()
    
    return StrategyDetailResponse(
        strategy={
            "id": strategy.id,
            "name": strategy.name,
            "consensus": strategy.consensus,
            "controversies": strategy.controversies,
            "gaps": strategy.gaps,
            "backtestability": strategy.backtestability,
            "updated_at": strategy.updated_at.isoformat(),
        },
        sources=[
            Source(
                id=s.id,
                url=s.url,
                source_type=s.source_type,
                title=s.title,
                author=s.author,
                published_date=s.published_date,
                platform_metrics=s.platform_metrics,
                transcript_or_content=s.transcript_or_content[:500] + "...",  # Truncate for response
                extracted_data=s.extracted_data,
                quality_metrics=s.quality_metrics,
            )
            for s in sources
        ]
    )


@router.post("/strategies/{strategy_id}/synthesize")
async def synthesize_strategy(
    strategy_id: str,
    request: SynthesizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Synthesize consensus view from multiple sources."""
    from app.synthesis import synthesize_consensus
    
    # Get sources
    result = await db.execute(
        select(SourceDB).where(SourceDB.id.in_(request.source_ids))
    )
    sources = result.scalars().all()
    
    if len(sources) < 2:
        raise HTTPException(
            status_code=400, 
            detail="At least 2 sources required for synthesis"
        )
    
    # Synthesize
    consensus_result = synthesize_consensus([s.extracted_data for s in sources])
    
    # Update or create strategy aggregate
    existing = await db.execute(
        select(StrategyAggregateDB).where(StrategyAggregateDB.id == strategy_id)
    )
    strategy = existing.scalar_one_or_none()
    
    if strategy:
        strategy.source_ids = request.source_ids
        strategy.consensus = consensus_result.consensus
        strategy.controversies = consensus_result.controversies
        strategy.gaps = consensus_result.gaps
    else:
        strategy = StrategyAggregateDB(
            id=strategy_id,
            name=strategy_id.replace("-", " ").title(),
            source_ids=request.source_ids,
            consensus=consensus_result.consensus,
            controversies=consensus_result.controversies,
            gaps=consensus_result.gaps,
        )
        db.add(strategy)
    
    await db.commit()
    
    return {
        "success": True,
        "strategy": {
            "id": strategy.id,
            "name": strategy.name,
            "consensus": strategy.consensus,
            "controversies": strategy.controversies,
            "gaps": strategy.gaps,
        }
    }
