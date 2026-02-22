import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useApi } from '../../hooks/useApi';

export default function Dashboard() {
    const { user } = useAuth();
    const { get } = useApi();
    const [stats, setStats] = useState({ totalDocs: 0, validated: 0, authentic: 0, suspicious: 0, fake: 0 });
    const [recentResults, setRecentResults] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            // Fetch documents
            const docsResponse = await get('/upload/list?page=1&per_page=50');
            const docs = docsResponse.data.documents;

            // Fetch validation history
            const historyResponse = await get('/history?page=1&per_page=50');
            const results = historyResponse.data.results;

            // Calculate stats
            const authentic = results.filter(r => r.verdict === 'AUTHENTIC').length;
            const suspicious = results.filter(r => r.verdict === 'SUSPICIOUS').length;
            const fake = results.filter(r => r.verdict === 'FAKE').length;

            setStats({
                totalDocs: docsResponse.data.pagination.total,
                validated: historyResponse.data.pagination.total,
                authentic,
                suspicious,
                fake,
            });

            setRecentResults(results.slice(0, 5));
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const statCards = [
        { label: 'Total Documents', value: stats.totalDocs, icon: '📁', color: 'brand' },
        { label: 'Validated', value: stats.validated, icon: '✅', color: 'brand' },
        { label: 'Authentic', value: stats.authentic, icon: '🛡️', color: 'success' },
        { label: 'Suspicious', value: stats.suspicious, icon: '⚠️', color: 'warning' },
        { label: 'Fake', value: stats.fake, icon: '❌', color: 'danger' },
    ];

    const getVerdictBadge = (verdict) => {
        const badges = {
            AUTHENTIC: 'badge-success',
            SUSPICIOUS: 'badge-warning',
            FAKE: 'badge-danger',
        };
        return badges[verdict] || 'badge';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Welcome Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-surface-100">
                        Welcome back, <span className="bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent">{user?.name}</span>
                    </h1>
                    <p className="text-surface-400 mt-1">Here's an overview of your document validations</p>
                </div>
                <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
                    <span>📤</span> Upload Document
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                {statCards.map(({ label, value, icon, color }) => (
                    <div key={label} className="card-hover text-center">
                        <div className="text-2xl mb-2">{icon}</div>
                        <div className={`text-2xl font-bold ${color === 'success' ? 'text-success-400' :
                                color === 'warning' ? 'text-warning-400' :
                                    color === 'danger' ? 'text-danger-400' :
                                        'text-brand-400'
                            }`}>
                            {value}
                        </div>
                        <div className="text-xs text-surface-400 mt-1">{label}</div>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Recent Results */}
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-surface-200">Recent Results</h2>
                        <Link to="/history" className="text-sm text-brand-400 hover:text-brand-300 transition-colors">View all →</Link>
                    </div>

                    {recentResults.length === 0 ? (
                        <div className="text-center py-8">
                            <p className="text-surface-500 text-sm">No validations yet</p>
                            <Link to="/upload" className="text-brand-400 text-sm hover:underline mt-1 inline-block">
                                Upload your first document
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recentResults.map((result) => (
                                <Link
                                    key={result.id}
                                    to={`/results/${result.document_id}`}
                                    className="flex items-center justify-between p-3 rounded-xl bg-surface-800/40 hover:bg-surface-800/70 transition-colors group"
                                >
                                    <div className="flex items-center gap-3 min-w-0">
                                        <div className="w-8 h-8 bg-brand-600/15 rounded-lg flex items-center justify-center text-sm shrink-0">
                                            📄
                                        </div>
                                        <div className="min-w-0">
                                            <p className="text-sm font-medium text-surface-200 truncate">
                                                {result.document?.filename || `Document #${result.document_id}`}
                                            </p>
                                            <p className="text-xs text-surface-500">
                                                Score: {(result.scores.final_score * 100).toFixed(1)}%
                                            </p>
                                        </div>
                                    </div>
                                    <span className={getVerdictBadge(result.verdict)}>{result.verdict}</span>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>

                {/* Quick Upload */}
                <div className="card flex flex-col items-center justify-center text-center py-12">
                    <div className="w-16 h-16 bg-brand-600/10 rounded-2xl flex items-center justify-center mb-4">
                        <span className="text-3xl">📤</span>
                    </div>
                    <h3 className="text-lg font-semibold text-surface-200 mb-2">Validate a Document</h3>
                    <p className="text-surface-400 text-sm mb-6 max-w-xs">
                        Upload a document to verify its authenticity using our AI-powered analysis
                    </p>
                    <Link to="/upload" className="btn-primary">
                        Upload & Validate
                    </Link>
                </div>
            </div>
        </div>
    );
}
