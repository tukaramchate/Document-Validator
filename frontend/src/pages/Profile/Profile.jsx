import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import { User, Mail, Calendar, Award, Settings, ArrowLeft, ShieldCheck } from 'lucide-react';

export default function Profile() {
    const { user } = useAuth();

    const getRoleLabel = (role) => {
        switch (role) {
            case 'admin': return 'Administrator';
            case 'institution': return 'Institution';
            default: return 'User';
        }
    };

    const getRoleBadgeClasses = (role) => {
        switch (role) {
            case 'admin': return 'bg-danger-500/10 text-danger-400 border-danger-500/20';
            case 'institution': return 'bg-warning-500/10 text-warning-400 border-warning-500/20';
            default: return 'bg-success-500/10 text-success-400 border-success-500/20';
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-6">
                <div className="w-20 h-20 bg-brand-500/10 rounded-full flex items-center justify-center">
                    <User size={40} className="text-brand-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">{user?.name}</h1>
                    <span className={`inline-flex items-center px-3 py-1 mt-2 rounded-xl text-xs font-black uppercase tracking-widest border ${getRoleBadgeClasses(user?.role)}`}>
                        {getRoleLabel(user?.role)}
                    </span>
                </div>
            </div>

            {/* Account Information */}
            <div className="card rounded-[2rem] p-8">
                <h2 className="text-xl font-bold text-surface-100 mb-6">Account Information</h2>
                <div className="space-y-1">
                    <div className="flex items-center gap-4 py-4 border-b border-surface-800/50">
                        <div className="p-2.5 bg-brand-500/10 rounded-xl text-brand-400">
                            <Mail size={20} />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-surface-500">Email</p>
                            <p className="text-surface-200 font-bold mt-1">{user?.email}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 py-4 border-b border-surface-800/50">
                        <div className="p-2.5 bg-brand-500/10 rounded-xl text-brand-400">
                            <Award size={20} />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-surface-500">Role</p>
                            <p className="text-surface-200 font-bold mt-1">{getRoleLabel(user?.role)}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 py-4">
                        <div className="p-2.5 bg-brand-500/10 rounded-xl text-brand-400">
                            <Calendar size={20} />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-surface-500">Member Since</p>
                            <p className="text-surface-200 font-bold mt-1">
                                {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) : 'N/A'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Subscription Status */}
            {user?.role === 'user' && (
                <div className="card rounded-[2rem] p-8 bg-brand-600/5 border-brand-500/20">
                    <h2 className="text-xl font-bold text-surface-100 mb-4">Subscription</h2>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-bold text-surface-200">
                                {user?.is_paid ? 'Pro Plan' : 'Free Plan'}
                            </p>
                            <p className="text-sm text-surface-400 mt-1 font-medium">
                                {user?.is_paid
                                    ? 'Unlimited validations'
                                    : `${user?.validation_count || 0} of 10 validations used`}
                            </p>
                        </div>
                        {!user?.is_paid && (
                            <Link to="/pricing" className="btn-primary px-6 py-3 rounded-xl font-bold">
                                Upgrade to Pro
                            </Link>
                        )}
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
                <Link to="/settings" className="btn-primary px-6 py-3 rounded-xl font-bold flex items-center gap-2">
                    <Settings size={18} />
                    <span>Settings</span>
                </Link>
                <Link to="/dashboard" className="btn-secondary px-6 py-3 rounded-xl font-bold flex items-center gap-2">
                    <ArrowLeft size={18} />
                    <span>Back to Dashboard</span>
                </Link>
            </div>
        </div>
    );
}
