import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Landing from './pages/Landing/Landing';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import Upload from './pages/Upload/Upload';
import Results from './pages/Results/Results';
import History from './pages/History/History';
import InstitutionRecords from './pages/Institution/InstitutionRecords';
import AdminRegister from './pages/AdminRegister/AdminRegister';
import Profile from './pages/Profile/Profile';
import Settings from './pages/Settings/Settings';
import Pricing from './pages/Pricing/Pricing';
import Help from './pages/Help/Help';
import NotFound from './pages/NotFound/NotFound';
import ServerError from './pages/Error/ServerError';

import { ThemeProvider } from './context/ThemeContext';

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/admin/signup" element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminRegister />
                </ProtectedRoute>
              } />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/help" element={<Help />} />

              {/* Protected Routes */}
              <Route element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/upload" element={
                  <ProtectedRoute allowedRoles={['user', 'admin']}>
                    <Upload />
                  </ProtectedRoute>
                } />
                <Route path="/results/:docId" element={<Results />} />
                <Route path="/history" element={
                  <ProtectedRoute allowedRoles={['user', 'admin']}>
                    <History />
                  </ProtectedRoute>
                } />
                <Route path="/institution/records" element={
                  <ProtectedRoute allowedRoles={['institution', 'admin']}>
                    <InstitutionRecords />
                  </ProtectedRoute>
                } />
                <Route path="/profile" element={<Profile />} />
                <Route path="/settings" element={<Settings />} />
              </Route>

              {/* Error Routes */}
              <Route path="/error" element={<ServerError />} />
              <Route path="/404" element={<NotFound />} />

              {/* Fallback */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
