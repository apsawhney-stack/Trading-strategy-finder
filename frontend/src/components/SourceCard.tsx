import { useState } from 'react';
import type { Source } from '../types';
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

    // Combined score (average of specificity and trust)
    const specScore = quality?.specificity_score || 0;
    const trustScore = quality?.trust_score || 0;
    const combinedScore = ((specScore + trustScore) / 2);

    // Score tier for color coding
    const scoreTier = combinedScore >= 7 ? 'high' : combinedScore >= 4 ? 'medium' : 'low';

    // Get underlying and DTE for badges
    const underlying = data?.setup_rules?.underlying?.value;
    const dte = data?.setup_rules?.dte?.value;
    const dteLabel = dte !== undefined && dte !== null ? `${dte} DTE` : null;

    // Build title from strategy name or source title
    const title = data?.strategy_name?.value || source.title || 'Unknown Strategy';

    // Include underlying and DTE in display title if available
    const displayTitle = [
        title,
        underlying,
        dteLabel
    ].filter(Boolean).join(' ');

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

    const formatDelta = (delta: number | string | null | undefined) => {
        if (delta === null || delta === undefined) return null;
        const val = typeof delta === 'string' ? parseFloat(delta) : delta;
        if (isNaN(val)) return String(delta);
        return val < 1 ? `${Math.round(val * 100)}Δ` : `${val}Δ`;
    };

    return (
        <div className={`source-card ${scoreTier} ${isExpanded ? 'expanded' : ''}`}>
            {/* Card Header */}
            <div className="card-header" onClick={handleToggle}>
                <button className="expand-btn" aria-label={isExpanded ? 'Collapse' : 'Expand'}>
                    <span className={`chevron ${isExpanded ? 'up' : 'down'}`}>▼</span>
                </button>

                <span className="source-icon">{sourceIcon}</span>

                <div className="card-content">
                    <h4 className="card-title">{displayTitle}</h4>
                    <span className="card-author">Author: {source.author || 'Unknown'}</span>
                </div>

                {/* Symbol Badge */}
                {underlying && (
                    <span className={`symbol-badge ${underlying.toLowerCase()}`}>{underlying}</span>
                )}

                {/* Combined Score */}
                <div className={`score-badge ${scoreTier}`}>
                    {combinedScore.toFixed(1)}
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="card-body" onClick={onClick}>
                    <div className="params-grid">
                        {underlying && (
                            <div className="param-item">
                                <span className="param-label">Underlying</span>
                                <span className="param-value">{underlying}</span>
                            </div>
                        )}
                        {dteLabel && (
                            <div className="param-item">
                                <span className="param-label">DTE</span>
                                <span className="param-value">{dteLabel}</span>
                            </div>
                        )}
                        {data?.setup_rules?.delta?.value && (
                            <div className="param-item">
                                <span className="param-label">Delta</span>
                                <span className="param-value">{formatDelta(data.setup_rules.delta.value)}</span>
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

                    {data?.key_insights && data.key_insights.length > 0 && (
                        <div className="insights-section">
                            <span className="section-label">💡 Key Insights</span>
                            <ul className="insights-list">
                                {data.key_insights.slice(0, 2).map((insight, i) => (
                                    <li key={i}>{insight}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div className="card-actions">
                        {onDelete && !showDeleteConfirm && (
                            <button className="btn-action btn-delete" onClick={handleDeleteClick}>
                                🗑️ Delete
                            </button>
                        )}
                        {showDeleteConfirm && (
                            <div className="delete-confirm">
                                <span>Delete this source?</span>
                                <button className="btn-yes" onClick={handleConfirmDelete} disabled={isDeleting}>
                                    {isDeleting ? '...' : 'Yes'}
                                </button>
                                <button className="btn-no" onClick={handleCancelDelete} disabled={isDeleting}>
                                    No
                                </button>
                            </div>
                        )}
                        <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-action btn-link"
                            onClick={e => e.stopPropagation()}
                        >
                            View Source →
                        </a>
                    </div>
                </div>
            )}
        </div>
    );
}
