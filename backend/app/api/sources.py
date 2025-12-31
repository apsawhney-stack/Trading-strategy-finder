"""
API router for source CRUD operations.
Handles persistence of extracted sources to SQLite database.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db, SourceDB, init_db
from app.models import Source

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class SourceListResponse(BaseModel):
    """Response for list sources endpoint."""
    sources: List[Source]
    total: int


class SourceResponse(BaseModel):
    """Response for single source operations."""
    success: bool
    source: Optional[Source] = None
    message: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

def source_db_to_model(db_source: SourceDB) -> Source:
    """Convert database model to Pydantic model."""
    from app.models import (
        ExtractedStrategy, QualityMetrics, PlatformMetrics,
        ExtractedField, ExtractedNumericField, SetupRules, ManagementRules,
        RiskProfile, PerformanceClaims, FailureModeAnalysis, SpecificityBreakdown
    )
    
    # Reconstruct extracted_data from JSON
    ed = db_source.extracted_data or {}
    
    def parse_field(data: dict) -> ExtractedField:
        if not data:
            return ExtractedField()
        return ExtractedField(
            value=data.get("value"),
            confidence=data.get("confidence", 0),
            source_quote=data.get("source_quote"),
            interpretation=data.get("interpretation", "missing"),
        )
    
    def parse_numeric(data: dict) -> ExtractedNumericField:
        if not data:
            return ExtractedNumericField()
        return ExtractedNumericField(
            value=data.get("value"),
            confidence=data.get("confidence", 0),
            source_quote=data.get("source_quote"),
            interpretation=data.get("interpretation", "missing"),
        )
    
    extracted_data = ExtractedStrategy(
        strategy_name=parse_field(ed.get("strategy_name", {})),
        variation=parse_field(ed.get("variation", {})),
        trader_name=parse_field(ed.get("trader_name", {})),
        experience_level=parse_field(ed.get("experience_level", {})),
        setup_rules=SetupRules(
            underlying=parse_field(ed.get("setup_rules", {}).get("underlying", {})),
            option_type=parse_field(ed.get("setup_rules", {}).get("option_type", {})),
            strike_selection=parse_field(ed.get("setup_rules", {}).get("strike_selection", {})),
            dte=parse_numeric(ed.get("setup_rules", {}).get("dte", {})),
            width=parse_numeric(ed.get("setup_rules", {}).get("width", {})),
            delta=parse_numeric(ed.get("setup_rules", {}).get("delta", {})),
            entry_criteria=parse_field(ed.get("setup_rules", {}).get("entry_criteria", {})),
            entry_timing=parse_field(ed.get("setup_rules", {}).get("entry_timing", {})),
            buying_power_effect=parse_field(ed.get("setup_rules", {}).get("buying_power_effect", {})),
        ),
        management_rules=ManagementRules(
            profit_target=parse_field(ed.get("management_rules", {}).get("profit_target", {})),
            stop_loss=parse_field(ed.get("management_rules", {}).get("stop_loss", {})),
            time_exit=parse_field(ed.get("management_rules", {}).get("time_exit", {})),
            adjustment_rules=parse_field(ed.get("management_rules", {}).get("adjustment_rules", {})),
            rolling_rules=parse_field(ed.get("management_rules", {}).get("rolling_rules", {})),
            defensive_maneuvers=parse_field(ed.get("management_rules", {}).get("defensive_maneuvers", {})),
        ),
        risk_profile=RiskProfile(
            max_loss_per_trade=parse_field(ed.get("risk_profile", {}).get("max_loss_per_trade", {})),
            win_rate=parse_numeric(ed.get("risk_profile", {}).get("win_rate", {})),
            risk_reward_ratio=parse_field(ed.get("risk_profile", {}).get("risk_reward_ratio", {})),
            max_drawdown=parse_numeric(ed.get("risk_profile", {}).get("max_drawdown", {})),
        ),
        performance_claims=PerformanceClaims(
            starting_capital=parse_numeric(ed.get("performance_claims", {}).get("starting_capital", {})),
            ending_capital=parse_numeric(ed.get("performance_claims", {}).get("ending_capital", {})),
            total_return_percent=parse_numeric(ed.get("performance_claims", {}).get("total_return_percent", {})),
            time_period=parse_field(ed.get("performance_claims", {}).get("time_period", {})),
            profits_withdrawn=parse_numeric(ed.get("performance_claims", {}).get("profits_withdrawn", {})),
            verified=ed.get("performance_claims", {}).get("verified", False),
        ),
        failure_analysis=FailureModeAnalysis(
            failure_modes_mentioned=ed.get("failure_analysis", {}).get("failure_modes_mentioned", []),
            discusses_losses=ed.get("failure_analysis", {}).get("discusses_losses", False),
            max_drawdown_mentioned=ed.get("failure_analysis", {}).get("max_drawdown_mentioned"),
            recovery_strategy=ed.get("failure_analysis", {}).get("recovery_strategy"),
            bias_detected=ed.get("failure_analysis", {}).get("bias_detected", True),
        ),
        key_insights=ed.get("key_insights", []),
        warnings=ed.get("warnings", []),
        quotes=ed.get("quotes", []),
    )
    
    # Reconstruct quality_metrics from JSON
    qm = db_source.quality_metrics or {}
    sb = qm.get("specificity_breakdown", {})
    quality_metrics = QualityMetrics(
        specificity_score=qm.get("specificity_score", 0),
        trust_score=qm.get("trust_score", 0),
        specificity_breakdown=SpecificityBreakdown(
            strike_selection=sb.get("strike_selection", 0),
            entry_criteria=sb.get("entry_criteria", 0),
            dte=sb.get("dte", 0),
            buying_power_effect=sb.get("buying_power_effect", 0),
            profit_target=sb.get("profit_target", 0),
            stop_loss=sb.get("stop_loss", 0),
            adjustments=sb.get("adjustments", 0),
            failure_modes=sb.get("failure_modes", 0),
            real_pnl=sb.get("real_pnl", 0),
            backtest_evidence=sb.get("backtest_evidence", 0),
        ),
        has_backtest=qm.get("has_backtest", False),
        has_real_pnl=qm.get("has_real_pnl", False),
        gaps=qm.get("gaps", []),
    )
    
    # Reconstruct platform_metrics
    pm = db_source.platform_metrics or {}
    platform_metrics = PlatformMetrics(
        views=pm.get("views"),
        likes=pm.get("likes"),
        upvotes=pm.get("upvotes"),
        comments_count=pm.get("comments_count"),
        author_karma=pm.get("author_karma"),
    )
    
    return Source(
        id=db_source.id,
        url=db_source.url,
        source_type=db_source.source_type,
        title=db_source.title,
        author=db_source.author,
        published_date=db_source.published_date.isoformat() if db_source.published_date else None,
        platform_metrics=platform_metrics,
        transcript_or_content=db_source.transcript_or_content,
        comment_content=db_source.comment_content,
        extracted_data=extracted_data,
        quality_metrics=quality_metrics,
    )


def source_to_db(source: Source) -> SourceDB:
    """Convert Pydantic model to database model."""
    return SourceDB(
        id=source.id,
        url=source.url,
        source_type=source.source_type,
        title=source.title,
        author=source.author,
        published_date=datetime.fromisoformat(source.published_date) if source.published_date else None,
        transcript_or_content=source.transcript_or_content or "",
        comment_content=source.comment_content,
        platform_metrics=source.platform_metrics.model_dump() if source.platform_metrics else {},
        extracted_data=source.extracted_data.model_dump() if source.extracted_data else {},
        quality_metrics=source.quality_metrics.model_dump() if source.quality_metrics else {},
        specificity_score=source.quality_metrics.specificity_score if source.quality_metrics else 0,
        trust_score=source.quality_metrics.trust_score if source.quality_metrics else 0,
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/sources", response_model=SourceListResponse)
async def list_sources(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all saved sources with pagination."""
    # Get total count
    count_result = await db.execute(select(SourceDB))
    all_sources = count_result.scalars().all()
    total = len(all_sources)
    
    # Get paginated sources
    result = await db.execute(
        select(SourceDB)
        .order_by(SourceDB.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    db_sources = result.scalars().all()
    
    sources = [source_db_to_model(s) for s in db_sources]
    
    return SourceListResponse(sources=sources, total=total)


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single source by ID."""
    result = await db.execute(select(SourceDB).where(SourceDB.id == source_id))
    db_source = result.scalar_one_or_none()
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return SourceResponse(success=True, source=source_db_to_model(db_source))


@router.post("/sources", response_model=SourceResponse)
async def save_source(source: Source, db: AsyncSession = Depends(get_db)):
    """Save a new source or update existing."""
    # Check if source already exists
    result = await db.execute(select(SourceDB).where(SourceDB.id == source.id))
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing source
        existing.title = source.title
        existing.author = source.author
        existing.extracted_data = source.extracted_data.model_dump() if source.extracted_data else {}
        existing.quality_metrics = source.quality_metrics.model_dump() if source.quality_metrics else {}
        existing.specificity_score = source.quality_metrics.specificity_score if source.quality_metrics else 0
        existing.trust_score = source.quality_metrics.trust_score if source.quality_metrics else 0
        existing.updated_at = datetime.utcnow()
        await db.commit()
        return SourceResponse(success=True, source=source, message="Source updated")
    else:
        # Create new source
        db_source = source_to_db(source)
        db.add(db_source)
        await db.commit()
        return SourceResponse(success=True, source=source, message="Source saved")


@router.delete("/sources/{source_id}", response_model=SourceResponse)
async def delete_source(source_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a source by ID."""
    result = await db.execute(select(SourceDB).where(SourceDB.id == source_id))
    db_source = result.scalar_one_or_none()
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    await db.execute(delete(SourceDB).where(SourceDB.id == source_id))
    await db.commit()
    
    return SourceResponse(success=True, message="Source deleted")
