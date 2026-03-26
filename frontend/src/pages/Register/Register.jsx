import { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';
import AuthBrandPanel from '../../components/AuthBrandPanel';
import { ShieldCheck, Loader2, ChevronLeft, Mail, Lock, User } from 'lucide-react';

export default function Register() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [role, setRole] = useState('user'); // 'user', 'institution'
    const { register, registerInstitution, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        try {
            if (role === 'institution') {
                await registerInstitution(email, password, name);
            } else {
                await register(email, password, name);
            }
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Registration failed');
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

                <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full overflow-y-auto">
                    {/* Icon */}
                    <div className="mb-6">
                        <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center">
                            <ShieldCheck className="text-brand-500" size={32} />
                        </div>
                    </div>

                    {/* Heading */}
                    <h1 className="text-3xl font-bold text-surface-900 mb-2">Create Account</h1>
                    <p className="text-surface-600 mb-6">Join our verification network today</p>

                    {/* Tabs */}
                    <div className="flex gap-4 mb-6 border-b border-surface-200">
                        <Link to="/login" className="pb-3 font-semibold text-surface-400 hover:text-surface-600 transition-colors">
                            Login
                        </Link>
                        <button className="pb-3 font-semibold text-brand-500 border-b-2 border-brand-500">
                            Register
                        </button>
                    </div>

                    {/* Role Selection */}
                    <div className="flex gap-3 mb-6">
                        {['user', 'institution'].map((r) => (
                            <button
                                key={r}
                                type="button"
                                onClick={() => setRole(r)}
                                className={`flex-1 py-2 px-3 text-sm font-semibold rounded-lg border-2 transition-all ${role === r
                                    ? 'bg-brand-50 border-brand-500 text-brand-600'
                                    : 'bg-white border-surface-200 text-surface-600 hover:border-surface-300'
                                    }`}
                            >
                                {r === 'user' ? 'Student' : 'Institution'}
                            </button>
                        ))}
                    </div>

                    <AlertMessage type="error" message={error} onClose={() => setError('')} />

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                        <div>
                            <label htmlFor="register-name" className="block text-sm font-semibold text-surface-700 mb-2">Full Name</label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    id="register-name"
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border border-surface-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                                    placeholder="John Doe"
                                    required
                                    minLength={2}
                                    autoComplete="name"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="register-email" className="block text-sm font-semibold text-surface-700 mb-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    id="register-email"
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
                            <label htmlFor="register-password" className="block text-sm font-semibold text-surface-700 mb-2">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    id="register-password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border border-surface-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                                    placeholder="Min. 6 characters"
                                    required
                                    minLength={6}
                                    autoComplete="new-password"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="register-confirm-password" className="block text-sm font-semibold text-surface-700 mb-2">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    id="register-confirm-password"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border border-surface-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                                    placeholder="Re-enter password"
                                    required
                                    autoComplete="new-password"
                                />
                            </div>
                        </div>

                        <button
                            id="register-submit"
                            type="submit"
                            disabled={loading}
                            className="w-full bg-brand-500 hover:bg-brand-600 text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2 mt-6"
                            aria-label="Create your account"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Creating Account...
                                </>
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>

                    <div className="mt-4 text-center">
                        <p className="text-sm text-surface-600">
                            Already have an account?{' '}
                            <Link to="/login" className="text-brand-500 hover:text-brand-600 font-semibold">
                                Sign in
                            </Link>
                        </p>
                    </div>

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
