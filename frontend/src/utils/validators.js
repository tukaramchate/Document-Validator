import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from './constants';

/**
 * Check if a file has a valid type.
 * @param {File} file
 * @returns {boolean}
 */
export function isValidFileType(file) {
    return ALLOWED_FILE_TYPES.includes(file.type);
}

/**
 * Check if a file is within the size limit.
 * @param {File} file
 * @returns {boolean}
 */
export function isValidFileSize(file) {
    return file.size <= MAX_FILE_SIZE;
}

/**
 * Validate a file and return an error message or null.
 * @param {File} file
 * @returns {string|null} Error message or null if valid
 */
export function validateFile(file) {
    if (!isValidFileType(file)) {
        return 'Invalid file type. Allowed: PDF, JPG, PNG';
    }
    if (!isValidFileSize(file)) {
        return 'File too large. Maximum size: 16MB';
    }
    return null;
}

/**
 * Basic email format validation.
 * @param {string} email
 * @returns {boolean}
 */
export function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Format file size to human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Format a date string to a human-readable format.
 * @param {string} dateStr
 * @returns {string}
 */
export function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}
