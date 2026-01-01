import { useState, useEffect, useCallback } from 'react';
import type { Source } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

interface UseSourcesResult {
    sources: Source[];
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
    deleteSource: (id: string) => Promise<boolean>;
}

/**
 * Hook to fetch and manage sources from the API.
 * Auto-fetches on mount and provides refresh/delete functionality.
 */
export function useSources(): UseSourcesResult {
    const [sources, setSources] = useState<Source[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchSources = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(`${API_BASE}/api/sources`);

            if (!response.ok) {
                throw new Error(`Failed to fetch sources: ${response.statusText}`);
            }

            const data = await response.json();
            setSources(data.sources || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load sources');
            console.error('Error fetching sources:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteSource = useCallback(async (id: string): Promise<boolean> => {
        try {
            const response = await fetch(`${API_BASE}/api/sources/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(`Failed to delete source: ${response.statusText}`);
            }

            // Remove from local state
            setSources(prev => prev.filter(s => s.id !== id));
            return true;
        } catch (err) {
            console.error('Error deleting source:', err);
            return false;
        }
    }, []);

    // Fetch on mount
    useEffect(() => {
        fetchSources();
    }, [fetchSources]);

    return {
        sources,
        loading,
        error,
        refresh: fetchSources,
        deleteSource,
    };
}
