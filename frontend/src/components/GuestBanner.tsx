/**
 * GuestBanner.tsx
 *
 * A sticky banner shown at the very top of the app layout when a guest
 * (unauthenticated) user is browsing in preview / demo mode.
 */

import { Eye, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function GuestBanner() {
  const navigate = useNavigate();

  return (
    <div className="fixed top-0 left-0 right-0 z-[60] bg-[#1E5F3A] text-white">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-center gap-3 text-sm">
        <Eye className="w-3.5 h-3.5 shrink-0 opacity-80" />
        <span className="font-medium">
          👀 You're viewing a <strong>live demo</strong> — data shown is sample data
        </span>
        <span className="hidden sm:inline text-white/60">·</span>
        <button
          onClick={() => navigate('/login')}
          className="hidden sm:flex items-center gap-1 font-semibold text-white underline underline-offset-2 hover:text-green-200 transition-colors"
        >
          Sign up free
          <ArrowRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}
