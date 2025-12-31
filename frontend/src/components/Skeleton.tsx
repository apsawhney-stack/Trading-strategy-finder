import './Skeleton.css';

interface SkeletonProps {
    variant?: 'text' | 'circular' | 'rectangular';
    width?: string | number;
    height?: string | number;
    className?: string;
}

export function Skeleton({
    variant = 'text',
    width,
    height,
    className = ''
}: SkeletonProps) {
    const style: React.CSSProperties = {};

    if (width) style.width = typeof width === 'number' ? `${width}px` : width;
    if (height) style.height = typeof height === 'number' ? `${height}px` : height;

    return (
        <div
            className={`skeleton skeleton-${variant} ${className}`}
            style={style}
        />
    );
}

export function SourceCardSkeleton() {
    return (
        <div className="source-card-skeleton card">
            <div className="skeleton-header">
                <Skeleton variant="circular" width={40} height={40} />
                <div className="skeleton-meta">
                    <Skeleton width="60%" height={16} />
                    <Skeleton width="40%" height={12} />
                </div>
                <div className="skeleton-scores">
                    <Skeleton width={50} height={24} />
                    <Skeleton width={50} height={24} />
                </div>
            </div>
            <div className="skeleton-content">
                <Skeleton width="80%" height={14} />
                <Skeleton width="100%" height={14} />
                <Skeleton width="70%" height={14} />
            </div>
            <div className="skeleton-footer">
                <Skeleton width="30%" height={12} />
                <Skeleton width={80} height={20} />
            </div>
        </div>
    );
}

export function ConsensusViewSkeleton() {
    return (
        <div className="consensus-skeleton">
            <Skeleton width="40%" height={24} />
            <div className="skeleton-items">
                {[1, 2, 3].map(i => (
                    <div key={i} className="skeleton-item">
                        <Skeleton width="25%" height={12} />
                        <Skeleton width="100%" height={20} />
                        <Skeleton width="50%" height={12} />
                    </div>
                ))}
            </div>
        </div>
    );
}
