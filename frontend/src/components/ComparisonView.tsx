import { useState } from 'react';
import type { Source } from '../types';
import { ScoreBadge } from './ScoreBadge';
import './ComparisonView.css';

interface ComparisonViewProps {
    sources: Source[];
    onClose: () => void;
}

const COMPARISON_FIELDS = [
    { key: 'underlying', label: 'Underlying', path: 'setup_rules.underlying' },
    { key: 'dte', label: 'DTE', path: 'setup_rules.dte' },
    { key: 'delta', label: 'Delta', path: 'setup_rules.delta' },
    { key: 'strike', label: 'Strike Selection', path: 'setup_rules.strike_selection' },
    { key: 'width', label: 'Width', path: 'setup_rules.width' },
    { key: 'entry', label: 'Entry Criteria', path: 'setup_rules.entry_criteria' },
    { key: 'profit', label: 'Profit Target', path: 'management_rules.profit_target' },
    { key: 'stop', label: 'Stop Loss', path: 'management_rules.stop_loss' },
    { key: 'adjustments', label: 'Adjustments', path: 'management_rules.adjustment_rules' },
    { key: 'winrate', label: 'Win Rate', path: 'risk_profile.win_rate' },
];

function getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, key) => acc?.[key], obj);
}

export function ComparisonView({ sources, onClose }: ComparisonViewProps) {
    const [selectedSources, setSelectedSources] = useState<Set<string>>(
        new Set(sources.slice(0, 4).map(s => s.id))
    );

    const toggleSource = (id: string) => {
        setSelectedSources(prev => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else if (next.size < 4) {
                next.add(id);
            }
            return next;
        });
    };

    const compareSources = sources.filter(s => selectedSources.has(s.id));

    return (
        <div className="comparison-overlay" onClick={onClose}>
            <div className="comparison-modal" onClick={e => e.stopPropagation()}>
                <header className="comparison-header">
                    <h2>Compare Sources</h2>
                    <button className="close-btn" onClick={onClose}>✕</button>
                </header>

                <div className="source-selector">
                    <span className="selector-label">Select up to 4 sources:</span>
                    <div className="source-chips">
                        {sources.map(source => (
                            <button
                                key={source.id}
                                className={`source-chip ${selectedSources.has(source.id) ? 'selected' : ''}`}
                                onClick={() => toggleSource(source.id)}
                            >
                                {source.extracted_data?.strategy_name?.value || source.title}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="comparison-table-container">
                    <table className="comparison-table">
                        <thead>
                            <tr>
                                <th className="field-header">Field</th>
                                {compareSources.map(source => (
                                    <th key={source.id} className="source-header">
                                        <div className="source-header-content">
                                            <span className="source-name">
                                                {source.extracted_data?.strategy_name?.value || source.title}
                                            </span>
                                            <span className="source-author">{source.author}</span>
                                            <div className="source-scores">
                                                <ScoreBadge label="Spec" score={source.quality_metrics.specificity_score} />
                                            </div>
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {COMPARISON_FIELDS.map(field => (
                                <tr key={field.key}>
                                    <td className="field-label">{field.label}</td>
                                    {compareSources.map(source => {
                                        const fieldData = getNestedValue(source.extracted_data, field.path);
                                        const value = fieldData?.value || fieldData?.value_range
                                            ? (fieldData.value_range
                                                ? `${fieldData.value_range[0]}-${fieldData.value_range[1]}`
                                                : fieldData.value)
                                            : '—';
                                        const confidence = fieldData?.confidence || 0;

                                        return (
                                            <td
                                                key={source.id}
                                                className={`field-value ${confidence < 0.5 ? 'low-confidence' : ''}`}
                                            >
                                                <span className="data-value">{value}</span>
                                                {confidence > 0 && (
                                                    <span className={`confidence-indicator conf-${confidence >= 0.8 ? 'high' :
                                                            confidence >= 0.5 ? 'medium' : 'low'
                                                        }`} />
                                                )}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <footer className="comparison-footer">
                    <span className="comparison-hint">
                        💡 Green = high confidence, Yellow = medium, Red = low
                    </span>
                </footer>
            </div>
        </div>
    );
}
