import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export function Breadcrumb({ items }) {
    return (
        <nav className="flex items-center gap-1 text-sm" aria-label="Breadcrumb">
            {items.map((item, index) => (
                <div key={index} className="flex items-center gap-1">
                    {index > 0 && <ChevronRight size={16} className="text-surface-400" />}
                    {item.href ? (
                        <Link
                            to={item.href}
                            className="text-brand-500 hover:text-brand-600 transition-colors font-medium"
                        >
                            {item.label}
                        </Link>
                    ) : (
                        <span className="text-surface-600">{item.label}</span>
                    )}
                </div>
            ))}
        </nav>
    );
}

export function PageHeader({ title, subtitle, actions }) {
    return (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6 mb-8">
            <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-surface-900">{title}</h1>
                {subtitle && <p className="text-surface-600 mt-2">{subtitle}</p>}
            </div>
            {actions && <div className="flex gap-3">{actions}</div>}
        </div>
    );
}
