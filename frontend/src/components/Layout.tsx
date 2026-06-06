import { useState, useCallback } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import GuestBanner from './GuestBanner';
import { useGuestMode } from '@/context/GuestModeContext';

/**
 * Layout offset constants (px):
 *   BANNER_H  = 32  (h-8)
 *   HEADER_H  = 56  (h-14, mobile-only)
 *
 * Guest fixed-element offsets:
 *   Header  → top: 32px   (below banner)
 *   Sidebar → top: 32px   (below banner)
 *
 * Main content padding-top:
 *   Mobile  + guest   = 32 + 56 = 88px
 *   Mobile  + authed  = 56px
 *   Desktop + guest   = 32px
 *   Desktop + authed  = 0px
 */

const BANNER_H = 32;  // px
const HEADER_H = 56;  // px

export default function Layout() {
  const { isGuest } = useGuestMode();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = useCallback(() => setSidebarOpen((prev) => !prev), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  // How many px the fixed header/sidebar should be pushed down
  const fixedOffset = isGuest ? BANNER_H : 0;

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Demo mode banner — fixed top-0, h-8 (32px) */}
      {isGuest && <GuestBanner />}

      {/* Mobile header — sits below the banner when guest */}
      <Header
        onMenuToggle={toggleSidebar}
        sidebarOpen={sidebarOpen}
        offsetTop={fixedOffset}
      />

      {/* Sidebar — sits below the banner when guest */}
      <Sidebar
        open={sidebarOpen}
        onClose={closeSidebar}
        offsetTop={fixedOffset}
      />

      {/*
        Main scrollable area.
        We push the content down with padding-top to clear both the banner
        and the mobile header.  On desktop (md+) there's no mobile header,
        so only the banner height is needed.
      */}
      <main className="flex-1 md:ml-[220px] px-6 md:px-8 pb-8">
        {/* Mobile: clear banner + header */}
        <div
          className="md:hidden"
          style={{ paddingTop: isGuest ? BANNER_H + HEADER_H : HEADER_H }}
        />
        {/* Desktop: clear banner only */}
        <div
          className="hidden md:block"
          style={{ paddingTop: isGuest ? BANNER_H : 0 }}
        />

        <div className="max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
