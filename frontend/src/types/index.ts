/**
 * TypeScript type definitions for the Strategy Finder frontend.
 * Mirrors the backend Pydantic models.
 */

// ============================================================================
// Extracted Fields with Confidence
// ============================================================================

export interface ExtractedField {
    value: string | null;
    confidence: number;
    source_quote: string | null;
    interpretation: 'explicit' | 'implicit' | 'inferred' | 'missing';
}

export interface ExtractedNumericField {
    value: number | null;
    value_range: [number, number] | null;
    confidence: number;
    source_quote: string | null;
    interpretation: 'explicit' | 'implicit' | 'inferred' | 'missing';
}

// ============================================================================
// Strategy Components
// ============================================================================

export interface SetupRules {
    underlying: ExtractedField;
    option_type: ExtractedField;
    strike_selection: ExtractedField;
    dte: ExtractedNumericField;
    width: ExtractedNumericField;
    delta: ExtractedNumericField;
    entry_criteria: ExtractedField;
    entry_timing: ExtractedField;
    buying_power_effect: ExtractedField;
}

export interface ManagementRules {
    profit_target: ExtractedField;
    stop_loss: ExtractedField;
    time_exit: ExtractedField;
    adjustment_rules: ExtractedField;
    rolling_rules: ExtractedField;
    defensive_maneuvers: ExtractedField;
}

export interface RiskProfile {
    max_loss_per_trade: ExtractedField;
    win_rate: ExtractedNumericField;
    risk_reward_ratio: ExtractedField;
    max_drawdown: ExtractedNumericField;
}

export interface PerformanceClaims {
    starting_capital: ExtractedNumericField;
    ending_capital: ExtractedNumericField;
    total_return_percent: ExtractedNumericField;
    time_period: ExtractedField;
    profits_withdrawn: ExtractedNumericField;
    verified: boolean;
}

export interface FailureModeAnalysis {
    failure_modes_mentioned: string[];
    discusses_losses: boolean;
    max_drawdown_mentioned: number | null;
    recovery_strategy: string | null;
    bias_detected: boolean;
}

export interface MarketContext {
    published_date: string | null;
    vix_level: number | null;
    vix_percentile: number | null;
    spx_30d_trend: 'bullish' | 'bearish' | 'neutral' | null;
    spx_30d_return: number | null;
    regime_label: string | null;
}

// ============================================================================
// Extracted Strategy
// ============================================================================

export interface ExtractedStrategy {
    strategy_name: ExtractedField;
    variation: ExtractedField;
    trader_name: ExtractedField;
    experience_level: ExtractedField;
    setup_rules: SetupRules;
    management_rules: ManagementRules;
    risk_profile: RiskProfile;
    performance_claims: PerformanceClaims;
    failure_analysis: FailureModeAnalysis;
    key_insights: string[];
    warnings: string[];
    quotes: string[];
}

// ============================================================================
// Quality Metrics
// ============================================================================

export interface SpecificityBreakdown {
    strike_selection: number;
    entry_criteria: number;
    dte: number;
    buying_power_effect: number;
    profit_target: number;
    stop_loss: number;
    adjustments: number;
    failure_modes: number;
    real_pnl: number;
    backtest_evidence: number;
}

export interface QualityMetrics {
    specificity_score: number;
    specificity_breakdown: SpecificityBreakdown;
    trust_score: number;
    has_backtest: boolean;
    has_real_pnl: boolean;
    gaps: string[];
}

// ============================================================================
// Platform Metrics
// ============================================================================

export interface PlatformMetrics {
    views?: number;
    likes?: number;
    dislikes?: number;
    upvotes?: number;
    downvotes?: number;
    comments?: number;
    subscribers?: number;
}

// ============================================================================
// Source
// ============================================================================

export interface Source {
    id: string;
    url: string;
    source_type: 'youtube' | 'reddit' | 'article';
    title: string;
    author: string;
    published_date: string | null;
    platform_metrics: PlatformMetrics;
    market_context: MarketContext;
    transcript_or_content: string;
    comment_content: string | null;
    extracted_data: ExtractedStrategy;
    quality_metrics: QualityMetrics;
    created_at: string;
    updated_at: string;
}

// ============================================================================
// API Types
// ============================================================================

export interface ExtractionResponse {
    success: boolean;
    source: Source | null;
    error: string | null;
}

export type ExtractionStep =
    | 'fetching_content'
    | 'analyzing_structure'
    | 'extracting_strategy'
    | 'calculating_scores'
    | 'enriching_context'
    | 'complete'
    | 'error';

export interface DiscoveryCandidate {
    url: string;
    title: string;
    author: string;
    source_type: 'youtube' | 'reddit' | 'article';
    quality_tier: 'high' | 'medium' | 'low';
    quality_signals: string[];
    metrics: Record<string, number>;
}

export interface ConsensusItem {
    topic: string;
    consensus_value: string | null;
    agreement_rate: number;
    positions: Array<{
        value: string;
        source_count: number;
        sources: string[];
    }>;
    sources: string[];
}

export interface Controversy {
    topic: string;
    positions: Array<{
        value: string;
        source_count: number;
        sources: string[];
    }>;
}
