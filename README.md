# Document-Validator

A full-stack AI-powered document validation system that verifies document authenticity using CNN analysis, OCR text extraction, and database cross-verification.

## Overview

Final year project that combines AI-based document analysis with database verification. The system processes uploaded documents through a multi-stage pipeline — CNN for visual authenticity, OCR for text extraction, and fuzzy matching against trusted records — to produce a confidence score and verdict.

## Project Structure

```
Document-Validator/
├── backend/                    # Flask REST API
│   ├── app.py                  # Application factory
│   ├── config.py               # Dev/Prod/Test configuration
│   ├── blueprints/             # Route handlers (auth, upload, validation)
│   ├── models/                 # SQLAlchemy models (User, Document, Result)
│   ├── services/               # Business logic layer
│   ├── middleware/              # JWT auth & error handling
│   ├── utils/                  # File & response utilities
│   └── tests/                  # Pytest test suite (30 tests)
├── frontend/                   # React + Vite SPA
│   └── src/
│       ├── pages/              # Login, Register, Dashboard, Upload, Results, History
│       ├── components/         # Navbar, Layout, ProtectedRoute
│       ├── context/            # AuthContext (JWT state management)
│       ├── hooks/              # useApi (generic API wrapper)
│       └── api/                # Axios instance with interceptors
├── AI Model/                   # ML models (CNN, OCR) — in development
└── Documentation/              # Implementation plans
```

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS v4, Recharts, Axios, React Router |
| **Backend** | Flask, Flask-SQLAlchemy, Flask-Migrate, PyJWT, bcrypt |
| **AI/ML** | TensorFlow/Keras (CNN), Tesseract (OCR), OpenCV, scikit-learn |
| **Database** | SQLite (dev), PostgreSQL-ready (prod) |
| **Testing** | pytest, pytest-cov |

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env with your secret keys

python app.py
# → API running at http://localhost:5000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → App running at http://localhost:5173
```

### 3. Run Tests

```bash
cd backend
python -m pytest tests/ -v
# 30 tests — auth, upload, validation
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | — | Register new user |
| `POST` | `/api/auth/login` | — | Login & get JWT token |
| `GET` | `/api/auth/profile` | ✓ | Get user profile |
| `POST` | `/api/upload` | ✓ | Upload document (PDF/JPG/PNG, ≤16MB) |
| `GET` | `/api/upload/list` | ✓ | List documents (paginated) |
| `DELETE` | `/api/upload/<id>` | ✓ | Delete document |
| `POST` | `/api/validate/<id>` | ✓ | Run AI validation pipeline |
| `GET` | `/api/results/<id>` | ✓ | Get validation result |
| `GET` | `/api/history` | ✓ | Validation history (paginated) |
| `GET` | `/api/health` | — | Health check |

## Features

- **🔐 Authentication** — JWT-based register/login with protected routes
- **📤 Document Upload** — Drag-and-drop with file type/size validation & UUID storage
- **🧠 AI Validation Pipeline** — CNN visual analysis + OCR text extraction + DB cross-verification
- **📊 Score Visualization** — Circular score chart, breakdown bars, and verdict badges (Recharts)
- **📋 Validation History** — Paginated list with verdict filter tabs (Authentic/Suspicious/Fake)
- **🌙 Dark Mode UI** — Glassmorphism design with smooth animations
- **🛡️ Security** — Path traversal prevention, file whitelist, ownership checks

## How It Works

```
Upload → Preprocess → CNN Analysis → OCR Extraction → DB Matching → Score & Verdict
                        (40%)           (20%)            (40%)
```

1. User uploads a document through the React frontend
2. Backend saves the file securely with UUID naming
3. **CNN** analyzes visual authenticity (score 0–1)
4. **OCR** extracts text fields & measures confidence (score 0–1)
5. **Database** cross-verifies extracted fields via fuzzy matching (score 0–1)
6. Weighted final score → verdict: **AUTHENTIC** (≥90%), **SUSPICIOUS** (≥70%), or **FAKE** (<70%)
7. Results displayed with interactive charts and field-by-field breakdown

> **Note:** The AI pipeline currently uses mock scores. Replace the mock functions in `services/validation_service.py` with real model calls once the CNN is trained.

## Environment Variables

### Backend (`backend/.env`)
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///dev.db
FLASK_ENV=development
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:5000/api
```

## License

See [LICENSE](LICENSE) file for details.
