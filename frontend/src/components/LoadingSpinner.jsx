export default function LoadingSpinner({ size = 'md', text = '' }) {
    const sizes = {
        sm: 'w-5 h-5 border-2',
        md: 'w-8 h-8 border-3',
        lg: 'w-10 h-10 border-3',
    };

    return (
        <div className="flex flex-col items-center justify-center gap-3" role="status" aria-label="Loading">
            <div className={`${sizes[size]} border-brand-500 border-t-transparent rounded-full animate-spin`} />
            {text && <p className="text-surface-400 text-sm">{text}</p>}
            <span className="sr-only">Loading...</span>
        </div>
    );
}
