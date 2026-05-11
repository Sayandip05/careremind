import { useState, useCallback } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuthStore } from '@/store/authStore';

export default function Layout() {
  const { isAuthenticated } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = useCallback(() => setSidebarOpen((prev) => !prev), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Mobile top header bar — hidden on md+ */}
      <Header onMenuToggle={toggleSidebar} sidebarOpen={sidebarOpen} />

      {/* Sidebar — desktop persistent / mobile slide-in drawer */}
      <Sidebar open={sidebarOpen} onClose={closeSidebar} />

      {/* Main content
          - On desktop: offset by sidebar width (ml-[220px])
          - On mobile:  no left margin, but push down below the fixed header (pt-14)
      */}
      <main className="flex-1 pt-14 md:pt-0 md:ml-[220px] p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
