import { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { useTheme } from '../context/ThemeContext';

export const Select = forwardRef(({ 
    label, 
    error,
    options = [],
    placeholder = 'Select an option',
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
            <select
                ref={ref}
                className={`w-full px-4 py-3 border rounded-lg transition-all appearance-none ${
                    isDark
                        ? 'bg-surface-900/50 border-surface-700/50 text-surface-100 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/30'
                        : 'bg-white border-surface-200 text-surface-900 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/20'
                } ${error ? 'border-danger-500' : ''} ${className}`}
                {...props}
            >
                <option value="">{placeholder}</option>
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            {error && (
                <p className="text-xs text-danger-500 mt-1 font-medium">{error}</p>
            )}
        </div>
    );
});

Select.displayName = 'Select';

Select.propTypes = {
    label: PropTypes.string,
    error: PropTypes.string,
    options: PropTypes.arrayOf(
        PropTypes.shape({
            value: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
        })
    ),
    placeholder: PropTypes.string,
    className: PropTypes.string,
    containerClass: PropTypes.string,
    value: PropTypes.string,
    onChange: PropTypes.func,
    disabled: PropTypes.bool,
};
