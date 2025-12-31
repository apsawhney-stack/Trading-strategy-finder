import type { ConsensusItem, Controversy } from '../types';
import './ConsensusView.css';

interface ConsensusViewProps {
    sourcesAnalyzed: number;
    consensus: ConsensusItem[];
    controversies: Controversy[];
    gaps: string[];
}

export function ConsensusView({
    sourcesAnalyzed,
    consensus,
    controversies,
    gaps
}: ConsensusViewProps) {
    const getAgreementClass = (rate: number) => {
        if (rate >= 0.8) return 'strong';
        if (rate >= 0.6) return 'moderate';
        return 'weak';
    };

    return (
        <div className="consensus-view">
            <div className="consensus-header">
                <h3>Consensus View</h3>
                <span className="sources-count">{sourcesAnalyzed} sources analyzed</span>
            </div>

            {consensus.length > 0 && (
                <section className="consensus-section">
                    <h4>📊 Agreement Points</h4>
                    <div className="agreement-list">
                        {consensus.map((item, i) => (
                            <div key={i} className="agreement-item">
                                <div className="agreement-header">
                                    <span className="topic-label">{item.topic}</span>
                                    <span className={`agreement-rate ${getAgreementClass(item.agreement_rate)}`}>
                                        {Math.round(item.agreement_rate * 100)}% agree
                                    </span>
                                </div>
                                <div className="agreement-value data-value">
                                    {item.consensus_value || '—'}
                                </div>
                                <div className="source-attribution">
                                    {item.sources.slice(0, 3).map((s, j) => (
                                        <span key={j} className="source-tag">{s}</span>
                                    ))}
                                    {item.sources.length > 3 && (
                                        <span className="source-tag more">+{item.sources.length - 3}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {controversies.length > 0 && (
                <section className="controversy-section">
                    <h4>⚡ Controversies</h4>
                    <div className="controversy-list">
                        {controversies.map((item, i) => (
                            <div key={i} className="controversy-item">
                                <span className="topic-label">{item.topic}</span>
                                <div className="positions-list">
                                    {item.positions.map((pos, j) => (
                                        <div key={j} className="position-item">
                                            <div className="position-bar" style={{ width: `${(pos.source_count / sourcesAnalyzed) * 100}%` }} />
                                            <span className="position-value data-value">{pos.value}</span>
                                            <span className="position-count">{pos.source_count} sources</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {gaps.length > 0 && (
                <section className="gaps-section">
                    <h4>❓ Gaps Across Sources</h4>
                    <ul className="common-gaps-list">
                        {gaps.map((gap, i) => (
                            <li key={i}>{gap}</li>
                        ))}
                    </ul>
                </section>
            )}

            {consensus.length === 0 && controversies.length === 0 && (
                <div className="empty-consensus">
                    <p>Add more sources to generate consensus analysis.</p>
                </div>
            )}
        </div>
    );
}
