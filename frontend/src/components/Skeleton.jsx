/**
 * Reusable loading skeleton components for dark mode.
 */
export function Skeleton({ className = '', variant = 'rectangular' }) {
    const roundedClass = variant === 'circular' ? 'rounded-full' : 'rounded-2xl';

    return (
        <div className={`animate-pulse bg-surface-800/50 ${roundedClass} ${className}`} />
    );
}

export function StatCardSkeleton() {
    return (
        <div className="card rounded-[2rem] p-6">
            <div className="flex items-start justify-between">
                <div>
                    <Skeleton className="h-4 w-24 mb-3" />
                    <Skeleton className="h-8 w-16" />
                </div>
                <Skeleton variant="circular" className="h-12 w-12" />
            </div>
        </div>
    );
}

export function TableRowSkeleton() {
    return (
        <div className="flex items-center justify-between p-4 bg-surface-800/10 rounded-2xl border border-surface-800/30 mb-3">
            <div className="flex items-center gap-4">
                <Skeleton variant="circular" className="h-10 w-10 shrink-0" />
                <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-48" />
                </div>
            </div>
            <div className="flex items-center gap-3">
                <Skeleton className="h-6 w-20 rounded-full" />
                <Skeleton className="h-8 w-8" />
            </div>
        </div>
    );
}
