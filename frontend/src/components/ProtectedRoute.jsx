import { Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

export default function ProtectedRoute({ children, allowedRoles, loadingTimeout = 10000 }) {
    const { isAuthenticated, loading, user } = useAuth();
    const [timedOut, setTimedOut] = useState(false);

    useEffect(() => {
        if (!loading) return;

        const timer = setTimeout(() => {
            setTimedOut(true);
        }, loadingTimeout);

        return () => clearTimeout(timer);
    }, [loading, loadingTimeout]);

    if ((loading && !timedOut) || timedOut) {
        if (timedOut && loading) {
            return <Navigate to="/login" replace />;
        }
        return (
            <div className="min-h-screen flex items-center justify-center bg-surface-950">
                <LoadingSpinner size="lg" text="Loading..." />
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // Role-based check
    if (allowedRoles && !allowedRoles.includes(user?.role)) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
}
