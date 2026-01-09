import { useState } from 'react';
import type { Source } from '../types';
import './SourceCard.css';

interface SourceCardProps {
  source: Source;
  onClick?: () => void;
  onDelete?: (id: string) => Promise<boolean>;
  defaultExpanded?: boolean;
}

export function SourceCard({
  source,
  onClick,
  onDelete,
  defaultExpanded = false,
}: SourceCardProps) {
  const { extracted_data: data, quality_metrics: quality } = source;
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Platform-specific icons (SVG inline)
  const sourceIcons: Record<string, React.ReactNode> = {
    youtube: (
      <svg className="platform-icon youtube" viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
      </svg>
    ),
    reddit: (
      <svg className="platform-icon reddit" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z" />
      </svg>
    ),
    article: (
      <svg className="platform-icon article" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
      </svg>
    ),
  };
  const sourceIcon = sourceIcons[source.source_type] || sourceIcons.article;

  // Dynamic author label based on source type
  const authorLabel =
    {
      youtube: 'Channel',
      reddit: 'Subreddit',
      article: 'Author',
    }[source.source_type] || 'Source';

  // Combined score (average of specificity and trust)
  const specScore = quality?.specificity_score || 0;
  const trustScore = quality?.trust_score || 0;
  const combinedScore = (specScore + trustScore) / 2;

  // Score tier for color coding
  const scoreTier = combinedScore >= 7 ? 'high' : combinedScore >= 4 ? 'medium' : 'low';

  // Get underlying and DTE for badges
  const underlying = data?.setup_rules?.underlying?.value;
  const dte = data?.setup_rules?.dte?.value;
  const dteLabel = dte !== undefined && dte !== null ? `${dte} DTE` : null;

  // Build title from strategy name or source title
  const title = data?.strategy_name?.value || source.title || 'Unknown Strategy';

  // Include underlying and DTE in display title if available
  const displayTitle = [title, underlying, dteLabel].filter(Boolean).join(' ');

  const handleToggle = (e: React.MouseEvent | React.KeyboardEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle(e);
    }
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
      <div
        className="card-header"
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        aria-label={`${isExpanded ? 'Collapse' : 'Expand'} details for ${displayTitle}`}
      >
        <div className="expand-btn" aria-hidden="true">
          <span className={`chevron ${isExpanded ? 'up' : 'down'}`}>▼</span>
        </div>

        <span className="source-icon">{sourceIcon}</span>

        <div className="card-content">
          <h4 className="card-title">{displayTitle}</h4>
          <span className="card-author">
            {authorLabel}: {source.author || 'Unknown'}
          </span>
        </div>

        {/* Quick Stats Row */}
        <div className="quick-stats">
          {/* Symbol Badge */}
          {underlying && (
            <span className={`symbol-badge ${underlying.toLowerCase()}`}>{underlying}</span>
          )}

          {/* DTE Badge */}
          {dteLabel && <span className="stat-badge dte">{dteLabel}</span>}

          {/* Delta */}
          {data?.setup_rules?.delta?.value && (
            <span className="stat-badge delta">{formatDelta(data.setup_rules.delta.value)}</span>
          )}

          {/* Profit Target */}
          {data?.management_rules?.profit_target?.value && (
            <span className="stat-badge target">
              🎯{' '}
              {typeof data.management_rules.profit_target.value === 'string'
                ? data.management_rules.profit_target.value.substring(0, 15) +
                  (data.management_rules.profit_target.value.length > 15 ? '...' : '')
                : data.management_rules.profit_target.value}
            </span>
          )}

          {/* Win Rate */}
          {data?.risk_profile?.win_rate?.value && (
            <span className="stat-badge winrate">📈 {data.risk_profile.win_rate.value}%</span>
          )}
        </div>

        {/* Combined Score */}
        <div className={`score-badge ${scoreTier}`}>{combinedScore.toFixed(1)}</div>
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
                <span className="param-value success">
                  {data.management_rules.profit_target.value}
                </span>
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
              onClick={(e) => e.stopPropagation()}
            >
              View Source →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
