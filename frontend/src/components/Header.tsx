import './Header.css';

interface HeaderProps {
    onDiscoverClick?: () => void;
}

export function Header({ onDiscoverClick }: HeaderProps) {
    return (
        <header className="header">
            <div className="container header-content">
                <div className="logo">
                    <span className="logo-icon">▣</span>
                    <span className="logo-text">STRATEGY FINDER</span>
                </div>
                <nav className="nav">
                    <button
                        className="btn btn-secondary"
                        onClick={onDiscoverClick}
                        aria-label="Discover sources"
                    >
                        <span>🔍</span> Discover
                    </button>
                </nav>
            </div>
        </header>
    );
}
