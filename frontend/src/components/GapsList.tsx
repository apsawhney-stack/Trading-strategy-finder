import './GapsList.css';

interface GapsListProps {
    gaps: string[];
}

const GAP_ICONS: Record<string, string> = {
    'stop': '🛑',
    'loss': '🛑',
    'adjustment': '🔄',
    'defense': '🔄',
    'failure': '⚠️',
    'backtest': '📊',
    'sizing': '💰',
    'bpe': '💰',
    'criteria': '🎯',
    'entry': '🎯',
    'dte': '📅',
    'strike': '🎯',
    'default': '❓',
};

function getGapIcon(gap: string): string {
    const gapLower = gap.toLowerCase();
    for (const [key, icon] of Object.entries(GAP_ICONS)) {
        if (gapLower.includes(key)) {
            return icon;
        }
    }
    return GAP_ICONS.default;
}

export function GapsList({ gaps }: GapsListProps) {
    if (!gaps || gaps.length === 0) {
        return (
            <div className="gaps-list gaps-empty">
                <span className="gaps-check">✓</span>
                <span>No major gaps detected</span>
            </div>
        );
    }

    return (
        <div className="gaps-list">
            <h4>Missing Information</h4>
            <ul className="gaps-items">
                {gaps.map((gap, index) => (
                    <li key={index} className="gap-item">
                        <span className="gap-icon">{getGapIcon(gap)}</span>
                        <span className="gap-text">{gap}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
