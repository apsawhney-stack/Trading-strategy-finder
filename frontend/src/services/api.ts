/**
 * API service for backend communication.
 */

import type { ExtractionResponse, Source } from '../types';

const API_BASE = 'http://localhost:8000/api';

/**
 * Extract strategy from a URL.
 */
export async function extractSource(url: string): Promise<ExtractionResponse> {
    try {
        const response = await fetch(`${API_BASE}/extract`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) {
            const error = await response.json();
            return {
                success: false,
                source: null,
                error: error.detail || 'Extraction failed',
            };
        }

        return await response.json();
    } catch (error) {
        // Handle network errors or backend not running
        if (error instanceof TypeError && error.message.includes('fetch')) {
            return {
                success: false,
                source: null,
                error: 'Cannot connect to backend. Make sure the server is running on port 8000.',
            };
        }
        return {
            success: false,
            source: null,
            error: error instanceof Error ? error.message : 'Unknown error',
        };
    }
}

/**
 * Get all strategies.
 */
export async function getStrategies(): Promise<{ strategies: Source[] }> {
    const response = await fetch(`${API_BASE}/strategies`);
    return response.json();
}

/**
 * Get strategy by ID.
 */
export async function getStrategy(id: string): Promise<{ strategy: any; sources: Source[] }> {
    const response = await fetch(`${API_BASE}/strategies/${id}`);
    return response.json();
}

/**
 * Discover sources for a query.
 */
export async function discoverSources(
    query: string,
    sources: ('youtube' | 'reddit' | 'web')[] = ['youtube', 'reddit']
): Promise<{ candidates: any[]; filters_applied: string[] }> {
    const response = await fetch(`${API_BASE}/discover`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, sources }),
    });
    return response.json();
}
