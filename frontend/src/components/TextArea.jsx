import { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { useTheme } from '../context/ThemeContext';

export const TextArea = forwardRef(({ 
    label, 
    error, 
    rows = 4,
    className = '', 
    containerClass = '',
    ...props 
}, ref) => {
    const { theme } = useTheme();
    const isDark = theme === 'dark';

    return (
        <div className={containerClass}>
            {label && (
                <label className={`block text-sm font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'} mb-2`}>
                    {label}
                </label>
            )}
            <textarea
                ref={ref}
                rows={rows}
                className={`w-full px-4 py-3 border rounded-lg transition-all resize-none ${
                    isDark
                        ? 'bg-surface-900/50 border-surface-700/50 text-surface-100 placeholder-surface-600 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/30'
                        : 'bg-white border-surface-200 text-surface-900 placeholder-surface-400 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/20'
                } ${error ? 'border-danger-500' : ''} ${className}`}
                {...props}
            />
            {error && (
                <p className="text-xs text-danger-500 mt-1 font-medium">{error}</p>
            )}
        </div>
    );
});

TextArea.displayName = 'TextArea';

TextArea.propTypes = {
    label: PropTypes.string,
    error: PropTypes.string,
    rows: PropTypes.number,
    className: PropTypes.string,
    containerClass: PropTypes.string,
    placeholder: PropTypes.string,
    value: PropTypes.string,
    onChange: PropTypes.func,
    disabled: PropTypes.bool,
};
