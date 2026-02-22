import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';

export default function Upload() {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [validating, setValidating] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState('');
    const { post } = useApi();
    const navigate = useNavigate();

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    const maxSize = 16 * 1024 * 1024; // 16MB

    const validateFile = (file) => {
        if (!allowedTypes.includes(file.type)) {
            setError('Invalid file type. Allowed: PDF, JPG, PNG');
            return false;
        }
        if (file.size > maxSize) {
            setError('File too large. Maximum size: 16MB');
            return false;
        }
        return true;
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
        setError('');
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && validateFile(droppedFile)) setFile(droppedFile);
    }, []);

    const handleFileInput = (e) => {
        setError('');
        const selectedFile = e.target.files[0];
        if (selectedFile && validateFile(selectedFile)) setFile(selectedFile);
    };

    const handleUploadAndValidate = async () => {
        if (!file) return;
        setError('');
        setUploading(true);
        setUploadProgress(0);

        try {
            // Upload
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

            // Validate
            await post(`/validate/${docId}`);
            navigate(`/results/${docId}`);
        } catch (err) {
            setError(err.response?.data?.error?.message || 'Upload failed');
            setUploading(false);
            setValidating(false);
        }
    };

    const formatSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold text-surface-100">Upload Document</h1>
                <p className="text-surface-400 mt-1">Upload a document to verify its authenticity</p>
            </div>

            {error && (
                <div className="px-4 py-3 bg-danger-500/10 border border-danger-500/20 rounded-xl text-danger-400 text-sm">
                    {error}
                </div>
            )}

            {/* Drop Zone */}
            <div
                className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${dragActive
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
            >
                <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileInput}
                    className="hidden"
                />

                {file ? (
                    <div className="space-y-3">
                        <div className="inline-flex items-center justify-center w-14 h-14 bg-success-500/15 rounded-2xl mb-2">
                            <span className="text-3xl">📄</span>
                        </div>
                        <div>
                            <p className="text-surface-200 font-medium">{file.name}</p>
                            <p className="text-surface-500 text-sm">{formatSize(file.size)} — {file.type}</p>
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); setFile(null); }}
                            className="text-surface-400 text-sm hover:text-danger-400 transition-colors"
                        >
                            Remove file
                        </button>
                    </div>
                ) : (
                    <div className="space-y-3">
                        <div className="inline-flex items-center justify-center w-14 h-14 bg-brand-600/10 rounded-2xl mb-2">
                            <span className="text-3xl">{dragActive ? '📥' : '📤'}</span>
                        </div>
                        <div>
                            <p className="text-surface-200 font-medium">
                                {dragActive ? 'Drop your file here' : 'Drag & drop your document'}
                            </p>
                            <p className="text-surface-500 text-sm mt-1">
                                or click to browse — PDF, JPG, PNG up to 16MB
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Upload Progress */}
            {(uploading || validating) && (
                <div className="card space-y-3">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-surface-300">
                            {validating ? '🔍 Analyzing document...' : '📤 Uploading...'}
                        </span>
                        <span className="text-sm text-brand-400">
                            {validating ? 'AI Processing' : `${uploadProgress}%`}
                        </span>
                    </div>
                    <div className="w-full bg-surface-800 rounded-full h-2 overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${validating ? 'bg-brand-500 animate-pulse-slow w-full' : 'bg-brand-500'
                                }`}
                            style={!validating ? { width: `${uploadProgress}%` } : {}}
                        />
                    </div>
                </div>
            )}

            {/* Submit Button */}
            <button
                id="upload-submit"
                onClick={handleUploadAndValidate}
                disabled={!file || uploading || validating}
                className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            >
                {uploading || validating ? (
                    <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        {validating ? 'Validating...' : 'Uploading...'}
                    </>
                ) : (
                    <>🚀 Upload & Validate</>
                )}
            </button>
        </div>
    );
}
