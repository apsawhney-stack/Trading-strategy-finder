import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ConsensusView } from '../components/ConsensusView';
import { SourceCard } from '../components/SourceCard';
import { SourceDetail } from '../components/SourceDetail';
import type { Source, ConsensusItem, Controversy } from '../types';
import { getStrategy } from '../services/api';
import './StrategyPage.css';

interface StrategyData {
    id: string;
    name: string;
    sources: Source[];
    consensus: ConsensusItem[];
    controversies: Controversy[];
    gaps: string[];
}

export function StrategyPage() {
    const { id } = useParams<{ id: string }>();
    const [strategy, setStrategy] = useState<StrategyData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedSource, setSelectedSource] = useState<Source | null>(null);

    useEffect(() => {
        async function loadStrategy() {
            if (!id) return;

            try {
                setLoading(true);
                const result = await getStrategy(id);
                setStrategy({
                    id,
                    name: result.strategy?.name || 'Strategy Analysis',
                    sources: result.sources || [],
                    consensus: result.strategy?.consensus || [],
                    controversies: result.strategy?.controversies || [],
                    gaps: result.strategy?.gaps || [],
                });
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load strategy');
            } finally {
                setLoading(false);
            }
        }

        loadStrategy();
    }, [id]);

    if (loading) {
        return (
            <div className="strategy-page">
                <div className="container">
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading strategy analysis...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error || !strategy) {
        return (
            <div className="strategy-page">
                <div className="container">
                    <div className="error-state">
                        <p>⚠️ {error || 'Strategy not found'}</p>
                        <Link to="/" className="btn btn-primary">Back to Home</Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="strategy-page">
            <div className="container">
                <header className="strategy-header">
                    <Link to="/" className="back-link">← Back</Link>
                    <h1>{strategy.name}</h1>
                    <span className="source-count">{strategy.sources.length} sources analyzed</span>
                </header>

                <div className="strategy-content">
                    <section className="consensus-section">
                        <ConsensusView
                            sourcesAnalyzed={strategy.sources.length}
                            consensus={strategy.consensus}
                            controversies={strategy.controversies}
                            gaps={strategy.gaps}
                        />
                    </section>

                    <section className="sources-section">
                        <h2>Sources</h2>
                        <div className="sources-grid">
                            {strategy.sources.map(source => (
                                <SourceCard
                                    key={source.id}
                                    source={source}
                                    onClick={() => setSelectedSource(source)}
                                />
                            ))}
                        </div>
                    </section>
                </div>
            </div>

            {selectedSource && (
                <SourceDetail
                    source={selectedSource}
                    onClose={() => setSelectedSource(null)}
                />
            )}
        </div>
    );
}
