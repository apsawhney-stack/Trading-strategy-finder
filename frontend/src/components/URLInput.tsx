import { useState } from 'react';
import './URLInput.css';

interface URLInputProps {
    onSubmit: (url: string) => void;
    disabled?: boolean;
}

export function URLInput({ onSubmit, disabled }: URLInputProps) {
    const [url, setUrl] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (url.trim()) {
            onSubmit(url.trim());
            setUrl('');
        }
    };

    const detectSourceType = (url: string): 'youtube' | 'reddit' | 'article' | null => {
        if (url.includes('youtube.com') || url.includes('youtu.be')) return 'youtube';
        if (url.includes('reddit.com') || url.includes('redd.it')) return 'reddit';
        if (url.startsWith('http')) return 'article';
        return null;
    };

    const sourceType = detectSourceType(url);

    return (
        <form className="url-input-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
                <input
                    type="text"
                    className="input url-input"
                    placeholder="Paste YouTube, Reddit, or article URL..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={disabled}
                    aria-label="Paste URL to extract"
                />
                {sourceType && (
                    <>
                        <span className="sr-only" role="status" aria-live="polite">
                            Detected source type: {sourceType}
                        </span>
                        <span className={`source-badge source-${sourceType}`} aria-hidden="true">
                            {sourceType === 'youtube' && '📹'}
                            {sourceType === 'reddit' && '📄'}
                            {sourceType === 'article' && '🌐'}
                            {sourceType}
                        </span>
                    </>
                )}
            </div>
            <button
                type="submit"
                className="btn btn-primary extract-btn"
                disabled={disabled || !url.trim()}
                aria-label={disabled ? 'Extracting strategy...' : 'Extract strategy'}
            >
                {disabled ? (
                    <>
                        <span className="spinner" aria-hidden="true"></span>
                        Extracting...
                    </>
                ) : (
                    'Extract'
                )}
            </button>
        </form>
    );
}
