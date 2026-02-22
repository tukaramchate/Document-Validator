import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { user, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navLinks = [
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/upload', label: 'Upload', icon: '📤' },
        { path: '/history', label: 'History', icon: '📋' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="glass-panel border-b border-surface-800/50 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center gap-2.5 group">
                        <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:shadow-brand-500/40 transition-shadow">
                            <span className="text-white font-bold text-sm">DV</span>
                        </div>
                        <span className="text-lg font-bold bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent hidden sm:block">
                            DocValidator
                        </span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="flex items-center gap-1">
                        {navLinks.map(({ path, label, icon }) => (
                            <Link
                                key={path}
                                to={path}
                                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${isActive(path)
                                        ? 'bg-brand-600/15 text-brand-400 border border-brand-500/20'
                                        : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'
                                    }`}
                            >
                                <span className="text-base">{icon}</span>
                                <span className="hidden sm:inline">{label}</span>
                            </Link>
                        ))}
                    </div>

                    {/* User Menu */}
                    <div className="flex items-center gap-3">
                        <div className="hidden sm:flex flex-col items-end">
                            <span className="text-sm font-medium text-surface-200">{user?.name}</span>
                            <span className="text-xs text-surface-500">{user?.email}</span>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="px-3 py-2 text-sm text-surface-400 hover:text-danger-400 hover:bg-danger-500/10 rounded-lg transition-all duration-200"
                            title="Logout"
                        >
                            ⬅ Exit
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
