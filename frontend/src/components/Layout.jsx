import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export default function Layout() {
    return (
        <div className="min-h-screen bg-surface-950">
            {/* Background decorative elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-brand-600/5 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-brand-500/5 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10">
                <Navbar />
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
