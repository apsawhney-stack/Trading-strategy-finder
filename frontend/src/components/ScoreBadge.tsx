import './ScoreBadge.css';

interface ScoreBadgeProps {
    label: string;
    score: number;
}

export function ScoreBadge({ label, score }: ScoreBadgeProps) {
    const tier = score >= 7 ? 'high' : score >= 4 ? 'medium' : 'low';

    return (
        <div className={`score-badge score-${tier}`}>
            <span className="score-label">{label}</span>
            <span className="score-value">{score.toFixed(1)}</span>
        </div>
    );
}
