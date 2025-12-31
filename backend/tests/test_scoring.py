"""
Unit tests for Specificity and Trust scoring.
Test cases TC-SS-001 through TC-SS-005.
"""

import pytest
from app.scoring.scorer import calculate_specificity_score, calculate_trust_score
from app.models import (
    ExtractedStrategy,
    ExtractedField,
    ExtractedNumericField,
    SetupRules,
    ManagementRules,
    RiskProfile,
    PerformanceClaims,
    FailureModeAnalysis,
)


class TestSpecificityScoring:
    """Test suite for Specificity scoring."""

    def _create_strategy(self, **kwargs) -> ExtractedStrategy:
        """Helper to create strategy with custom fields."""
        strategy = ExtractedStrategy()
        for key, value in kwargs.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)
        return strategy

    # TC-SS-001: Complete high-specificity strategy
    def test_high_specificity_strategy(self):
        """Test scoring for strategy with all fields explicit."""
        strategy = ExtractedStrategy(
            strategy_name=ExtractedField(value="Put Credit Spread", confidence=1.0, interpretation="explicit"),
            setup_rules=SetupRules(
                underlying=ExtractedField(value="SPX", confidence=1.0, interpretation="explicit"),
                strike_selection=ExtractedField(value="16 delta, 10pt wide", confidence=1.0, interpretation="explicit"),
                dte=ExtractedNumericField(value=30, confidence=1.0, interpretation="explicit"),
                delta=ExtractedNumericField(value=0.16, confidence=1.0, interpretation="explicit"),
                entry_criteria=ExtractedField(value="VIX > 15, no earnings", confidence=0.9, interpretation="explicit"),
                buying_power_effect=ExtractedField(value="5% per trade", confidence=0.9, interpretation="explicit"),
            ),
            management_rules=ManagementRules(
                profit_target=ExtractedField(value="50%", confidence=1.0, interpretation="explicit"),
                stop_loss=ExtractedField(value="100% of credit", confidence=1.0, interpretation="explicit"),
                adjustment_rules=ExtractedField(value="Roll at 21 DTE", confidence=0.9, interpretation="explicit"),
            ),
            risk_profile=RiskProfile(
                win_rate=ExtractedNumericField(value=0.75, confidence=0.9, interpretation="explicit"),
                max_drawdown=ExtractedNumericField(value=15.0, confidence=0.8, interpretation="explicit"),
            ),
            performance_claims=PerformanceClaims(
                starting_capital=ExtractedNumericField(value=3200, confidence=1.0, interpretation="explicit"),
                ending_capital=ExtractedNumericField(value=12000, confidence=1.0, interpretation="explicit"),
                time_period=ExtractedField(value="9 months", confidence=1.0, interpretation="explicit"),
            ),
            failure_analysis=FailureModeAnalysis(
                failure_modes_mentioned=["gap down", "VIX spike"],
                discusses_losses=True,
                bias_detected=False,
            ),
        )
        
        metrics = calculate_specificity_score(strategy)
        assert metrics.specificity_score >= 7.0
        assert len(metrics.gaps) <= 2

    # TC-SS-002: Vague strategy with missing fields
    def test_low_specificity_strategy(self):
        """Test scoring for strategy with vague/missing fields."""
        strategy = ExtractedStrategy(
            strategy_name=ExtractedField(value="Credit Spread", confidence=0.5, interpretation="inferred"),
            setup_rules=SetupRules(),  # All defaults (missing)
            management_rules=ManagementRules(),
        )
        
        metrics = calculate_specificity_score(strategy)
        assert metrics.specificity_score < 3.0
        assert len(metrics.gaps) >= 5

    # TC-SS-003: Strategy with implicit values
    def test_implicit_specificity_strategy(self):
        """Test scoring for strategy with implicit interpretations."""
        strategy = ExtractedStrategy(
            strategy_name=ExtractedField(value="Iron Condor", confidence=0.8, interpretation="implicit"),
            setup_rules=SetupRules(
                dte=ExtractedNumericField(value=45, confidence=0.7, interpretation="implicit"),
            ),
        )
        
        metrics = calculate_specificity_score(strategy)
        # Implicit fields score lower than explicit
        assert metrics.specificity_score < 5.0

    # TC-SS-004: Gaps detection
    def test_gaps_detection(self):
        """Test that gaps are properly identified."""
        strategy = ExtractedStrategy(
            strategy_name=ExtractedField(value="Wheel", confidence=1.0, interpretation="explicit"),
            # Missing: stop_loss, adjustments, failure_modes
        )
        
        metrics = calculate_specificity_score(strategy)
        assert "Stop loss not defined" in metrics.gaps
        assert "Adjustment/defense strategy not explained" in metrics.gaps

    # TC-SS-005: Real P&L detection
    def test_real_pnl_detection(self):
        """Test P&L detection affects has_real_pnl flag."""
        strategy = ExtractedStrategy(
            performance_claims=PerformanceClaims(
                starting_capital=ExtractedNumericField(value=5000, confidence=1.0, interpretation="explicit"),
                ending_capital=ExtractedNumericField(value=15000, confidence=1.0, interpretation="explicit"),
            ),
        )
        
        metrics = calculate_specificity_score(strategy)
        assert metrics.has_real_pnl is True


class TestTrustScoring:
    """Test suite for Trust scoring."""

    def test_high_trust_balanced_content(self):
        """Test high trust score for balanced content."""
        strategy = ExtractedStrategy(
            failure_analysis=FailureModeAnalysis(
                failure_modes_mentioned=["gap risk", "assignment", "VIX spike"],
                discusses_losses=True,
                max_drawdown_mentioned=20.0,
                bias_detected=False,
            ),
            warnings=["Not suitable for small accounts", "Requires margin"],
            risk_profile=RiskProfile(
                max_drawdown=ExtractedNumericField(value=20.0, confidence=0.9, interpretation="explicit"),
            ),
        )
        
        trust_score = calculate_trust_score(strategy)
        assert trust_score >= 7.0

    def test_low_trust_win_only_content(self):
        """Test low trust score for win-only content."""
        strategy = ExtractedStrategy(
            failure_analysis=FailureModeAnalysis(
                failure_modes_mentioned=[],
                discusses_losses=False,
                bias_detected=True,
            ),
            warnings=[],
        )
        
        trust_score = calculate_trust_score(strategy)
        assert trust_score < 3.0
