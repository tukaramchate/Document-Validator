import { useAuth } from '../../context/AuthContext';
import UserDashboard from './UserDashboard';
import AdminDashboard from './AdminDashboard';
import InstitutionDashboard from './InstitutionDashboard';

export default function Dashboard() {
    const { user } = useAuth();

    // Route based on role
    if (user?.role === 'admin') {
        return <AdminDashboard />;
    }

    if (user?.role === 'institution') {
        return <InstitutionDashboard />;
    }

    // Default to user dashboard
    return <UserDashboard />;
}
