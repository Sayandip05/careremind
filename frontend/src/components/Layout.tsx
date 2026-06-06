import { useState, useCallback } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import GuestBanner from './GuestBanner';
import { useGuestMode } from '@/context/GuestModeContext';

/**
 * Layout offset constants (px):
 *   BANNER_H   = 32   (h-8,  guest banner)
 *   HEADER_H   = 56   (h-14, mobile header)
 *   PAGE_GAP   = 32   (breathing room between fixed bar and content, same on all pages)
 *
 * Total padding-top applied to main content:
 *   Mobile  + guest   = BANNER_H + HEADER_H + PAGE_GAP = 32+56+32 = 120px
 *   Mobile  + authed  = HEADER_H + PAGE_GAP             = 56+32   =  88px
 *   Desktop + guest   = BANNER_H + PAGE_GAP             = 32+32   =  64px
 *   Desktop + authed  = PAGE_GAP                        =    32   =  32px
 */

const BANNER_H = 32;
const HEADER_H = 56;
const PAGE_GAP = 32; // consistent breathing room on every page

export default function Layout() {
  const { isGuest } = useGuestMode();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = useCallback(() => setSidebarOpen((prev) => !prev), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  const fixedOffset = isGuest ? BANNER_H : 0;

  const mobilePaddingTop  = (isGuest ? BANNER_H : 0) + HEADER_H + PAGE_GAP;
  const desktopPaddingTop = (isGuest ? BANNER_H : 0) + PAGE_GAP;

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Guest demo banner — fixed top-0, 32px tall */}
      {isGuest && <GuestBanner />}

      {/* Mobile header — offset below banner when guest */}
      <Header
        onMenuToggle={toggleSidebar}
        sidebarOpen={sidebarOpen}
        offsetTop={fixedOffset}
      />

      {/* Sidebar — offset below banner when guest */}
      <Sidebar
        open={sidebarOpen}
        onClose={closeSidebar}
        offsetTop={fixedOffset}
      />

      {/*
        Main content area.
        padding-top = fixed bars + consistent PAGE_GAP breathing room.
        We use a single inline style driven by a CSS custom property trick
        via two hidden spacer divs (one per breakpoint).
      */}
      <main className="flex-1 md:ml-[220px] px-6 md:px-8 pb-10">
        {/* Mobile spacer */}
        <div className="md:hidden" style={{ height: mobilePaddingTop }} />
        {/* Desktop spacer */}
        <div className="hidden md:block" style={{ height: desktopPaddingTop }} />

        <div className="max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
