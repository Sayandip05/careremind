/**
 * GuestModeContext.tsx
 *
 * Provides two things to the entire component tree:
 *   - `isGuest`     — true when the user is NOT authenticated
 *   - `requireAuth` — call this before any mutating action; if the user is a
 *                     guest it opens the sign-up modal instead of executing
 *                     the callback. Optionally accepts a callback to run when
 *                     the user IS authenticated.
 */

import { createContext, useCallback, useContext, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import GuestAuthModal from '@/components/GuestAuthModal';

// ── Context shape ─────────────────────────────────────────────────────────────

interface GuestModeContextValue {
  isGuest: boolean;
  /**
   * Wrap any interactive action with this helper.
   * - Authenticated users: `onAuthed()` executes immediately.
   * - Guest users:         the sign-up modal is shown; `onAuthed` is ignored.
   */
  requireAuth: (onAuthed?: () => void) => void;
}

const GuestModeContext = createContext<GuestModeContextValue>({
  isGuest: false,
  requireAuth: () => {},
});

// ── Provider ──────────────────────────────────────────────────────────────────

export function GuestModeProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  const isGuest = !isAuthenticated;

  const [modalOpen, setModalOpen] = useState(false);

  const requireAuth = useCallback(
    (onAuthed?: () => void) => {
      if (isAuthenticated) {
        onAuthed?.();
      } else {
        setModalOpen(true);
      }
    },
    [isAuthenticated],
  );

  return (
    <GuestModeContext.Provider value={{ isGuest, requireAuth }}>
      {children}
      {modalOpen && <GuestAuthModal onClose={() => setModalOpen(false)} />}
    </GuestModeContext.Provider>
  );
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useGuestMode(): GuestModeContextValue {
  return useContext(GuestModeContext);
}
