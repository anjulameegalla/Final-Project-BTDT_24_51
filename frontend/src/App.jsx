import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/common/ProtectedRoute'

import LandingPage    from './pages/LandingPage'
import LoginPage      from './pages/LoginPage'
import RegisterPage   from './pages/RegisterPage'
import DashboardPage  from './pages/DashboardPage'
import ConnectAWSPage from './pages/ConnectAWSPage'
import ScanPage       from './pages/ScanPage'
import ReportsPage    from './pages/ReportsPage'
import AlertsPage     from './pages/AlertsPage'
import AdminPage      from './pages/AdminPage'
import ProfilePage    from './pages/ProfilePage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/"         element={<LandingPage />} />
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected */}
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/connect"   element={<ProtectedRoute><ConnectAWSPage /></ProtectedRoute>} />
        <Route path="/scan"      element={<ProtectedRoute><ScanPage /></ProtectedRoute>} />
        <Route path="/reports"   element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
        <Route path="/alerts"    element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
        <Route path="/profile"   element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

        {/* Admin only */}
        <Route path="/admin" element={<ProtectedRoute adminOnly><AdminPage /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
