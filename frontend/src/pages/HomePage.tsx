import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Header } from '../components/Header';
import { URLInput } from '../components/URLInput';
import { SourceCard } from '../components/SourceCard';
import { SourceDetail } from '../components/SourceDetail';
import { ExtractionProgress } from '../components/ExtractionProgress';
import { DiscoveryModal } from '../components/DiscoveryModal';
import { extractSource } from '../services/api';
import type { Source, ExtractionStep } from '../types';
import './HomePage.css';

export function HomePage() {
    const [sources, setSources] = useState<Source[]>([]);
    const [isExtracting, setIsExtracting] = useState(false);
    const [currentStep, setCurrentStep] = useState<ExtractionStep>('fetching_content');
    const [error, setError] = useState<string | null>(null);
    const [selectedSource, setSelectedSource] = useState<Source | null>(null);
    const [showDiscovery, setShowDiscovery] = useState(false);

    const handleExtract = async (url: string) => {
        setIsExtracting(true);
        setError(null);
        setCurrentStep('fetching_content');

        try {
            const steps: ExtractionStep[] = [
                'fetching_content',
                'analyzing_structure',
                'extracting_strategy',
                'calculating_scores',
                'complete'
            ];

            let stepIndex = 0;
            const stepInterval = setInterval(() => {
                stepIndex++;
                if (stepIndex < steps.length - 1) {
                    setCurrentStep(steps[stepIndex]);
                }
            }, 2000);

            const result = await extractSource(url);
            clearInterval(stepInterval);

            if (result.success && result.source) {
                setCurrentStep('complete');
                setSources(prev => [result.source!, ...prev]);
            } else {
                setError(result.error || 'Extraction failed');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Extraction failed');
        } finally {
            setIsExtracting(false);
        }
    };

    const handleBatchExtract = async (urls: string[]) => {
        for (const url of urls) {
            await handleExtract(url);
        }
    };

    // Group sources by strategy type
    const strategyGroups = sources.reduce((acc, source) => {
        const strategyName = source.extracted_data?.strategy_name?.value || 'Other';
        if (!acc[strategyName]) {
            acc[strategyName] = [];
        }
        acc[strategyName].push(source);
        return acc;
    }, {} as Record<string, Source[]>);

    return (
        <div className="home-page">
            <Header onDiscoverClick={() => setShowDiscovery(true)} />

            <main className="main-content">
                <div className="container">
                    <section className="hero-section">
                        <h1>Options Strategy Research</h1>
                        <p className="hero-subtitle">
                            Extract, analyze, and synthesize trading strategies from YouTube, Reddit, and articles.
                        </p>
                        <URLInput onSubmit={handleExtract} disabled={isExtracting} />

                        {isExtracting && (
                            <ExtractionProgress currentStep={currentStep} />
                        )}

                        {error && (
                            <div className="error-message">
                                <span>⚠️</span> {error}
                            </div>
                        )}
                    </section>

                    {sources.length === 0 ? (
                        <section className="empty-section">
                            <div className="empty-state">
                                <div className="empty-icon">📊</div>
                                <h2>Start Your Research</h2>
                                <p>Paste a URL above or discover sources for popular strategies.</p>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => setShowDiscovery(true)}
                                >
                                    🔍 Discover Sources
                                </button>
                            </div>
                        </section>
                    ) : (
                        <>
                            {Object.entries(strategyGroups).map(([strategyName, groupSources]) => (
                                <section key={strategyName} className="strategy-group">
                                    <div className="group-header">
                                        <h2>{strategyName}</h2>
                                        <span className="group-count">{groupSources.length} sources</span>
                                        {groupSources.length >= 2 && (
                                            <Link
                                                to={`/strategy/${encodeURIComponent(strategyName)}`}
                                                className="btn btn-secondary btn-sm"
                                            >
                                                View Consensus →
                                            </Link>
                                        )}
                                    </div>
                                    <div className="sources-list">
                                        {groupSources.map(source => (
                                            <SourceCard
                                                key={source.id}
                                                source={source}
                                                onClick={() => setSelectedSource(source)}
                                            />
                                        ))}
                                    </div>
                                </section>
                            ))}
                        </>
                    )}
                </div>
            </main>

            {selectedSource && (
                <SourceDetail
                    source={selectedSource}
                    onClose={() => setSelectedSource(null)}
                />
            )}

            {showDiscovery && (
                <DiscoveryModal
                    onClose={() => setShowDiscovery(false)}
                    onExtract={handleBatchExtract}
                />
            )}
        </div>
    );
}
