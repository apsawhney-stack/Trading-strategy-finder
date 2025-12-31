import { useState } from 'react';
import type { Source } from '../types';
import { ScoreBadge } from './ScoreBadge';
import './SourceCard.css';

interface SourceCardProps {
    source: Source;
    onClick?: () => void;
    onDelete?: (id: string) => Promise<boolean>;
}

export function SourceCard({ source, onClick, onDelete }: SourceCardProps) {
    const { extracted_data: data, quality_metrics: quality } = source;
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const sourceIcon = {
        youtube: '📹',
        reddit: '📄',
        article: '🌐',
    }[source.source_type];

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return null;
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    // Format DTE nicely
    const formatDTE = (dte: number | string | null | undefined) => {
        if (dte === null || dte === undefined) return null;
        const val = typeof dte === 'string' ? parseInt(dte) : dte;
        if (isNaN(val)) return String(dte);
        if (val === 0) return '0 DTE';
        return `${val} DTE`;
    };

    // Format delta nicely
    const formatDelta = (delta: number | string | null | undefined) => {
        if (delta === null || delta === undefined) return null;
        const val = typeof delta === 'string' ? parseFloat(delta) : delta;
        if (isNaN(val)) return String(delta);
        return val < 1 ? `${Math.round(val * 100)}Δ` : `${val}Δ`;
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

        if (!success) {
            setShowDeleteConfirm(false);
        }
    };

    const handleCancelDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowDeleteConfirm(false);
    };

    return (
        <div className="source-card card" onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
            <div className="source-header">
                <div className="source-info">
                    <span className="source-icon">{sourceIcon}</span>
                    <div className="source-meta">
                        <h4 className="source-title">{source.title || data.strategy_name?.value || 'Unknown Strategy'}</h4>
                        <span className="source-author text-muted">{source.author || 'Unknown Author'}</span>
                    </div>
                </div>
                <div className="source-scores">
                    <ScoreBadge label="Spec" score={quality.specificity_score} />
                    <ScoreBadge label="Trust" score={quality.trust_score} />
                </div>
            </div>

            {/* Strategy details in a clean grid */}
            <div className="source-details">
                <div className="detail-grid">
                    {data.setup_rules?.underlying?.value && (
                        <div className="detail-item">
                            <span className="data-label">Underlying</span>
                            <span className="data-value highlight">{data.setup_rules.underlying.value}</span>
                        </div>
                    )}
                    {data.setup_rules?.dte?.value !== undefined && data.setup_rules?.dte?.value !== null && (
                        <div className="detail-item">
                            <span className="data-label">Expiration</span>
                            <span className="data-value">{formatDTE(data.setup_rules.dte.value)}</span>
                        </div>
                    )}
                    {data.setup_rules?.delta?.value && (
                        <div className="detail-item">
                            <span className="data-label">Delta</span>
                            <span className="data-value">{formatDelta(data.setup_rules.delta.value)}</span>
                        </div>
                    )}
                    {data.management_rules?.profit_target?.value && (
                        <div className="detail-item">
                            <span className="data-label">Target</span>
                            <span className="data-value success">{data.management_rules.profit_target.value}</span>
                        </div>
                    )}
                    {data.management_rules?.stop_loss?.value && (
                        <div className="detail-item">
                            <span className="data-label">Stop</span>
                            <span className="data-value danger">{data.management_rules.stop_loss.value}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Key insights first - more valuable than gaps */}
            {data.key_insights?.length > 0 && (
                <div className="source-insights">
                    <span className="data-label">💡 Key Insights</span>
                    <ul className="insights-list">
                        {data.key_insights.slice(0, 2).map((insight, i) => (
                            <li key={i}>{insight}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Gaps as warnings */}
            {quality.gaps.length > 0 && (
                <div className="source-gaps">
                    <span className="data-label">⚠️ Missing Info</span>
                    <div className="gaps-list">
                        {quality.gaps.slice(0, 3).map((gap, i) => (
                            <span key={i} className="gap-tag">{gap}</span>
                        ))}
                    </div>
                </div>
            )}

            <div className="source-footer">
                <span className="text-muted">
                    {formatDate(source.published_date)}
                    {source.platform_metrics?.views && ` • ${source.platform_metrics.views.toLocaleString()} views`}
                    {source.platform_metrics?.upvotes && ` • ${source.platform_metrics.upvotes} upvotes`}
                </span>
                <div className="source-actions">
                    {onDelete && !showDeleteConfirm && (
                        <button
                            className="btn-icon btn-delete"
                            onClick={handleDeleteClick}
                            title="Delete source"
                        >
                            🗑️
                        </button>
                    )}
                    {showDeleteConfirm && (
                        <div className="delete-confirm">
                            <span className="confirm-text">Delete?</span>
                            <button
                                className="btn-confirm btn-yes"
                                onClick={handleConfirmDelete}
                                disabled={isDeleting}
                            >
                                {isDeleting ? '...' : 'Yes'}
                            </button>
                            <button
                                className="btn-confirm btn-no"
                                onClick={handleCancelDelete}
                                disabled={isDeleting}
                            >
                                No
                            </button>
                        </div>
                    )}
                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-link" onClick={e => e.stopPropagation()}>
                        View Source →
                    </a>
                </div>
            </div>
        </div>
    );
}
