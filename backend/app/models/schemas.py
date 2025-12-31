"""
Pydantic models for extracted strategy data.
These define the schema for LLM extraction output.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Extracted Field with Confidence
# ============================================================================

class ExtractedField(BaseModel):
    """A single extracted field with confidence and source quote."""
    value: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_quote: Optional[str] = Field(default=None, max_length=500)
    interpretation: Literal["explicit", "implicit", "inferred", "missing"] = "missing"


class ExtractedNumericField(BaseModel):
    """Extracted numeric field with range support."""
    value: Optional[float] = None
    value_range: Optional[tuple[float, float]] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_quote: Optional[str] = Field(default=None, max_length=500)
    interpretation: Literal["explicit", "implicit", "inferred", "missing"] = "missing"


# ============================================================================
# Setup Rules
# ============================================================================

class SetupRules(BaseModel):
    """Strategy setup/entry rules."""
    underlying: ExtractedField = Field(default_factory=ExtractedField)
    option_type: ExtractedField = Field(default_factory=ExtractedField)
    strike_selection: ExtractedField = Field(default_factory=ExtractedField)
    dte: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    width: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    delta: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    entry_criteria: ExtractedField = Field(default_factory=ExtractedField)
    entry_timing: ExtractedField = Field(default_factory=ExtractedField)
    buying_power_effect: ExtractedField = Field(default_factory=ExtractedField)


# ============================================================================
# Management Rules
# ============================================================================

class ManagementRules(BaseModel):
    """Strategy management/exit rules."""
    profit_target: ExtractedField = Field(default_factory=ExtractedField)
    stop_loss: ExtractedField = Field(default_factory=ExtractedField)
    time_exit: ExtractedField = Field(default_factory=ExtractedField)
    adjustment_rules: ExtractedField = Field(default_factory=ExtractedField)
    rolling_rules: ExtractedField = Field(default_factory=ExtractedField)
    defensive_maneuvers: ExtractedField = Field(default_factory=ExtractedField)


# ============================================================================
# Risk Profile
# ============================================================================

class RiskProfile(BaseModel):
    """Risk characteristics of the strategy."""
    max_loss_per_trade: ExtractedField = Field(default_factory=ExtractedField)
    win_rate: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    risk_reward_ratio: ExtractedField = Field(default_factory=ExtractedField)
    max_drawdown: ExtractedNumericField = Field(default_factory=ExtractedNumericField)


# ============================================================================
# Performance Claims
# ============================================================================

class PerformanceClaims(BaseModel):
    """P&L and performance data claimed by author."""
    starting_capital: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    ending_capital: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    total_return_percent: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    time_period: ExtractedField = Field(default_factory=ExtractedField)
    profits_withdrawn: ExtractedNumericField = Field(default_factory=ExtractedNumericField)
    verified: bool = False


# ============================================================================
# Failure Mode Analysis (Survivorship Bias Detection)
# ============================================================================

class FailureModeAnalysis(BaseModel):
    """Analysis of failure modes and bias detection."""
    failure_modes_mentioned: List[str] = Field(default_factory=list)
    discusses_losses: bool = False
    max_drawdown_mentioned: Optional[float] = None
    recovery_strategy: Optional[str] = None
    bias_detected: bool = True  # Default to true if no failure modes mentioned


# ============================================================================
# Market Context
# ============================================================================

class MarketContext(BaseModel):
    """Market conditions at time of publication."""
    published_date: Optional[datetime] = None
    vix_level: Optional[float] = None
    vix_percentile: Optional[float] = None
    spx_30d_trend: Optional[Literal["bullish", "bearish", "neutral"]] = None
    spx_30d_return: Optional[float] = None
    regime_label: Optional[str] = None


# ============================================================================
# Extracted Strategy (Complete)
# ============================================================================

class ExtractedStrategy(BaseModel):
    """Complete extracted strategy data from a source."""
    strategy_name: ExtractedField = Field(default_factory=ExtractedField)
    variation: ExtractedField = Field(default_factory=ExtractedField)
    trader_name: ExtractedField = Field(default_factory=ExtractedField)
    experience_level: ExtractedField = Field(default_factory=ExtractedField)
    
    setup_rules: SetupRules = Field(default_factory=SetupRules)
    management_rules: ManagementRules = Field(default_factory=ManagementRules)
    risk_profile: RiskProfile = Field(default_factory=RiskProfile)
    performance_claims: PerformanceClaims = Field(default_factory=PerformanceClaims)
    failure_analysis: FailureModeAnalysis = Field(default_factory=FailureModeAnalysis)
    
    key_insights: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    quotes: List[str] = Field(default_factory=list)


# ============================================================================
# Quality Metrics
# ============================================================================

class SpecificityBreakdown(BaseModel):
    """Detailed breakdown of specificity score."""
    strike_selection: float = 0.0
    entry_criteria: float = 0.0
    dte: float = 0.0
    buying_power_effect: float = 0.0
    profit_target: float = 0.0
    stop_loss: float = 0.0
    adjustments: float = 0.0
    failure_modes: float = 0.0
    real_pnl: float = 0.0
    backtest_evidence: float = 0.0


class QualityMetrics(BaseModel):
    """Quality scoring for extracted content."""
    specificity_score: float = Field(default=0.0, ge=0.0, le=10.0)
    specificity_breakdown: SpecificityBreakdown = Field(default_factory=SpecificityBreakdown)
    trust_score: float = Field(default=0.0, ge=0.0, le=10.0)
    has_backtest: bool = False
    has_real_pnl: bool = False
    gaps: List[str] = Field(default_factory=list)


# ============================================================================
# Platform Metrics
# ============================================================================

class PlatformMetrics(BaseModel):
    """Engagement metrics from source platform."""
    views: Optional[int] = None
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None
    comments: Optional[int] = None
    subscribers: Optional[int] = None


# ============================================================================
# Source (Complete Entity)
# ============================================================================

class Source(BaseModel):
    """A complete source with extracted data."""
    id: str
    url: str
    source_type: Literal["youtube", "reddit", "article"]
    title: str
    author: str
    published_date: Optional[datetime] = None
    
    platform_metrics: PlatformMetrics = Field(default_factory=PlatformMetrics)
    market_context: MarketContext = Field(default_factory=MarketContext)
    
    transcript_or_content: str = ""
    comment_content: Optional[str] = None
    
    extracted_data: ExtractedStrategy = Field(default_factory=ExtractedStrategy)
    quality_metrics: QualityMetrics = Field(default_factory=QualityMetrics)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
