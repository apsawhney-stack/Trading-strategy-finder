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
                <label htmlFor="url-input" className="sr-only">
                    Paste YouTube, Reddit, or article URL
                </label>
                <input
                    id="url-input"
                    type="text"
                    className="input url-input"
                    placeholder="Paste YouTube, Reddit, or article URL..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={disabled}
                />
                {sourceType && (
                    <span className={`source-badge source-${sourceType}`}>
                        {sourceType === 'youtube' && '📹'}
                        {sourceType === 'reddit' && '📄'}
                        {sourceType === 'article' && '🌐'}
                        {sourceType}
                    </span>
                )}
            </div>
            <button
                type="submit"
                className="btn btn-primary extract-btn"
                disabled={disabled || !url.trim()}
            >
                {disabled ? (
                    <>
                        <span className="spinner"></span>
                        Extracting...
                    </>
                ) : (
                    'Extract'
                )}
            </button>
        </form>
    );
}
