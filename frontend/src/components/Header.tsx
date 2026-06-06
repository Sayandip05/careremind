import { Menu, BellRing, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

interface HeaderProps {
  onMenuToggle: () => void;
  sidebarOpen: boolean;
  /** Vertical offset in px (used to push header below the guest banner). */
  offsetTop?: number;
}

/**
 * Mobile-only top header bar.
 * Hidden on md+ screens where the persistent sidebar takes over.
 */
export default function Header({ onMenuToggle, sidebarOpen, offsetTop = 0 }: HeaderProps) {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  /** Navigate to the landing page root and scroll to the very top. */
  const handleBrandClick = () => {
    navigate('/');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header
      className="fixed left-0 right-0 z-40 flex items-center justify-between px-4 h-14 bg-white border-b border-slate-200 md:hidden"
      style={{ top: offsetTop }}
    >
      {/* Brand — clickable, scrolls user to top of landing page */}
      <button
        onClick={handleBrandClick}
        aria-label="Go to top of page"
        className="flex items-center gap-2 rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1E5F3A] focus-visible:ring-offset-2"
      >
        <div className="w-7 h-7 bg-[#1E5F3A] rounded-md flex items-center justify-center text-white flex-shrink-0">
          <BellRing className="w-4 h-4" />
        </div>
        <span className="text-[15px] font-semibold text-slate-800">CareRemind</span>
      </button>

      {/* Right side: user avatar + hamburger */}
      <div className="flex items-center gap-3">
        {/* User avatar */}
        <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-semibold text-slate-600 border border-slate-200">
          {user?.doctor_name?.charAt(0)?.toUpperCase() || 'D'}
        </div>

        {/* Hamburger / Close toggle */}
        <button
          onClick={onMenuToggle}
          aria-label={sidebarOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={sidebarOpen}
          className="w-8 h-8 flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>
    </header>
  );
}
