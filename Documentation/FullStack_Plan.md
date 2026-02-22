# Full-Stack Integration Plan — Document-Validator

## Overview

This document describes how the three independent layers — **Frontend (React)**, **Backend (Flask)**, and **AI Model (CNN + OCR)** — connect and communicate to form a complete document validation system.

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                             │
└────────────────────────────┬───────────────────────────────────────┘
                             │  HTTP / REST API
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│  FRONTEND (React 19 + Vite + Tailwind)     Port: 5173 (dev)      │
│                                                                    │
│  Pages: Login → Register → Dashboard → Upload → Results → History │
│  State: AuthContext (JWT token, user object)                       │
│  HTTP: Axios instance with JWT interceptor                         │
│  Charts: Recharts (bar, pie, gauge)                                │
└────────────────────────────┬───────────────────────────────────────┘
                             │  JSON / multipart/form-data
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│  BACKEND (Flask 3.0)                       Port: 5000             │
│                                                                    │
│  Blueprints: auth | upload | validation                            │
│  Middleware: JWT auth | error handler                              │
│  Services: auth_service | upload_service | validation_service      │
│  ORM: SQLAlchemy (User, Document, Result, TrustedRecord)           │
└────────┬───────────────────┬───────────────────┬──────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐
│   DATABASE   │   │ FILE STORAGE │   │      AI MODEL            │
│   SQLite /   │   │  uploads/    │   │                          │
│   PostgreSQL │   │              │   │  preprocessing/          │
│              │   │              │   │  cnn/ (predict)          │
│  Users       │   │  .pdf        │   │  ocr/ (extract text)     │
│  Documents   │   │  .jpg        │   │  verification/ (match)   │
│  Results     │   │  .png        │   │  score_calculator        │
│  Records     │   │              │   │                          │
└──────────────┘   └──────────────┘   └──────────────────────────┘
```

---

## Integration Point 1: Frontend ↔ Backend API

### 1.1 API Communication Map

Every frontend page calls specific backend endpoints:

| Frontend Page | API Calls | Endpoint | Method |
|---|---|---|---|
| **LoginPage** | Login | `/api/auth/login` | POST |
| **RegisterPage** | Register | `/api/auth/register` | POST |
| **DashboardPage** | Load profile | `/api/auth/profile` | GET |
| | Recent history | `/api/history?per_page=5` | GET |
| **UploadPage** | Upload file | `/api/upload` | POST |
| | Trigger validation | `/api/validate/<doc_id>` | POST |
| **ResultsPage** | Get results | `/api/results/<doc_id>` | GET |
| **HistoryPage** | All history | `/api/history?page=1` | GET |
| | List docs | `/api/upload/list` | GET |

### 1.2 Authentication Flow (End-to-End)

```
FRONTEND                              BACKEND
────────                              ───────
1. User fills login form
2. POST /api/auth/login ──────────►  3. Validate email + password
   {email, password}                  4. Generate JWT (user_id, exp: 24h)
                                      5. Return {user, token}
6. Store token in localStorage  ◄──── 
7. Set user in AuthContext
8. Redirect to /dashboard
9. All future requests include:
   Authorization: Bearer <token> ──►  10. @token_required verifies token
                                      11. Attaches current_user to request
```

### 1.3 File Upload + Validation Flow (End-to-End)

```
FRONTEND                              BACKEND                         AI MODEL
────────                              ───────                         ────────
1. User selects file
2. Client-side validation
   (type, size)
3. POST /api/upload ──────────────►  4. secure_filename()
   multipart/form-data                5. Save to uploads/
                                      6. Create Document record
                                      7. Return {doc_id}
8. Receive doc_id  ◄──────────────── 
9. POST /api/validate/<doc_id> ───►  10. Load image from uploads/
                                      11. Call validation_service ──►  12. Preprocess image
                                                                       13. CNN predict → score
                                                                       14. OCR extract → fields
                                      15. Query DB for record          
                                      16. Compare fields (fuzzy)  ◄──  
                                      17. Calculate final score
                                      18. Save Result record
                                      19. Return full result
20. Receive result ◄─────────────────
21. Render ResultsPage
    - ScoreGauge (final %)
    - ScoreChart (CNN/OCR/DB bars)
    - Field match table
```

### 1.4 CORS Configuration

Frontend (port 5173) and backend (port 5000) run on different ports, requiring CORS:

```python
# Backend app.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 1.5 Standard Response Contract

All API responses follow the same JSON structure for consistent frontend parsing:

```javascript
// Frontend (axios interceptor or useApi hook)
try {
    const response = await axiosInstance.post('/upload', formData);
    // response.data = { success: true, data: {...}, message: "..." }
    const result = response.data.data;
} catch (error) {
    // error.response.data = { success: false, error: { code: "...", message: "..." } }
    const errorMsg = error.response?.data?.error?.message || 'Unknown error';
}
```

---

## Integration Point 2: Backend ↔ AI Model

### 2.1 How Backend Calls the AI Model

The `validation_service.py` in the backend imports and calls the AI model:

```python
# backend/services/validation_service.py

import sys
sys.path.insert(0, '../ai_model')  # or use proper package install

from model import DocumentValidator

validator = DocumentValidator()
validator.load_model()

def validate_document(document):
    image_path = os.path.join('uploads', document.stored_name)
    result = validator.validate(image_path, db_session=db.session)
    return result
```

### 2.2 Data Flow: Backend → AI → Backend

```
validation_service.validate_document(doc_id)
    │
    ├── Input:  image_path = "uploads/a1b2c3d4.jpg"
    │
    ├── Calls:  validator.validate(image_path, db_session)
    │           │
    │           ├── preprocessing.preprocess_for_cnn(path)
    │           │   └── Returns: numpy array (1, 224, 224, 3)
    │           │
    │           ├── cnn.predict(preprocessed_image)
    │           │   └── Returns: {"score": 0.85, "label": "real"}
    │           │
    │           ├── ocr.extract_text(path)
    │           │   └── Returns: {"raw_text": "...", "confidence": 0.92}
    │           │
    │           ├── ocr.parse_fields(raw_text)
    │           │   └── Returns: {"name": "Rahul", "roll_no": "123"}
    │           │
    │           ├── verification.match_against_db(fields, db_session)
    │           │   └── Returns: {"score": 0.60, "matches": {...}}
    │           │
    │           └── verification.calculate_final_score(0.85, 0.92, 0.60)
    │               └── Returns: {"final_score": 0.764, "verdict": "SUSPICIOUS"}
    │
    └── Output: Complete result object → saved to DB → returned to frontend
```

### 2.3 Integration Strategy: Mock → Real

| Phase | CNN | OCR | DB Matching |
|---|---|---|---|
| **Phase A** (Immediate) | Mock random scores | Mock extracted fields | Mock match results |
| **Phase B** (After OCR setup) | Mock | Real Tesseract/EasyOCR | Mock |
| **Phase C** (After CNN training) | Real CNN model | Real OCR | Real DB matching |
| **Phase D** (Production) | Optimized CNN | Optimized OCR | Full trusted records |

This allows the **full API pipeline** to be tested immediately, while AI components are developed in parallel.

---

## Integration Point 3: Backend ↔ Database

### 3.1 Database Schema Relationships

```
Users ──1:N──► Documents ──1:1──► Results
                                      │
                                      │ (extracted fields compared against)
                                      ▼
                              Trusted_Records
```

### 3.2 Key Database Operations

| Operation | Service | SQL/ORM |
|---|---|---|
| Create user | `auth_service.register_user()` | `db.session.add(user)` |
| Find user by email | `auth_service.login_user()` | `User.query.filter_by(email=email)` |
| Save document record | `upload_service.save_file()` | `db.session.add(document)` |
| Get user's documents | `upload_service.get_user_documents()` | `Document.query.filter_by(user_id=uid).paginate()` |
| Save validation result | `validation_service.validate_document()` | `db.session.add(result)` |
| Get result by doc_id | `validation_service.get_result()` | `Result.query.filter_by(document_id=doc_id)` |
| Get user's history | `validation_service.get_history()` | Join Document + Result, filter by user_id |
| Lookup trusted record | `db_matcher.match_against_db()` | `TrustedRecord.query.filter_by(identifier=id)` |

### 3.3 Database Migration Strategy

```bash
# Initial setup
flask db init
flask db migrate -m "Initial: User, Document, Result, TrustedRecord"
flask db upgrade

# After model changes
flask db migrate -m "Description of change"
flask db upgrade
```

---

## Environment Configuration

### 4.1 Environment Variables

**Backend (`.env`):**
```
SECRET_KEY=randomly-generated-secret-key-here
JWT_SECRET_KEY=another-random-secret-for-jwt
DATABASE_URL=sqlite:///dev.db
FLASK_ENV=development
FLASK_DEBUG=1
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=16
```

**Frontend (`.env`):**
```
VITE_API_URL=http://localhost:5000/api
```

### 4.2 Port Configuration

| Service | Dev Port | Production |
|---|---|---|
| Frontend (Vite) | 5173 | 80 (Nginx) |
| Backend (Flask) | 5000 | 5000 (Gunicorn) |
| Database | — (SQLite file) | 5432 (PostgreSQL) |

---

## Development Workflow

### 5.1 Starting All Services (Development)

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py
# → Running on http://localhost:5000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
# → Running on http://localhost:5173

# Terminal 3: AI Model (for training)
cd ai_model
pip install -r requirements.txt
python cnn/train.py
```

### 5.2 Development Order

The recommended order for building the full stack:

```
Step 1: Backend Phase 1 (Config + DB Models)
    │   → Foundation must exist first
    ▼
Step 2: Backend Phase 2 (Auth)
    │   → Need login before protecting routes
    ▼
Step 3: Frontend Phase 1 (Router + Auth Context)
    │   → Can now test login/register end-to-end
    ▼
Step 4: Frontend Phase 2 (Login + Register Pages)
    │   → Full auth flow working
    ▼
Step 5: Backend Phase 3 (Upload)
    │   → Upload API ready
    ▼
Step 6: Frontend Phase 3 (Dashboard + Upload Pages)
    │   → Can upload files through UI
    ▼
Step 7: Backend Phase 4 (Validation - mock AI)
    │   → Full pipeline testable with mock scores
    ▼
Step 8: Frontend Phase 4 (Results + History Pages)
    │   → Full UI working with mock data
    ▼
Step 9: AI Model Phases 1–5 (Preprocessing, CNN, OCR, Matching)
    │   → Real AI pipeline ready
    ▼
Step 10: Backend — Replace mock AI with real AI calls
    │   → System fully functional
    ▼
Step 11: Backend Phase 5–6 (Error handling + Tests)
    │   → Production-ready
    ▼
Step 12: Frontend Phase 5–6 (Polish + Responsive)
         → Deployment-ready
```

---

## Testing Strategy (Full-Stack)

### 6.1 Testing Levels

| Level | What | Tools |
|---|---|---|
| **Unit Tests** | Individual functions (services, utils, components) | pytest (backend), Jest (frontend) |
| **Integration Tests** | API endpoint behavior (routes + DB) | pytest + Flask test client |
| **Component Tests** | React components render correctly | React Testing Library |
| **E2E Tests** | Full user flows (login → upload → view result) | Browser tool or Playwright |

### 6.2 Key Test Scenarios

| # | Scenario | Expected Result |
|---|---|---|
| 1 | Register → Login → Upload → Validate → View Result | All succeed, result shows scores |
| 2 | Upload invalid file type (.exe) | 400 error, file rejected |
| 3 | Access upload without login | 401 redirect to login |
| 4 | Upload → Validate → Check History | Document appears in history |
| 5 | Login with wrong password | 401 error, descriptive message |
| 6 | Upload file > 16MB | 413 error, file rejected |
| 7 | View result for another user's document | 403 forbidden |
| 8 | Validate same document twice | Returns existing result (no re-process) |

---

## Production Deployment

### 7.1 Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/docvalidator
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - uploads:/app/uploads
      - models:/app/models
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=docvalidator
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  uploads:
  models:
  pgdata:
```

### 7.2 Deployment Steps

```
1. Build frontend:   cd frontend && npm run build
2. Build Docker:     docker-compose build
3. Start services:   docker-compose up -d
4. Run migrations:   docker-compose exec backend flask db upgrade
5. Seed data:        docker-compose exec backend python seed_trusted_records.py
6. Verify:           curl http://localhost/api/health
```

---

## Project Timeline Summary

| Week | Backend | Frontend | AI Model |
|---|---|---|---|
| **Week 1** | Config, DB models, Auth | Router, AuthContext, Login/Register | Preprocessing pipeline |
| **Week 2** | Upload, Validation (mock AI) | Dashboard, Upload, Results pages | CNN architecture + training start |
| **Week 3** | Error handling, Tests | History, Polish, Responsive | OCR integration, DB matching |
| **Week 4** | Replace mock → real AI | E2E testing, Bug fixes | CNN training, Evaluation |
| **Week 5** | Dockerize, Deploy | Final polish | Model optimization |

**Total estimated effort: 4–5 weeks** (working part-time/evenings alongside college)

---

*Plan prepared: February 22, 2026*
*Project: Document-Validator — AI-Powered Document Authenticity Verification System*
