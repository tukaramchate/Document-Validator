import { FileText, Search, Inbox } from 'lucide-react';
import { Button } from './Button';

export function EmptyState({ 
    icon: Icon = Inbox, 
    title, 
    description, 
    action,
    actionLabel = 'Get Started',
    className = ''
}) {
    return (
        <div className={`flex flex-col items-center justify-center py-16 text-center ${className}`}>
            <div className="w-16 h-16 bg-surface-100 rounded-2xl flex items-center justify-center mb-6">
                <Icon size={32} className="text-surface-600" />
            </div>
            <h3 className="text-xl font-bold text-surface-900 mb-2">{title}</h3>
            <p className="text-surface-600 mb-8 max-w-sm">{description}</p>
            {action && (
                <Button onClick={action}>
                    {actionLabel}
                </Button>
            )}
        </div>
    );
}

export function SearchEmpty() {
    return (
        <EmptyState
            icon={Search}
            title="No results found"
            description="Try adjusting your search terms or filters"
        />
    );
}

export function NoData() {
    return (
        <EmptyState
            icon={FileText}
            title="No data available"
            description="There's nothing to show here yet"
        />
    );
}
