import type { Source } from '../types';
import { ScoreBadge } from './ScoreBadge';
import './SourceCard.css';

interface SourceCardProps {
    source: Source;
    onClick?: () => void;
}

export function SourceCard({ source, onClick }: SourceCardProps) {
    const { extracted_data: data, quality_metrics: quality } = source;

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

    return (
        <div className="source-card card" onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
            <div className="source-header">
                <div className="source-info">
                    <span className="source-icon">{sourceIcon}</span>
                    <div className="source-meta">
                        <h4 className="source-title">{source.title || data.strategy_name?.value || 'Unknown Strategy'}</h4>
                        <span className="source-author text-muted">{source.author}</span>
                    </div>
                </div>
                <div className="source-scores">
                    <ScoreBadge label="Spec" score={quality.specificity_score} />
                    <ScoreBadge label="Trust" score={quality.trust_score} />
                </div>
            </div>

            {data.strategy_name?.value && (
                <div className="source-strategy">
                    <span className="data-label">Strategy</span>
                    <span className="data-value">{data.strategy_name.value}</span>
                    {data.variation?.value && (
                        <span className="text-muted"> • {data.variation.value}</span>
                    )}
                </div>
            )}

            <div className="source-details">
                <div className="detail-grid">
                    {data.setup_rules?.underlying?.value && (
                        <div className="detail-item">
                            <span className="data-label">Underlying</span>
                            <span className="data-value">{data.setup_rules.underlying.value}</span>
                        </div>
                    )}
                    {data.setup_rules?.dte?.value && (
                        <div className="detail-item">
                            <span className="data-label">DTE</span>
                            <span className="data-value">{data.setup_rules.dte.value}</span>
                        </div>
                    )}
                    {data.setup_rules?.delta?.value && (
                        <div className="detail-item">
                            <span className="data-label">Delta</span>
                            <span className="data-value">{data.setup_rules.delta.value}</span>
                        </div>
                    )}
                    {data.management_rules?.profit_target?.value && (
                        <div className="detail-item">
                            <span className="data-label">Profit</span>
                            <span className="data-value">{data.management_rules.profit_target.value}</span>
                        </div>
                    )}
                    {data.management_rules?.stop_loss?.value && (
                        <div className="detail-item">
                            <span className="data-label">Stop</span>
                            <span className="data-value">{data.management_rules.stop_loss.value}</span>
                        </div>
                    )}
                </div>
            </div>

            {quality.gaps.length > 0 && (
                <div className="source-gaps">
                    <span className="data-label">Gaps</span>
                    <div className="gaps-list">
                        {quality.gaps.slice(0, 3).map((gap, i) => (
                            <span key={i} className="gap-tag">⚠️ {gap}</span>
                        ))}
                    </div>
                </div>
            )}

            {data.key_insights?.length > 0 && (
                <div className="source-insights">
                    <span className="data-label">Key Insights</span>
                    <ul className="insights-list">
                        {data.key_insights.slice(0, 3).map((insight, i) => (
                            <li key={i}>{insight}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="source-footer">
                <span className="text-muted">
                    {formatDate(source.published_date)}
                    {source.platform_metrics?.views && ` • ${source.platform_metrics.views.toLocaleString()} views`}
                    {source.platform_metrics?.upvotes && ` • ${source.platform_metrics.upvotes} upvotes`}
                </span>
                <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-link" onClick={e => e.stopPropagation()}>
                    View Source →
                </a>
            </div>
        </div>
    );
}
