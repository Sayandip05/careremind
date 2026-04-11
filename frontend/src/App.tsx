import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Upload from '@/pages/Upload';
import Patients from '@/pages/Patients';
import Reminders from '@/pages/Reminders';
import Admin from '@/pages/Admin';
import Settings from '@/pages/Settings';
import Billing from '@/pages/Billing';
import Staff from '@/pages/Staff';
import Landing from '@/pages/Landing';
import Onboarding from '@/pages/Onboarding';
import NotFound from '@/pages/NotFound';
import { useAuthStore } from '@/store/authStore';

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page at root for unauthenticated users */}
        <Route path="/" element={!isAuthenticated ? <Landing /> : <Navigate to="/dashboard" replace />} />
        
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />
        <Route path="/onboarding" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Onboarding />} />

        {/* Protected routes with Layout */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/staff" element={<Staff />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
