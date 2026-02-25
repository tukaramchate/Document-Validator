import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import { ALLOWED_EXTENSIONS, MAX_FILE_SIZE_LABEL } from '../../utils/constants';
import { validateFile, formatFileSize } from '../../utils/validators';
import AlertMessage from '../../components/AlertMessage';
import {
    UploadCloud,
    FileText,
    X,
    Search,
    Rocket,
    ShieldCheck,
    Files,
    Loader2,
    BrainCircuit,
    CheckCircle2,
    Eye,
    Sparkles,
} from 'lucide-react';

// OCR Service URL — runs separately (uvicorn main:app --port 8001)
const OCR_API_URL = import.meta.env.VITE_OCR_API_URL || 'http://localhost:8001';

async function callOcrApi(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${OCR_API_URL}/extract/`, {
        method: 'POST',
        body: formData,
    });
    if (!res.ok) throw new Error(`OCR API error: ${res.status}`);
    return res.json();
}

export default function Upload() {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [validating, setValidating] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState('');
    const [ocrData, setOcrData] = useState(null);
    const [ocrLoading, setOcrLoading] = useState(false);
    const [ocrError, setOcrError] = useState('');
    const { post } = useApi();
    const navigate = useNavigate();

    const handleFileSelect = async (selectedFile) => {
        setError('');
        setOcrData(null);
        setOcrError('');
        if (!selectedFile) return;
        const validationError = validateFile(selectedFile);
        if (validationError) {
            setError(validationError);
            return;
        }
        setFile(selectedFile);

        // Auto-call OCR API as soon as a file is selected
        setOcrLoading(true);
        try {
            const result = await callOcrApi(selectedFile);
            if (result.error) {
                setOcrError(result.error);
            } else {
                setOcrData(result);
            }
        } catch (e) {
            setOcrError('OCR service unavailable. Make sure the OCR API is running on port 8001.');
        } finally {
            setOcrLoading(false);
        }
    };

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
        else if (e.type === 'dragleave') setDragActive(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        handleFileSelect(e.dataTransfer.files[0]);
    }, []);

    const handleFileInput = (e) => {
        handleFileSelect(e.target.files[0]);
    };

    const handleUploadAndValidate = async () => {
        if (!file) return;
        setError('');
        setUploading(true);
        setUploadProgress(0);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await post('/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (event) => {
                    const percent = Math.round((event.loaded * 100) / event.total);
                    setUploadProgress(percent);
                },
            });

            const docId = uploadResponse.data.document.id;
            setUploading(false);
            setValidating(true);

            await post(`/validate/${docId}`);
            navigate(`/results/${docId}`);
        } catch (err) {
            const code = err.response?.data?.error?.code;
            if (code === 'USAGE_LIMIT_REACHED') {
                setError('You have reached your 10-document validation limit. Please upgrade to continue.');
            } else {
                setError(err.response?.data?.error?.message || 'Upload failed');
            }
            setUploading(false);
            setValidating(false);
        }
    };

    // Helper to render OCR field label nicely
    const formatKey = (key) => key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

    return (
        <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-brand-500/10 rounded-2xl flex items-center justify-center text-brand-400">
                    <Files size={24} />
                </div>
                <div>
                    <h1 className="text-3xl font-black text-surface-100 tracking-tight">Upload Document</h1>
                    <p className="text-surface-400 mt-1 font-medium">AI-powered OCR preview + authenticity analysis</p>
                </div>
            </div>

            <AlertMessage type="error" message={error} onClose={() => setError('')} />

            {/* Drop Zone */}
            <div
                className={`relative border-2 border-dashed rounded-[2.5rem] p-16 text-center transition-all duration-300 cursor-pointer overflow-hidden group ${dragActive
                    ? 'border-brand-500 bg-brand-500/5 scale-[1.01]'
                    : file
                        ? 'border-success-500/40 bg-success-500/5'
                        : 'border-surface-700 hover:border-surface-500 bg-surface-900/40'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input').click()}
                role="button"
                tabIndex={0}
                aria-label="Upload document drop zone. Click or drag and drop a file here."
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') document.getElementById('file-input').click(); }}
            >
                <input
                    id="file-input"
                    type="file"
                    accept={ALLOWED_EXTENSIONS}
                    onChange={handleFileInput}
                    className="hidden"
                    aria-label="Select file to upload"
                />

                {file ? (
                    <div className="space-y-6 animate-scale-in">
                        <div className="relative inline-flex items-center justify-center w-20 h-20 bg-success-500/15 rounded-3xl mb-2">
                            <FileText size={32} className="text-success-400" />
                            <div className="absolute -top-2 -right-2 bg-success-500 text-white rounded-full p-1 shadow-lg">
                                <ShieldCheck size={14} />
                            </div>
                        </div>
                        <div>
                            <p className="text-xl font-bold text-surface-200">{file.name}</p>
                            <p className="text-surface-500 font-medium mt-1">{formatFileSize(file.size)} — {file.type}</p>
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); setFile(null); setOcrData(null); setOcrError(''); }}
                            className="flex items-center gap-2 mx-auto px-4 py-2 rounded-xl text-surface-400 text-sm font-bold bg-surface-800/50 hover:bg-danger-500/10 hover:text-danger-400 transition-all"
                            aria-label="Remove selected file"
                        >
                            <X size={16} />
                            <span>Remove and change</span>
                        </button>
                    </div>
                ) : (
                    <div className="space-y-6">
                        <div className="relative inline-flex items-center justify-center w-20 h-20 bg-brand-500/10 rounded-3xl mb-2 group-hover:scale-110 group-hover:bg-brand-500/20 transition-all duration-300">
                            {dragActive ? (
                                <Files size={32} className="text-brand-400 animate-bounce" />
                            ) : (
                                <UploadCloud size={32} className="text-brand-400" />
                            )}
                        </div>
                        <div>
                            <p className="text-xl font-bold text-surface-200 tracking-tight">
                                {dragActive ? 'Drop your file here' : 'Drag & drop document'}
                            </p>
                            <p className="text-surface-500 font-medium mt-2 max-w-xs mx-auto">
                                or click to browse files — PDF, JPG, PNG up to {MAX_FILE_SIZE_LABEL}
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* ───────── Gemini OCR Preview Panel ───────── */}
            {ocrLoading && (
                <div className="card rounded-[2rem] p-8 border-brand-500/20 bg-brand-500/5 flex items-center gap-4 animate-fade-in">
                    <div className="w-12 h-12 bg-brand-500/20 rounded-2xl flex items-center justify-center text-brand-400 shrink-0">
                        <BrainCircuit size={24} className="animate-pulse" />
                    </div>
                    <div>
                        <p className="font-bold text-surface-100 flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
                            Gemini OCR — Reading document...
                        </p>
                        <p className="text-xs text-surface-500 mt-1">Extracting structured data from your image</p>
                    </div>
                </div>
            )}

            {ocrError && !ocrLoading && (
                <div className="card rounded-[2rem] p-6 border-warning-500/20 bg-warning-500/5 animate-fade-in">
                    <p className="text-warning-400 font-bold flex items-center gap-2 text-sm">
                        <Eye size={16} />
                        {ocrError}
                    </p>
                </div>
            )}

            {ocrData && !ocrLoading && (
                <div className="card rounded-[2rem] p-8 border-success-500/20 bg-success-500/5 overflow-hidden animate-fade-in">
                    {/* Header */}
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-success-500/20 rounded-2xl flex items-center justify-center text-success-400">
                            <Sparkles size={20} />
                        </div>
                        <div>
                            <h3 className="text-lg font-black text-surface-100">OCR Preview</h3>
                            <p className="text-[10px] uppercase tracking-widest text-surface-500 font-bold">Extracted by Gemini AI</p>
                        </div>
                        <div className="ml-auto flex items-center gap-2 px-3 py-1.5 bg-success-500/10 border border-success-500/20 rounded-xl">
                            <CheckCircle2 size={14} className="text-success-400" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-success-400">Extracted</span>
                        </div>
                    </div>

                    {/* Fields Table */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-1 divide-y divide-surface-800/30">
                        {Object.entries(ocrData).map(([key, value]) => (
                            <div key={key} className="flex justify-between items-start py-3 border-b border-surface-800/30 last:border-0">
                                <span className="text-[11px] font-black uppercase tracking-widest text-surface-500 shrink-0 mr-4">
                                    {formatKey(key)}
                                </span>
                                <span className="text-sm font-bold text-surface-200 text-right">
                                    {value !== null && value !== undefined && value !== '' ? String(value) : (
                                        <span className="text-surface-600 italic font-medium text-xs">Not found</span>
                                    )}
                                </span>
                            </div>
                        ))}
                    </div>

                    <p className="text-xs text-surface-600 mt-6 text-center font-medium">
                        This is a live preview. The final validation uses a more detailed AI pipeline.
                    </p>
                </div>
            )}

            {/* Upload Progress */}
            {(uploading || validating) && (
                <div className="card rounded-[2rem] p-8 space-y-4 bg-surface-900/60 backdrop-blur-xl border-brand-500/20 shadow-2xl shadow-brand-500/5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            {validating ? (
                                <Search size={20} className="text-brand-400 animate-pulse" />
                            ) : (
                                <UploadCloud size={20} className="text-brand-400" />
                            )}
                            <span className="font-bold text-surface-200">
                                {validating ? 'Running full AI validation pipeline...' : 'Uploading securely...'}
                            </span>
                        </div>
                        <span className="text-sm font-black text-brand-400 tracking-widest">
                            {validating ? 'AI ANALYSIS' : `${uploadProgress}%`}
                        </span>
                    </div>
                    <div className="w-full bg-surface-800 rounded-full h-3 overflow-hidden shadow-inner" role="progressbar" aria-valuenow={validating ? 100 : uploadProgress} aria-valuemin={0} aria-valuemax={100}>
                        <div
                            className={`h-full rounded-full transition-all duration-500 relative ${validating ? 'bg-brand-500 w-full' : 'bg-brand-500'
                                }`}
                            style={!validating ? { width: `${uploadProgress}%` } : {}}
                        >
                            {validating && (
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Submit Button */}
            <button
                id="upload-submit"
                onClick={handleUploadAndValidate}
                disabled={!file || uploading || validating || ocrLoading}
                className="btn-primary w-full flex items-center justify-center gap-3 py-4.5 rounded-[1.25rem] text-lg font-bold shadow-2xl shadow-brand-500/25 hover:shadow-brand-500/40 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:translate-y-0"
                aria-label="Upload and validate selected document"
            >
                {uploading || validating ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>{validating ? 'Validating...' : 'Uploading...'}</span>
                    </>
                ) : ocrLoading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Reading document...</span>
                    </>
                ) : (
                    <>
                        <Rocket size={22} />
                        <span>Upload & Begin AI Validation</span>
                    </>
                )}
            </button>
        </div>
    );
}
