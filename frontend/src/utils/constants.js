// ─── API Routes ───
export const API_ROUTES = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        PROFILE: '/auth/profile',
    },
    UPLOAD: {
        UPLOAD: '/upload',
        LIST: '/upload/list',
    },
    VALIDATE: (docId) => `/validate/${docId}`,
    RESULTS: (docId) => `/results/${docId}`,
    HISTORY: '/history',
    INSTITUTION: {
        RECORDS: '/institution/records',
        BULK_UPLOAD: '/institution/records/bulk',
    },
    REPORT: (docId) => `/results/${docId}/report`,
};

// ─── File Validation ───
export const ALLOWED_FILE_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
];

export const ALLOWED_EXTENSIONS = '.pdf,.jpg,.jpeg,.png';

export const MAX_FILE_SIZE = 16 * 1024 * 1024; // 16MB

export const MAX_FILE_SIZE_LABEL = '16MB';

// ─── Score Thresholds ───
export const SCORE_THRESHOLDS = {
    AUTHENTIC: 0.90,   // ≥ 90%
    SUSPICIOUS: 0.70,  // 70–89%
    // Below 70% = FAKE
};

// ─── Pagination ───
export const DEFAULT_PER_PAGE = 10;

// ─── Verdict Colors ───
export const VERDICT_CONFIG = {
    AUTHENTIC: {
        color: '#10b981',
        bg: 'bg-success-500/10',
        border: 'border-success-500/20',
        text: 'text-success-400',
        badge: 'badge-success',
        label: 'Authentic',
    },
    SUSPICIOUS: {
        color: '#f59e0b',
        bg: 'bg-warning-500/10',
        border: 'border-warning-500/20',
        text: 'text-warning-400',
        badge: 'badge-warning',
        label: 'Suspicious',
    },
    FAKE: {
        color: '#ef4444',
        bg: 'bg-danger-500/10',
        border: 'border-danger-500/20',
        text: 'text-danger-400',
        badge: 'badge-danger',
        label: 'Fake',
    },
};
