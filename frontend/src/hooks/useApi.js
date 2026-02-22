import { useState, useCallback } from 'react';
import api from '../api/axios';

export function useApi() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const request = useCallback(async (method, url, data = null, config = {}) => {
        setLoading(true);
        setError(null);
        try {
            const response = await api({ method, url, data, ...config });
            return response.data;
        } catch (err) {
            const message = err.response?.data?.error?.message || err.message || 'Something went wrong';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const get = useCallback((url, config) => request('GET', url, null, config), [request]);
    const post = useCallback((url, data, config) => request('POST', url, data, config), [request]);
    const del = useCallback((url, config) => request('DELETE', url, null, config), [request]);

    return { loading, error, setError, get, post, del };
}
