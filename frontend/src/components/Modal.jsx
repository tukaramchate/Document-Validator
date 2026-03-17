import { useEffect } from 'react';
import PropTypes from 'prop-types';
import { X } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function Modal({ isOpen, onClose, title, children, size = 'md', className = '' }) {
    const { theme } = useTheme();
    const isDark = theme === 'dark';

    const sizes = {
        sm: 'max-w-sm',
        md: 'max-w-md',
        lg: 'max-w-lg',
        xl: 'max-w-xl',
    };

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div 
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className={`relative ${isDark ? 'bg-surface-900/95 text-surface-100' : 'bg-white text-surface-900'} rounded-2xl shadow-xl max-w-full w-full mx-4 ${sizes[size]} ${className}`}>
                {/* Header */}
                {title && (
                    <div className={`flex items-center justify-between p-6 border-b ${isDark ? 'border-surface-800/50' : 'border-surface-200'}`}>
                        <h2 className="text-xl font-bold">{title}</h2>
                        <button 
                            onClick={onClose}
                            className={`p-2 rounded-lg transition-colors ${isDark ? 'hover:bg-surface-800/50 text-surface-400' : 'hover:bg-surface-100 text-surface-600'}`}
                            aria-label="Close modal"
                        >
                            <X size={20} />
                        </button>
                    </div>
                )}

                {/* Content */}
                <div className="p-6">
                    {children}
                </div>
            </div>
        </div>
    );
}

Modal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string,
    children: PropTypes.node,
    size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl']),
    className: PropTypes.string,
};
