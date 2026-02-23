import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useApi } from '../../hooks/useApi';
import { VERDICT_CONFIG } from '../../utils/constants';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';
import {
    Files,
    CheckCircle,
    ShieldCheck,
    AlertTriangle,
    AlertOctagon,
    Upload as UploadIcon,
    FileText,
    ArrowRight,
    Search,
    Zap
} from 'lucide-react';

export default function Dashboard() {
    const { user } = useAuth();
    const { get } = useApi();
    const [stats, setStats] = useState({ totalDocs: 0, validated: 0, authentic: 0, suspicious: 0, fake: 0 });
    const [recentResults, setRecentResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [docsData, historyData] = await Promise.all([
                get('/upload/list?page=1&per_page=50'),
                get('/history?page=1&per_page=50'),
            ]);

            const results = historyData.data.results;

            const authentic = results.filter(r => r.verdict === 'AUTHENTIC').length;
            const suspicious = results.filter(r => r.verdict === 'SUSPICIOUS').length;
            const fake = results.filter(r => r.verdict === 'FAKE').length;

            setStats({
                totalDocs: docsData.data.pagination.total,
                validated: historyData.data.pagination.total,
                authentic,
                suspicious,
                fake,
            });

            setRecentResults(results.slice(0, 5));
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    const statCards = [
        { label: 'Total Documents', value: stats.totalDocs, icon: Files, color: 'brand' },
        { label: 'Validated', value: stats.validated, icon: CheckCircle, color: 'brand' },
        { label: 'Authentic', value: stats.authentic, icon: ShieldCheck, color: 'success' },
        { label: 'Suspicious', value: stats.suspicious, icon: AlertTriangle, color: 'warning' },
        { label: 'Fake', value: stats.fake, icon: AlertOctagon, color: 'danger' },
    ];

    const getVerdictBadge = (verdict) => {
        return VERDICT_CONFIG[verdict]?.badge || 'badge';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <LoadingSpinner />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-16 animate-fade-in space-y-4">
                <AlertMessage type="error" message={error} />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Welcome Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">
                        Welcome back, <span className="bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent">{user?.name}</span>
                    </h1>
                    <p className="text-surface-400 mt-1 font-medium">Here's an overview of your document validations</p>
                </div>
                <Link to="/upload" className="btn-primary inline-flex items-center gap-2 px-6 py-3 rounded-xl shadow-lg shadow-brand-500/20">
                    <UploadIcon size={18} />
                    <span>Upload Document</span>
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                {statCards.map(({ label, value, icon: Icon, color }) => (
                    <div key={label} className="card-hover text-center p-6 rounded-[2rem]">
                        <div className={`p-3 rounded-2xl w-fit mx-auto mb-4 ${color === 'success' ? 'bg-success-500/10 text-success-400' :
                            color === 'warning' ? 'bg-warning-500/10 text-warning-400' :
                                color === 'danger' ? 'bg-danger-500/10 text-danger-400' :
                                    'bg-brand-500/10 text-brand-400'
                            }`}>
                            <Icon size={24} />
                        </div>
                        <div className={`text-3xl font-black tracking-tight ${color === 'success' ? 'text-success-400' :
                            color === 'warning' ? 'text-warning-400' :
                                color === 'danger' ? 'text-danger-400' :
                                    'text-brand-400'
                            }`}>
                            {value}
                        </div>
                        <div className="text-[10px] uppercase tracking-widest text-surface-500 font-bold mt-2">{label}</div>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Results */}
                <div className="card lg:col-span-2 rounded-[2rem] p-8">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-surface-800/50 rounded-xl flex items-center justify-center text-brand-400">
                                <Search size={20} />
                            </div>
                            <h2 className="text-xl font-bold text-surface-100">Recent Results</h2>
                        </div>
                        <Link to="/history" className="text-sm font-semibold text-brand-400 hover:text-brand-300 transition-colors flex items-center gap-1 group">
                            <span>View All</span>
                            <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                        </Link>
                    </div>

                    {recentResults.length === 0 ? (
                        <div className="text-center py-12 bg-surface-950/30 rounded-2xl border border-dashed border-surface-800">
                            <FileText className="w-12 h-12 text-surface-700 mx-auto mb-3" />
                            <p className="text-surface-400 font-medium">No validations yet</p>
                            <Link to="/upload" className="text-brand-400 text-sm font-bold hover:underline mt-2 inline-block">
                                Upload your first document
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recentResults.map((result) => (
                                <Link
                                    key={result.id}
                                    to={`/results/${result.document_id}`}
                                    className="flex items-center justify-between p-4 rounded-2xl bg-surface-800/30 hover:bg-surface-800/60 border border-surface-700/0 hover:border-surface-700/50 transition-all group"
                                >
                                    <div className="flex items-center gap-4 min-w-0">
                                        <div className="w-10 h-10 bg-brand-500/10 rounded-xl flex items-center justify-center text-brand-400 shrink-0 group-hover:scale-110 transition-transform">
                                            <FileText size={20} />
                                        </div>
                                        <div className="min-w-0">
                                            <p className="text-sm font-bold text-surface-200 truncate pr-2">
                                                {result.document?.filename || `Document #${result.document_id}`}
                                            </p>
                                            <p className="text-xs text-surface-500 font-medium mt-0.5 flex items-center gap-1.5">
                                                <Zap size={10} className="text-brand-500" />
                                                <span>Score: {(result.scores.final_score * 100).toFixed(1)}%</span>
                                            </p>
                                        </div>
                                    </div>
                                    <span className={`${getVerdictBadge(result.verdict)} !px-3 font-bold`}>{result.verdict}</span>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>

                {/* Quick Upload */}
                <div className="card rounded-[2rem] flex flex-col items-center justify-center text-center p-8 bg-gradient-to-br from-brand-600/5 to-transparent">
                    <div className="w-20 h-20 bg-brand-500/10 rounded-3xl flex items-center justify-center mb-6 relative group">
                        <div className="absolute inset-0 bg-brand-500/10 rounded-3xl animate-pulse group-hover:animate-none group-hover:scale-110 transition-transform" />
                        <UploadIcon className="text-brand-400 relative z-10" size={32} />
                    </div>
                    <h3 className="text-xl font-bold text-surface-100 mb-3">Validate a Document</h3>
                    <p className="text-surface-400 text-sm mb-8 max-w-[240px] font-medium leading-relaxed">
                        Upload a document to verify its authenticity using our AI-powered analysis
                    </p>
                    <Link to="/upload" className="btn-primary w-full py-4 rounded-2xl shadow-xl shadow-brand-500/20 flex items-center justify-center gap-2 group">
                        <span>Upload & Validate</span>
                        <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </Link>
                </div>
            </div>
        </div>
    );
}
