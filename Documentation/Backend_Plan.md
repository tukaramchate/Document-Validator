# Backend Implementation Plan — Document-Validator

## Overview

Transform the current minimal Flask backend into a production-ready API server with authentication, database, secure file handling, and AI pipeline orchestration.

**Current State:** Single `app.py` (40 lines) with `/api/health` and `/api/upload` — no database, no auth, no AI integration.

---

## Target Architecture

```
backend/
├── app.py                          # Application factory (create_app)
├── config.py                       # Dev / Prod / Test configuration
├── requirements.txt                # Python dependencies
├── .env                            # Environment secrets (not in Git)
├── .env.example                    # Template for .env
├── .gitignore                      # Ignore .env, uploads/, __pycache__/
│
├── blueprints/                     # Flask Blueprints (route modules)
│   ├── __init__.py
│   ├── auth.py                     # Register, Login, Profile endpoints
│   ├── upload.py                   # Upload, List, Delete document endpoints
│   └── validation.py              # Validate, Results, History endpoints
│
├── models/                         # SQLAlchemy ORM models
│   ├── __init__.py                 # db = SQLAlchemy()
│   ├── user.py                     # User model
│   ├── document.py                 # Document model
│   └── result.py                   # Validation Result model
│
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py             # Registration, login, token generation
│   ├── upload_service.py           # File save, list, delete logic
│   └── validation_service.py      # AI pipeline orchestration
│
├── middleware/                      # Request/response processing
│   ├── __init__.py
│   ├── auth_middleware.py          # @token_required JWT decorator
│   └── error_handler.py           # Global exception handler
│
├── utils/                          # Helper utilities
│   ├── __init__.py
│   ├── file_utils.py              # File type validation, UUID naming
│   └── response_utils.py          # Standardized JSON responses
│
├── uploads/                        # Uploaded files (generated, gitignored)
├── migrations/                     # Alembic DB migrations (generated)
└── tests/                          # Pytest test suite
    ├── __init__.py
    ├── conftest.py                 # Test fixtures
    ├── test_auth.py
    ├── test_upload.py
    └── test_validation.py
```

---

## Phase 1: Foundation — Config, Database & Models

### 1.1 Dependencies to Add

```
# requirements.txt
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.0
PyJWT==2.8.0
Werkzeug==3.0.1
bcrypt==4.1.2
pytest==7.4.0
```

### 1.2 Configuration (`config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### 1.3 Database Models

**User Model:**
| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key, Auto-increment |
| `email` | String(120) | Unique, Not Null |
| `password_hash` | String(256) | Not Null |
| `name` | String(100) | Not Null |
| `role` | String(20) | Default: "user" |
| `created_at` | DateTime | Default: utcnow |

Methods:
- `set_password(password)` — hashes using `werkzeug.security.generate_password_hash()`
- `check_password(password)` — verifies using `werkzeug.security.check_password_hash()`
- `to_dict()` — serializes to JSON-safe dict (excludes `password_hash`)

**Document Model:**
| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `filename` | String(255) | Original name, Not Null |
| `stored_name` | String(255) | UUID-based name, Unique |
| `file_type` | String(10) | "pdf", "jpg", "png" |
| `file_size` | Integer | Size in bytes |
| `user_id` | Integer | Foreign Key → User.id |
| `uploaded_at` | DateTime | Default: utcnow |

Relationships:
- `user` → belongs to User
- `result` → has one Result

**Result Model:**
| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `document_id` | Integer | Foreign Key → Document.id, Unique |
| `cnn_score` | Float | Visual analysis score (0–1) |
| `ocr_confidence` | Float | OCR confidence score (0–1) |
| `db_match_score` | Float | Database match score (0–1) |
| `final_score` | Float | Weighted combined score (0–1) |
| `verdict` | String(20) | "AUTHENTIC" / "SUSPICIOUS" / "FAKE" |
| `extracted_data` | JSON | OCR-extracted fields |
| `field_matches` | JSON | Per-field match details |
| `validated_at` | DateTime | Default: utcnow |

### 1.4 Application Factory (`app.py`)

```python
def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(validation_bp, url_prefix='/api')

    # Register error handlers
    register_error_handlers(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
```

---

## Phase 2: Authentication (JWT)

### 2.1 Endpoints

| Method | Endpoint | Auth Required | Request Body | Response |
|---|---|---|---|---|
| POST | `/api/auth/register` | No | `{"email", "password", "name"}` | `201 {success, data: {user, token}}` |
| POST | `/api/auth/login` | No | `{"email", "password"}` | `200 {success, data: {user, token}}` |
| GET | `/api/auth/profile` | Yes | — | `200 {success, data: {user}}` |

### 2.2 JWT Middleware (`@token_required`)

```python
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error_response('Token is missing', 'AUTH_ERROR', 401)
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
        except jwt.ExpiredSignatureError:
            return error_response('Token has expired', 'AUTH_ERROR', 401)
        except jwt.InvalidTokenError:
            return error_response('Token is invalid', 'AUTH_ERROR', 401)
        return f(current_user, *args, **kwargs)
    return decorated
```

### 2.3 Auth Service Logic

**Registration Flow:**
```
Input: email, password, name
  → Validate email format & password strength (min 6 chars)
  → Check if email already exists → 409 Conflict
  → Hash password with werkzeug.security
  → Create User record in DB
  → Generate JWT token (payload: user_id, exp: 24h)
  → Return user dict + token
```

**Login Flow:**
```
Input: email, password
  → Find user by email → 401 if not found
  → Check password hash → 401 if wrong
  → Generate JWT token
  → Return user dict + token
```

### 2.4 Validation Rules

| Field | Rule |
|---|---|
| `email` | Required, valid email format, unique |
| `password` | Required, minimum 6 characters |
| `name` | Required, minimum 2 characters |

---

## Phase 3: Secure File Upload

### 3.1 Endpoints

| Method | Endpoint | Auth | Request | Response |
|---|---|---|---|---|
| POST | `/api/upload` | Yes | `multipart/form-data (file)` | `201 {document_id, filename}` |
| GET | `/api/upload/list` | Yes | `?page=1&per_page=10` | `200 {documents: [...], total, pages}` |
| DELETE | `/api/upload/<id>` | Yes | — | `200 {message}` |

### 3.2 Security Measures

| Threat | Defense |
|---|---|
| Path traversal (`../../etc/passwd`) | `werkzeug.utils.secure_filename()` |
| Malicious file types | Extension whitelist: `pdf, jpg, jpeg, png` |
| File size attack | `MAX_CONTENT_LENGTH = 16MB` (Flask rejects before read) |
| Filename collision | UUID-based stored names (`uuid4() + extension`) |
| Unauthorized access | `@token_required` on all endpoints |
| Accessing other users' files | Service layer checks `user_id` ownership |

### 3.3 Upload Service Flow

```
Input: file object, user_id
  → Check file exists → 400 if not
  → Validate extension (allowed_file) → 400 if invalid
  → Generate stored_name: uuid4().hex + "." + extension
  → secure_filename(original_name) for display
  → Save file to uploads/ directory
  → Create Document record in DB
  → Return document dict
```

---

## Phase 4: AI Validation Pipeline

### 4.1 Endpoints

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| POST | `/api/validate/<doc_id>` | Yes | `200 {result with all scores}` |
| GET | `/api/results/<doc_id>` | Yes | `200 {result}` |
| GET | `/api/history` | Yes | `200 {results: [...], total, pages}` |

### 4.2 Validation Service — Pipeline Steps

```
validate_document(doc_id, user_id):
    │
    ├── Step 1: Verify document exists and belongs to user
    │           → 404 if not found, 403 if not owner
    │
    ├── Step 2: Check if already validated
    │           → Return existing result if yes
    │
    ├── Step 3: Load image from uploads/ directory
    │           → Use PIL/OpenCV to open the file
    │
    ├── Step 4: PREPROCESS
    │           → Resize to 224×224
    │           → Normalize pixel values to 0.0–1.0
    │           → Convert to RGB array
    │
    ├── Step 5: CNN PREDICTION
    │           → Load trained model (.h5 file)
    │           → model.predict(preprocessed_image)
    │           → cnn_score = prediction[0][0]  (0.0 to 1.0)
    │
    ├── Step 6: OCR EXTRACTION
    │           → Run Tesseract/EasyOCR on original image
    │           → Extract raw text
    │           → Parse into structured fields (name, roll_no, etc.)
    │           → ocr_confidence = average character confidence
    │
    ├── Step 7: DATABASE CROSS-VERIFICATION
    │           → Query Trusted_Records table with extracted identifier
    │           → Compare each field (fuzzy match for OCR errors)
    │           → db_match_score = matched_fields / total_fields
    │
    ├── Step 8: SCORE COMBINATION
    │           → final_score = cnn×0.4 + ocr_conf×0.2 + db_match×0.4
    │           → verdict:
    │               ≥ 0.90 → "AUTHENTIC"
    │               ≥ 0.70 → "SUSPICIOUS"
    │               < 0.70 → "FAKE"
    │
    └── Step 9: SAVE & RETURN
              → Create Result record in DB
              → Return complete result with breakdown
```

### 4.3 Initial Implementation (Mock Mode)

For the initial build, the AI steps will return **simulated scores** so the full API pipeline can be tested:

```python
# Placeholder until real AI model is trained
def mock_cnn_predict(image_path):
    return random.uniform(0.6, 0.95)

def mock_ocr_extract(image_path):
    return {
        "fields": {"name": "Sample Name", "id": "12345"},
        "confidence": random.uniform(0.7, 0.98)
    }

def mock_db_match(extracted_fields):
    return {
        "score": random.uniform(0.5, 1.0),
        "matches": {"name": True, "id": False}
    }
```

This will be replaced with real CNN/OCR calls once the AI model is trained.

---

## Phase 5: Error Handling & Logging

### 5.1 Global Error Handlers

| Status Code | Scenario | Response |
|---|---|---|
| 400 | Bad request, missing fields, invalid input | `{"success": false, "error": {"code": "BAD_REQUEST", "message": "..."}}` |
| 401 | Missing/expired/invalid JWT token | `{"success": false, "error": {"code": "UNAUTHORIZED", "message": "..."}}` |
| 403 | User not authorized for this resource | `{"success": false, "error": {"code": "FORBIDDEN", "message": "..."}}` |
| 404 | Resource not found | `{"success": false, "error": {"code": "NOT_FOUND", "message": "..."}}` |
| 413 | File too large (>16MB) | `{"success": false, "error": {"code": "FILE_TOO_LARGE", "message": "..."}}` |
| 500 | Unexpected server error | `{"success": false, "error": {"code": "INTERNAL_ERROR", "message": "..."}}` |

### 5.2 Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

Key log points:
- User registration/login (INFO)
- File upload success/failure (INFO/WARNING)
- Validation pipeline start/completion (INFO)
- All errors (ERROR with stack trace)

---

## Phase 6: Testing Strategy

### 6.1 Test Configuration

- **Framework:** pytest
- **Database:** In-memory SQLite for test isolation
- **Fixtures:** Test app, test client, registered user, auth token

### 6.2 Test Coverage

| Module | Test Cases |
|---|---|
| **Auth** | Register success, duplicate email (409), missing fields (400), login success, wrong password (401), invalid email (401), access protected route without token (401), expired token (401) |
| **Upload** | Upload valid PDF (201), upload valid JPG (201), upload invalid type .exe (400), upload without auth (401), list documents, delete own document (200), delete other user's doc (403) |
| **Validation** | Validate document (200 with scores), validate non-existent doc (404), get results (200), get history with pagination |

### 6.3 Run Commands

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/test_auth.py -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=. --cov-report=term-missing
```

---

## Implementation Timeline

| Phase | Task | Estimated Time |
|---|---|---|
| Phase 1 | Config, models, app factory | 2–3 hours |
| Phase 2 | JWT auth (register, login, middleware) | 3–4 hours |
| Phase 3 | Secure file upload | 2–3 hours |
| Phase 4 | Validation pipeline (mock AI initially) | 3–4 hours |
| Phase 5 | Error handling & logging | 1–2 hours |
| Phase 6 | Tests | 3–4 hours |
| **Total** | | **14–20 hours** |

---

*Plan prepared: February 22, 2026*
