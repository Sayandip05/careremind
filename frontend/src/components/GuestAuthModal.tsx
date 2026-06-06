/**
 * GuestAuthModal.tsx
 *
 * A polished modal that appears whenever a guest (unauthenticated) user tries
 * to perform an action that requires an account.  Provides clear CTAs to sign
 * up or log in, and can be dismissed to stay on the preview page.
 */

import { useEffect } from 'react';
import { X, BellRing, ArrowRight, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface GuestAuthModalProps {
  onClose: () => void;
}

export default function GuestAuthModal({ onClose }: GuestAuthModalProps) {
  const navigate = useNavigate();

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Prevent body scroll while modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  const handleSignUp = () => {
    navigate('/login');
    onClose();
  };

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Modal card */}
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">

        {/* Green accent header bar */}
        <div className="bg-gradient-to-r from-[#1E5F3A] to-[#22c55e] px-6 pt-8 pb-10">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
              <BellRing className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-bold text-lg">CareRemind</span>
          </div>
          <h2 className="text-2xl font-bold text-white leading-snug">
            You're viewing a demo
          </h2>
          <p className="text-white/80 text-sm mt-1">
            Create a free account to use all features and manage your clinic.
          </p>
        </div>

        {/* Close button — sits on the header */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white transition-colors"
          aria-label="Close"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Body */}
        <div className="px-6 pt-4 pb-6 -mt-4">
          {/* Feature bullets */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 mb-5 space-y-2.5">
            {[
              'Automated WhatsApp reminders',
              'AI notepad scanning',
              'Patient self-booking via chat',
              'Midnight PDF schedule report',
            ].map((feat) => (
              <div key={feat} className="flex items-center gap-2.5">
                <div className="w-4 h-4 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                  <svg className="w-2.5 h-2.5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-sm text-slate-700">{feat}</span>
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div className="flex flex-col gap-3">
            <button
              onClick={handleSignUp}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-[#1E5F3A] hover:bg-[#15472B] text-white font-semibold rounded-xl transition-colors"
            >
              <Sparkles className="w-4 h-4" />
              Start Free 14-Day Trial
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={handleSignUp}
              className="w-full py-3 px-4 border border-slate-200 hover:bg-slate-50 text-slate-700 font-medium rounded-xl transition-colors text-sm"
            >
              Already have an account? Log In
            </button>
          </div>

          <p className="text-center text-xs text-slate-400 mt-4">
            No credit card required · Free for 14 days
          </p>
        </div>
      </div>
    </div>
  );
}
