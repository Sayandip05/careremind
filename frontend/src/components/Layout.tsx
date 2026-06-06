import { useState, useCallback } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import GuestBanner from './GuestBanner';
import { useGuestMode } from '@/context/GuestModeContext';

export default function Layout() {
  const { isGuest } = useGuestMode();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = useCallback(() => setSidebarOpen((prev) => !prev), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Demo mode sticky banner — only visible to guests */}
      {isGuest && <GuestBanner />}

      {/* Mobile top header bar — hidden on md+ */}
      {/* Push header below the guest banner (h-8) when shown */}
      <div className={isGuest ? 'mt-8' : ''}>
        <Header onMenuToggle={toggleSidebar} sidebarOpen={sidebarOpen} />
      </div>

      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onClose={closeSidebar} />

      {/*
        Main content area.
        - isGuest adds extra top padding to account for the sticky banner (h-8 = 32px)
          plus the mobile header (pt-14 on mobile / 0 on desktop).
        - Sidebar offset on md+ remains the same.
      */}
      <main
        className={`flex-1 md:ml-[220px] p-6 md:p-8 ${
          isGuest ? 'pt-22 md:pt-8' : 'pt-14 md:pt-0'
        }`}
      >
        <div className="max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
