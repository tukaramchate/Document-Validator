import { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([]);
    const [hoveredId, setHoveredId] = useState(null);
    const timersRef = useRef({});

    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
        if (timersRef.current[id]) {
            clearTimeout(timersRef.current[id]);
            delete timersRef.current[id];
        }
    }, []);

    const addToast = useCallback((type, message) => {
        const id = Math.random().toString(36).substr(2, 9);
        setToasts((prev) => [...prev, { id, type, message }]);
        
        // Set auto-dismiss timer, but allow pause on hover
        timersRef.current[id] = setTimeout(() => {
            removeToast(id);
        }, 5000);
    }, [removeToast]);

    // Clear timer when hovering, restart when leaving
    const handleMouseEnter = (id) => {
        setHoveredId(id);
        if (timersRef.current[id]) {
            clearTimeout(timersRef.current[id]);
        }
    };

    const handleMouseLeave = (id) => {
        setHoveredId(null);
        timersRef.current[id] = setTimeout(() => {
            removeToast(id);
        }, 2000); // Resume with 2 second remaining
    };

    const toast = {
        success: (msg) => addToast('success', msg),
        error: (msg) => addToast('error', msg),
        info: (msg) => addToast('info', msg),
    };

    // Cleanup timers on unmount
    useEffect(() => {
        return () => {
            Object.values(timersRef.current).forEach(timer => clearTimeout(timer));
        };
    }, []);

    return (
        <ToastContext.Provider value={{ toast }}>
            {children}
            {/* Toast Container */}
            <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
                {toasts.map((t) => (
                    <div
                        key={t.id}
                        onMouseEnter={() => handleMouseEnter(t.id)}
                        onMouseLeave={() => handleMouseLeave(t.id)}
                        className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-lg border animate-slide-up backdrop-blur-md w-80 transition-opacity ${
                            hoveredId === t.id ? 'opacity-100' : 'opacity-90'
                        } ${t.type === 'success'
                                ? 'bg-success-950/90 border-success-500/20 text-success-400'
                                : t.type === 'error'
                                    ? 'bg-danger-950/90 border-danger-500/20 text-danger-400'
                                    : 'bg-brand-950/90 border-brand-500/20 text-brand-400'
                            }`}
                    >
                        <div className="shrink-0 mt-0.5">
                            {t.type === 'success' ? <CheckCircle size={18} /> : t.type === 'error' ? <XCircle size={18} /> : <Info size={18} />}
                        </div>
                        <p className="flex-1 text-sm font-medium text-surface-200">{t.message}</p>
                        <button
                            onClick={() => removeToast(t.id)}
                            className="shrink-0 text-surface-500 hover:text-surface-300 transition-colors"
                            aria-label="Dismiss notification"
                        >
                            <X size={16} />
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) throw new Error('useToast must be used within a ToastProvider');
    return context.toast;
};
