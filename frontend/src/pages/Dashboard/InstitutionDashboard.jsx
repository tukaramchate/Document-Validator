import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';
import {
    Database,
    UploadCloud,
    ShieldCheck,
    FileSearch,
    Plus,
    Building2,
    CheckCircle2,
    FileText
} from 'lucide-react';

export default function InstitutionDashboard() {
    const { user } = useAuth();
    const { get } = useApi();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchInstitutionData();
    }, []);

    const fetchInstitutionData = async () => {
        try {
            const response = await get('/institution/stats');
            setStats(response.data);
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Failed to load institution data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <AlertMessage type="error" message={error} />;

    const statCards = [
        { label: 'Verification Records', value: stats?.total_records || 0, icon: Database, color: 'brand' },
        { label: 'Trust Score', value: '99.8%', icon: ShieldCheck, color: 'brand' },
        { label: 'Matches Found', value: '142', icon: CheckCircle2, color: 'success' },
    ];

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Institution Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">
                        Institution <span className="text-brand-400">Portal</span>
                    </h1>
                    <p className="text-surface-400 mt-1 font-medium italic">{stats?.institution_name}</p>
                </div>
                <div className="flex gap-3">
                    <Link to="/institution/records" className="btn-primary inline-flex items-center gap-2 px-6 py-3 rounded-xl shadow-lg shadow-brand-500/20">
                        <Plus size={18} />
                        <span>Add Record</span>
                    </Link>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {statCards.map(({ label, value, icon: Icon, color }) => (
                    <div key={label} className="card-hover p-8 rounded-[2rem] border-brand-500/10">
                        <div className={`p-4 rounded-2xl w-fit mb-6 ${color === 'success' ? 'bg-success-500/10 text-success-400' : 'bg-brand-500/10 text-brand-400'}`}>
                            <Icon size={28} />
                        </div>
                        <div className="text-4xl font-black tracking-tight text-surface-100">{value}</div>
                        <div className="text-xs uppercase tracking-[0.2em] text-surface-500 font-black mt-3">{label}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Manage Records Card */}
                <div className="card rounded-[2.5rem] p-10 bg-gradient-to-br from-brand-600/10 to-transparent border-brand-500/20 group overflow-hidden relative">
                    <div className="absolute -right-8 -bottom-8 text-brand-500/5 rotate-12 group-hover:scale-110 transition-transform duration-700">
                        <Database size={240} />
                    </div>

                    <div className="relative z-10">
                        <div className="w-16 h-16 bg-brand-500/20 rounded-2xl flex items-center justify-center text-brand-400 mb-8">
                            <UploadCloud size={32} />
                        </div>
                        <h2 className="text-2xl font-black text-surface-100 mb-4">Verification Truth Data</h2>
                        <p className="text-surface-400 font-medium mb-10 max-w-sm leading-relaxed">
                            Upload your official student or employee records to enable seamless AI-powered verification across the EduVerify AI network.
                        </p>
                        <div className="flex gap-4">
                            <Link to="/institution/records" className="btn-primary px-8 py-3 rounded-xl font-bold">
                                Manage Records
                            </Link>
                            <button className="px-6 py-3 bg-surface-800 hover:bg-surface-700 text-surface-200 rounded-xl font-bold transition-all">
                                How it works
                            </button>
                        </div>
                    </div>
                </div>

                {/* Integration Info */}
                <div className="card rounded-[2.5rem] p-10 border-surface-800/50">
                    <div className="w-16 h-16 bg-surface-800 rounded-2xl flex items-center justify-center text-brand-400 mb-8">
                        <Building2 size={32} />
                    </div>
                    <h2 className="text-2xl font-black text-surface-100 mb-4">Enterprise Integration</h2>
                    <p className="text-surface-400 font-medium mb-6 leading-relaxed">
                        Your institution is currently using the **Standard Tier**. You can issue verifiable credentials that are cryptographically secured.
                    </p>

                    <div className="space-y-4">
                        {[
                            { label: 'Blockchain Verification', status: 'Enabled', icon: ShieldCheck },
                            { label: 'Bulk Record Upload', status: 'Active', icon: FileSearch },
                            { label: 'API Access', status: 'Coming Soon', icon: FileText },
                        ].map((item) => (
                            <div key={item.label} className="flex items-center justify-between p-4 bg-surface-950/50 rounded-2xl border border-surface-800/50">
                                <div className="flex items-center gap-3">
                                    <item.icon size={18} className="text-brand-500" />
                                    <span className="text-sm font-bold text-surface-200">{item.label}</span>
                                </div>
                                <span className={`text-[10px] font-black uppercase tracking-widest ${item.status === 'Enabled' || item.status === 'Active' ? 'text-success-500' : 'text-surface-500'}`}>
                                    {item.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
