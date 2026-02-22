import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';

export default function History() {
    const { get } = useApi();
    const [results, setResults] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');
    const perPage = 10;

    useEffect(() => {
        fetchHistory();
    }, [page]);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const response = await get(`/history?page=${page}&per_page=${perPage}`);
            setResults(response.data.results);
            setTotal(response.data.pagination.total);
            setTotalPages(response.data.pagination.pages);
        } catch (error) {
            console.error('Failed to fetch history:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredResults = filter === 'ALL'
        ? results
        : results.filter(r => r.verdict === filter);

    const getVerdictBadge = (verdict) => {
        const badges = {
            AUTHENTIC: 'badge-success',
            SUSPICIOUS: 'badge-warning',
            FAKE: 'badge-danger',
        };
        return badges[verdict] || 'badge';
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const filters = ['ALL', 'AUTHENTIC', 'SUSPICIOUS', 'FAKE'];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-surface-100">Validation History</h1>
                    <p className="text-surface-400 mt-1">{total} total validations</p>
                </div>
                <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
                    <span>📤</span> New Validation
                </Link>
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-2">
                {filters.map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${filter === f
                                ? 'bg-brand-600/15 text-brand-400 border border-brand-500/20'
                                : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'
                            }`}
                    >
                        {f === 'ALL' ? 'All' : f.charAt(0) + f.slice(1).toLowerCase()}
                    </button>
                ))}
            </div>

            {/* Results List */}
            {loading ? (
                <div className="flex items-center justify-center h-32">
                    <div className="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : filteredResults.length === 0 ? (
                <div className="card text-center py-16">
                    <span className="text-4xl mb-4 block">📋</span>
                    <h3 className="text-lg font-semibold text-surface-300">No results found</h3>
                    <p className="text-surface-500 text-sm mt-1">
                        {filter !== 'ALL' ? `No ${filter.toLowerCase()} results` : 'Upload a document to get started'}
                    </p>
                </div>
            ) : (
                <div className="space-y-3">
                    {filteredResults.map((result, index) => (
                        <Link
                            key={result.id}
                            to={`/results/${result.document_id}`}
                            className="card-hover flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 group animate-slide-up"
                            style={{ animationDelay: `${index * 50}ms` }}
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-brand-600/15 rounded-xl flex items-center justify-center text-lg shrink-0">
                                    📄
                                </div>
                                <div>
                                    <h3 className="text-sm font-semibold text-surface-200 group-hover:text-brand-300 transition-colors">
                                        {result.document?.filename || `Document #${result.document_id}`}
                                    </h3>
                                    <p className="text-xs text-surface-500 mt-0.5">
                                        {formatDate(result.validated_at)}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-4 sm:gap-6">
                                {/* Score bars */}
                                <div className="hidden md:flex items-center gap-3">
                                    <div className="flex items-center gap-1.5">
                                        <span className="text-xs text-surface-500">CNN</span>
                                        <div className="w-16 bg-surface-800 rounded-full h-1.5">
                                            <div className="h-full rounded-full bg-brand-500" style={{ width: `${result.scores.cnn_score * 100}%` }} />
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <span className="text-xs text-surface-500">OCR</span>
                                        <div className="w-16 bg-surface-800 rounded-full h-1.5">
                                            <div className="h-full rounded-full bg-brand-400" style={{ width: `${result.scores.ocr_confidence * 100}%` }} />
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <span className="text-xs text-surface-500">DB</span>
                                        <div className="w-16 bg-surface-800 rounded-full h-1.5">
                                            <div className="h-full rounded-full bg-brand-300" style={{ width: `${result.scores.db_match_score * 100}%` }} />
                                        </div>
                                    </div>
                                </div>

                                {/* Final Score */}
                                <span className="text-sm font-bold text-surface-200 w-14 text-right">
                                    {(result.scores.final_score * 100).toFixed(1)}%
                                </span>

                                {/* Verdict Badge */}
                                <span className={`${getVerdictBadge(result.verdict)} min-w-[90px] text-center`}>
                                    {result.verdict}
                                </span>

                                {/* Arrow */}
                                <span className="text-surface-600 group-hover:text-brand-400 transition-colors">→</span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 pt-4">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="btn-secondary px-3 py-2 text-sm disabled:opacity-30"
                    >
                        ← Prev
                    </button>
                    <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                            const pageNum = i + 1;
                            return (
                                <button
                                    key={pageNum}
                                    onClick={() => setPage(pageNum)}
                                    className={`w-9 h-9 rounded-lg text-sm font-medium transition-all ${page === pageNum
                                            ? 'bg-brand-600 text-white'
                                            : 'text-surface-400 hover:bg-surface-800'
                                        }`}
                                >
                                    {pageNum}
                                </button>
                            );
                        })}
                    </div>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="btn-secondary px-3 py-2 text-sm disabled:opacity-30"
                    >
                        Next →
                    </button>
                </div>
            )}
        </div>
    );
}
