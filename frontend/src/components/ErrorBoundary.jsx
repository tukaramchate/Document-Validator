import { Component } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

/**
 * React Error Boundary — catches unhandled render errors
 * and shows a fallback UI instead of a white screen.
 */
export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-surface-950 flex items-center justify-center px-4">
                    <div className="text-center max-w-md animate-fade-in">
                        <div className="w-20 h-20 bg-danger-500/15 border border-danger-500/20 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <AlertTriangle size={40} className="text-danger-400" />
                        </div>
                        <h1 className="text-2xl font-bold text-surface-100 mb-4">
                            Something went wrong
                        </h1>
                        <p className="text-surface-400 mb-8 leading-relaxed font-medium">
                            {this.state.error?.message || 'An unexpected error occurred. Please try refreshing the page.'}
                        </p>
                        <div className="flex gap-3 justify-center">
                            <button
                                onClick={() => window.location.reload()}
                                className="btn-primary px-6 py-3 rounded-xl font-bold flex items-center gap-2"
                            >
                                <RefreshCw size={18} />
                                Refresh Page
                            </button>
                            <a href="/" className="btn-secondary px-6 py-3 rounded-xl font-bold flex items-center gap-2">
                                <Home size={18} />
                                Go Home
                            </a>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
