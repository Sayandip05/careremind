import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Upload from '@/pages/Upload';
import Patients from '@/pages/Patients';
import Reminders from '@/pages/Reminders';
import Admin from '@/pages/Admin';
import Landing from '@/pages/Landing';
import { useAuthStore } from '@/store/authStore';

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/home" element={!isAuthenticated ? <Landing /> : <Navigate to="/" replace />} />
        
        <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />

        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/admin" element={<Admin />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
