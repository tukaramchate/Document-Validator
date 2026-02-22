# Frontend Implementation Plan — Document-Validator

## Overview

Transform the default Vite+React boilerplate into a fully functional document validation UI with authentication, file upload, results visualization, and history tracking.

**Current State:** Default Vite counter template in `App.jsx`. Only `FileUpload.jsx` and `axios.js` are custom code.

---

## Target Architecture

```
frontend/src/
├── api/
│   └── axios.js                    # ✅ EXISTS — Axios instance with JWT interceptors
│
├── assets/
│   ├── react.svg                   # ✅ EXISTS
│   └── logo.svg                    # (New) App logo
│
├── components/
│   ├── FileUpload.jsx              # ✅ EXISTS — Enhance with drag-and-drop, preview
│   ├── Navbar.jsx                  # (New) Navigation bar with auth-aware links
│   ├── ProtectedRoute.jsx          # (New) Redirects to /login if not authenticated
│   ├── ResultCard.jsx              # (New) Displays single verification result
│   ├── ScoreChart.jsx              # (New) Recharts bar/pie/gauge visualization
│   ├── ScoreGauge.jsx              # (New) Circular gauge for final score
│   ├── DocumentHistory.jsx         # (New) Table of past validations
│   ├── LoadingSpinner.jsx          # (New) Loading indicator
│   ├── AlertMessage.jsx            # (New) Success/error/warning banners
│   └── Footer.jsx                  # (New) App footer
│
├── pages/
│   ├── LoginPage.jsx               # (New) Login form
│   ├── RegisterPage.jsx            # (New) Registration form
│   ├── DashboardPage.jsx           # (New) Overview after login
│   ├── UploadPage.jsx              # (New) Full upload interface
│   ├── ResultsPage.jsx             # (New) Verification results with charts
│   └── HistoryPage.jsx             # (New) Past validation history
│
├── context/
│   └── AuthContext.jsx             # (New) React Context for auth state
│
├── hooks/
│   ├── useAuth.js                  # (New) Custom hook for auth operations
│   └── useApi.js                   # (New) Custom hook for API calls (loading/error)
│
├── utils/
│   ├── constants.js                # (New) API routes, score thresholds, file limits
│   └── validators.js               # (New) File type/size validation helpers
│
├── App.jsx                         # (Modify) Replace boilerplate with Router + layout
├── App.css                         # (Modify) Global styles for app layout
├── main.jsx                        # (Modify) Wrap App with AuthProvider
└── index.css                       # ✅ EXISTS — Tailwind directives
```

---

## Phase 1: Core Setup — Routing, Auth Context & Layout

### 1.1 React Router Setup (`App.jsx`)

Replace the default Vite template with a proper router:

```
Routes:
  /login          → LoginPage
  /register       → RegisterPage
  /dashboard      → DashboardPage       (protected)
  /upload         → UploadPage           (protected)
  /results/:id    → ResultsPage          (protected)
  /history        → HistoryPage          (protected)
  /               → Redirect to /dashboard if logged in, else /login
```

### 1.2 Auth Context (`context/AuthContext.jsx`)

Global authentication state management:

```
State:
  - user: { id, email, name, role } | null
  - token: string | null
  - isAuthenticated: boolean
  - loading: boolean

Actions:
  - login(email, password) → calls /api/auth/login → stores token & user
  - register(email, password, name) → calls /api/auth/register → stores token & user
  - logout() → clears token & user from state and localStorage
  - loadUser() → reads token from localStorage on mount, validates, loads profile

Persistence:
  - Token stored in localStorage
  - On app load: check localStorage for token → if valid, auto-login
```

### 1.3 Protected Route (`components/ProtectedRoute.jsx`)

```
Logic:
  - If isAuthenticated === true → render children
  - If isAuthenticated === false → redirect to /login
  - If loading === true → show LoadingSpinner
```

### 1.4 Navbar (`components/Navbar.jsx`)

```
When NOT logged in:
  [Logo]  [Login]  [Register]

When logged in:
  [Logo]  [Dashboard]  [Upload]  [History]  [User Name ▾]  [Logout]
```

Responsive: Hamburger menu on mobile.

---

## Phase 2: Authentication Pages

### 2.1 Login Page (`pages/LoginPage.jsx`)

```
┌──────────────────────────────────────┐
│                                      │
│         Document Validator           │
│         ──────────────────           │
│                                      │
│   Email:    [____________________]   │
│   Password: [____________________]   │
│                                      │
│          [ Login Button ]            │
│                                      │
│   Don't have an account? Register    │
│                                      │
└──────────────────────────────────────┘
```

Features:
- Form validation (email format, password required)
- Loading state during API call
- Error message display (wrong credentials)
- Redirect to `/dashboard` on success
- Link to Register page

### 2.2 Register Page (`pages/RegisterPage.jsx`)

```
┌──────────────────────────────────────┐
│                                      │
│        Create an Account             │
│        ─────────────────             │
│                                      │
│   Name:     [____________________]   │
│   Email:    [____________________]   │
│   Password: [____________________]   │
│   Confirm:  [____________________]   │
│                                      │
│         [ Register Button ]          │
│                                      │
│   Already have an account? Login     │
│                                      │
└──────────────────────────────────────┘
```

Features:
- All fields required
- Password match validation
- Password strength indicator
- Redirect to `/dashboard` on success

---

## Phase 3: Dashboard & Upload

### 3.1 Dashboard Page (`pages/DashboardPage.jsx`)

```
┌────────────────────────────────────────────────────────────┐
│  Welcome back, [User Name]!                                │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Total Docs   │  │  Authentic   │  │  Suspicious  │     │
│  │     12       │  │      8       │  │      3       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                            │
│  [ Upload New Document ]                                   │
│                                                            │
│  ── Recent Verifications ───────────────────────────────   │
│  │ Document        │ Date       │ Verdict    │ Score  │    │
│  │ marksheet.pdf   │ Feb 22     │ AUTHENTIC  │ 94%   │    │
│  │ certificate.jpg │ Feb 21     │ SUSPICIOUS │ 78%   │    │
│  │ id_card.png     │ Feb 20     │ FAKE       │ 45%   │    │
│  ─────────────────────────────────────────────────────     │
│                                  [ View All History → ]    │
└────────────────────────────────────────────────────────────┘
```

Features:
- Summary stats cards (total docs, authentic count, suspicious count, fake count)
- Quick upload button → navigates to `/upload`
- Last 5 recent verifications table
- Link to full history

### 3.2 Upload Page (`pages/UploadPage.jsx`)

```
┌────────────────────────────────────────────────────────────┐
│  Upload Document for Verification                          │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │       📄  Drag & drop your file here                 │  │
│  │           or click to browse                         │  │
│  │                                                      │  │
│  │       Supports: PDF, JPG, PNG (max 16MB)             │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  Selected: marksheet.pdf (2.3 MB)      [ ✕ Remove ]       │
│  [████████████████████░░░░] 75% uploading...               │
│                                                            │
│              [ Upload & Validate ]                          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

Features:
- Drag-and-drop zone with visual feedback
- File type and size validation (client-side)
- File preview (image thumbnail or PDF icon)
- Upload progress bar
- After upload → auto-trigger validation → redirect to `/results/:id`

---

## Phase 4: Results & History

### 4.1 Results Page (`pages/ResultsPage.jsx`)

```
┌──────────────────────────────────────────────────────────────┐
│  Verification Results — marksheet.pdf                        │
│                                                              │
│   ┌───────────────────────────────────────────────────────┐  │
│   │                                                       │  │
│   │          FINAL VERDICT: SUSPICIOUS                    │  │
│   │          Final Score: 77.4%                            │  │
│   │          [    ████████████░░░░░ 77%    ]              │  │
│   │                                                       │  │
│   └───────────────────────────────────────────────────────┘  │
│                                                              │
│   ── Score Breakdown ──────────────────────────────────────   │
│                                                              │
│   ┌──────────────────┐   ┌──────────────────┐                │
│   │   BAR CHART      │   │   PIE CHART      │                │
│   │                  │   │                  │                │
│   │ CNN:  ████ 85%   │   │   ┌────┐         │                │
│   │ OCR:  █████ 92%  │   │  /  OK  \        │                │
│   │ DB:   ███ 60%    │   │ | WARN |         │                │
│   │                  │   │  \ FAIL /         │                │
│   └──────────────────┘   └──────────────────┘                │
│                                                              │
│   ── Extracted Data ───────────────────────────────────────   │
│   │ Field      │ Extracted    │ Database     │ Match │       │
│   │ Name       │ Rahul Sharma │ Rahul Sharma │  ✅   │       │
│   │ Roll No    │ 2022CSE1045  │ 2022CSE1045  │  ✅   │       │
│   │ CGPA       │ 8.5          │ 7.2          │  ❌   │       │
│   ──────────────────────────────────────────────────────     │
│                                                              │
│   [ ← Back to Dashboard ]        [ Upload Another ]         │
└──────────────────────────────────────────────────────────────┘
```

Components used:
- `ScoreGauge` — circular gauge for final score
- `ScoreChart` — Recharts bar chart for CNN/OCR/DB breakdown
- `ResultCard` — field-level match table
- Color coding: green (≥90%), orange (70–89%), red (<70%)

### 4.2 History Page (`pages/HistoryPage.jsx`)

```
┌──────────────────────────────────────────────────────────────┐
│  Verification History                                        │
│                                                              │
│  Search: [__________________]  Filter: [All Verdicts ▾]     │
│                                                              │
│  │ # │ Document         │ Type │ Date       │ Verdict    │ Score │
│  │ 1 │ marksheet.pdf    │ PDF  │ 2026-02-22 │ AUTHENTIC  │ 94%  │
│  │ 2 │ certificate.jpg  │ JPG  │ 2026-02-21 │ SUSPICIOUS │ 78%  │
│  │ 3 │ id_card.png      │ PNG  │ 2026-02-20 │ FAKE       │ 45%  │
│  │ 4 │ degree.pdf       │ PDF  │ 2026-02-19 │ AUTHENTIC  │ 91%  │
│  │ 5 │ license.jpg      │ JPG  │ 2026-02-18 │ AUTHENTIC  │ 96%  │
│                                                              │
│  Showing 1–5 of 12         [ < Prev ]  1  2  3  [ Next > ]  │
└──────────────────────────────────────────────────────────────┘
```

Features:
- Paginated table (10 per page)
- Search by filename
- Filter by verdict (All / Authentic / Suspicious / Fake)
- Click any row → navigate to `/results/:id`
- Color-coded verdict badges

---

## Phase 5: UI Components

### 5.1 Component Specifications

| Component | Props | Purpose |
|---|---|---|
| `Navbar` | — | Top navigation bar, reads `useAuth()` for state |
| `ProtectedRoute` | `children` | Wraps routes that require authentication |
| `FileUpload` | `onUploadSuccess(doc)` | Upload form with drag-and-drop |
| `ResultCard` | `result` | Displays full result breakdown |
| `ScoreChart` | `cnn, ocr, db` | Recharts bar chart of three scores |
| `ScoreGauge` | `score, verdict` | Circular gauge showing final percentage |
| `DocumentHistory` | `documents, onPageChange` | Paginated history table |
| `LoadingSpinner` | `size, text` | Centered spinner with optional text |
| `AlertMessage` | `type, message, onClose` | Dismissible success/error/warning banner |
| `Footer` | — | App footer with copyright |

### 5.2 Custom Hooks

| Hook | Returns | Purpose |
|---|---|---|
| `useAuth()` | `{user, token, isAuthenticated, login, register, logout, loading}` | Consumes AuthContext |
| `useApi(url, options)` | `{data, loading, error, execute}` | Generic API call hook with states |

### 5.3 Utilities

| Utility | Function | Purpose |
|---|---|---|
| `constants.js` | `API_ROUTES`, `SCORE_THRESHOLDS`, `ALLOWED_TYPES`, `MAX_FILE_SIZE` | Centralized constants |
| `validators.js` | `isValidFileType(file)`, `isValidFileSize(file)`, `isValidEmail(email)` | Client-side validations |

---

## Phase 6: Styling & Design System

### 6.1 Color Palette

| Purpose | Color | Tailwind Class |
|---|---|---|
| Primary | `#3B82F6` (Blue) | `bg-blue-500` |
| Success / Authentic | `#10B981` (Green) | `bg-emerald-500` |
| Warning / Suspicious | `#F59E0B` (Amber) | `bg-amber-500` |
| Danger / Fake | `#EF4444` (Red) | `bg-red-500` |
| Background | `#F8FAFC` (Light Gray) | `bg-slate-50` |
| Card Background | `#FFFFFF` (White) | `bg-white` |
| Text Primary | `#1E293B` (Dark Slate) | `text-slate-800` |
| Text Secondary | `#64748B` (Gray) | `text-slate-500` |

### 6.2 Design Principles

- **Card-based layout** — each section in a white card with `rounded-xl shadow-md`
- **Consistent spacing** — `p-6` for card padding, `gap-6` between cards
- **Responsive** — Mobile-first with `sm:`, `md:`, `lg:` breakpoints
- **Animations** — Subtle `transition-all duration-300` on hover effects
- **Typography** — Inter or system font stack

---

## Implementation Timeline

| Phase | Task | Estimated Time |
|---|---|---|
| Phase 1 | Router, AuthContext, ProtectedRoute, Navbar | 3–4 hours |
| Phase 2 | Login + Register pages | 2–3 hours |
| Phase 3 | Dashboard + Upload pages | 3–4 hours |
| Phase 4 | Results + History pages (with Recharts) | 4–5 hours |
| Phase 5 | Reusable components + hooks + utils | 2–3 hours |
| Phase 6 | Styling, polish, responsive | 2–3 hours |
| **Total** | | **16–22 hours** |

---

*Plan prepared: February 22, 2026*
