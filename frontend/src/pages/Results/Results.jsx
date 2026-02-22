import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import { RadialBarChart, RadialBar, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Results() {
    const { docId } = useParams();
    const { get } = useApi();
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchResults();
    }, [docId]);

    const fetchResults = async () => {
        try {
            const response = await get(`/results/${docId}`);
            setResult(response.data.result);
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Failed to load results');
        } finally {
            setLoading(false);
        }
    };

    const getVerdictConfig = (verdict) => {
        const configs = {
            AUTHENTIC: { color: '#10b981', bg: 'bg-success-500/10', border: 'border-success-500/20', text: 'text-success-400', icon: '🛡️', label: 'Authentic' },
            SUSPICIOUS: { color: '#f59e0b', bg: 'bg-warning-500/10', border: 'border-warning-500/20', text: 'text-warning-400', icon: '⚠️', label: 'Suspicious' },
            FAKE: { color: '#ef4444', bg: 'bg-danger-500/10', border: 'border-danger-500/20', text: 'text-danger-400', icon: '❌', label: 'Fake' },
        };
        return configs[verdict] || configs.SUSPICIOUS;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-10 h-10 border-3 border-brand-500 border-t-transparent rounded-full animate-spin" />
                    <p className="text-surface-400 text-sm">Loading results...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-16 animate-fade-in">
                <p className="text-danger-400 mb-4">{error}</p>
                <Link to="/upload" className="btn-primary">Upload a Document</Link>
            </div>
        );
    }

    const verdictConfig = getVerdictConfig(result.verdict);
    const scores = result.scores;
    const finalPercent = (scores.final_score * 100).toFixed(1);

    const scoreBreakdown = [
        { name: 'CNN Analysis', value: scores.cnn_score, weight: '40%', icon: '🧠', desc: 'Visual authenticity' },
        { name: 'OCR Confidence', value: scores.ocr_confidence, weight: '20%', icon: '📝', desc: 'Text recognition' },
        { name: 'DB Verification', value: scores.db_match_score, weight: '40%', icon: '🔍', desc: 'Record matching' },
    ];

    const pieData = [
        { name: 'Score', value: scores.final_score * 100 },
        { name: 'Remaining', value: 100 - scores.final_score * 100 },
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-surface-100">Validation Results</h1>
                    <p className="text-surface-400 mt-1">Document #{docId}</p>
                </div>
                <div className="flex gap-3">
                    <Link to="/upload" className="btn-secondary">Upload Another</Link>
                    <Link to="/history" className="btn-secondary">View History</Link>
                </div>
            </div>

            {/* Verdict Card */}
            <div className={`card ${verdictConfig.bg} ${verdictConfig.border} border`}>
                <div className="flex flex-col sm:flex-row items-center gap-6">
                    {/* Score Circle */}
                    <div className="relative w-40 h-40 shrink-0">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={50}
                                    outerRadius={65}
                                    startAngle={90}
                                    endAngle={-270}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    <Cell fill={verdictConfig.color} />
                                    <Cell fill="rgba(100,116,139,0.15)" />
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className={`text-2xl font-bold ${verdictConfig.text}`}>{finalPercent}%</span>
                            <span className="text-xs text-surface-400">Score</span>
                        </div>
                    </div>

                    {/* Verdict Info */}
                    <div className="text-center sm:text-left">
                        <div className="text-4xl mb-2">{verdictConfig.icon}</div>
                        <h2 className={`text-3xl font-bold ${verdictConfig.text}`}>{verdictConfig.label}</h2>
                        <p className="text-surface-400 mt-2">
                            {result.verdict === 'AUTHENTIC' && 'This document appears to be genuine based on our AI analysis.'}
                            {result.verdict === 'SUSPICIOUS' && 'This document has some inconsistencies that require further review.'}
                            {result.verdict === 'FAKE' && 'This document shows significant signs of being fraudulent.'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {scoreBreakdown.map(({ name, value, weight, icon, desc }) => (
                    <div key={name} className="card-hover">
                        <div className="flex items-center gap-2 mb-3">
                            <span className="text-xl">{icon}</span>
                            <div>
                                <h3 className="text-sm font-semibold text-surface-200">{name}</h3>
                                <span className="text-xs text-surface-500">Weight: {weight}</span>
                            </div>
                        </div>
                        <div className="flex items-end gap-2 mb-2">
                            <span className="text-2xl font-bold text-surface-100">{(value * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-surface-800 rounded-full h-2 overflow-hidden">
                            <div
                                className="h-full rounded-full bg-brand-500 transition-all duration-1000"
                                style={{ width: `${value * 100}%` }}
                            />
                        </div>
                        <p className="text-xs text-surface-500 mt-2">{desc}</p>
                    </div>
                ))}
            </div>

            {/* Extracted Data & Field Matches */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Extracted Data */}
                {result.extracted_data && (
                    <div className="card">
                        <h3 className="text-lg font-semibold text-surface-200 mb-4">📝 Extracted Data</h3>
                        <div className="space-y-2">
                            {Object.entries(result.extracted_data).map(([key, value]) => (
                                <div key={key} className="flex justify-between py-2 border-b border-surface-800 last:border-0">
                                    <span className="text-sm text-surface-400 capitalize">{key.replace(/_/g, ' ')}</span>
                                    <span className="text-sm text-surface-200 font-medium">{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Field Matches */}
                {result.field_matches && (
                    <div className="card">
                        <h3 className="text-lg font-semibold text-surface-200 mb-4">🔍 Field Verification</h3>
                        <div className="space-y-2">
                            {Object.entries(result.field_matches).map(([key, matched]) => (
                                <div key={key} className="flex items-center justify-between py-2 border-b border-surface-800 last:border-0">
                                    <span className="text-sm text-surface-400 capitalize">{key.replace(/_/g, ' ')}</span>
                                    <span className={matched ? 'badge-success' : 'badge-danger'}>
                                        {matched ? '✓ Match' : '✗ Mismatch'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
