import { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';
import AuthBrandPanel from '../../components/AuthBrandPanel';
import { ShieldCheck, Loader2, ChevronLeft, Mail } from 'lucide-react';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex bg-white">
            {/* Left Side - Brand Section */}
            <AuthBrandPanel />

            {/* Right Side - Form Section */}
            <div className="w-full lg:w-1/2 flex flex-col bg-white p-6 sm:p-8 lg:p-12">
                {/* Back to Home */}
                <Link to="/" className="flex items-center gap-2 text-surface-600 hover:text-surface-900 mb-8 w-fit font-medium">
                    <ChevronLeft size={18} />
                    Back to Home
                </Link>

                <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full">
                    {/* Icon */}
                    <div className="mb-6">
                        <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center">
                            <ShieldCheck className="text-brand-500" size={32} />
                        </div>
                    </div>

                    {/* Heading */}
                    <h1 className="text-3xl font-bold text-surface-900 mb-2">Welcome Back</h1>
                    <p className="text-surface-600 mb-8">Sign in to your account or create a new one</p>

                    {/* Tabs */}
                    <div className="flex gap-4 mb-8 border-b border-surface-200">
                        <button className="pb-3 font-semibold text-brand-500 border-b-2 border-brand-500">
                            Login
                        </button>
                        <Link to="/register" className="pb-3 font-semibold text-surface-400 hover:text-surface-600 transition-colors">
                            Register
                        </Link>
                    </div>

                    <AlertMessage type="error" message={error} onClose={() => setError('')} />

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
                        <div>
                            <label htmlFor="login-email" className="block text-sm font-semibold text-surface-700 mb-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    id="login-email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border border-surface-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                                    placeholder="you@example.com"
                                    required
                                    autoComplete="email"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="login-password" className="block text-sm font-semibold text-surface-700 mb-2">Password</label>
                            <input
                                id="login-password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 border border-surface-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                                placeholder="••••••••"
                                required
                                autoComplete="current-password"
                            />
                        </div>

                        <button
                            id="login-submit"
                            type="submit"
                            disabled={loading}
                            className="w-full bg-brand-500 hover:bg-brand-600 text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                            aria-label="Sign in to your account"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Signing In...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <Link to="/help" className="text-brand-500 hover:text-brand-600 font-medium text-sm transition-colors">
                            Need help? Contact Support
                        </Link>
                    </div>
                </div>

                {/* Footer Links */}
                <div className="flex items-center justify-center gap-6 mt-8 text-xs text-surface-500">
                    <a href="#" className="hover:text-surface-700">Terms of Service</a>
                    <span>•</span>
                    <a href="#" className="hover:text-surface-700">Privacy Policy</a>
                </div>
            </div>
        </div>
    );
}
