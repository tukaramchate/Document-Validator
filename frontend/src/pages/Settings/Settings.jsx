import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useApi } from '../../hooks/useApi';
import { useToast } from '../../context/ToastContext';
import { Settings as SettingsIcon, Lock, Bell, LogOut, Loader2, Check } from 'lucide-react';

export default function Settings() {
    const { user, logout } = useAuth();
    const { put } = useApi();
    const toast = useToast();
    const [activeTab, setActiveTab] = useState('account');

    // Password change state
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [changingPassword, setChangingPassword] = useState(false);

    const handleChangePassword = async (e) => {
        e.preventDefault();

        if (newPassword !== confirmPassword) {
            toast.error('New passwords do not match');
            return;
        }
        if (newPassword.length < 6) {
            toast.error('New password must be at least 6 characters');
            return;
        }

        setChangingPassword(true);
        try {
            await put('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword,
            });
            toast.success('Password updated successfully');
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (err) {
            toast.error(err.response?.data?.error?.message || 'Failed to update password');
        } finally {
            setChangingPassword(false);
        }
    };

    const tabs = [
        { id: 'account', label: 'Account' },
        { id: 'security', label: 'Security' },
        { id: 'preferences', label: 'Preferences' },
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-brand-500/10 rounded-2xl flex items-center justify-center">
                    <SettingsIcon size={24} className="text-brand-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">Settings</h1>
                    <p className="text-surface-400 font-medium">Manage your account and preferences</p>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2 p-1 bg-surface-900/40 rounded-[1rem] border border-surface-800/50 w-fit">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${activeTab === tab.id
                            ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/20'
                            : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/30'
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Account Tab */}
            {activeTab === 'account' && (
                <div className="card rounded-[2rem] p-8">
                    <h2 className="text-xl font-bold text-surface-100 mb-6">Personal Information</h2>
                    <div className="space-y-5">
                        <div>
                            <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Full Name</label>
                            <input
                                type="text"
                                defaultValue={user?.name}
                                className="input-field"
                                disabled
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Email</label>
                            <input
                                type="email"
                                defaultValue={user?.email}
                                className="input-field"
                                disabled
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Role</label>
                            <input
                                type="text"
                                defaultValue={user?.role}
                                className="input-field"
                                disabled
                            />
                        </div>
                        <p className="text-xs text-surface-500 font-medium">Contact support to update your name or email.</p>
                    </div>
                </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
                <div className="space-y-6">
                    <div className="card rounded-[2rem] p-8">
                        <h2 className="text-xl font-bold text-surface-100 mb-6">Change Password</h2>
                        <form onSubmit={handleChangePassword} className="space-y-5">
                            <div>
                                <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Current Password</label>
                                <input
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="input-field"
                                    placeholder="Enter current password"
                                    required
                                    autoComplete="current-password"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">New Password</label>
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="input-field"
                                    placeholder="Min. 6 characters"
                                    required
                                    minLength={6}
                                    autoComplete="new-password"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Confirm New Password</label>
                                <input
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="input-field"
                                    placeholder="Re-enter new password"
                                    required
                                    autoComplete="new-password"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={changingPassword}
                                className="btn-primary px-6 py-3 rounded-xl font-bold flex items-center gap-2"
                            >
                                {changingPassword ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Updating...
                                    </>
                                ) : (
                                    <>
                                        <Check size={18} />
                                        Update Password
                                    </>
                                )}
                            </button>
                        </form>
                    </div>

                    <div className="card rounded-[2rem] p-8">
                        <h2 className="text-xl font-bold text-surface-100 mb-4">Two-Factor Authentication</h2>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-bold text-surface-200">2FA Status</p>
                                <p className="text-sm text-surface-400 mt-1 font-medium">Not enabled</p>
                            </div>
                            <button className="btn-secondary px-6 py-3 rounded-xl font-bold opacity-50 cursor-not-allowed" disabled>
                                Coming Soon
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
                <div className="card rounded-[2rem] p-8">
                    <h2 className="text-xl font-bold text-surface-100 mb-6">Email Notifications</h2>
                    <div className="space-y-4">
                        {[
                            { label: 'Verification Results', desc: 'Get notified when document validation completes', defaultChecked: true },
                            { label: 'Weekly Summary', desc: 'Receive a weekly report of your activity', defaultChecked: true },
                            { label: 'Product Updates', desc: 'Learn about new features and improvements', defaultChecked: false },
                        ].map((item) => (
                            <label key={item.label} className="flex items-center justify-between p-4 bg-surface-800/30 rounded-2xl border border-surface-700/30 hover:border-surface-700/50 transition-colors cursor-pointer group">
                                <div>
                                    <span className="text-sm font-bold text-surface-200 group-hover:text-surface-100 transition-colors">{item.label}</span>
                                    <p className="text-xs text-surface-500 mt-0.5 font-medium">{item.desc}</p>
                                </div>
                                <input type="checkbox" defaultChecked={item.defaultChecked} className="w-5 h-5 accent-brand-500 rounded" />
                            </label>
                        ))}
                    </div>
                    <p className="text-xs text-surface-500 font-medium mt-6">Notification preferences will be saved automatically.</p>
                </div>
            )}

            {/* Danger Zone */}
            <div className="card rounded-[2rem] p-8 bg-danger-500/5 border-danger-500/20">
                <h2 className="text-xl font-bold text-danger-400 mb-4">Danger Zone</h2>
                <div className="flex items-center justify-between">
                    <div>
                        <p className="font-bold text-surface-200">Sign out</p>
                        <p className="text-sm text-surface-400 mt-1 font-medium">End your session and sign out</p>
                    </div>
                    <button
                        onClick={() => {
                            logout();
                            window.location.href = '/login';
                        }}
                        className="btn-secondary px-6 py-3 rounded-xl font-bold flex items-center gap-2 text-danger-400 hover:bg-danger-500/10 hover:border-danger-500/30"
                    >
                        <LogOut size={18} />
                        Sign Out
                    </button>
                </div>
            </div>
        </div>
    );
}
