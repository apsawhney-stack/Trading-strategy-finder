import { useMemo, useState, useRef, useEffect } from 'react';
import type { Source } from '../types';
import './FilterChips.css';

export interface Filters {
    underlying: string[];
    sourceType: string[];
    dte: string[];
    search: string;
}

interface FilterChipsProps {
    sources: Source[];
    filters: Filters;
    onFilterChange: (filters: Filters) => void;
    sortBy: string;
    onSortChange: (sortBy: string) => void;
}

const SORT_OPTIONS = [
    { value: 'specificity', label: 'Specificity ↓' },
    { value: 'trust', label: 'Trust ↓' },
    { value: 'date', label: 'Date ↓' },
    { value: 'title', label: 'Title A-Z' },
];

export function FilterChips({
    sources,
    filters,
    onFilterChange,
    sortBy,
    onSortChange
}: FilterChipsProps) {
    const [sortOpen, setSortOpen] = useState(false);
    const sortRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (sortRef.current && !sortRef.current.contains(e.target as Node)) {
                setSortOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Extract unique values from sources
    const { underlyings, sourceTypes, dtes } = useMemo(() => {
        const underlyings = new Set<string>();
        const sourceTypes = new Set<string>();
        const dtes = new Set<string>();

        sources.forEach(source => {
            const underlying = source.extracted_data?.setup_rules?.underlying?.value;
            if (underlying) underlyings.add(underlying);

            sourceTypes.add(source.source_type);

            const dte = source.extracted_data?.setup_rules?.dte?.value;
            if (dte !== undefined && dte !== null) {
                dtes.add(String(dte));
            }
        });

        return {
            underlyings: Array.from(underlyings).sort(),
            sourceTypes: Array.from(sourceTypes).sort(),
            dtes: Array.from(dtes).sort((a, b) => parseInt(a) - parseInt(b)),
        };
    }, [sources]);

    const toggleFilter = (category: keyof Omit<Filters, 'search'>, value: string) => {
        const current = filters[category] as string[];
        const updated = current.includes(value)
            ? current.filter(v => v !== value)
            : [...current, value];
        onFilterChange({ ...filters, [category]: updated });
    };

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onFilterChange({ ...filters, search: e.target.value });
    };

    const handleSortSelect = (value: string) => {
        onSortChange(value);
        setSortOpen(false);
    };

    const sourceTypeLabels: Record<string, string> = {
        youtube: 'YouTube',
        reddit: 'Reddit',
        article: 'Article',
    };

    const formatDTE = (dte: string) => {
        const val = parseInt(dte);
        return `${val} DTE`;
    };

    const currentSortLabel = SORT_OPTIONS.find(o => o.value === sortBy)?.label || 'Sort';

    return (
        <div className="filter-bar">
            {/* Search Input */}
            <div className="search-container">
                <span className="search-icon">🔍</span>
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search strategies, authors..."
                    value={filters.search}
                    onChange={handleSearchChange}
                />
            </div>

            {/* Filter Chips Row */}
            <div className="chips-row">
                {/* Underlying Chips */}
                <div className="chip-group">
                    {underlyings.map(sym => (
                        <button
                            key={sym}
                            className={`chip ${filters.underlying.includes(sym) ? 'active' : ''} ${sym.toLowerCase()}`}
                            onClick={() => toggleFilter('underlying', sym)}
                        >
                            {sym}
                        </button>
                    ))}
                </div>

                {/* Separator */}
                {underlyings.length > 0 && sourceTypes.length > 0 && (
                    <div className="chip-separator" />
                )}

                {/* Source Type Chips */}
                <div className="chip-group">
                    {sourceTypes.map(type => (
                        <button
                            key={type}
                            className={`chip ${filters.sourceType.includes(type) ? 'active' : ''}`}
                            onClick={() => toggleFilter('sourceType', type)}
                        >
                            {sourceTypeLabels[type] || type}
                        </button>
                    ))}
                </div>

                {/* Separator */}
                {sourceTypes.length > 0 && dtes.length > 0 && (
                    <div className="chip-separator" />
                )}

                {/* DTE Chips */}
                <div className="chip-group">
                    {dtes.slice(0, 4).map(dte => (
                        <button
                            key={dte}
                            className={`chip ${filters.dte.includes(dte) ? 'active' : ''}`}
                            onClick={() => toggleFilter('dte', dte)}
                        >
                            {formatDTE(dte)}
                        </button>
                    ))}
                </div>

                {/* Spacer */}
                <div className="chip-spacer" />

                {/* Custom Sort Dropdown */}
                <div className="sort-container" ref={sortRef}>
                    <span className="sort-label">Sort:</span>
                    <button
                        className={`sort-button ${sortOpen ? 'open' : ''}`}
                        onClick={() => setSortOpen(!sortOpen)}
                    >
                        {currentSortLabel}
                        <span className="sort-chevron">▼</span>
                    </button>
                    {sortOpen && (
                        <div className="sort-dropdown">
                            {SORT_OPTIONS.map(option => (
                                <button
                                    key={option.value}
                                    className={`sort-option ${sortBy === option.value ? 'active' : ''}`}
                                    onClick={() => handleSortSelect(option.value)}
                                >
                                    {sortBy === option.value && <span className="check">✓</span>}
                                    {option.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
