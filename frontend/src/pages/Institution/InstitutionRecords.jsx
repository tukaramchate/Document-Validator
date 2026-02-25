import { useState, useEffect } from 'react';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../../components/LoadingSpinner';
import AlertMessage from '../../components/AlertMessage';
import {
    Users,
    Plus,
    Search,
    Database,
    Upload,
    Trash2,
    FileJson,
    ShieldCheck,
    AlertCircle
} from 'lucide-react';

export default function InstitutionRecords() {
    const { get, post, del } = useApi();
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [search, setSearch] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [newRecord, setNewRecord] = useState({ name: '', id_number: '', metadata: {} });
    const [bulkJson, setBulkJson] = useState('');

    useEffect(() => {
        fetchRecords();
    }, []);

    const fetchRecords = async () => {
        try {
            const response = await get('/institution/records');
            setRecords(response.data.records);
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Failed to load records');
        } finally {
            setLoading(false);
        }
    };

    const handleAddRecord = async (e) => {
        e.preventDefault();
        try {
            await post('/institution/records', newRecord);
            fetchRecords();
            setShowAddModal(false);
            setNewRecord({ name: '', id_number: '', metadata: {} });
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Failed to add record');
        }
    };

    const handleBulkUpload = async () => {
        try {
            const data = JSON.parse(bulkJson);
            await post('/institution/records/bulk', data);
            fetchRecords();
            setBulkJson('');
        } catch (err) {
            setError('Invalid JSON format or upload failed');
        }
    };

    const filteredRecords = records.filter(r =>
        r.name.toLowerCase().includes(search.toLowerCase()) ||
        r.id_number.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) return <LoadingSpinner size="lg" text="Syncing records..." />;

    return (
        <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">Institution Records</h1>
                    <p className="text-surface-400 mt-1 font-medium">Manage student/employee "Truth Data" for cross-verification</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="btn-primary rounded-xl flex items-center gap-2"
                    >
                        <Plus size={18} />
                        <span>Add Record</span>
                    </button>
                </div>
            </div>

            <AlertMessage type="error" message={error} onClose={() => setError('')} />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Sidebar Controls */}
                <div className="space-y-6">
                    <div className="card rounded-[2rem] p-6">
                        <h3 className="text-sm font-bold text-surface-300 uppercase tracking-widest mb-4">Search Records</h3>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-500" size={16} />
                            <input
                                type="text"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="input-field pl-10 text-sm"
                                placeholder="Name or ID..."
                            />
                        </div>
                    </div>

                    <div className="card rounded-[2rem] p-6 bg-brand-600/5 border-brand-500/20">
                        <div className="flex items-center gap-3 mb-4 text-brand-400">
                            <FileJson size={20} />
                            <h3 className="text-sm font-bold uppercase tracking-widest">Bulk Import</h3>
                        </div>
                        <p className="text-xs text-surface-400 mb-4 leading-relaxed font-medium">
                            Paste a JSON array of records to update your database in bulk.
                        </p>
                        <textarea
                            value={bulkJson}
                            onChange={(e) => setBulkJson(e.target.value)}
                            className="input-field text-[10px] font-mono h-32 mb-4"
                            placeholder='{ "records": [{ "name": "...", "id_number": "..." }] }'
                        />
                        <button
                            onClick={handleBulkUpload}
                            disabled={!bulkJson}
                            className="btn-secondary w-full text-xs font-bold py-3 rounded-xl border-brand-500/20 hover:bg-brand-500/10 text-brand-400 disabled:opacity-50"
                        >
                            Process JSON
                        </button>
                    </div>
                </div>

                {/* Records List */}
                <div className="lg:col-span-3 space-y-4">
                    {filteredRecords.length === 0 ? (
                        <div className="card rounded-[2rem] p-12 text-center bg-surface-950/30 border-dashed border-surface-800">
                            <Database size={48} className="text-surface-700 mx-auto mb-4" />
                            <p className="text-surface-400 font-bold text-lg">No records found</p>
                            <p className="text-surface-600 text-sm mt-1">Try another search or add a new record to your institution database.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-3">
                            {filteredRecords.map((record) => (
                                <div key={record.id} className="card-hover p-4 rounded-2xl flex items-center justify-between group">
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 bg-surface-800/50 rounded-xl flex items-center justify-center text-surface-400 group-hover:text-brand-400 transition-colors">
                                            <Users size={24} />
                                        </div>
                                        <div>
                                            <h4 className="text-surface-100 font-bold">{record.name}</h4>
                                            <p className="text-xs text-surface-500 font-medium">ID: {record.id_number} • {Object.keys(record.metadata || {}).length} Fields</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="hidden md:flex flex-wrap gap-2 mr-4">
                                            {Object.entries(record.metadata || {}).map(([key, val]) => (
                                                <span key={key} className="px-2 py-1 bg-surface-800 rounded-md text-[10px] text-surface-400 font-bold uppercase tracking-tighter">
                                                    {key}: {val}
                                                </span>
                                            ))}
                                        </div>
                                        <button className="p-2.5 text-surface-600 hover:text-danger-400 transition-colors">
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Simple Modal Shim (could be a component) */}
            {showAddModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-950/80 backdrop-blur-sm animate-fade-in">
                    <div className="card w-full max-w-lg rounded-[2.5rem] p-10 shadow-2xl animate-scale-in">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-12 h-12 bg-brand-500/10 rounded-2xl flex items-center justify-center text-brand-400">
                                <Plus size={24} />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-surface-100">Add Record</h2>
                                <p className="text-surface-500 text-sm font-medium">Manual data entry for verification</p>
                            </div>
                        </div>

                        <form onSubmit={handleAddRecord} className="space-y-5">
                            <div>
                                <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Subject Name</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    placeholder="Full name as on document"
                                    value={newRecord.name}
                                    onChange={(e) => setNewRecord({ ...newRecord, name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-black uppercase tracking-widest text-surface-500 mb-2">Identification ID</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    placeholder="e.g. STUDENT_2024_001"
                                    value={newRecord.id_number}
                                    onChange={(e) => setNewRecord({ ...newRecord, id_number: e.target.value })}
                                />
                            </div>
                            <div className="flex gap-4 mt-10">
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="btn-secondary flex-1 py-4 rounded-2xl"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn-primary flex-1 py-4 rounded-2xl shadow-lg shadow-brand-500/20"
                                >
                                    Save Record
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
