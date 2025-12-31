import { useState, useMemo } from 'react';
import { Header } from '../components/Header';
import { URLInput } from '../components/URLInput';
import { SourceCard } from '../components/SourceCard';
import { SourceDetail } from '../components/SourceDetail';
import { ExtractionProgress } from '../components/ExtractionProgress';
import { DiscoveryModal } from '../components/DiscoveryModal';
import { FilterChips } from '../components/FilterChips';
import type { Filters } from '../components/FilterChips';
import { extractSource } from '../services/api';
import { useSources } from '../hooks/useSources';
import type { Source, ExtractionStep } from '../types';
import './HomePage.css';

export function HomePage() {
    // Load saved sources from API
    const { sources: savedSources, loading: loadingSources, refresh: refreshSources, deleteSource } = useSources();

    // Local sources from current session
    const [sessionSources, setSessionSources] = useState<Source[]>([]);
    const [isExtracting, setIsExtracting] = useState(false);
    const [currentStep, setCurrentStep] = useState<ExtractionStep>('fetching_content');
    const [error, setError] = useState<string | null>(null);
    const [selectedSource, setSelectedSource] = useState<Source | null>(null);
    const [showDiscovery, setShowDiscovery] = useState(false);

    // Filter and sort state
    const [filters, setFilters] = useState<Filters>({
        underlying: [],
        sourceType: [],
        dte: [],
    });
    const [sortBy, setSortBy] = useState('specificity');

    // Combine saved and session sources, deduping by ID
    const allSources = useMemo(() => {
        const combined = [...sessionSources];
        savedSources.forEach(saved => {
            if (!combined.some(s => s.id === saved.id)) {
                combined.push(saved);
            }
        });
        return combined;
    }, [sessionSources, savedSources]);

    // Apply filters
    const filteredSources = useMemo(() => {
        return allSources.filter(source => {
            // Filter by underlying
            if (filters.underlying.length > 0) {
                const underlying = source.extracted_data?.setup_rules?.underlying?.value;
                if (!underlying || !filters.underlying.includes(underlying)) return false;
            }

            // Filter by source type
            if (filters.sourceType.length > 0) {
                if (!filters.sourceType.includes(source.source_type)) return false;
            }

            // Filter by DTE
            if (filters.dte.length > 0) {
                const dte = source.extracted_data?.setup_rules?.dte?.value;
                if (dte === undefined || dte === null || !filters.dte.includes(String(dte))) return false;
            }

            return true;
        });
    }, [allSources, filters]);

    // Apply sorting
    const sortedSources = useMemo(() => {
        const sorted = [...filteredSources];
        sorted.sort((a, b) => {
            switch (sortBy) {
                case 'specificity':
                    return (b.quality_metrics?.specificity_score || 0) - (a.quality_metrics?.specificity_score || 0);
                case 'trust':
                    return (b.quality_metrics?.trust_score || 0) - (a.quality_metrics?.trust_score || 0);
                case 'date':
                    const dateA = a.published_date ? new Date(a.published_date).getTime() : 0;
                    const dateB = b.published_date ? new Date(b.published_date).getTime() : 0;
                    return dateB - dateA;
                case 'title':
                    const titleA = a.title || '';
                    const titleB = b.title || '';
                    return titleA.localeCompare(titleB);
                default:
                    return 0;
            }
        });
        return sorted;
    }, [filteredSources, sortBy]);

    // Handle source deletion
    const handleDelete = async (id: string): Promise<boolean> => {
        const success = await deleteSource(id);
        if (success) {
            setSessionSources(prev => prev.filter(s => s.id !== id));
        }
        return success;
    };

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
                setSessionSources(prev => [result.source!, ...prev]);
                refreshSources();
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

                    {loadingSources ? (
                        <section className="empty-section">
                            <div className="empty-state">
                                <div className="spinner"></div>
                                <p>Loading saved sources...</p>
                            </div>
                        </section>
                    ) : allSources.length === 0 ? (
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
                        <section className="sources-section">
                            <div className="sources-header">
                                <h2>Your Sources</h2>
                                <span className="sources-count">{sortedSources.length} of {allSources.length}</span>
                            </div>

                            <FilterChips
                                sources={allSources}
                                filters={filters}
                                onFilterChange={setFilters}
                                sortBy={sortBy}
                                onSortChange={setSortBy}
                            />

                            <div className="sources-list">
                                {sortedSources.map(source => (
                                    <SourceCard
                                        key={source.id}
                                        source={source}
                                        onClick={() => setSelectedSource(source)}
                                        onDelete={handleDelete}
                                    />
                                ))}
                            </div>

                            {sortedSources.length === 0 && allSources.length > 0 && (
                                <div className="no-results">
                                    <p>No sources match your filters.</p>
                                    <button
                                        className="btn btn-secondary"
                                        onClick={() => setFilters({ underlying: [], sourceType: [], dte: [] })}
                                    >
                                        Clear Filters
                                    </button>
                                </div>
                            )}
                        </section>
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
