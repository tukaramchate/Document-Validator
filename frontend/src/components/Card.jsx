import PropTypes from 'prop-types';

export function Card({ children, className = '', onClick, ...props }) {
    return (
        <div
            className={`p-6 rounded-2xl bg-surface-900/40 border border-surface-800/40 backdrop-blur-sm transition-all duration-300 hover:border-brand-500/30 hover:bg-surface-800/40 ${className}`}
            onClick={onClick}
            {...props}
        >
            {children}
        </div>
    );
}

Card.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    onClick: PropTypes.func,
};

export function CardHeader({ children, className = '' }) {
    return <div className={`mb-6 ${className}`}>{children}</div>;
}

CardHeader.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
};

export function CardTitle({ children, className = '', size = 'default' }) {
    const sizeClasses = {
        sm: 'text-lg',
        default: 'text-xl',
        lg: 'text-2xl',
    };
    return <h3 className={`font-bold text-surface-100 ${sizeClasses[size]} ${className}`}>{children}</h3>;
}

CardTitle.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    size: PropTypes.oneOf(['sm', 'default', 'lg']),
};

export function CardContent({ children, className = '' }) {
    return <div className={`space-y-4 ${className}`}>{children}</div>;
}

CardContent.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
};

export function CardFooter({ children, className = '' }) {
    return <div className={`mt-6 flex gap-3 ${className}`}>{children}</div>;
}

CardFooter.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
};
