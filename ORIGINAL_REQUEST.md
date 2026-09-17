# Original User Request

## 2026-09-17T02:58:00Z

Build a high-performance, mobile-first Next.js (React) application with Tailwind CSS and PWA support inside the `frontend/` directory for Coach AI, while preserving full backward compatibility and operational stability of the existing root Streamlit application.

Working directory: c:\Users\Luis Eletro\Documents\antigravity\kind-raman
Integrity mode: benchmark

## Requirements

### R1. Next.js App Scaffold & PWA Setup (`frontend/`)
Scaffold a Next.js 14+ application with App Router, TypeScript, and Tailwind CSS inside `frontend/`. Include PWA configuration with `manifest.json` (or web app manifest), responsive viewport settings, and mobile touch optimizations.

### R2. Supabase Integration & Authentication
Configure `@supabase/supabase-js` to connect to the existing Supabase project. Implement athlete authentication (Login, Register with name/email/password) sharing the existing `profiles` table and session model.

### R3. Mobile Athlete Dashboard & Workout Spotlight
Implement a mobile-first Athlete Dashboard displaying:
- Athlete profile header with quick stats.
- Next Workout Spotlight card with workout details (type, target distance, pace/zone).
- Weekly progress metrics (completed vs pending sessions, total distance).
- Workout schedule list.

### R4. Streamlit Zero-Regression Guarantee
The existing Python Streamlit application at the repository root must remain 100% operational. Do not modify root files or alter database schemas in any way that breaks existing Streamlit functionality.

## Acceptance Criteria

### Next.js Mobile Frontend
- [ ] `frontend/` contains a valid Next.js project with `package.json`, Tailwind configuration, and App Router structure.
- [ ] Next.js build succeeds cleanly via `npm run build` with exit code 0.
- [ ] Web App Manifest (`manifest.json` / `manifest.ts`) is present with valid app name, standalone display mode, and icons.
- [ ] Supabase client helper connects cleanly to Supabase URL and anon key.
- [ ] Athlete login and dashboard pages render without unhandled errors.

### Backward Compatibility & Verification
- [ ] Root Streamlit application compiles cleanly with zero syntax errors via `python -m py_compile app.py config.py services/*.py components/*.py views/*.py`.
- [ ] All new files and dependencies are strictly confined to `frontend/` (plus repository-level config like `.gitignore`).
