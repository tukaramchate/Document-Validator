export function Badge({ children, variant = 'default', className = '' }) {
    const variants = {
        default: 'bg-surface-800/50 text-surface-300 border border-surface-700/50',
        brand: 'bg-brand-500/10 text-brand-400 border border-brand-500/20',
        success: 'bg-success-500/10 text-success-400 border border-success-500/20',
        warning: 'bg-warning-500/10 text-warning-400 border border-warning-500/20',
        danger: 'bg-danger-500/10 text-danger-400 border border-danger-500/20',
    };

    return (
        <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold ${variants[variant]} ${className}`}>
            {children}
        </span>
    );
}

export function Pill({ children, icon: Icon, className = '' }) {
    return (
        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-800/50 text-surface-300 border border-surface-700/50 text-xs font-semibold ${className}`}>
            {Icon && <Icon size={14} />}
            {children}
        </div>
    );
}
