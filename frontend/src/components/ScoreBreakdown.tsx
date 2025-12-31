import './ScoreBreakdown.css';

interface ScoreBreakdownProps {
    breakdown: {
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
    };
}

const CRITERIA = [
    { key: 'strike_selection', label: 'Strike Selection', weight: 12 },
    { key: 'entry_criteria', label: 'Entry Criteria', weight: 12 },
    { key: 'stop_loss', label: 'Stop Loss', weight: 12 },
    { key: 'adjustments', label: 'Adjustments', weight: 12 },
    { key: 'buying_power_effect', label: 'Buying Power', weight: 12 },
    { key: 'profit_target', label: 'Profit Target', weight: 8 },
    { key: 'dte', label: 'DTE', weight: 8 },
    { key: 'failure_modes', label: 'Failure Modes', weight: 8 },
    { key: 'real_pnl', label: 'Real P&L', weight: 8 },
    { key: 'backtest_evidence', label: 'Backtest', weight: 8 },
];

export function ScoreBreakdown({ breakdown }: ScoreBreakdownProps) {
    const getScoreClass = (score: number) => {
        if (score >= 7) return 'high';
        if (score >= 4) return 'medium';
        return 'low';
    };

    return (
        <div className="score-breakdown">
            <h4>Specificity Breakdown</h4>
            <div className="criteria-list">
                {CRITERIA.map(({ key, label, weight }) => {
                    const score = breakdown[key as keyof typeof breakdown] || 0;
                    const scoreClass = getScoreClass(score);

                    return (
                        <div key={key} className="criterion-row">
                            <div className="criterion-info">
                                <span className="criterion-label">{label}</span>
                                <span className="criterion-weight">{weight}%</span>
                            </div>
                            <div className="criterion-bar-container">
                                <div
                                    className={`criterion-bar criterion-${scoreClass}`}
                                    style={{ width: `${score * 10}%` }}
                                />
                            </div>
                            <span className={`criterion-score score-${scoreClass}`}>
                                {score.toFixed(1)}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
