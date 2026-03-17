import { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { useTheme } from '../context/ThemeContext';

export const Input = forwardRef(({ 
    label, 
    error, 
    icon: Icon,
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
            <div className="relative">
                {Icon && (
                    <Icon className={`absolute left-3 top-1/2 -translate-y-1/2 ${isDark ? 'text-surface-500' : 'text-surface-400'}`} size={18} />
                )}
                <input
                    ref={ref}
                    className={`w-full ${Icon ? 'pl-10' : 'pl-4'} pr-4 py-3 border rounded-lg transition-all ${
                        isDark
                            ? 'bg-surface-900/50 border-surface-700/50 text-surface-100 placeholder-surface-600 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/30'
                            : 'bg-white border-surface-200 text-surface-900 placeholder-surface-400 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/20'
                    } ${error ? 'border-danger-500' : ''} ${className}`}
                    {...props}
                />
            </div>
            {error && (
                <p className="text-xs text-danger-500 mt-1 font-medium">{error}</p>
            )}
        </div>
    );
});

Input.displayName = 'Input';

Input.propTypes = {
    label: PropTypes.string,
    error: PropTypes.string,
    icon: PropTypes.elementType,
    className: PropTypes.string,
    containerClass: PropTypes.string,
    type: PropTypes.string,
    placeholder: PropTypes.string,
    value: PropTypes.string,
    onChange: PropTypes.func,
    disabled: PropTypes.bool,
};
