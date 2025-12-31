import './MissingChecklist.css';

interface MissingChecklistProps {
    gaps: string[];
    onFindSources?: (gap: string) => void;
}

const GAP_CATEGORIES: Record<string, { icon: string; category: string; suggestion: string }> = {
    'stop': { icon: '🛑', category: 'Risk Management', suggestion: 'Look for videos mentioning "stop loss" or "max loss"' },
    'loss': { icon: '🛑', category: 'Risk Management', suggestion: 'Search for content about position sizing and risk limits' },
    'adjustment': { icon: '🔄', category: 'Trade Management', suggestion: 'Find content on rolling, adjusting, or defending trades' },
    'defense': { icon: '🔄', category: 'Trade Management', suggestion: 'Look for "what to do when trade goes against you"' },
    'entry': { icon: '🎯', category: 'Entry Rules', suggestion: 'Search for specific entry criteria and setups' },
    'criteria': { icon: '🎯', category: 'Entry Rules', suggestion: 'Find content that defines exact entry conditions' },
    'dte': { icon: '📅', category: 'Timing', suggestion: 'Look for "days to expiration" or DTE recommendations' },
    'timing': { icon: '📅', category: 'Timing', suggestion: 'Search for optimal entry timing strategies' },
    'sizing': { icon: '💰', category: 'Position Sizing', suggestion: 'Find content on capital allocation and position size' },
    'bpe': { icon: '💰', category: 'Position Sizing', suggestion: 'Search for "buying power" or "margin requirements"' },
    'capital': { icon: '💰', category: 'Position Sizing', suggestion: 'Look for recommended account sizes' },
    'backtest': { icon: '📊', category: 'Evidence', suggestion: 'Find content with actual backtest results or paper trades' },
    'evidence': { icon: '📊', category: 'Evidence', suggestion: 'Search for verified performance data' },
    'failure': { icon: '⚠️', category: 'Risk Awareness', suggestion: 'Look for content discussing what can go wrong' },
    'drawdown': { icon: '⚠️', category: 'Risk Awareness', suggestion: 'Find discussions about max drawdown scenarios' },
};

function categorizeGap(gap: string): { icon: string; category: string; suggestion: string } {
    const gapLower = gap.toLowerCase();
    for (const [key, value] of Object.entries(GAP_CATEGORIES)) {
        if (gapLower.includes(key)) {
            return value;
        }
    }
    return { icon: '❓', category: 'Other', suggestion: 'Search for more detailed sources' };
}

export function MissingChecklist({ gaps, onFindSources }: MissingChecklistProps) {
    if (gaps.length === 0) {
        return (
            <div className="missing-checklist complete">
                <span className="complete-icon">✓</span>
                <span>All key parameters covered!</span>
            </div>
        );
    }

    // Group gaps by category
    const groupedGaps = gaps.reduce((acc, gap) => {
        const { category } = categorizeGap(gap);
        if (!acc[category]) {
            acc[category] = [];
        }
        acc[category].push(gap);
        return acc;
    }, {} as Record<string, string[]>);

    return (
        <div className="missing-checklist">
            <h4>What's Missing</h4>

            {Object.entries(groupedGaps).map(([category, categoryGaps]) => (
                <div key={category} className="gap-category">
                    <h5>{category}</h5>
                    <ul className="gap-list">
                        {categoryGaps.map((gap, i) => {
                            const { icon, suggestion } = categorizeGap(gap);
                            return (
                                <li key={i} className="gap-item">
                                    <div className="gap-header">
                                        <span className="gap-icon">{icon}</span>
                                        <span className="gap-text">{gap}</span>
                                    </div>
                                    <div className="gap-suggestion">
                                        💡 {suggestion}
                                        {onFindSources && (
                                            <button
                                                className="find-btn"
                                                onClick={() => onFindSources(gap)}
                                            >
                                                Find Sources →
                                            </button>
                                        )}
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            ))}
        </div>
    );
}
