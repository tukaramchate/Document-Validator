import { Link } from 'react-router-dom';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { useMemo } from 'react';

export default function ServerError() {
    // Generate a stable error ID that doesn't change on re-render
    const errorId = useMemo(() => Math.random().toString(36).substr(2, 9), []);

    return (
        <div className="min-h-screen bg-surface-950 flex items-center justify-center px-4">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-danger-500/8 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 left-1/3 w-80 h-80 bg-danger-600/6 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 text-center max-w-md animate-fade-in">
                <div className="mb-8">
                    <div className="w-20 h-20 bg-danger-500/15 border border-danger-500/20 rounded-3xl flex items-center justify-center mx-auto mb-6">
                        <AlertTriangle size={40} className="text-danger-400" />
                    </div>
                    <div className="text-6xl font-black text-danger-400 mb-2">500</div>
                    <p className="text-lg text-surface-400 font-medium">Server error</p>
                </div>

                <h1 className="text-2xl font-bold text-surface-100 mb-4">
                    Something went wrong
                </h1>

                <p className="text-surface-400 mb-10 leading-relaxed font-medium">
                    Our servers are experiencing issues. Our team has been notified and is working on a fix.
                </p>

                <div className="flex gap-3 justify-center">
                    <button
                        onClick={() => window.location.reload()}
                        className="btn-primary px-6 py-3 rounded-xl font-bold flex items-center gap-2 bg-danger-600 hover:bg-danger-500 shadow-lg shadow-danger-600/20"
                    >
                        <RefreshCw size={18} />
                        Try Again
                    </button>
                    <Link to="/" className="btn-secondary px-6 py-3 rounded-xl font-bold flex items-center gap-2">
                        <Home size={18} />
                        Go Home
                    </Link>
                </div>

                <div className="mt-12">
                    <div className="text-xs text-surface-600 font-mono bg-surface-900/40 border border-surface-800/50 px-4 py-2 rounded-xl inline-block">
                        Error ID: {errorId}
                    </div>
                </div>
            </div>
        </div>
    );
}
