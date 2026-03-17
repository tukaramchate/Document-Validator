import { forwardRef } from 'react';
import PropTypes from 'prop-types';

export const Button = forwardRef(({ 
    children, 
    variant = 'primary',
    size = 'md',
    disabled = false,
    isLoading = false,
    className = '',
    icon: Icon,
    ...props 
}, ref) => {
    const variants = {
        primary: 'bg-brand-500 hover:bg-brand-600 text-white shadow-lg shadow-brand-500/20',
        secondary: 'bg-surface-800 hover:bg-surface-700 text-surface-100',
        outline: 'border border-surface-700 hover:border-surface-600 text-surface-300 hover:text-surface-100',
        danger: 'bg-danger-500 hover:bg-danger-600 text-white shadow-lg shadow-danger-500/20',
        success: 'bg-success-500 hover:bg-success-600 text-white shadow-lg shadow-success-500/20',
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2.5 text-sm',
        lg: 'px-6 py-3 text-base',
    };

    return (
        <button
            ref={ref}
            disabled={disabled || isLoading}
            className={`inline-flex items-center gap-2 font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
            {...props}
        >
            {isLoading ? (
                <>
                    <div className="w-4 h-4 border-2 border-current border-r-transparent rounded-full animate-spin" />
                    {children}
                </>
            ) : (
                <>
                    {Icon && <Icon size={18} />}
                    {children}
                </>
            )}
        </button>
    );
});

Button.displayName = 'Button';

Button.propTypes = {
    children: PropTypes.node,
    variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'danger', 'success']),
    size: PropTypes.oneOf(['sm', 'md', 'lg']),
    disabled: PropTypes.bool,
    isLoading: PropTypes.bool,
    className: PropTypes.string,
    icon: PropTypes.elementType,
    onClick: PropTypes.func,
};
