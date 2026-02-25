import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';
import {
    Users,
    Building2,
    ShieldCheck,
    BarChart3,
    Activity,
    ShieldAlert,
    ExternalLink,
    Clock
} from 'lucide-react';

export default function AdminDashboard() {
    const { user } = useAuth();
    const { get } = useApi();
    const [stats, setStats] = useState(null);
    const [activity, setActivity] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAdminData();
    }, []);

    const fetchAdminData = async () => {
        try {
            const [statsRes, activityRes] = await Promise.all([
                get('/admin/stats'),
                get('/admin/activity'),
            ]);
            setStats(statsRes.data);
            setActivity(activityRes.data.activity);
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Failed to load system metrics');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <AlertMessage type="error" message={error} />;

    const statCards = [
        { label: 'Total Users', value: stats?.users, icon: Users, color: 'brand' },
        { label: 'Institutions', value: stats?.institutions, icon: Building2, color: 'brand' },
        { label: 'Documents', value: stats?.documents, icon: BarChart3, color: 'brand' },
        { label: 'Validations', value: stats?.validations, icon: ShieldCheck, color: 'success' },
    ];

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Admin Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">
                        System <span className="text-red-500">Overview</span>
                    </h1>
                    <p className="text-surface-400 mt-1 font-medium italic">Administrative Control Panel • {user?.name}</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-surface-800 hover:bg-surface-700 text-surface-200 rounded-xl text-sm font-bold transition-colors">
                        System Health
                    </button>
                    <button className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-red-600/20 transition-all group">
                        Maintenance Mode
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {statCards.map(({ label, value, icon: Icon, color }) => (
                    <div key={label} className="card-hover p-6 rounded-[2rem] border-surface-800/50">
                        <div className={`p-3 rounded-2xl w-fit mb-4 ${color === 'success' ? 'bg-success-500/10 text-success-400' : 'bg-brand-500/10 text-brand-400'}`}>
                            <Icon size={24} />
                        </div>
                        <div className="text-3xl font-black tracking-tight text-surface-100">{value}</div>
                        <div className="text-[10px] uppercase tracking-widest text-surface-500 font-bold mt-2">{label}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* System Activity */}
                <div className="card lg:col-span-2 rounded-[2rem] p-8 border-red-900/10">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-red-500/10 rounded-xl flex items-center justify-center text-red-500">
                            <Activity size={20} />
                        </div>
                        <h2 className="text-xl font-bold text-surface-100">Global Activity</h2>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-[10px] uppercase tracking-widest text-surface-500 font-black border-b border-surface-800">
                                    <th className="pb-4 px-2">Timestamp</th>
                                    <th className="pb-4 px-2">File</th>
                                    <th className="pb-4 px-2">Verdict</th>
                                    <th className="pb-4 px-2">Score</th>
                                    <th className="pb-4 px-2 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-surface-800/50">
                                {activity.map((act) => (
                                    <tr key={act.id} className="text-sm text-surface-400 hover:bg-surface-800/20 transition-colors group">
                                        <td className="py-4 px-2 whitespace-nowrap">
                                            <div className="flex items-center gap-2">
                                                <Clock size={12} className="text-surface-600" />
                                                <span>{new Date(act.validated_at).toLocaleTimeString()}</span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-2 font-medium text-surface-200 max-w-[150px] truncate">{act.filename}</td>
                                        <td className="py-4 px-2">
                                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${act.verdict === 'AUTHENTIC' ? 'bg-success-500/10 text-success-400' :
                                                act.verdict === 'FAKE' ? 'bg-danger-500/10 text-danger-400' : 'bg-warning-500/10 text-warning-400'
                                                }`}>
                                                {act.verdict}
                                            </span>
                                        </td>
                                        <td className="py-4 px-2 font-mono text-xs">{(act.score * 100).toFixed(1)}%</td>
                                        <td className="py-4 px-2 text-right">
                                            <Link to={`/results/${act.document_id}`} className="text-surface-600 hover:text-brand-400 transition-colors">
                                                <ExternalLink size={16} />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Verdict Distribution */}
                <div className="card rounded-[2rem] p-8 border-surface-800/50">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 bg-brand-500/10 rounded-xl flex items-center justify-center text-brand-400">
                            <ShieldAlert size={20} />
                        </div>
                        <h2 className="text-xl font-bold text-surface-100">Distribution</h2>
                    </div>

                    <div className="space-y-6">
                        {['authentic', 'suspicious', 'fake'].map((key) => {
                            const count = stats?.distribution[key] || 0;
                            const total = stats?.validations || 1;
                            const percent = (count / total) * 100;
                            const color = key === 'authentic' ? 'bg-success-500' : key === 'fake' ? 'bg-danger-500' : 'bg-warning-500';

                            return (
                                <div key={key}>
                                    <div className="flex justify-between text-xs font-bold uppercase tracking-widest mb-2">
                                        <span className="text-surface-400">{key}</span>
                                        <span className="text-surface-200">{percent.toFixed(0)}%</span>
                                    </div>
                                    <div className="h-2 bg-surface-800 rounded-full overflow-hidden">
                                        <div className={`h-full ${color}`} style={{ width: `${percent}%` }} />
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="mt-12 p-4 bg-surface-950/50 rounded-2xl border border-surface-800/50">
                        <p className="text-[10px] text-surface-500 font-bold uppercase tracking-widest leading-relaxed">
                            AI Confidence Threshold is currently set to 90% for <span className="text-success-500">AUTHENTIC</span> categorization.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
