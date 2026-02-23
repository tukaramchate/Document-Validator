const typeConfig = {
    error: {
        bg: 'bg-danger-500/10',
        border: 'border-danger-500/20',
        text: 'text-danger-400',
        icon: '⚠️',
    },
    success: {
        bg: 'bg-success-500/10',
        border: 'border-success-500/20',
        text: 'text-success-400',
        icon: '✅',
    },
    warning: {
        bg: 'bg-warning-500/10',
        border: 'border-warning-500/20',
        text: 'text-warning-400',
        icon: '⚡',
    },
};

export default function AlertMessage({ type = 'error', message, onClose }) {
    if (!message) return null;

    const config = typeConfig[type] || typeConfig.error;

    return (
        <div
            className={`flex items-center justify-between px-4 py-3 ${config.bg} border ${config.border} rounded-xl ${config.text} text-sm animate-fade-in`}
            role="alert"
        >
            <div className="flex items-center gap-2">
                <span>{config.icon}</span>
                <span>{message}</span>
            </div>
            {onClose && (
                <button
                    onClick={onClose}
                    className="ml-3 text-current opacity-60 hover:opacity-100 transition-opacity"
                    aria-label="Dismiss alert"
                >
                    ✕
                </button>
            )}
        </div>
    );
}
