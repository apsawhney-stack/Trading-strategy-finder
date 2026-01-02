import { useState } from 'react';
import type { DiscoveryCandidate } from '../types';
import { discoverSources } from '../services/api';
import './DiscoveryModal.css';

interface DiscoveryModalProps {
    onClose: () => void;
    onExtract: (urls: string[]) => void;
}

export function DiscoveryModal({ onClose, onExtract }: DiscoveryModalProps) {
    const [query, setQuery] = useState('');
    const [platforms, setPlatforms] = useState<('youtube' | 'reddit' | 'web')[]>(['youtube', 'reddit', 'web']);
    const [candidates, setCandidates] = useState<DiscoveryCandidate[]>([]);
    const [selected, setSelected] = useState<Set<string>>(new Set());
    const [isSearching, setIsSearching] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async () => {
        if (!query.trim()) return;

        setIsSearching(true);
        setError(null);

        try {
            const result = await discoverSources(query, platforms);
            setCandidates(result.candidates);
            setSelected(new Set());
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Discovery failed');
        } finally {
            setIsSearching(false);
        }
    };

    const togglePlatform = (platform: 'youtube' | 'reddit' | 'web') => {
        setPlatforms(prev =>
            prev.includes(platform)
                ? prev.filter(p => p !== platform)
                : [...prev, platform]
        );
    };

    const toggleCandidate = (url: string) => {
        setSelected(prev => {
            const next = new Set(prev);
            if (next.has(url)) {
                next.delete(url);
            } else {
                next.add(url);
            }
            return next;
        });
    };

    const selectAll = () => {
        setSelected(new Set(candidates.map(c => c.url)));
    };

    const handleExtract = () => {
        if (selected.size > 0) {
            onExtract(Array.from(selected));
            onClose();
        }
    };

    const tierClass = (tier: string) =>
        tier === 'high' ? 'tier-high' : tier === 'medium' ? 'tier-medium' : 'tier-low';

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="discovery-modal" onClick={e => e.stopPropagation()}>
                <header className="discovery-header">
                    <h2>Discover Sources</h2>
                    <button className="close-btn" onClick={onClose}>✕</button>
                </header>

                <div className="discovery-search">
                    <input
                        type="text"
                        className="input search-input"
                        placeholder="Search for a strategy, e.g. 'SPX put credit spread 45 DTE'"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSearch()}
                    />
                    <button
                        className="btn btn-primary"
                        onClick={handleSearch}
                        disabled={isSearching || !query.trim()}
                    >
                        {isSearching ? 'Searching...' : 'Search'}
                    </button>
                </div>

                <div className="platform-filters">
                    {(['youtube', 'reddit', 'web'] as const).map(platform => (
                        <label key={platform} className="platform-toggle">
                            <input
                                type="checkbox"
                                checked={platforms.includes(platform)}
                                onChange={() => togglePlatform(platform)}
                            />
                            <span className={`platform-label platform-${platform}`}>
                                {platform === 'youtube' && '📹'}
                                {platform === 'reddit' && '📄'}
                                {platform === 'web' && '🌐'}
                                {platform.charAt(0).toUpperCase() + platform.slice(1)}
                            </span>
                        </label>
                    ))}
                </div>

                {error && (
                    <div className="discovery-error">⚠️ {error}</div>
                )}

                <div className="candidates-container">
                    {candidates.length === 0 ? (
                        <div className="candidates-empty">
                            {isSearching
                                ? 'Searching platforms...'
                                : 'Enter a strategy query to discover sources'}
                        </div>
                    ) : (
                        <>
                            <div className="candidates-header">
                                <span>{candidates.length} sources found</span>
                                <button className="btn-link" onClick={selectAll}>Select All</button>
                            </div>
                            <div className="candidates-list">
                                {candidates.map(candidate => {
                                    const views = candidate.metrics?.views;
                                    const publishDate = candidate.published_at
                                        ? new Date(candidate.published_at).toLocaleDateString('en-US', {
                                            month: 'short',
                                            year: 'numeric'
                                        })
                                        : null;

                                    const formatViews = (v: number) => {
                                        if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M`;
                                        if (v >= 1000) return `${(v / 1000).toFixed(0)}K`;
                                        return v.toString();
                                    };

                                    return (
                                        <div
                                            key={candidate.url}
                                            className={`candidate-item ${selected.has(candidate.url) ? 'selected' : ''}`}
                                            onClick={() => toggleCandidate(candidate.url)}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selected.has(candidate.url)}
                                                onChange={() => toggleCandidate(candidate.url)}
                                            />
                                            <div className="candidate-info">
                                                <span className="candidate-title">{candidate.title}</span>
                                                <div className="candidate-meta">
                                                    <span className="candidate-author">{candidate.author}</span>
                                                    {views && views > 0 && (
                                                        <span className="candidate-views">👁 {formatViews(views)}</span>
                                                    )}
                                                    {publishDate && (
                                                        <span className="candidate-date">📅 {publishDate}</span>
                                                    )}
                                                </div>
                                                {candidate.quality_signals && candidate.quality_signals.length > 0 && (
                                                    <div className="candidate-signals">
                                                        {candidate.quality_signals.slice(0, 3).map((signal, i) => (
                                                            <span key={i} className="signal-tag">{signal}</span>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                            <span className={`tier-badge ${tierClass(candidate.quality_tier)}`}>
                                                {candidate.quality_tier}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    )}
                </div>

                <footer className="discovery-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button
                        className="btn btn-primary"
                        onClick={handleExtract}
                        disabled={selected.size === 0}
                    >
                        Extract {selected.size > 0 ? `(${selected.size})` : ''}
                    </button>
                </footer>
            </div>
        </div>
    );
}
