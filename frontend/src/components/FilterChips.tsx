import { useMemo } from 'react';
import type { Source } from '../types';
import './FilterChips.css';

export interface Filters {
    underlying: string[];
    sourceType: string[];
    dte: string[];
}

interface FilterChipsProps {
    sources: Source[];
    filters: Filters;
    onFilterChange: (filters: Filters) => void;
    sortBy: string;
    onSortChange: (sortBy: string) => void;
}

export function FilterChips({
    sources,
    filters,
    onFilterChange,
    sortBy,
    onSortChange
}: FilterChipsProps) {
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

    const toggleFilter = (category: keyof Filters, value: string) => {
        const current = filters[category];
        const updated = current.includes(value)
            ? current.filter(v => v !== value)
            : [...current, value];
        onFilterChange({ ...filters, [category]: updated });
    };

    const clearAllFilters = () => {
        onFilterChange({ underlying: [], sourceType: [], dte: [] });
    };

    const hasActiveFilters =
        filters.underlying.length > 0 ||
        filters.sourceType.length > 0 ||
        filters.dte.length > 0;

    const formatDTE = (dte: string) => {
        const val = parseInt(dte);
        if (val === 0) return '0 DTE';
        return `${val} DTE`;
    };

    const sourceTypeLabels: Record<string, string> = {
        youtube: '📹 YouTube',
        reddit: '💬 Reddit',
        article: '📰 Article',
    };

    return (
        <div className="filter-bar">
            <div className="filter-groups">
                {/* Underlying Filters */}
                {underlyings.length > 0 && (
                    <div className="filter-group">
                        {underlyings.map(sym => (
                            <button
                                key={sym}
                                className={`chip ${filters.underlying.includes(sym) ? 'active' : ''}`}
                                onClick={() => toggleFilter('underlying', sym)}
                            >
                                {sym}
                            </button>
                        ))}
                    </div>
                )}

                {/* Source Type Filters */}
                {sourceTypes.length > 1 && (
                    <div className="filter-group">
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
                )}

                {/* DTE Filters */}
                {dtes.length > 0 && (
                    <div className="filter-group">
                        {dtes.slice(0, 5).map(dte => (
                            <button
                                key={dte}
                                className={`chip ${filters.dte.includes(dte) ? 'active' : ''}`}
                                onClick={() => toggleFilter('dte', dte)}
                            >
                                {formatDTE(dte)}
                            </button>
                        ))}
                    </div>
                )}

                {/* Clear Filters */}
                {hasActiveFilters && (
                    <button className="chip chip-clear" onClick={clearAllFilters}>
                        ✕ Clear
                    </button>
                )}
            </div>

            {/* Sort Dropdown */}
            <div className="sort-dropdown">
                <label htmlFor="sort-select">Sort:</label>
                <select
                    id="sort-select"
                    value={sortBy}
                    onChange={e => onSortChange(e.target.value)}
                >
                    <option value="specificity">Specificity ↓</option>
                    <option value="trust">Trust ↓</option>
                    <option value="date">Date ↓</option>
                    <option value="title">Title A-Z</option>
                </select>
            </div>
        </div>
    );
}
