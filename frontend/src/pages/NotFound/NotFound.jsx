import { Link } from 'react-router-dom';
import { ShieldCheck, Home, LayoutDashboard } from 'lucide-react';

export default function NotFound() {
    return (
        <div className="min-h-screen bg-surface-950 flex items-center justify-center px-4">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-brand-600/8 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-brand-500/6 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 text-center max-w-md animate-fade-in">
                <div className="mb-8">
                    <div className="text-8xl font-black bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent mb-3">404</div>
                    <p className="text-lg text-surface-400 font-medium">Page not found</p>
                </div>

                <h1 className="text-2xl font-bold text-surface-100 mb-4">
                    Oops! This page doesn't exist
                </h1>

                <p className="text-surface-400 mb-10 leading-relaxed font-medium">
                    The page you're looking for might have been removed or is temporarily unavailable.
                </p>

                <div className="flex gap-3 justify-center">
                    <Link to="/" className="btn-primary px-6 py-3 rounded-xl font-bold flex items-center gap-2">
                        <Home size={18} />
                        Back to Home
                    </Link>
                    <Link to="/dashboard" className="btn-secondary px-6 py-3 rounded-xl font-bold flex items-center gap-2">
                        <LayoutDashboard size={18} />
                        Dashboard
                    </Link>
                </div>

                <div className="mt-12">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-500/10 rounded-xl border border-brand-500/20">
                        <ShieldCheck size={18} className="text-brand-400" />
                        <span className="text-sm text-brand-400 font-medium">Need help? Contact support</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
