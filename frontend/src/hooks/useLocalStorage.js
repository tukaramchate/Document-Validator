import { useState, useEffect, useCallback, useRef } from 'react';

export function useLocalStorage(key, initialValue) {
    const [storedValue, setStoredValue] = useState(() => {
        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            console.error('Error reading localStorage:', error);
            return initialValue;
        }
    });

    const setValue = useCallback((value) => {
        try {
            setStoredValue((prevValue) => {
                const valueToStore = value instanceof Function ? value(prevValue) : value;
                window.localStorage.setItem(key, JSON.stringify(valueToStore));
                return valueToStore;
            });
        } catch (error) {
            console.error('Error setting localStorage:', error);
        }
    }, [key]);

    return [storedValue, setValue];
}

export function useAsync(asyncFunction, immediate = true) {
    const [status, setStatus] = useState('idle');
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    const execute = useCallback(async () => {
        setStatus('pending');
        setData(null);
        setError(null);
        try {
            const response = await asyncFunction();
            setData(response);
            setStatus('success');
            return response;
        } catch (error) {
            setError(error);
            setStatus('error');
        }
    }, [asyncFunction]);

    useEffect(() => {
        if (immediate) {
            execute();
        }
    }, [execute, immediate]);

    return { execute, status, data, error };
}

export function useDebounce(value, delay = 500) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => clearTimeout(handler);
    }, [value, delay]);

    return debouncedValue;
}

export function useThrottle(value, delay = 500) {
    const [throttledValue, setThrottledValue] = useState(value);
    const lastUpdateRef = useRef(Date.now());

    useEffect(() => {
        const now = Date.now();
        if (now >= lastUpdateRef.current + delay) {
            lastUpdateRef.current = now;
            setThrottledValue(value);
        } else {
            const timer = setTimeout(() => {
                setThrottledValue(value);
                lastUpdateRef.current = Date.now();
            }, delay - (now - lastUpdateRef.current));
            return () => clearTimeout(timer);
        }
    }, [value, delay]);

    return throttledValue;
}
