"""
Consensus synthesis from multiple sources.
Identifies agreements, controversies, and gaps.
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from collections import defaultdict

from app.models import ExtractedStrategy


class ConsensusItem(BaseModel):
    """A topic where sources agree or have positions."""
    topic: str
    consensus_value: str | None = None
    agreement_rate: float = 0.0
    positions: List[Dict[str, Any]] = []
    sources: List[str] = []


class Controversy(BaseModel):
    """A topic where sources disagree."""
    topic: str
    positions: List[Dict[str, Any]] = []


class ConsensusResult(BaseModel):
    """Result of consensus synthesis."""
    sources_analyzed: int
    consensus: List[ConsensusItem] = []
    controversies: List[Controversy] = []
    gaps: List[str] = []


def _extract_value(field) -> str | None:
    """Extract string value from ExtractedField."""
    if hasattr(field, 'value') and field.value:
        return str(field.value)
    return None


def _normalize_value(value: str | None) -> str | None:
    """Normalize value for comparison."""
    if value is None:
        return None
    return value.lower().strip()


def synthesize_consensus(extractions: List[ExtractedStrategy]) -> ConsensusResult:
    """
    Synthesize consensus view from multiple strategy extractions.
    """
    if not extractions:
        return ConsensusResult(sources_analyzed=0)
    
    n = len(extractions)
    consensus_items = []
    controversies = []
    gaps = []
    
    # Topics to analyze
    topics = [
        ("Underlying", lambda e: _extract_value(e.setup_rules.underlying)),
        ("Option Type", lambda e: _extract_value(e.setup_rules.option_type)),
        ("Strike Selection", lambda e: _extract_value(e.setup_rules.strike_selection)),
        ("DTE", lambda e: str(e.setup_rules.dte.value) if e.setup_rules.dte.value else None),
        ("Delta", lambda e: str(e.setup_rules.delta.value) if e.setup_rules.delta.value else None),
        ("Entry Criteria", lambda e: _extract_value(e.setup_rules.entry_criteria)),
        ("Profit Target", lambda e: _extract_value(e.management_rules.profit_target)),
        ("Stop Loss", lambda e: _extract_value(e.management_rules.stop_loss)),
        ("Adjustments", lambda e: _extract_value(e.management_rules.adjustment_rules)),
        ("Time Exit", lambda e: _extract_value(e.management_rules.time_exit)),
    ]
    
    for topic_name, extractor in topics:
        # Collect values from all sources
        values = []
        for i, extraction in enumerate(extractions):
            value = extractor(extraction)
            if value:
                values.append({
                    "value": value,
                    "normalized": _normalize_value(value),
                    "source_index": i,
                })
        
        if not values:
            gaps.append(f"{topic_name} not mentioned in any source")
            continue
        
        # Group by normalized value
        groups = defaultdict(list)
        for v in values:
            groups[v["normalized"]].append(v)
        
        # Check for consensus
        if len(groups) == 1:
            # Full agreement
            value = list(groups.keys())[0]
            consensus_items.append(ConsensusItem(
                topic=topic_name,
                consensus_value=values[0]["value"],  # Use original case
                agreement_rate=len(values) / n,
                sources=[f"Source {v['source_index'] + 1}" for v in values],
            ))
        else:
            # Disagreement - create controversy
            positions = []
            for norm_value, group in groups.items():
                positions.append({
                    "value": group[0]["value"],
                    "source_count": len(group),
                    "sources": [f"Source {v['source_index'] + 1}" for v in group],
                })
            
            # Sort by source count (most popular first)
            positions.sort(key=lambda p: p["source_count"], reverse=True)
            
            # If one position has majority, it's still partial consensus
            top_count = positions[0]["source_count"]
            agreement_rate = top_count / n
            
            if agreement_rate >= 0.6:
                # Majority consensus with some disagreement
                consensus_items.append(ConsensusItem(
                    topic=topic_name,
                    consensus_value=positions[0]["value"],
                    agreement_rate=agreement_rate,
                    positions=positions[1:],  # Include minority positions
                    sources=positions[0]["sources"],
                ))
            else:
                # True controversy
                controversies.append(Controversy(
                    topic=topic_name,
                    positions=positions,
                ))
    
    # Check for common gaps
    gap_topics = [
        ("Stop Loss", lambda e: e.management_rules.stop_loss.interpretation != "missing"),
        ("Adjustments", lambda e: e.management_rules.adjustment_rules.interpretation != "missing"),
        ("Failure Modes", lambda e: bool(e.failure_analysis.failure_modes_mentioned)),
        ("Backtest Data", lambda e: e.risk_profile.win_rate.value is not None),
    ]
    
    for topic_name, has_data in gap_topics:
        sources_with_data = sum(1 for e in extractions if has_data(e))
        if sources_with_data < n * 0.5:
            if topic_name not in [g.split()[0] for g in gaps]:
                gaps.append(f"{topic_name} missing in most sources")
    
    return ConsensusResult(
        sources_analyzed=n,
        consensus=consensus_items,
        controversies=controversies,
        gaps=gaps,
    )
