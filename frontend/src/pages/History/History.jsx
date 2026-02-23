import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import { VERDICT_CONFIG, DEFAULT_PER_PAGE } from '../../utils/constants';
import { formatDate } from '../../utils/validators';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
    FileText,
    Search,
    Plus,
    ChevronLeft,
    ChevronRight,
    History as HistoryIcon,
    X,
    Filter,
    ArrowRight,
    ClipboardList,
    Activity
} from 'lucide-react';

export default function History() {
    const { get } = useApi();
    const [results, setResults] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');
    const [search, setSearch] = useState('');
    const [searchInput, setSearchInput] = useState('');
    const perPage = DEFAULT_PER_PAGE;

    const fetchHistory = useCallback(async () => {
        setLoading(true);
        try {
            let url = `/history?page=${page}&per_page=${perPage}`;
            if (filter !== 'ALL') {
                url += `&verdict=${filter}`;
            }
            if (search.trim()) {
                url += `&search=${encodeURIComponent(search.trim())}`;
            }
            const response = await get(url);
            setResults(response.data.results);
            setTotal(response.data.pagination.total);
            setTotalPages(response.data.pagination.pages);
        } catch (error) {
            console.error('Failed to fetch history:', error);
        } finally {
            setLoading(false);
        }
    }, [page, filter, search, perPage, get]);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    // Reset to page 1 when filter or search changes
    const handleFilterChange = (newFilter) => {
        setFilter(newFilter);
        setPage(1);
    };

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        setSearch(searchInput);
        setPage(1);
    };

    const handleSearchClear = () => {
        setSearchInput('');
        setSearch('');
        setPage(1);
    };

    const getVerdictBadge = (verdict) => {
        return VERDICT_CONFIG[verdict]?.badge || 'badge';
    };

    // Sliding pagination window
    const getPaginationRange = () => {
        const delta = 2;
        const range = [];
        const rangeWithDots = [];

        const left = Math.max(2, page - delta);
        const right = Math.min(totalPages - 1, page + delta);

        range.push(1);
        for (let i = left; i <= right; i++) {
            range.push(i);
        }
        if (totalPages > 1) {
            range.push(totalPages);
        }

        let prev = 0;
        for (const i of range) {
            if (prev && i - prev > 1) {
                rangeWithDots.push('...');
            }
            rangeWithDots.push(i);
            prev = i;
        }

        return rangeWithDots;
    };

    const filters = ['ALL', 'AUTHENTIC', 'SUSPICIOUS', 'FAKE'];

    return (
        <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">Validation History</h1>
                    <p className="text-surface-400 mt-1 font-medium flex items-center gap-2">
                        <HistoryIcon size={14} className="text-brand-500" />
                        {total} total documents verified
                    </p>
                </div>
                <Link to="/upload" className="btn-primary inline-flex items-center gap-2 px-6 py-3 rounded-xl shadow-lg shadow-brand-500/20">
                    <Plus size={18} />
                    <span>New Validation</span>
                </Link>
            </div>

            {/* Search and Filters */}
            <div className="flex flex-col md:flex-row gap-4">
                {/* Search Bar */}
                <form onSubmit={handleSearchSubmit} className="flex-1 flex gap-2">
                    <div className="relative flex-1">
                        <input
                            type="text"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="Search by filename..."
                            className="input-field pl-11 h-12 rounded-xl"
                            aria-label="Search documents by filename"
                        />
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-surface-500" size={18} />
                    </div>
                    <button type="submit" className="btn-primary px-6 rounded-xl font-bold">
                        Search
                    </button>
                    {search && (
                        <button type="button" onClick={handleSearchClear} className="p-3 bg-surface-800/50 text-surface-400 hover:text-danger-400 rounded-xl transition-all" aria-label="Clear search">
                            <X size={20} />
                        </button>
                    )}
                </form>

                {/* Filter Tabs */}
                <div className="flex gap-2 p-1 bg-surface-900/40 rounded-[1rem] border border-surface-800/50" role="tablist" aria-label="Filter by verdict">
                    {filters.map((f) => (
                        <button
                            key={f}
                            onClick={() => handleFilterChange(f)}
                            role="tab"
                            aria-selected={filter === f}
                            className={`px-5 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${filter === f
                                ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/20'
                                : 'text-surface-500 hover:text-surface-200 hover:bg-surface-800/30'
                                }`}
                        >
                            {f === 'ALL' ? 'All' : f}
                        </button>
                    ))}
                </div>
            </div>

            {/* Results List */}
            {loading ? (
                <div className="flex flex-col items-center justify-center h-64 bg-surface-900/20 rounded-[2.5rem] border border-surface-800/30">
                    <LoadingSpinner />
                </div>
            ) : results.length === 0 ? (
                <div className="card rounded-[2.5rem] text-center py-20 bg-surface-900/40">
                    <div className="w-20 h-20 bg-surface-800/50 rounded-3xl flex items-center justify-center mx-auto mb-6 text-surface-600">
                        <ClipboardList size={40} />
                    </div>
                    <h3 className="text-xl font-bold text-surface-200">No results found</h3>
                    <p className="text-surface-500 font-medium mt-2 max-w-xs mx-auto leading-relaxed">
                        {search ? `We couldn't find any documents matching "${search}"` :
                            filter !== 'ALL' ? `You don't have any validations with ${filter.toLowerCase()} verdict yet.` : 'Upload a document to start your validation history.'}
                    </p>
                    {filter !== 'ALL' || search ? (
                        <button onClick={() => { handleSearchClear(); setFilter('ALL'); }} className="mt-6 text-brand-400 font-bold hover:underline">
                            Clear all filters
                        </button>
                    ) : (
                        <Link to="/upload" className="btn-primary mt-8 inline-flex">Get Started</Link>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {results.map((result, index) => (
                        <Link
                            key={result.id}
                            to={`/results/${result.document_id}`}
                            className="card-hover flex flex-col sm:flex-row sm:items-center justify-between gap-6 p-6 rounded-[2rem] group animate-slide-up relative overflow-hidden active:scale-[0.99] transition-all"
                            style={{ animationDelay: `${index * 50}ms` }}
                        >
                            <div className="flex items-center gap-5">
                                <div className="w-14 h-14 bg-brand-500/10 rounded-2xl flex items-center justify-center text-brand-400 shrink-0 group-hover:scale-110 group-hover:bg-brand-500/20 transition-all duration-300">
                                    <FileText size={24} />
                                </div>
                                <div className="min-w-0">
                                    <h3 className="text-lg font-bold text-surface-100 group-hover:text-brand-400 transition-colors truncate pr-4">
                                        {result.document?.filename || `Document #${result.document_id}`}
                                    </h3>
                                    <p className="text-xs text-surface-500 font-medium mt-1 flex items-center gap-1.5">
                                        <Activity size={12} className="text-brand-500/40" />
                                        {formatDate(result.validated_at)}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center justify-between sm:justify-end gap-6 md:gap-10 border-t sm:border-t-0 border-surface-800/50 pt-4 sm:pt-0">
                                {/* Score Breakdown bars - Hidden on very small mobile */}
                                <div className="hidden lg:flex items-center gap-6">
                                    {[
                                        { label: 'CNN', val: result.scores.cnn_score },
                                        { label: 'OCR', val: result.scores.ocr_confidence },
                                        { label: 'DB', val: result.scores.db_match_score }
                                    ].map((s) => (
                                        <div key={s.label} className="flex flex-col gap-1.5">
                                            <div className="flex justify-between items-center px-0.5">
                                                <span className="text-[10px] font-black tracking-widest text-surface-600 uppercase">{s.label}</span>
                                                <span className="text-[10px] font-bold text-surface-400">{(s.val * 100).toFixed(0)}%</span>
                                            </div>
                                            <div className="w-20 bg-surface-800/50 rounded-full h-1.5 overflow-hidden">
                                                <div className="h-full rounded-full bg-brand-600" style={{ width: `${s.val * 100}%` }} />
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Final Score */}
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] font-black text-surface-600 tracking-widest uppercase mb-0.5">Trust</span>
                                    <span className="text-xl font-black text-surface-100">
                                        {(result.scores.final_score * 100).toFixed(1)}%
                                    </span>
                                </div>

                                {/* Verdict Badge */}
                                <span className={`${getVerdictBadge(result.verdict)} !px-4 py-2 font-black text-[10px] uppercase tracking-widest min-w-[110px] text-center rounded-xl`}>
                                    {result.verdict}
                                </span>

                                {/* Arrow */}
                                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-surface-700 bg-surface-800/30 group-hover:text-brand-400 group-hover:bg-brand-500/10 transition-all">
                                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <nav className="flex items-center justify-center gap-2 pt-8" aria-label="Pagination">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="p-3 bg-surface-900/60 border border-surface-800/50 rounded-xl text-surface-400 hover:text-surface-100 hover:bg-surface-800 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                        aria-label="Previous page"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <div className="flex items-center gap-1.5">
                        {getPaginationRange().map((item, i) =>
                            item === '...' ? (
                                <span key={`dots-${i}`} className="w-10 text-center text-surface-600 font-bold">...</span>
                            ) : (
                                <button
                                    key={item}
                                    onClick={() => setPage(item)}
                                    aria-current={page === item ? 'page' : undefined}
                                    className={`w-10 h-10 rounded-xl text-sm font-black transition-all ${page === item
                                        ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/30 scale-110'
                                        : 'text-surface-500 hover:text-surface-200 hover:bg-surface-800'
                                        }`}
                                >
                                    {item}
                                </button>
                            )
                        )}
                    </div>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="p-3 bg-surface-900/60 border border-surface-800/50 rounded-xl text-surface-400 hover:text-surface-100 hover:bg-surface-800 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                        aria-label="Next page"
                    >
                        <ChevronRight size={20} />
                    </button>
                </nav>
            )}
        </div>
    );
}
