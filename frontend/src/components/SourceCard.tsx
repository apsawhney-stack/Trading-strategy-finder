import { useState } from 'react';
import type { Source } from '../types';
import { ScoreBadge } from './ScoreBadge';
import './SourceCard.css';

interface SourceCardProps {
    source: Source;
    onClick?: () => void;
    onDelete?: (id: string) => Promise<boolean>;
    defaultExpanded?: boolean;
}

export function SourceCard({ source, onClick, onDelete, defaultExpanded = false }: SourceCardProps) {
    const { extracted_data: data, quality_metrics: quality } = source;
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const sourceIcon = {
        youtube: '📹',
        reddit: '💬',
        article: '📰',
    }[source.source_type] || '📄';

    const formatDTE = (dte: number | string | null | undefined) => {
        if (dte === null || dte === undefined) return null;
        const val = typeof dte === 'string' ? parseInt(dte) : dte;
        if (isNaN(val)) return String(dte);
        if (val === 0) return '0 DTE';
        return `${val} DTE`;
    };

    const formatDelta = (delta: number | string | null | undefined) => {
        if (delta === null || delta === undefined) return null;
        const val = typeof delta === 'string' ? parseFloat(delta) : delta;
        if (isNaN(val)) return String(delta);
        return val < 1 ? `${Math.round(val * 100)}Δ` : `${val}Δ`;
    };

    const handleToggle = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsExpanded(!isExpanded);
    };

    const handleDeleteClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowDeleteConfirm(true);
    };

    const handleConfirmDelete = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!onDelete) return;
        setIsDeleting(true);
        const success = await onDelete(source.id);
        setIsDeleting(false);
        if (!success) setShowDeleteConfirm(false);
    };

    const handleCancelDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowDeleteConfirm(false);
    };

    // Get underlying for badge display
    const underlying = data?.setup_rules?.underlying?.value;
    const dte = data?.setup_rules?.dte?.value;

    return (
        <div className={`source-card card ${isExpanded ? 'expanded' : 'collapsed'}`}>
            {/* Collapsed Header - Always Visible */}
            <div className="card-header" onClick={handleToggle}>
                <button className="expand-btn" aria-label={isExpanded ? 'Collapse' : 'Expand'}>
                    <span className={`chevron ${isExpanded ? 'up' : 'down'}`}>▼</span>
                </button>

                <span className="source-icon">{sourceIcon}</span>

                <div className="card-title-section">
                    <h4 className="card-title">{source.title || data?.strategy_name?.value || 'Unknown Strategy'}</h4>
                    <span className="card-author">{source.author || 'Unknown'}</span>
                </div>

                {/* Quick badges in collapsed view */}
                <div className="quick-badges">
                    {underlying && <span className="badge badge-underlying">{underlying}</span>}
                    {dte !== undefined && dte !== null && <span className="badge badge-dte">{formatDTE(dte)}</span>}
                </div>

                <div className="card-scores">
                    <ScoreBadge label="Spec" score={quality?.specificity_score || 0} />
                    <ScoreBadge label="Trust" score={quality?.trust_score || 0} />
                </div>

                {/* Actions in header when collapsed */}
                <div className="card-actions">
                    {onDelete && !showDeleteConfirm && (
                        <button className="btn-icon btn-delete" onClick={handleDeleteClick} title="Delete">
                            🗑️
                        </button>
                    )}
                    {showDeleteConfirm && (
                        <div className="delete-confirm" onClick={e => e.stopPropagation()}>
                            <button className="btn-confirm btn-yes" onClick={handleConfirmDelete} disabled={isDeleting}>
                                {isDeleting ? '...' : '✓'}
                            </button>
                            <button className="btn-confirm btn-no" onClick={handleCancelDelete} disabled={isDeleting}>
                                ✗
                            </button>
                        </div>
                    )}
                    <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-icon btn-link"
                        onClick={e => e.stopPropagation()}
                        title="View source"
                    >
                        ↗
                    </a>
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="card-body" onClick={onClick}>
                    {/* Strategy Parameters Grid */}
                    <div className="params-grid">
                        {underlying && (
                            <div className="param-item">
                                <span className="param-label">Underlying</span>
                                <span className="param-value highlight">{underlying}</span>
                            </div>
                        )}
                        {dte !== undefined && dte !== null && (
                            <div className="param-item">
                                <span className="param-label">DTE</span>
                                <span className="param-value">{formatDTE(dte)}</span>
                            </div>
                        )}
                        {data?.setup_rules?.delta?.value && (
                            <div className="param-item">
                                <span className="param-label">Delta</span>
                                <span className="param-value">{formatDelta(data.setup_rules.delta.value)}</span>
                            </div>
                        )}
                        {data?.setup_rules?.width?.value && (
                            <div className="param-item">
                                <span className="param-label">Width</span>
                                <span className="param-value">{data.setup_rules.width.value} pts</span>
                            </div>
                        )}
                        {data?.management_rules?.profit_target?.value && (
                            <div className="param-item">
                                <span className="param-label">Target</span>
                                <span className="param-value success">{data.management_rules.profit_target.value}</span>
                            </div>
                        )}
                        {data?.management_rules?.stop_loss?.value && (
                            <div className="param-item">
                                <span className="param-label">Stop</span>
                                <span className="param-value danger">{data.management_rules.stop_loss.value}</span>
                            </div>
                        )}
                    </div>

                    {/* Key Insights */}
                    {data?.key_insights && data.key_insights.length > 0 && (
                        <div className="insights-section">
                            <span className="section-label">💡 Key Insights</span>
                            <ul className="insights-list">
                                {data.key_insights.slice(0, 3).map((insight, i) => (
                                    <li key={i}>{insight}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Gaps/Warnings */}
                    {quality?.gaps && quality.gaps.length > 0 && (
                        <div className="gaps-section">
                            <span className="section-label">⚠️ Missing Info</span>
                            <div className="gaps-list">
                                {quality.gaps.slice(0, 4).map((gap, i) => (
                                    <span key={i} className="gap-tag">{gap}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
