import { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';
import { ShieldCheck, Loader2 } from 'lucide-react';

export default function Register() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register, isAuthenticated } = useAuth();
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
            await register(email, password, name);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-surface-950 px-4">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-brand-600/8 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 left-1/3 w-80 h-80 bg-brand-500/6 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 w-full max-w-md animate-fade-in">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-brand-500 to-brand-700 rounded-2xl shadow-lg shadow-brand-500/25 mb-4">
                        <ShieldCheck className="text-white" size={28} />
                    </div>
                    <h1 className="text-2xl font-bold text-surface-100">Create account</h1>
                    <p className="text-surface-400 mt-1">Get started with DocValidator</p>
                </div>

                {/* Form */}
                <div className="card">
                    <AlertMessage type="error" message={error} onClose={() => setError('')} />

                    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                        <div>
                            <label htmlFor="register-name" className="block text-sm font-medium text-surface-300 mb-1.5">Full Name</label>
                            <input
                                id="register-name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="input-field"
                                placeholder="John Doe"
                                required
                                minLength={2}
                                autoComplete="name"
                            />
                        </div>

                        <div>
                            <label htmlFor="register-email" className="block text-sm font-medium text-surface-300 mb-1.5">Email</label>
                            <input
                                id="register-email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="input-field"
                                placeholder="you@example.com"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div>
                            <label htmlFor="register-password" className="block text-sm font-medium text-surface-300 mb-1.5">Password</label>
                            <input
                                id="register-password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input-field"
                                placeholder="Min. 6 characters"
                                required
                                minLength={6}
                                autoComplete="new-password"
                            />
                        </div>

                        <div>
                            <label htmlFor="register-confirm-password" className="block text-sm font-medium text-surface-300 mb-1.5">Confirm Password</label>
                            <input
                                id="register-confirm-password"
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="input-field"
                                placeholder="Re-enter password"
                                required
                                autoComplete="new-password"
                            />
                        </div>

                        <button
                            id="register-submit"
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full flex items-center justify-center gap-2"
                            aria-label="Create your account"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Creating account...
                                </>
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>

                    <p className="text-center text-sm text-surface-400 mt-4">
                        Already have an account?{' '}
                        <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
