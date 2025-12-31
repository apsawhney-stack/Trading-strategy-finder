"""
Specificity and Trust score calculation.
Implements the scoring rubric from the PRD.
"""

from typing import List
from app.models import (
    ExtractedStrategy,
    QualityMetrics,
    SpecificityBreakdown,
)


# ============================================================================
# Specificity Score Weights (from PRD)
# ============================================================================

SPECIFICITY_WEIGHTS = {
    "strike_selection": 0.12,
    "entry_criteria": 0.12,
    "dte": 0.08,
    "buying_power_effect": 0.12,
    "profit_target": 0.08,
    "stop_loss": 0.12,
    "adjustments": 0.12,
    "failure_modes": 0.08,
    "real_pnl": 0.08,
    "backtest_evidence": 0.08,
}

# ============================================================================
# Trust Score Weights
# ============================================================================

TRUST_WEIGHTS = {
    "discusses_failures": 0.30,
    "mentions_drawdowns": 0.25,
    "shows_losing_trades": 0.25,
    "balanced_claims": 0.20,
}


# ============================================================================
# Specificity Scoring
# ============================================================================

def _score_field_specificity(field, field_name: str) -> float:
    """Score a single field's specificity (0-10)."""
    if not field or not hasattr(field, 'confidence'):
        return 0.0
    
    # Base score from confidence
    confidence = getattr(field, 'confidence', 0)
    interpretation = getattr(field, 'interpretation', 'missing')
    value = getattr(field, 'value', None)
    
    if interpretation == "missing" or value is None:
        return 0.0
    
    # Score based on interpretation type
    if interpretation == "explicit":
        base_score = 8.0 + (confidence * 2.0)  # 8-10
    elif interpretation == "implicit":
        base_score = 5.0 + (confidence * 3.0)  # 5-8
    elif interpretation == "inferred":
        base_score = 2.0 + (confidence * 3.0)  # 2-5
    else:
        base_score = 1.0
    
    return min(10.0, base_score)


def calculate_specificity_score(extraction: ExtractedStrategy) -> QualityMetrics:
    """
    Calculate specificity score for extracted strategy.
    Returns QualityMetrics with breakdown.
    """
    breakdown = SpecificityBreakdown()
    gaps = []
    
    # Score each criterion
    
    # 1. Strike Selection
    strike_score = _score_field_specificity(extraction.setup_rules.strike_selection, "strike_selection")
    if extraction.setup_rules.delta.value:
        strike_score = (strike_score + _score_field_specificity(extraction.setup_rules.delta, "delta")) / 2
    breakdown.strike_selection = strike_score
    if strike_score < 3:
        gaps.append("Strike selection not clearly defined")
    
    # 2. Entry Criteria
    entry_score = _score_field_specificity(extraction.setup_rules.entry_criteria, "entry_criteria")
    breakdown.entry_criteria = entry_score
    if entry_score < 3:
        gaps.append("Entry criteria unclear")
    
    # 3. DTE
    dte_score = _score_field_specificity(extraction.setup_rules.dte, "dte")
    breakdown.dte = dte_score
    if dte_score < 3:
        gaps.append("DTE not specified")
    
    # 4. Buying Power Effect
    bpe_score = _score_field_specificity(extraction.setup_rules.buying_power_effect, "buying_power_effect")
    breakdown.buying_power_effect = bpe_score
    if bpe_score < 3:
        gaps.append("Position sizing/BPE not defined")
    
    # 5. Profit Target
    profit_score = _score_field_specificity(extraction.management_rules.profit_target, "profit_target")
    breakdown.profit_target = profit_score
    if profit_score < 3:
        gaps.append("Profit target not specified")
    
    # 6. Stop Loss
    stop_score = _score_field_specificity(extraction.management_rules.stop_loss, "stop_loss")
    breakdown.stop_loss = stop_score
    if stop_score < 3:
        gaps.append("Stop loss not defined")
    
    # 7. Adjustments/Defense
    adjust_score = max(
        _score_field_specificity(extraction.management_rules.adjustment_rules, "adjustments"),
        _score_field_specificity(extraction.management_rules.defensive_maneuvers, "defensive")
    )
    breakdown.adjustments = adjust_score
    if adjust_score < 3:
        gaps.append("Adjustment/defense strategy not explained")
    
    # 8. Failure Modes
    if extraction.failure_analysis.failure_modes_mentioned:
        failure_score = min(10, len(extraction.failure_analysis.failure_modes_mentioned) * 3 + 4)
    elif extraction.failure_analysis.discusses_losses:
        failure_score = 5.0
    else:
        failure_score = 0.0
    breakdown.failure_modes = failure_score
    if failure_score < 3:
        gaps.append("Failure modes not discussed")
    
    # 9. Real P&L
    pnl_score = 0.0
    if extraction.performance_claims.starting_capital.value and extraction.performance_claims.ending_capital.value:
        pnl_score = 8.0
        if extraction.performance_claims.time_period.value:
            pnl_score = 10.0
    elif extraction.performance_claims.total_return_percent.value:
        pnl_score = 6.0
    breakdown.real_pnl = pnl_score
    
    # 10. Backtest Evidence
    backtest_score = 0.0
    if extraction.risk_profile.win_rate.value and extraction.risk_profile.win_rate.confidence > 0.7:
        backtest_score = 7.0
        if extraction.risk_profile.max_drawdown.value:
            backtest_score = 10.0
    breakdown.backtest_evidence = backtest_score
    if backtest_score < 3:
        gaps.append("No backtest or historical data")
    
    # Calculate weighted total
    total_score = (
        breakdown.strike_selection * SPECIFICITY_WEIGHTS["strike_selection"] +
        breakdown.entry_criteria * SPECIFICITY_WEIGHTS["entry_criteria"] +
        breakdown.dte * SPECIFICITY_WEIGHTS["dte"] +
        breakdown.buying_power_effect * SPECIFICITY_WEIGHTS["buying_power_effect"] +
        breakdown.profit_target * SPECIFICITY_WEIGHTS["profit_target"] +
        breakdown.stop_loss * SPECIFICITY_WEIGHTS["stop_loss"] +
        breakdown.adjustments * SPECIFICITY_WEIGHTS["adjustments"] +
        breakdown.failure_modes * SPECIFICITY_WEIGHTS["failure_modes"] +
        breakdown.real_pnl * SPECIFICITY_WEIGHTS["real_pnl"] +
        breakdown.backtest_evidence * SPECIFICITY_WEIGHTS["backtest_evidence"]
    )
    
    return QualityMetrics(
        specificity_score=round(total_score, 1),
        specificity_breakdown=breakdown,
        has_backtest=backtest_score >= 7.0,
        has_real_pnl=pnl_score >= 6.0,
        gaps=gaps,
    )


# ============================================================================
# Trust Score
# ============================================================================

def calculate_trust_score(extraction: ExtractedStrategy) -> float:
    """
    Calculate trust score based on bias detection.
    Returns score 0-10.
    """
    score = 0.0
    
    # 1. Discusses failures (30%)
    if extraction.failure_analysis.failure_modes_mentioned:
        failure_count = len(extraction.failure_analysis.failure_modes_mentioned)
        failure_score = min(10, failure_count * 3 + 4)
    elif extraction.failure_analysis.discusses_losses:
        failure_score = 5.0
    else:
        failure_score = 0.0
    score += failure_score * TRUST_WEIGHTS["discusses_failures"]
    
    # 2. Mentions drawdowns (25%)
    if extraction.failure_analysis.max_drawdown_mentioned or extraction.risk_profile.max_drawdown.value:
        drawdown_score = 10.0
    else:
        drawdown_score = 0.0
    score += drawdown_score * TRUST_WEIGHTS["mentions_drawdowns"]
    
    # 3. Shows losing trades (25%)
    # Hard to detect directly, use bias_detected flag
    if not extraction.failure_analysis.bias_detected:
        losing_score = 10.0
    elif extraction.failure_analysis.discusses_losses:
        losing_score = 5.0
    else:
        losing_score = 0.0
    score += losing_score * TRUST_WEIGHTS["shows_losing_trades"]
    
    # 4. Balanced claims (20%)
    # Check if warnings are present
    if extraction.warnings:
        balanced_score = min(10, len(extraction.warnings) * 3 + 4)
    else:
        balanced_score = 2.0  # Some content is just educational, not promotional
    score += balanced_score * TRUST_WEIGHTS["balanced_claims"]
    
    return round(score, 1)
