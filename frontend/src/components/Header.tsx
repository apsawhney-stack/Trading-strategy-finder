import './Header.css';

export function Header() {
    return (
        <header className="header">
            <div className="container header-content">
                <div className="logo">
                    <span className="logo-icon">▣</span>
                    <span className="logo-text">STRATEGY FINDER</span>
                </div>
                <nav className="nav">
                    <button className="btn btn-secondary">
                        <span>+</span> Add URL
                    </button>
                </nav>
            </div>
        </header>
    );
}
