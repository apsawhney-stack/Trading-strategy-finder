import type { Source } from '../types';
import './BacktestabilityCard.css';

interface BacktestabilityCardProps {
    source: Source;
}

const REQUIRED_PARAMS = [
    { key: 'underlying', label: 'Underlying', path: 'setup_rules.underlying' },
    { key: 'dte', label: 'DTE Range', path: 'setup_rules.dte' },
    { key: 'delta', label: 'Delta Target', path: 'setup_rules.delta' },
    { key: 'strike', label: 'Strike Selection', path: 'setup_rules.strike_selection' },
    { key: 'profit', label: 'Profit Target %', path: 'management_rules.profit_target' },
    { key: 'stop', label: 'Stop Loss', path: 'management_rules.stop_loss' },
];

const PLATFORM_REQUIREMENTS: Record<string, string[]> = {
    'tastytrade': ['underlying', 'dte', 'delta', 'profit', 'stop'],
    'thinkorswim': ['underlying', 'dte', 'delta', 'strike', 'profit'],
    'optionstrat': ['underlying', 'dte', 'strike', 'profit', 'stop'],
};

function getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, key) => acc?.[key], obj);
}

export function BacktestabilityCard({ source }: BacktestabilityCardProps) {
    const data = source.extracted_data;

    // Check which params are present
    const presentParams = REQUIRED_PARAMS.filter(param => {
        const field = getNestedValue(data, param.path);
        return field?.value || field?.value_range;
    }).map(p => p.key);

    // Calculate completeness for each platform
    const platformScores = Object.entries(PLATFORM_REQUIREMENTS).map(([platform, required]) => {
        const matched = required.filter(req => presentParams.includes(req));
        const score = (matched.length / required.length) * 100;
        return { platform, score, matched: matched.length, total: required.length };
    });

    const overallScore = Math.round(
        (presentParams.length / REQUIRED_PARAMS.length) * 100
    );

    const getScoreClass = (score: number) =>
        score >= 80 ? 'high' : score >= 50 ? 'medium' : 'low';

    return (
        <div className="backtestability-card">
            <div className="backtest-header">
                <h4>Backtest Ready?</h4>
                <div className={`backtest-score score-${getScoreClass(overallScore)}`}>
                    {overallScore}%
                </div>
            </div>

            <div className="param-checklist">
                {REQUIRED_PARAMS.map(param => {
                    const field = getNestedValue(data, param.path);
                    const hasValue = field?.value || field?.value_range;

                    return (
                        <div
                            key={param.key}
                            className={`param-item ${hasValue ? 'present' : 'missing'}`}
                        >
                            <span className="param-icon">{hasValue ? '✓' : '○'}</span>
                            <span className="param-label">{param.label}</span>
                            {hasValue && (
                                <span className="param-value data-value">
                                    {field.value || `${field.value_range[0]}-${field.value_range[1]}`}
                                </span>
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="platform-matches">
                <h5>Platform Compatibility</h5>
                {platformScores.map(({ platform, score, matched, total }) => (
                    <div key={platform} className="platform-item">
                        <span className="platform-name">{platform}</span>
                        <div className="platform-bar">
                            <div
                                className={`platform-fill ${getScoreClass(score)}`}
                                style={{ width: `${score}%` }}
                            />
                        </div>
                        <span className="platform-score">{matched}/{total}</span>
                    </div>
                ))}
            </div>

            {overallScore < 80 && (
                <div className="backtest-warning">
                    ⚠️ Missing parameters may limit backtest accuracy
                </div>
            )}
        </div>
    );
}
