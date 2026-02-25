import { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AlertMessage from '../../components/AlertMessage';
import { ShieldAlert, Loader2 } from 'lucide-react';

export default function AdminRegister() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { registerAdmin, isAuthenticated } = useAuth();
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
            await registerAdmin(email, password, name);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Admin registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-surface-950 px-4">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-red-600/8 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 left-1/3 w-80 h-80 bg-red-500/6 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 w-full max-w-md animate-fade-in">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl shadow-lg shadow-red-500/25 mb-4">
                        <ShieldAlert className="text-white" size={28} />
                    </div>
                    <h1 className="text-2xl font-bold text-surface-100">Administrator Setup</h1>
                    <p className="text-surface-400 mt-1">Create a master administrative account</p>
                </div>

                {/* Form */}
                <div className="card border-red-900/20">
                    <div className="mb-6 p-3 bg-red-950/20 border border-red-900/30 rounded-xl">
                        <p className="text-xs text-red-400 text-center font-medium uppercase tracking-wider">
                            Restricted Access Area
                        </p>
                    </div>

                    <AlertMessage type="error" message={error} onClose={() => setError('')} />

                    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                        <div>
                            <label htmlFor="admin-name" className="block text-sm font-medium text-surface-300 mb-1.5">Admin Name</label>
                            <input
                                id="admin-name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="input-field focus:ring-red-500/20 focus:border-red-500/50"
                                placeholder="Admin Name"
                                required
                                minLength={2}
                                autoComplete="name"
                            />
                        </div>

                        <div>
                            <label htmlFor="admin-email" className="block text-sm font-medium text-surface-300 mb-1.5">Admin Email</label>
                            <input
                                id="admin-email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="input-field focus:ring-red-500/20 focus:border-red-500/50"
                                placeholder="admin@eduverify.ai"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div>
                            <label htmlFor="admin-password" className="block text-sm font-medium text-surface-300 mb-1.5">Security Password</label>
                            <input
                                id="admin-password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input-field focus:ring-red-500/20 focus:border-red-500/50"
                                placeholder="••••••••"
                                required
                                minLength={6}
                                autoComplete="new-password"
                            />
                        </div>

                        <div>
                            <label htmlFor="admin-confirm-password" className="block text-sm font-medium text-surface-300 mb-1.5">Confirm Password</label>
                            <input
                                id="admin-confirm-password"
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="input-field focus:ring-red-500/20 focus:border-red-500/50"
                                placeholder="Re-enter password"
                                required
                                autoComplete="new-password"
                            />
                        </div>

                        <button
                            id="admin-submit"
                            type="submit"
                            disabled={loading}
                            className="bg-red-600 hover:bg-red-500 text-white py-2.5 rounded-xl font-semibold shadow-lg shadow-red-600/20 transition-all hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed w-full flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Initializing...
                                </>
                            ) : (
                                'Register Administrator'
                            )}
                        </button>
                    </form>

                    <p className="text-center text-sm text-surface-400 mt-4">
                        <Link to="/login" className="text-surface-400 hover:text-white transition-colors">
                            Return to login
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
