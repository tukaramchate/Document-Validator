import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useState } from 'react';
import {
    LayoutDashboard,
    Upload as UploadIcon,
    History as HistoryIcon,
    LogOut,
    Menu,
    X,
    Sun,
    Moon,
    ShieldCheck,
    Database
} from 'lucide-react';

export default function Navbar() {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navLinks = [
        {
            path: '/dashboard',
            label: user?.role === 'admin' ? 'Admin Panel' : user?.role === 'institution' ? 'Institution Portal' : 'Dashboard',
            icon: LayoutDashboard,
            condition: true
        },
        { path: '/upload', label: 'Upload', icon: UploadIcon, condition: user?.role === 'user' },
        { path: '/history', label: 'History', icon: HistoryIcon, condition: user?.role === 'user' },
        { path: '/institution/records', label: 'Manage Records', icon: Database, condition: user?.role === 'institution' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="glass-panel border-b border-surface-800/50 sticky top-0 z-50 transition-colors duration-300" aria-label="Main navigation">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center gap-2.5 group" aria-label="EduVerify AI Home">
                        <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-700 rounded-xl flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:shadow-brand-500/40 transition-all duration-300">
                            <ShieldCheck className="text-white w-5 h-5" />
                        </div>
                        <span className="text-lg font-bold bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent hidden sm:block">
                            EduVerify AI
                        </span>
                    </Link>

                    {/* Desktop Navigation Links */}
                    <div className="hidden md:flex items-center gap-1">
                        {navLinks.map(({ path, label, icon: Icon, condition }) => (
                            condition && (
                                <Link
                                    key={path}
                                    to={path}
                                    aria-current={isActive(path) ? 'page' : undefined}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${isActive(path)
                                        ? 'bg-brand-600/15 text-brand-400 border border-brand-500/20'
                                        : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'
                                        }`}
                                >
                                    <Icon size={18} />
                                    <span>{label}</span>
                                </Link>
                            )
                        ))}
                    </div>

                    {/* Right Side: Theme Toggle + User + Logout */}
                    <div className="flex items-center gap-2 sm:gap-4">
                        {/* Theme Toggle */}
                        <button
                            onClick={toggleTheme}
                            className="p-2.5 rounded-xl bg-surface-800/50 text-surface-400 hover:text-brand-400 hover:bg-brand-500/10 transition-all duration-200 border border-surface-700/50"
                            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                        >
                            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        </button>

                        {/* User Info */}
                        <div className="hidden lg:flex flex-col items-end mr-1">
                            <span className="text-sm font-semibold text-surface-100">{user?.name}</span>
                            <span className="text-[10px] uppercase tracking-wider text-surface-500 font-bold">{user?.email}</span>
                        </div>

                        {/* Logout */}
                        <button
                            onClick={handleLogout}
                            className="hidden md:flex items-center gap-2 px-4 py-2 text-sm font-medium text-surface-400 hover:text-danger-400 hover:bg-danger-500/10 border border-transparent hover:border-danger-500/20 rounded-xl transition-all duration-200"
                            aria-label="Logout"
                        >
                            <LogOut size={18} />
                            <span className="hidden lg:inline">Sign Out</span>
                        </button>

                        {/* Mobile Hamburger */}
                        <button
                            className="md:hidden p-2 text-surface-400 hover:text-surface-200 rounded-xl transition-all bg-surface-800/50 border border-surface-700/50"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            aria-label="Toggle menu"
                            aria-expanded={mobileMenuOpen}
                        >
                            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t border-surface-800/50 animate-fade-in bg-surface-950/80 backdrop-blur-xl">
                    <div className="px-4 py-4 space-y-2">
                        {navLinks.map(({ path, label, icon: Icon }) => (
                            <Link
                                key={path}
                                to={path}
                                onClick={() => setMobileMenuOpen(false)}
                                aria-current={isActive(path) ? 'page' : undefined}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${isActive(path)
                                    ? 'bg-brand-600/15 text-brand-400 border border-brand-500/20'
                                    : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'
                                    }`}
                            >
                                <Icon size={20} />
                                <span>{label}</span>
                            </Link>
                        ))}

                        <div className="border-t border-surface-800/50 pt-4 mt-2">
                            <div className="px-4 py-2 mb-2">
                                <p className="text-sm font-bold text-surface-100">{user?.name}</p>
                                <p className="text-xs text-surface-500">{user?.email}</p>
                            </div>
                            <button
                                onClick={() => { setMobileMenuOpen(false); handleLogout(); }}
                                className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-danger-400 hover:bg-danger-500/10 rounded-xl transition-all"
                                aria-label="Logout"
                            >
                                <LogOut size={20} />
                                <span>Logout</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </nav>
    );
}
