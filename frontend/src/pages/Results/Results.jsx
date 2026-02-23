import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import { VERDICT_CONFIG } from '../../utils/constants';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import {
    ShieldCheck,
    AlertTriangle,
    AlertOctagon,
    Cpu,
    FileText,
    Search,
    Check,
    X,
    ArrowLeft,
    Share2,
    Calendar,
    Settings,
    Layout
} from 'lucide-react';

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

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <LoadingSpinner size="lg" text="Loading results..." />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-16 animate-fade-in space-y-4">
                <AlertMessage type="error" message={error} />
                <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
                    <ArrowLeft size={18} />
                    <span>Back to Upload</span>
                </Link>
            </div>
        );
    }

    const verdictConfig = VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG.SUSPICIOUS;
    const scores = result.scores;
    const finalPercent = (scores.final_score * 100).toFixed(1);

    const scoreBreakdown = [
        { name: 'CNN Analysis', value: scores.cnn_score, weight: '40%', icon: Cpu, desc: 'Visual authenticity' },
        { name: 'OCR Confidence', value: scores.ocr_confidence, weight: '20%', icon: FileText, desc: 'Text recognition' },
        { name: 'DB Verification', value: scores.db_match_score, weight: '40%', icon: Search, desc: 'Record matching' },
    ];

    const pieData = [
        { name: 'Score', value: scores.final_score * 100 },
        { name: 'Remaining', value: 100 - scores.final_score * 100 },
    ];

    const getVerdictIcon = (verdict) => {
        switch (verdict) {
            case 'AUTHENTIC': return <ShieldCheck size={48} />;
            case 'SUSPICIOUS': return <AlertTriangle size={48} />;
            case 'FAKE': return <AlertOctagon size={48} />;
            default: return <AlertTriangle size={48} />;
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <Link to="/history" className="p-3 bg-surface-800/50 rounded-xl text-surface-400 hover:text-surface-100 transition-all">
                        <ArrowLeft size={20} />
                    </Link>
                    <div>
                        <h1 className="text-3xl font-black text-surface-100 tracking-tight">Validation Results</h1>
                        <p className="text-surface-400 mt-1 font-medium flex items-center gap-2">
                            <Calendar size={14} />
                            Document #{docId}
                        </p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button className="btn-secondary rounded-xl flex items-center gap-2">
                        <Share2 size={18} />
                        <span className="hidden sm:inline">Share</span>
                    </button>
                    <Link to="/upload" className="btn-primary rounded-xl px-6">Upload Another</Link>
                </div>
            </div>

            {/* Verdict Card */}
            <div className={`card overflow-hidden rounded-[2.5rem] ${verdictConfig.bg} ${verdictConfig.border} border-2 shadow-2xl shadow-brand-500/5`}>
                <div className="flex flex-col md:flex-row items-center gap-8 p-10">
                    {/* Score Circle */}
                    <div className="relative w-48 h-48 shrink-0 bg-surface-950/20 rounded-full p-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    startAngle={90}
                                    endAngle={-270}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    <Cell fill={verdictConfig.color} />
                                    <Cell fill="rgba(100,116,139,0.1)" />
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className={`text-3xl font-black ${verdictConfig.text}`}>{finalPercent}%</span>
                            <span className="text-[10px] uppercase font-bold tracking-widest text-surface-500">TRUST SCORE</span>
                        </div>
                    </div>

                    {/* Verdict Info */}
                    <div className="text-center md:text-left flex-1">
                        <div className={`${verdictConfig.text} mb-4 flex justify-center md:justify-start`}>
                            {getVerdictIcon(result.verdict)}
                        </div>
                        <h2 className={`text-4xl font-black tracking-tight ${verdictConfig.text}`}>{verdictConfig.label}</h2>
                        <p className="text-surface-400 mt-4 text-lg font-medium leading-relaxed max-w-xl">
                            {result.verdict === 'AUTHENTIC' && 'This document appears to be genuine based on our multi-layered AI analysis across visual patterns and text signatures.'}
                            {result.verdict === 'SUSPICIOUS' && 'This document has some inconsistencies that require further review. Some visual or text patterns do not fully match authentic records.'}
                            {result.verdict === 'FAKE' && 'This document shows significant signs of being fraudulent. Multiple verification layers have failed to validate its authenticity.'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {scoreBreakdown.map(({ name, value, weight, icon: Icon, desc }) => (
                    <div key={name} className="card-hover rounded-[2rem] p-8">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2.5 bg-brand-500/10 rounded-xl text-brand-400">
                                <Icon size={20} />
                            </div>
                            <div>
                                <h3 className="text-xs font-black uppercase tracking-widest text-surface-500">{name}</h3>
                                <span className="text-[10px] font-bold text-surface-600">Weight: {weight}</span>
                            </div>
                        </div>
                        <div className="flex items-baseline gap-2 mb-3">
                            <span className="text-4xl font-black text-surface-100 tracking-tight">{(value * 100).toFixed(1)}</span>
                            <span className="text-lg font-bold text-surface-500">%</span>
                        </div>
                        <div className="w-full bg-surface-800/50 rounded-full h-2.5 overflow-hidden" role="progressbar" aria-valuenow={Math.round(value * 100)} aria-valuemin={0} aria-valuemax={100}>
                            <div
                                className="h-full rounded-full bg-brand-500 transition-all duration-1000 shadow-[0_0_10px_rgba(59,130,246,0.3)]"
                                style={{ width: `${value * 100}%` }}
                            />
                        </div>
                        <p className="text-xs text-surface-400 font-medium mt-4 leading-relaxed">{desc}</p>
                    </div>
                ))}
            </div>

            {/* Extracted Data & Field Matches */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Extracted Data */}
                {result.extracted_data && (
                    <div className="card rounded-[2rem] p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <FileText size={20} className="text-brand-400" />
                            <h3 className="text-xl font-bold text-surface-100">Extracted Data</h3>
                        </div>
                        <div className="space-y-1">
                            {Object.entries(result.extracted_data).map(([key, value]) => (
                                <div key={key} className="flex justify-between py-3.5 border-b border-surface-800/50 last:border-0 hover:bg-surface-800/20 px-2 rounded-lg transition-colors">
                                    <span className="text-sm text-surface-500 font-bold uppercase tracking-wider">{key.replace(/_/g, ' ')}</span>
                                    <span className="text-sm text-surface-200 font-bold">{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Field Matches */}
                {result.field_matches && (
                    <div className="card rounded-[2rem] p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <Search size={20} className="text-brand-400" />
                            <h3 className="text-xl font-bold text-surface-100">Verification Check</h3>
                        </div>
                        <div className="space-y-1">
                            {Object.entries(result.field_matches).map(([key, matched]) => (
                                <div key={key} className="flex items-center justify-between py-3.5 border-b border-surface-800/50 last:border-0 hover:bg-surface-800/20 px-2 rounded-lg transition-colors">
                                    <span className="text-sm text-surface-500 font-bold uppercase tracking-wider">{key.replace(/_/g, ' ')}</span>
                                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest ${matched ? 'bg-success-500/10 text-success-400 border border-success-500/20' : 'bg-danger-500/10 text-danger-400 border border-danger-500/20'
                                        }`}>
                                        {matched ? <Check size={12} strokeWidth={4} /> : <X size={12} strokeWidth={4} />}
                                        {matched ? 'Matched' : 'Mismatch'}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
