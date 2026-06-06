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
import Landing from '@/pages/Landing';
import Onboarding from '@/pages/Onboarding';
import NotFound from '@/pages/NotFound';
import { useAuthStore } from '@/store/authStore';
import { GuestModeProvider } from '@/context/GuestModeContext';

/**
 * ProtectedRoute
 * - Authenticated users: renders children normally.
 * - Guests: still renders children (preview / demo mode) — no redirect.
 *   The GuestModeContext + GuestBanner + GuestAuthModal handle the UX.
 *
 * Admin-only routes remain hard-protected (redirect to /login for guests).
 */
function DemoRoute({ children }: { children: React.ReactNode }) {
  // Always render — guest mode is handled by context
  return <>{children}</>;
}

/**
 * StrictProtectedRoute — only for admin pages that must never be visible to guests.
 */
function StrictProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <GuestModeProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={!isAuthenticated ? <Landing /> : <Navigate to="/dashboard" replace />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />
          <Route path="/onboarding" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Onboarding />} />

          {/*
            Semi-open routes — accessible to both authenticated users and guests.
            Guests see demo data + the GuestBanner + action-gate modal.
            Layout itself now handles the banner rendering.
          */}
          <Route element={<DemoRoute><Layout /></DemoRoute>}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/reminders" element={<Reminders />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/billing" element={<Billing />} />
          </Route>

          {/* Strict admin — requires real authentication */}
          <Route
            path="/admin"
            element={
              <StrictProtectedRoute>
                <Layout />
              </StrictProtectedRoute>
            }
          >
            <Route index element={<Admin />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </GuestModeProvider>
    </BrowserRouter>
  );
}
