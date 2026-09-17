# Coach AI Mobile PWA & Athlete Dashboard — Test Infrastructure Specification

**Status**: Active  
**Author**: E2E Test Writer (`teamwork_preview_test_writer_e2e_1`)  
**Target Environment**: Windows (Node.js v22.21.0, Python 3.14.0)  
**Applicable Milestones**: M1 (PWA Scaffold), M2 (Supabase Auth), M3 (Athlete Dashboard), M4 (Root Isolation & Zero Regression), M5 (Hardening)

---

## 1. Test Philosophy & Principles

The Coach AI test infrastructure is architected around the following core tenets:

1. **Specification-Driven & Opaque-Box**:
   Tests are written strictly against user requirements (`ORIGINAL_REQUEST.md`) and interface contracts (`PROJECT.md`). Tests treat the frontend application and backend service layers as contracts rather than inspecting internal transient variables, preventing brittle facade tests.

2. **Zero-Regression Guarantee**:
   The root Streamlit application must remain completely unaffected. Test runners verify that root Python modules compile without syntax errors and that no root application files are modified.

3. **Deterministic & Self-Contained Execution on Windows**:
   All test suites run deterministically on Windows using standard runtime tools (`python` and `node`) without external unpinned global dependencies. Test runners output structured logs and explicit exit codes (`0` for success, non-zero for failure).

4. **Multi-Tier Verification Pyramid**:
   Tests are categorized into 4 rigorous tiers plus Streamlit regression verification, providing deep coverage across unit contracts, boundary conditions, cross-module workflows, and realistic user journeys.

---

## 2. Test Tier Breakdown & Feature Inventory

### Tier 1: Feature Coverage (Baseline Contracts)
Verifies that individual features, files, and component contracts meet specified schemas, standards, and required props/fields:
- **T1.1 — PWA Web App Manifest**:
  - Valid JSON syntax in `frontend/public/manifest.json`.
  - Required fields: `name`, `short_name`, `display: "standalone"`, `start_url: "/"`.
  - Color definitions: `theme_color` and `background_color`.
  - Icon definitions: 192x192 and 512x512 with valid mime types.
- **T1.2 — Layout & Mobile Viewport**:
  - `frontend/app/layout.tsx` exports viewport meta with `device-width` and non-zoomable constraints.
  - Mobile touch styling and CSS reset configured in `frontend/app/globals.css`.
  - Safe-area-inset padding declarations present for notched/island mobile displays.
- **T1.3 — Supabase Client & Config**:
  - `frontend/lib/supabase.ts` exports singleton client `supabase`.
  - Correct fallback handling when `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are not provided.
  - Type definitions in `frontend/lib/types.ts` match authoritative database schemas for `Profile`, `Workout`, and `Schedule`.
- **T1.4 — Athlete Authentication**:
  - Sign-in form fields (`email`, `password`) and submission contracts.
  - Sign-up form fields (`nome`, `email`, `password`, `confirm_password`).
  - Auth profile synchronization matching `public.profiles` columns (`id`, `nome`, `email`, `esportes_ativos`, `dias_disponiveis`, `nivel_experiencia`, `objetivo_principal`).
- **T1.5 — ProfileHeader Component**:
  - Greeting rendered with athlete's name (`Olá, {nome} 👋`).
  - Sport badge, experience level badge, and goal badge.
  - Quick stats summary displaying Total Workouts, Total Distance (km), Avg Pace, and Adherence %.
  - Sign-out / logout trigger contract.
- **T1.6 — Next Workout Spotlight Card**:
  - Hero card displays workout type (`tipo_treino`), day and scheduled date (`dia_semana`, `data_prevista`).
  - Prescription metrics: target distance (`distancia_km`), target pace (`pace_alvo`), RPE / effort (`rpe_alvo`), duration (`duracao_min`).
  - Structural breakdown (`estrutura_treino`).
  - Interactive "Concluir Treino" action button contract.
- **T1.7 — Weekly Progress Metrics**:
  - Calculates completed vs total scheduled sessions (`X de Y concluídos`).
  - Calculates completed vs planned distance (`X / Y km`).
  - Computes adherence percentage: `(completed / total) * 100`.
  - Progress bar width mapping.
- **T1.8 — Workout Schedule List**:
  - Chronological rendering of scheduled workouts.
  - Distinct status badges for `"Pendente"` and `"Concluído"`.
  - Filter chips/tabs: `"Todos"`, `"Pendentes"`, `"Concluídos"`.
  - Direct check-in action from list.

### Tier 2: Boundary & Corner Cases
Stress-tests boundary conditions, edge cases, and failure modes:
- **T2.1 — Empty Microcycle Schedule**:
  - Handles empty array `[]` gracefully without null-pointer crashes.
  - Spotlight card renders informative empty state banner.
  - Schedule list displays guidance to generate training plan.
- **T2.2 — 0/0 Adherence Division by Zero**:
  - Total planned workouts = 0 returns 0% adherence (not `NaN` or `Infinity`).
  - Planned distance = 0 returns 0% distance adherence.
- **T2.3 — Authentication Input Boundaries**:
  - Passwords shorter than 6 characters rejected before API call.
  - Password mismatch between `password` and `confirm_password` detected and rejected.
  - Malformed email address validation.
  - Special characters and XSS payloads in athlete name (e.g. `<script>`, `João & Maria`, `O'Connor`) safely sanitized and rendered without JSON corruption.
- **T2.4 — Missing Environment Variables Fallback**:
  - Supabase client initialization succeeds gracefully even when environment variables are omitted.
  - Application surfaces user-friendly connection warnings rather than unhandled promise rejections.
- **T2.5 — 320px Extreme Viewport Responsiveness**:
  - CSS and layout do not employ fixed widths exceeding 320px without responsive overrides.
  - Touch targets strictly maintain minimum 44px height (`min-h-[44px]`).

### Tier 3: Cross-Feature Combinations
Tests multi-component reactive state transitions and data flows:
- **T3.1 — Full Auth to Dashboard Handshake**:
  - Sign in restores user session -> loads athlete profile -> populates ProfileHeader and QuickStats.
- **T3.2 — Spotlight Check-in State Transition**:
  - Athlete clicks "Concluir Treino" on Spotlight Card -> triggers status change to `'Concluído'`.
  - Schedule item updates `status = 'Concluído'` and records `data_conclusao`.
  - Spotlight Card immediately shifts to display the *next* pending session.
  - WeeklyProgress recalculates adherence percentage (e.g. from 25% to 50%).
  - WorkoutScheduleList badge updates from amber ("Pendente") to green ("Concluído").

### Tier 4: Real-World Athlete Scenarios
End-to-end simulation of a complete athlete microcycle:
- **T4.1 — Microcycle Progression**:
  - Athlete starts weekly plan with 3 scheduled sessions:
    1. Tuesday: 8.0 km Rodagem Z2 (Pendente)
    2. Thursday: 10.0 km Intervalado VO2 (Pendente)
    3. Saturday: 18.0 km Longão Aeróbico (Pendente)
  - Initial state: 0/3 completed (0% adherence).
  - Session 1 completed -> adherence reaches 33.3%, Spotlight advances to Thursday workout.
  - Session 2 completed -> adherence reaches 66.7%, Spotlight advances to Saturday workout.
  - Session 3 completed -> adherence reaches 100%, Spotlight displays weekly celebration banner.
  - Filter toggle to "Concluídos" lists all 3 workouts; "Pendentes" shows empty state.

### Streamlit Zero-Regression Verification
- **SR.1 — Python Bytecode Compilation**:
  - Runs `python -m py_compile` across all 16 Streamlit application files (`app.py`, `config.py`, `services/*.py`, `components/*.py`, `views/*.py`).
  - Must return exit code 0 with zero syntax errors.
- **SR.2 — Source Tree Isolation**:
  - Verifies that no root Streamlit files were modified or deleted.
  - Verifies that all new code is strictly isolated inside `frontend/` and `tests/`.

---

## 3. Test Runner Commands

### Unified Master Runner (Python)
Executes all test tiers and Streamlit regression checks in sequence:
```powershell
python tests/run_all_tests.py
```

### Node.js Master Runner
Executes Tiers 1 through 4 via Node:
```powershell
node tests/run_all_tests.js
```

### Streamlit Regression Runner
Validates root Python Streamlit app compilation:
```powershell
python tests/streamlit_zero_regression.test.py
```

### Running Individual Tiers
```powershell
node tests/tier1_feature_coverage.test.js
node tests/tier2_boundary_corner.test.js
node tests/tier3_cross_feature.test.js
node tests/tier4_real_world_scenario.test.js
```

---

## 4. Pass / Fail Semantics

- **Exit Code 0**: All tests in all tiers passed completely. No regression in Streamlit.
- **Exit Code 1**: One or more assertions failed. The runner prints:
  - Exact file and test case name that failed.
  - Expected vs. Actual values.
  - Error stack trace and failure diagnostic.
- **Strict Benchmark Integrity**: Facade tests that do not evaluate actual logic are strictly prohibited. Every test asserts against explicit authoritative criteria.
