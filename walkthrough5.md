# Phase 6: React Dashboard — Walkthrough

> **Stack:** Vite + React 18 + TypeScript + Tailwind CSS + Zustand + React Router 6  
> **Dev server:** `http://localhost:3000`

---

## Architecture

```
src/
├── api/           6 modules (client, auth, dashboard, patients, reminders, upload)
├── store/         Zustand auth store with localStorage persistence
├── components/    Sidebar, Layout (auth guard), StatsCard
├── pages/         Login, Dashboard, Upload, Patients, Reminders
├── App.tsx        Protected routes via Layout wrapper
└── main.tsx       Entry point
```

## Pages Built

| Page | Features |
|------|----------|
| **Login** | Glassmorphism card, register/login toggle, specialty selector, gradient CTA, loading spinner, error display |
| **Dashboard** | 6 color-coded stats cards, quick actions grid, personalized greeting |
| **Upload** | Drag-and-drop zone, Excel/Photo toggle, progress spinner, result summary (rows, new patients, duplicates, skipped) |
| **Patients** | Paginated table with avatars, phone, age, gender, language, channel badges, Active/Opted Out status |
| **Reminders** | Status filter tabs (All/Pending/Sent/Failed/Optout), reminder cards with channel icons, scheduled/sent dates, error logs |

## Design System

- **Theme:** Dark mode (slate-950 background), emerald/cyan accent gradients
- **Font:** Inter from Google Fonts
- **Animations:** Fade-in, slide-up, hover scale, spin loaders
- **Glassmorphism:** Login card with backdrop-blur
- **Sidebar:** Fixed left nav, gradient logo, active state glow

## Verification

| Step | Result |
|------|--------|
| `npm install` | ✅ 160 packages installed |
| `npx vite --port 3000` | ✅ Server ready in 547ms |
| Dashboard compiles | ✅ No build errors |
