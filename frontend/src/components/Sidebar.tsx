import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useGuestMode } from '@/context/GuestModeContext';
import {
  LayoutDashboard,
  Upload,
  Bell,
  LogOut,
  BellRing,
  Shield,
  Settings,
  CreditCard,
  CalendarCheck,
  UserPlus,
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/upload',    label: 'Upload',     icon: Upload },
  { path: '/patients',  label: 'Bookings',   icon: CalendarCheck },
  { path: '/reminders', label: 'Reminders',  icon: Bell },
  { path: '/billing',   label: 'Billing',    icon: CreditCard },
  { path: '/settings',  label: 'Settings',   icon: Settings },
  { path: '/admin',     label: 'Admin',      icon: Shield },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
  /** Vertical offset in px — used to push sidebar below the guest banner. */
  offsetTop?: number;
}

export default function Sidebar({ open = false, onClose, offsetTop = 0 }: SidebarProps) {
  const { user, logout } = useAuthStore();
  const { isGuest } = useGuestMode();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* ── Backdrop overlay (mobile only) ─────────────────────── */}
      <div
        onClick={onClose}
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 40,
          background: 'rgba(0,0,0,0.4)',
          backdropFilter: 'blur(2px)',
          // Fade in/out
          opacity: open ? 1 : 0,
          pointerEvents: open ? 'auto' : 'none',
          transition: 'opacity 0.25s ease',
        }}
        className="md:hidden"
      />

      {/* ── Sidebar panel ──────────────────────────────────────────
          Uses inline style for transform so Tailwind v4 scanning
          issues cannot interfere with the open/close animation.
      ────────────────────────────────────────────────────────────── */}
      <aside
        style={open
          ? { transform: 'translateX(0)', top: offsetTop, height: `calc(100vh - ${offsetTop}px)` }
          : { top: offsetTop, height: `calc(100vh - ${offsetTop}px)` }
        }
        className="fixed left-0 w-[220px] bg-white border-r border-slate-200 flex flex-col z-50
                   -translate-x-full md:translate-x-0
                   transition-transform duration-300 ease-in-out"
      >
        {/* Brand — hidden on mobile (Header shows it) */}
        <div className="hidden md:flex px-5 py-5 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-[#1E5F3A] rounded-md flex items-center justify-center text-white">
              <BellRing className="w-4 h-4" />
            </div>
            <span className="text-[15px] font-semibold text-slate-800">CareRemind</span>
          </div>
        </div>

        {/* Spacer on mobile — pushes nav below the fixed header (56px) */}
        <div className="h-14 md:hidden" aria-hidden="true" />

        {/* Nav */}
        <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-100 text-slate-900'
                      : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* User info + action */}
        <div className="px-3 py-3 border-t border-slate-100">
          {isGuest ? (
            // Guest: show a sign-up CTA
            <button
              onClick={() => navigate('/login')}
              className="w-full flex items-center gap-2 px-3 py-2 text-[13px] font-medium text-[#1E5F3A] hover:bg-green-50 rounded-md transition-colors"
            >
              <UserPlus className="w-4 h-4" />
              Sign up / Log in
            </button>
          ) : (
            // Authenticated user
            <>
              <div className="flex items-center gap-2.5 px-3 py-2 mb-1">
                <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-xs font-semibold text-slate-600">
                  {user?.doctor_name?.charAt(0)?.toUpperCase() || 'D'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-medium text-slate-700 truncate">
                    {user?.doctor_name || 'Doctor'}
                  </p>
                  <p className="text-[11px] text-slate-400 truncate">
                    {user?.clinic_name || 'Clinic'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2 text-[13px] text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign out
              </button>
            </>
          )}
        </div>
      </aside>
    </>
  );
}
