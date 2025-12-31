import { useState } from 'react';
import type { Source, ExtractedField, ExtractedNumericField } from '../types';
import { ScoreBadge } from './ScoreBadge';
import './SourceDetail.css';

interface SourceDetailProps {
    source: Source;
    onClose: () => void;
}

function FieldValue({
    field,
    label
}: {
    field: ExtractedField | ExtractedNumericField | undefined;
    label: string
}) {
    if (!field || field.interpretation === 'missing') {
        return (
            <div className="field-item field-missing">
                <span className="field-label">{label}</span>
                <span className="field-value">—</span>
            </div>
        );
    }

    const confidenceClass =
        field.confidence >= 0.8 ? 'high' :
            field.confidence >= 0.5 ? 'medium' : 'low';

    const value = 'value_range' in field && field.value_range
        ? `${field.value_range[0]}-${field.value_range[1]}`
        : String(field.value);

    return (
        <div className="field-item" title={field.source_quote || undefined}>
            <span className="field-label">{label}</span>
            <div className="field-value-wrapper">
                <span className="field-value data-value">{value}</span>
                <span className={`confidence-dot confidence-${confidenceClass}`} />
                <span className={`interpretation-tag interp-${field.interpretation}`}>
                    {field.interpretation}
                </span>
            </div>
            {field.source_quote && (
                <div className="field-quote">"{field.source_quote}"</div>
            )}
        </div>
    );
}

export function SourceDetail({ source, onClose }: SourceDetailProps) {
    const { extracted_data: data, quality_metrics: quality } = source;
    const [activeTab, setActiveTab] = useState<'setup' | 'management' | 'risk' | 'insights'>('setup');

    return (
        <div className="source-detail-overlay" onClick={onClose}>
            <div className="source-detail-modal" onClick={e => e.stopPropagation()}>
                <header className="detail-header">
                    <div className="detail-header-left">
                        <h2>{data.strategy_name?.value || source.title}</h2>
                        <span className="text-muted">{source.author}</span>
                    </div>
                    <div className="detail-header-right">
                        <ScoreBadge label="Spec" score={quality.specificity_score} />
                        <ScoreBadge label="Trust" score={quality.trust_score} />
                        <button className="close-btn" onClick={onClose}>✕</button>
                    </div>
                </header>

                <nav className="detail-tabs">
                    {(['setup', 'management', 'risk', 'insights'] as const).map(tab => (
                        <button
                            key={tab}
                            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab)}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </nav>

                <div className="detail-content">
                    {activeTab === 'setup' && (
                        <div className="fields-grid">
                            <FieldValue field={data.setup_rules?.underlying} label="Underlying" />
                            <FieldValue field={data.setup_rules?.option_type} label="Option Type" />
                            <FieldValue field={data.setup_rules?.strike_selection} label="Strike Selection" />
                            <FieldValue field={data.setup_rules?.dte} label="DTE" />
                            <FieldValue field={data.setup_rules?.delta} label="Delta" />
                            <FieldValue field={data.setup_rules?.width} label="Width" />
                            <FieldValue field={data.setup_rules?.entry_criteria} label="Entry Criteria" />
                            <FieldValue field={data.setup_rules?.entry_timing} label="Entry Timing" />
                            <FieldValue field={data.setup_rules?.buying_power_effect} label="Buying Power Effect" />
                        </div>
                    )}

                    {activeTab === 'management' && (
                        <div className="fields-grid">
                            <FieldValue field={data.management_rules?.profit_target} label="Profit Target" />
                            <FieldValue field={data.management_rules?.stop_loss} label="Stop Loss" />
                            <FieldValue field={data.management_rules?.time_exit} label="Time Exit" />
                            <FieldValue field={data.management_rules?.adjustment_rules} label="Adjustments" />
                            <FieldValue field={data.management_rules?.rolling_rules} label="Rolling" />
                            <FieldValue field={data.management_rules?.defensive_maneuvers} label="Defense" />
                        </div>
                    )}

                    {activeTab === 'risk' && (
                        <div className="risk-section">
                            <div className="fields-grid">
                                <FieldValue field={data.risk_profile?.win_rate} label="Win Rate" />
                                <FieldValue field={data.risk_profile?.max_drawdown} label="Max Drawdown" />
                                <FieldValue field={data.risk_profile?.max_loss_per_trade} label="Max Loss/Trade" />
                                <FieldValue field={data.risk_profile?.risk_reward_ratio} label="Risk/Reward" />
                            </div>

                            {data.failure_analysis?.failure_modes_mentioned?.length > 0 && (
                                <div className="failure-modes">
                                    <h4>Failure Modes Mentioned</h4>
                                    <ul>
                                        {data.failure_analysis.failure_modes_mentioned.map((mode, i) => (
                                            <li key={i}>⚠️ {mode}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {data.performance_claims?.starting_capital?.value && (
                                <div className="pnl-claims">
                                    <h4>P&L Claims</h4>
                                    <div className="pnl-grid">
                                        <div>
                                            <span className="data-label">Starting</span>
                                            <span className="data-value">${data.performance_claims.starting_capital.value?.toLocaleString()}</span>
                                        </div>
                                        <div>
                                            <span className="data-label">Ending</span>
                                            <span className="data-value">${data.performance_claims.ending_capital?.value?.toLocaleString()}</span>
                                        </div>
                                        <div>
                                            <span className="data-label">Period</span>
                                            <span className="data-value">{data.performance_claims.time_period?.value}</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'insights' && (
                        <div className="insights-section">
                            {data.key_insights?.length > 0 && (
                                <div className="insight-block">
                                    <h4>💡 Key Insights</h4>
                                    <ul>
                                        {data.key_insights.map((insight, i) => (
                                            <li key={i}>{insight}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {data.warnings?.length > 0 && (
                                <div className="insight-block warnings">
                                    <h4>⚠️ Warnings</h4>
                                    <ul>
                                        {data.warnings.map((warning, i) => (
                                            <li key={i}>{warning}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {data.quotes?.length > 0 && (
                                <div className="insight-block quotes">
                                    <h4>💬 Notable Quotes</h4>
                                    <ul>
                                        {data.quotes.map((quote, i) => (
                                            <li key={i}>"{quote}"</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {quality.gaps?.length > 0 && (
                                <div className="insight-block gaps">
                                    <h4>❓ Missing Information</h4>
                                    <ul>
                                        {quality.gaps.map((gap, i) => (
                                            <li key={i}>{gap}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <footer className="detail-footer">
                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                        View Original Source
                    </a>
                </footer>
            </div>
        </div>
    );
}
