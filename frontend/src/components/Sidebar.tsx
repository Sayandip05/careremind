import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { LayoutDashboard, Users, Upload, Bell, LogOut, BellRing, Shield, Settings, CreditCard, UsersRound } from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/upload', label: 'Upload', icon: Upload },
  { path: '/patients', label: 'Patients', icon: Users },
  { path: '/reminders', label: 'Reminders', icon: Bell },
  { path: '/billing', label: 'Billing', icon: CreditCard },
  { path: '/settings', label: 'Settings', icon: Settings },
  { path: '/admin', label: 'Admin', icon: Shield },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-[220px] bg-white border-r border-slate-200 flex flex-col z-30">
      <div className="px-5 py-5 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-[#1E5F3A] rounded-md flex items-center justify-center text-white">
            <BellRing className="w-4 h-4" />
          </div>
          <span className="text-[15px] font-semibold text-slate-800">CareRemind</span>
        </div>
      </div>

      <nav className="flex-1 px-3 py-3 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
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

      <div className="px-3 py-3 border-t border-slate-100">
        <div className="flex items-center gap-2.5 px-3 py-2 mb-1">
          <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-xs font-semibold text-slate-600">
            {user?.doctor_name?.charAt(0) || 'D'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[13px] font-medium text-slate-700 truncate">{user?.doctor_name || 'Doctor'}</p>
            <p className="text-[11px] text-slate-400 truncate">{user?.clinic_name || 'Clinic'}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 text-[13px] text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
