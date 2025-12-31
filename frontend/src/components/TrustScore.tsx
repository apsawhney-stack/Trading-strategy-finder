import './TrustScore.css';

interface TrustScoreProps {
    score: number;
    failureAnalysis?: {
        failure_modes_mentioned: string[];
        discusses_losses: boolean;
        max_drawdown_mentioned: number | null;
        bias_detected: boolean;
    };
}

export function TrustScore({ score, failureAnalysis }: TrustScoreProps) {
    const tier = score >= 7 ? 'high' : score >= 4 ? 'medium' : 'low';
    const tierLabel = score >= 7 ? 'Balanced' : score >= 4 ? 'Partial' : 'Biased';

    const indicators = [
        {
            label: 'Discusses Losses',
            active: failureAnalysis?.discusses_losses ?? false,
            icon: '📉',
        },
        {
            label: 'Shows Failure Modes',
            active: (failureAnalysis?.failure_modes_mentioned?.length ?? 0) > 0,
            icon: '⚠️',
        },
        {
            label: 'Mentions Drawdown',
            active: failureAnalysis?.max_drawdown_mentioned != null,
            icon: '📊',
        },
        {
            label: 'No Survivorship Bias',
            active: !(failureAnalysis?.bias_detected ?? true),
            icon: '✓',
        },
    ];

    return (
        <div className="trust-score">
            <div className="trust-header">
                <div className={`trust-badge trust-${tier}`}>
                    <span className="trust-value">{score.toFixed(1)}</span>
                    <span className="trust-label">{tierLabel}</span>
                </div>
                <h4>Trust Score</h4>
            </div>

            <div className="trust-indicators">
                {indicators.map((ind, i) => (
                    <div
                        key={i}
                        className={`trust-indicator ${ind.active ? 'active' : 'inactive'}`}
                    >
                        <span className="indicator-icon">{ind.active ? ind.icon : '○'}</span>
                        <span className="indicator-label">{ind.label}</span>
                    </div>
                ))}
            </div>

            {tier === 'low' && (
                <div className="trust-warning">
                    ⚠️ This source may have survivorship bias. Content focuses heavily on wins without discussing risks or failures.
                </div>
            )}
        </div>
    );
}
