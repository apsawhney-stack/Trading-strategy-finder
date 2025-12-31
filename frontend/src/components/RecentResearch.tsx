import { Link } from 'react-router-dom';
import type { Source } from '../types';
import './RecentResearch.css';

interface RecentResearchProps {
    sources: Source[];
    maxItems?: number;
}

export function RecentResearch({ sources, maxItems = 5 }: RecentResearchProps) {
    if (sources.length === 0) return null;

    const recentSources = sources.slice(0, maxItems);

    // Group by date
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 86400000).toDateString();

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr).toDateString();
        if (date === today) return 'Today';
        if (date === yesterday) return 'Yesterday';
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <section className="recent-research">
            <h3>Recent Research</h3>
            <div className="recent-list">
                {recentSources.map(source => (
                    <Link
                        key={source.id}
                        to={`/strategy/${encodeURIComponent(source.extracted_data?.strategy_name?.value || source.id)}`}
                        className="recent-item"
                    >
                        <span className="recent-icon">
                            {source.source_type === 'youtube' ? '📹' :
                                source.source_type === 'reddit' ? '📄' : '🌐'}
                        </span>
                        <div className="recent-info">
                            <span className="recent-title">
                                {source.extracted_data?.strategy_name?.value || source.title}
                            </span>
                            <span className="recent-meta">
                                {formatDate(source.created_at)} • {source.author}
                            </span>
                        </div>
                        <div className="recent-score">
                            <span className={`score-dot score-${source.quality_metrics.specificity_score >= 7 ? 'high' :
                                    source.quality_metrics.specificity_score >= 4 ? 'medium' : 'low'
                                }`} />
                            {source.quality_metrics.specificity_score.toFixed(1)}
                        </div>
                    </Link>
                ))}
            </div>
        </section>
    );
}
