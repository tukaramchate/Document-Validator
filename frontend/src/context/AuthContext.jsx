import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(() => localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (token) {
            fetchProfile();
        } else {
            setLoading(false);
        }
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await api.get('/auth/profile');
            if (!response.data?.data?.user) {
                throw new Error('Invalid response structure from server');
            }
            setUser(response.data.data.user);
            setError(null);
        } catch (err) {
            console.error('Profile fetch failed:', err.message);
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
            setError(err.message || 'Failed to load profile');
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            setError(null);
            const response = await api.post('/auth/login', { email, password });
            const { user: userData, token: newToken } = response.data.data;
            localStorage.setItem('token', newToken);
            setToken(newToken);
            setUser(userData);
            return userData;
        } catch (err) {
            const errorMessage = err.response?.data?.error?.message || err.message || 'Login failed';
            setError(errorMessage);
            throw err;
        }
    };

    const register = async (email, password, name) => {
        try {
            setError(null);
            const response = await api.post('/auth/register', { email, password, name });
            const { user: userData, token: newToken } = response.data.data;
            localStorage.setItem('token', newToken);
            setToken(newToken);
            setUser(userData);
            return userData;
        } catch (err) {
            const errorMessage = err.response?.data?.error?.message || err.message || 'Registration failed';
            setError(errorMessage);
            throw err;
        }
    };

    const registerInstitution = async (email, password, name) => {
        try {
            setError(null);
            const response = await api.post('/auth/register/institution', { email, password, name });
            const { user: userData, token: newToken } = response.data.data;
            localStorage.setItem('token', newToken);
            setToken(newToken);
            setUser(userData);
            return userData;
        } catch (err) {
            const errorMessage = err.response?.data?.error?.message || err.message || 'Institution registration failed';
            setError(errorMessage);
            throw err;
        }
    };

    const registerAdmin = async (email, password, name) => {
        try {
            setError(null);
            const response = await api.post('/auth/register/admin', { email, password, name });
            const { user: userData, token: newToken } = response.data.data;
            localStorage.setItem('token', newToken);
            setToken(newToken);
            setUser(userData);
            return userData;
        } catch (err) {
            const errorMessage = err.response?.data?.error?.message || err.message || 'Admin registration failed';
            setError(errorMessage);
            throw err;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        setError(null);
    };

    const clearError = () => setError(null);

    return (
        <AuthContext.Provider value={{
            user,
            token,
            loading,
            error,
            clearError,
            login,
            register,
            registerInstitution,
            registerAdmin,
            logout,
            isAuthenticated: !!user
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within an AuthProvider');
    return context;
};
