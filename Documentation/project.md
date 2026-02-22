# Document-Validator — Complete Project Documentation

---

## Table of Contents

1. [Core Idea](#1-core-idea)
2. [Objectives](#2-objectives)
3. [Problem Statement](#3-problem-statement)
4. [Project Workflow](#4-project-workflow)
5. [System Block Diagram](#5-system-block-diagram)
6. [Technology Stack Overview](#6-technology-stack-overview)
7. [Frontend — Detailed Architecture](#7-frontend--detailed-architecture)
8. [Backend — Detailed Architecture](#8-backend--detailed-architecture)
9. [AI Model — Detailed Architecture](#9-ai-model--detailed-architecture)
10. [Database Design](#10-database-design)
11. [API Specification](#11-api-specification)
12. [Security Architecture](#12-security-architecture)
13. [Deployment Architecture](#13-deployment-architecture)
14. [Future Scope](#14-future-scope)

---

## 1. Core Idea

The **Document-Validator** is an AI-powered web application that determines whether a given document (certificate, marksheet, ID card, etc.) is **authentic or forged**. It achieves this by combining three independent verification strategies:

| Strategy | Technique | What It Checks |
|---|---|---|
| **Visual Analysis** | CNN (Convolutional Neural Network) | Template layout, seals, stamps, tampering artifacts, font consistency |
| **Text Extraction** | OCR (Optical Character Recognition) | Reads all text fields from the document image |
| **Data Verification** | Database Cross-Matching | Compares extracted text against trusted institutional records |

By combining image-level AI analysis with factual data verification, the system provides a **multi-layered authenticity assessment** that is far more reliable than any single-method approach.

### Real-World Use Case

> A university admissions office receives 500+ transfer certificates during admission season. Instead of manually verifying each one by contacting the issuing institution, an admin uploads the certificate to Document-Validator. Within seconds, the system:
> - Checks if the certificate visually matches the known template of that institution
> - Reads the student's name, roll number, and grades via OCR
> - Verifies those details against the institution's database
> - Returns a verdict: **Authentic**, **Suspicious**, or **Fake**

---

## 2. Objectives

### Primary Objectives

1. **Automate Document Verification** — Replace manual, time-consuming document verification processes with an instant, AI-driven system
2. **Detect Forged Documents** — Identify visually tampered, photoshopped, or synthetically generated fake documents using CNN-based image analysis
3. **Cross-Verify Document Data** — Extract text via OCR and validate it against trusted database records to catch factually incorrect documents
4. **Provide Confidence Scoring** — Deliver a quantitative authenticity score with a detailed breakdown across multiple validation points
5. **Visualize Results** — Present verification results through intuitive charts and reports for easy interpretation

### Secondary Objectives

6. **User Authentication** — Secure the system with JWT-based login/registration to control access
7. **Document History** — Maintain a record of all validated documents for audit trails
8. **Responsive UI** — Build a modern, mobile-friendly interface accessible from any device
9. **Scalable Architecture** — Design the system to support additional document types and verification methods in the future
10. **Data Privacy** — Ensure uploaded documents are handled securely and not exposed to unauthorized users

---

## 3. Problem Statement

In educational institutions, government offices, and corporate organizations, **document fraud is a growing concern**. Manually verifying the authenticity of certificates, marksheets, and identity documents is:

- **Time-consuming** — Each document requires contacting the issuing authority
- **Error-prone** — Human reviewers can miss subtle signs of tampering
- **Unscalable** — Verification queues grow during peak periods (admission seasons, hiring drives)
- **Inconsistent** — Different reviewers may reach different conclusions

**This project addresses these challenges** by providing an automated, AI-based verification system that delivers consistent, fast, and reliable results by combining visual pattern recognition with factual data verification.

---

## 4. Project Workflow

### 4.1 User Workflow (End-to-End)

```
Step 1: User registers/logs in to the system
              ↓
Step 2: User uploads a document image (PDF/JPEG/PNG)
              ↓
Step 3: System preprocesses the image (resize, normalize, denoise)
              ↓
Step 4: CNN model analyzes visual patterns (template, seals, tampering)
              ↓
Step 5: OCR engine extracts text fields (name, roll no, grades, etc.)
              ↓
Step 6: Extracted data is compared against the trusted database
              ↓
Step 7: Scores from all three checks are combined into a final verdict
              ↓
Step 8: Results are displayed with charts and detailed breakdown
              ↓
Step 9: Verification record is saved to document history
```

### 4.2 Detailed Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                            │
│                                                                     │
│   Browser → Login/Register → Upload Document → View Results        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS (REST API)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FLASK BACKEND                               │
│                                                                     │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│   │ Auth     │  │ File Upload  │  │ AI Service   │  │ Results   │ │
│   │ Module   │  │ Module       │  │ Module       │  │ Module    │ │
│   │          │  │              │  │              │  │           │ │
│   │ Register │  │ Validate     │  │ Preprocess   │  │ Calculate │ │
│   │ Login    │  │ Save         │  │ CNN Predict  │  │ Score     │ │
│   │ JWT      │  │ Serve        │  │ OCR Extract  │  │ Store     │ │
│   └──────────┘  └──────────────┘  │ DB Verify    │  │ History   │ │
│                                    └──────────────┘  └───────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ORM (SQLAlchemy)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE                                     │
│                                                                     │
│   Users Table │ Documents Table │ Results Table │ Records Table     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 AI Verification Pipeline (Internal)

```
Document Image
      │
      ▼
┌─────────────────┐
│  PREPROCESSING  │
│  - Resize 224²  │
│  - Normalize    │
│  - Denoise      │
│  - Grayscale    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────────┐
│  CNN   │ │   OCR      │
│ Model  │ │  Engine    │
│        │ │            │
│ Visual │ │ Text       │
│ Score  │ │ Extraction │
│ (0-1)  │ │            │
└───┬────┘ └─────┬──────┘
    │            │
    │            ▼
    │     ┌──────────────┐
    │     │  DB MATCHING │
    │     │              │
    │     │ Compare each │
    │     │ field against│
    │     │ trusted data │
    │     │              │
    │     │ Match Score  │
    │     │ (0-1)        │
    │     └──────┬───────┘
    │            │
    ▼            ▼
┌─────────────────────────┐
│    SCORE COMBINER       │
│                         │
│ Final = CNN×0.4         │
│       + OCR_Conf×0.2    │
│       + DB_Match×0.4    │
│                         │
│ ≥90% → AUTHENTIC       │
│ 70-89% → SUSPICIOUS    │
│ <70% → LIKELY FAKE     │
└─────────────────────────┘
```

---

## 5. System Block Diagram

### 5.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│   │  Login   │  │  Upload  │  │ Results  │  │  History  │  │
│   │  Page    │  │  Page    │  │  Page    │  │  Page     │  │
│   └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│                                                              │
│   React 19 + Vite + Tailwind CSS + Recharts + React Router  │
└──────────────────────────┬───────────────────────────────────┘
                           │ REST API (HTTP/JSON)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐   │
│   │              Flask Backend (Python)                   │   │
│   │                                                      │   │
│   │  ┌────────────┐ ┌────────────┐ ┌─────────────────┐   │   │
│   │  │ Auth       │ │ Upload     │ │ Validation      │   │   │
│   │  │ Blueprint  │ │ Blueprint  │ │ Blueprint       │   │   │
│   │  └────────────┘ └────────────┘ └─────────────────┘   │   │
│   │                                                      │   │
│   │  ┌────────────┐ ┌────────────┐ ┌─────────────────┐   │   │
│   │  │ JWT        │ │ File       │ │ Error           │   │   │
│   │  │ Middleware  │ │ Validation │ │ Handler         │   │   │
│   │  └────────────┘ └────────────┘ └─────────────────┘   │   │
│   └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────────┐
│    AI LAYER      │ │ DATABASE │ │   FILE STORAGE   │
│                  │ │          │ │                  │
│ CNN Model        │ │ Users    │ │ uploads/         │
│ OCR Engine       │ │ Documents│ │ models/          │
│ Preprocessor     │ │ Results  │ │ temp/            │
│ Score Calculator │ │ Records  │ │                  │
└──────────────────┘ └──────────┘ └──────────────────┘
```

### 5.2 Component Interaction Diagram

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ React  │────▶│ Flask  │────▶│  AI    │────▶│  DB    │
│Frontend│◀────│Backend │◀────│ Model  │     │        │
└────────┘JSON └────────┘     └────────┘     └────────┘
     │                              │              │
     │         ┌────────────────────┘              │
     │         ▼                                   │
     │    ┌────────┐                               │
     │    │  OCR   │───────────────────────────────┘
     │    │ Engine │  (cross-verify extracted text)
     │    └────────┘
     │
     ▼
┌────────┐
│Recharts│
│ Charts │ (visualize verification results)
└────────┘
```

---

## 6. Technology Stack Overview

### 6.1 Complete Tech Stack Table

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | React.js | 19.2.0 | Component-based UI framework |
| | Vite | 7.2.4 | Build tool and dev server |
| | Tailwind CSS | 4.1.18 | Utility-first CSS framework |
| | React Router DOM | 7.13.0 | Client-side page routing |
| | Axios | 1.13.4 | HTTP client for API calls |
| | Recharts | 3.7.0 | Data visualization / charts |
| **Backend** | Python | 3.10+ | Backend programming language |
| | Flask | 3.0.0 | Lightweight web framework |
| | Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| | PyJWT | 2.8.0 | JSON Web Token authentication |
| | Werkzeug | 3.0.1 | WSGI utility library |
| | python-dotenv | 1.0.0 | Environment variable management |
| | SQLAlchemy | (required) | ORM for database operations |
| **AI/ML** | TensorFlow / Keras | 2.13+ | CNN model training and inference |
| | Tesseract / EasyOCR | Latest | Optical Character Recognition |
| | OpenCV | 4.8+ | Image preprocessing |
| | NumPy | 1.24.3 | Numerical computing |
| | Pandas | 2.0.3 | Data manipulation |
| | scikit-learn | 1.3.0 | ML utilities, metrics |
| | Pillow | Latest | Image file handling |
| **Database** | SQLite (dev) / PostgreSQL (prod) | — | Relational data storage |
| **DevOps** | Docker | Latest | Containerization |
| | Docker Compose | Latest | Multi-container orchestration |

### 6.2 Why These Technologies?

| Choice | Reason |
|---|---|
| **React 19** | Latest stable version with concurrent features, component reusability, and massive ecosystem |
| **Vite** | 10–100× faster than Webpack for dev builds; native ES module support; HMR (Hot Module Replacement) |
| **Tailwind CSS** | Rapid UI development without writing custom CSS; consistent design system; small production bundle via purging |
| **Flask** | Lightweight, flexible, and ideal for ML-serving backends (vs Django which is heavier). Easy to integrate with Python ML libraries |
| **TensorFlow/Keras** | Industry-standard for CNN image classification; pre-built layers for transfer learning; wide community support |
| **Tesseract OCR** | Most widely-used open-source OCR engine; supports 100+ languages; free alternative to cloud APIs |
| **SQLAlchemy** | Pythonic ORM; supports multiple databases; migration support via Alembic |

---

## 7. Frontend — Detailed Architecture

### 7.1 Technology Breakdown

| Technology | Role in Project |
|---|---|
| **React 19** | Core UI framework — renders all pages as reusable components |
| **Vite** | Development server with HMR (instant page reload on code change) and optimized production builds |
| **Tailwind CSS** | Utility classes for styling (e.g., `bg-blue-500`, `p-4`, `rounded-lg`) — no separate CSS files needed |
| **React Router DOM** | Maps URLs to page components (e.g., `/login` → LoginPage, `/upload` → UploadPage) |
| **Axios** | Makes HTTP requests to Flask backend; handles JWT token injection via interceptors |
| **Recharts** | Renders bar charts, pie charts, and line charts for verification result visualization |

### 7.2 Module Structure

```
frontend/
├── public/
│   └── vite.svg                    # App favicon
├── src/
│   ├── api/
│   │   └── axios.js                # Axios instance with base URL and JWT interceptors
│   │
│   ├── assets/
│   │   └── react.svg               # Static assets (logos, icons, images)
│   │
│   ├── components/
│   │   ├── FileUpload.jsx          # Document upload form with drag-and-drop
│   │   ├── Navbar.jsx              # (Required) Navigation bar with auth state
│   │   ├── ResultCard.jsx          # (Required) Displays single verification result
│   │   ├── ScoreChart.jsx          # (Required) Recharts-based score visualization
│   │   ├── DocumentHistory.jsx     # (Required) List of past verifications
│   │   ├── ProtectedRoute.jsx      # (Required) Route guard — redirects if not logged in
│   │   └── LoadingSpinner.jsx      # (Required) Loading state indicator
│   │
│   ├── pages/
│   │   ├── LoginPage.jsx           # (Required) User login form
│   │   ├── RegisterPage.jsx        # (Required) User registration form
│   │   ├── DashboardPage.jsx       # (Required) Main dashboard after login
│   │   ├── UploadPage.jsx          # (Required) Full upload interface
│   │   ├── ResultsPage.jsx         # (Required) Verification results with charts
│   │   └── HistoryPage.jsx         # (Required) Past verification history
│   │
│   ├── context/
│   │   └── AuthContext.jsx         # (Required) React Context for auth state management
│   │
│   ├── hooks/
│   │   ├── useAuth.js              # (Required) Custom hook for authentication logic
│   │   └── useApi.js               # (Required) Custom hook for API calls with loading/error states
│   │
│   ├── utils/
│   │   ├── constants.js            # (Required) App-wide constants (API routes, thresholds)
│   │   └── validators.js           # (Required) File type/size validation helpers
│   │
│   ├── App.jsx                     # Root component — sets up Router and routes
│   ├── App.css                     # Global styles
│   ├── main.jsx                    # React DOM entry point
│   └── index.css                   # Tailwind directives (@tailwind base/components/utilities)
│
├── .env.example                    # Environment variable template
├── index.html                      # HTML entry point
├── package.json                    # Dependencies and scripts
├── postcss.config.js               # PostCSS configuration for Tailwind
├── tailwind.config.js              # Tailwind CSS configuration
└── vite.config.js                  # Vite build configuration
```

### 7.3 Module Descriptions

#### `api/axios.js` — HTTP Client Configuration
- Creates a configured Axios instance with the backend base URL
- **Request Interceptor**: Automatically attaches JWT token from `localStorage` to every request's `Authorization` header
- **Response Interceptor**: Catches 401 errors (expired/invalid token) and redirects to login page
- All API calls throughout the app use this single instance for consistency

#### `components/FileUpload.jsx` — Document Upload Component
- Renders a file input with styled drag-and-drop area
- Validates file type (only PDF, JPEG, PNG allowed) and size (max 16MB)
- Shows upload progress indicator
- Sends file as `multipart/form-data` to `/api/upload` endpoint
- Displays success/error messages based on response

#### `components/ScoreChart.jsx` — Results Visualization (Required)
- Uses Recharts library to render:
  - **Bar Chart**: Individual scores for CNN, OCR, and DB verification
  - **Pie Chart**: Overall authenticity breakdown (authentic vs suspicious vs fake)
  - **Gauge**: Final combined authenticity percentage
- Color-coded: Green (≥90%), Orange (70–89%), Red (<70%)

#### `pages/` — Application Pages
- **LoginPage / RegisterPage**: Forms with validation, connect to auth API
- **DashboardPage**: Landing page after login showing recent verifications and quick upload
- **UploadPage**: Full document upload interface with file preview
- **ResultsPage**: Detailed verification results with three-part score breakdown and charts
- **HistoryPage**: Paginated list of all past verifications with search/filter

#### `context/AuthContext.jsx` — State Management (Required)
- Uses React Context API to manage global authentication state
- Stores: `user` object, `token`, `isAuthenticated` boolean
- Provides: `login()`, `logout()`, `register()` functions
- Persists token in `localStorage` for session survival across page refreshes

---

## 8. Backend — Detailed Architecture

### 8.1 Technology Breakdown

| Technology | Role in Project |
|---|---|
| **Flask** | Web framework — handles HTTP requests, routing, and response formatting |
| **Flask-CORS** | Enables cross-origin requests from React frontend (different port/domain) |
| **PyJWT** | Generates and validates JSON Web Tokens for user authentication |
| **Werkzeug** | Provides utilities like `secure_filename` for safe file handling |
| **python-dotenv** | Loads environment variables from `.env` file into `os.environ` |
| **SQLAlchemy** | ORM — maps Python classes to database tables; handles queries and migrations |
| **bcrypt/hashlib** | Password hashing for secure credential storage |

### 8.2 Module Structure

```
backend/
├── app.py                          # Application entry point and factory
├── config.py                       # (Required) Configuration classes (Dev/Prod/Test)
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # (Required) Ignore .env, uploads/, __pycache__/
│
├── blueprints/                     # (Required) Flask Blueprints for route modules
│   ├── __init__.py
│   ├── auth.py                     # Authentication routes (register, login, profile)
│   ├── upload.py                   # File upload routes (upload, list, delete)
│   └── validation.py               # Validation routes (validate, results, history)
│
├── models/                         # (Required) SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py                     # User model (id, email, password_hash, role)
│   ├── document.py                 # Document model (id, filename, user_id, upload_date)
│   └── result.py                   # Result model (id, document_id, scores, verdict)
│
├── services/                       # (Required) Business logic layer
│   ├── __init__.py
│   ├── auth_service.py             # User registration, login, token management
│   ├── upload_service.py           # File validation, storage, retrieval
│   └── validation_service.py       # Orchestrates AI pipeline (preprocess → CNN → OCR → DB)
│
├── middleware/                      # (Required) Request/response processing
│   ├── __init__.py
│   ├── auth_middleware.py           # JWT token verification decorator
│   └── error_handler.py            # Global exception handling
│
├── utils/                           # (Required) Utility functions
│   ├── __init__.py
│   ├── file_utils.py               # File type validation, secure naming, cleanup
│   └── response_utils.py           # Standardized JSON response formatting
│
├── uploads/                         # (Generated) Uploaded document storage
├── migrations/                      # (Generated) Database migration scripts
└── tests/                           # (Required) Unit and integration tests
    ├── __init__.py
    ├── test_auth.py
    ├── test_upload.py
    └── test_validation.py
```

### 8.3 Module Descriptions

#### `app.py` — Application Entry Point
- Creates the Flask application instance using the **Factory Pattern**
- Registers all Blueprints (auth, upload, validation)
- Initializes database connection (SQLAlchemy)
- Configures CORS, file upload limits, and secret keys
- Registers global error handlers
- Starts the development server on port 5000

#### `blueprints/auth.py` — Authentication Blueprint
| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | POST | Create new user account (email, password, name) |
| `/api/auth/login` | POST | Authenticate user, return JWT token |
| `/api/auth/profile` | GET | Get current user's profile (protected) |
| `/api/auth/logout` | POST | Invalidate current token |

- Passwords are hashed using bcrypt before storage
- JWT tokens contain user ID and role, expire after 24 hours
- Protected routes require valid `Authorization: Bearer <token>` header

#### `blueprints/upload.py` — File Upload Blueprint
| Endpoint | Method | Description |
|---|---|---|
| `/api/upload` | POST | Upload a document file for validation |
| `/api/upload/list` | GET | List user's uploaded documents |
| `/api/upload/<id>` | DELETE | Delete an uploaded document |

- Validates file type against whitelist: `pdf`, `jpg`, `jpeg`, `png`
- Limits file size to 16MB
- Uses `secure_filename()` to prevent path traversal attacks
- Stores file with a unique UUID-based name to prevent collisions

#### `blueprints/validation.py` — Validation Blueprint
| Endpoint | Method | Description |
|---|---|---|
| `/api/validate/<doc_id>` | POST | Trigger AI validation on an uploaded document |
| `/api/results/<doc_id>` | GET | Get validation results for a document |
| `/api/history` | GET | Get all validation history for current user |

- Calls `validation_service.py` which orchestrates the full AI pipeline
- Stores results in the database for future retrieval
- Returns detailed score breakdown (CNN score, OCR confidence, DB match score, final verdict)

#### `services/validation_service.py` — AI Pipeline Orchestrator
This is the **core business logic** that ties everything together:

```
Input: document file path
    │
    ├── 1. Call preprocessor (resize, normalize)
    ├── 2. Call CNN model → get visual_score (0.0 to 1.0)
    ├── 3. Call OCR engine → get extracted_text (dict of fields)
    ├── 4. Query DB with extracted fields → get match_score (0.0 to 1.0)
    ├── 5. Calculate final_score = visual×0.4 + ocr_conf×0.2 + match×0.4
    ├── 6. Determine verdict based on threshold
    └── 7. Return complete result object

Output: {
    "visual_score": 0.85,
    "ocr_confidence": 0.92,
    "db_match_score": 0.60,
    "final_score": 0.774,
    "verdict": "SUSPICIOUS",
    "extracted_fields": {...},
    "field_matches": {...}
}
```

#### `models/` — Database Models

**User Model:**
| Field | Type | Description |
|---|---|---|
| id | Integer (PK) | Auto-increment primary key |
| email | String (unique) | User's email address |
| password_hash | String | bcrypt-hashed password |
| name | String | User's full name |
| role | String | "admin" or "user" |
| created_at | DateTime | Account creation timestamp |

**Document Model:**
| Field | Type | Description |
|---|---|---|
| id | Integer (PK) | Auto-increment primary key |
| filename | String | Original file name |
| stored_name | String | UUID-based stored file name |
| file_type | String | "pdf", "jpg", "png" |
| user_id | Integer (FK) | Reference to User |
| uploaded_at | DateTime | Upload timestamp |

**Result Model:**
| Field | Type | Description |
|---|---|---|
| id | Integer (PK) | Auto-increment primary key |
| document_id | Integer (FK) | Reference to Document |
| cnn_score | Float | Visual analysis score (0–1) |
| ocr_confidence | Float | OCR extraction confidence (0–1) |
| db_match_score | Float | Database match score (0–1) |
| final_score | Float | Weighted combined score (0–1) |
| verdict | String | "AUTHENTIC", "SUSPICIOUS", or "FAKE" |
| extracted_data | JSON | OCR-extracted text fields |
| field_matches | JSON | Per-field match results |
| validated_at | DateTime | Validation timestamp |

#### `middleware/auth_middleware.py` — JWT Protection
- Provides a `@token_required` decorator for protected routes
- Extracts JWT from `Authorization` header
- Decodes and validates the token using the secret key
- Attaches the `current_user` object to the request context
- Returns 401 if token is missing, expired, or invalid

---

## 9. AI Model — Detailed Architecture

### 9.1 Technology Breakdown

| Technology | Role in Project |
|---|---|
| **TensorFlow / Keras** | Deep learning framework for building and training the CNN model |
| **OpenCV (cv2)** | Image preprocessing — resizing, color conversion, noise reduction |
| **Tesseract OCR / EasyOCR** | Extracts text from document images |
| **NumPy** | Numerical operations on image arrays and score calculations |
| **Pandas** | Loading and manipulating training datasets and database records |
| **scikit-learn** | Model evaluation metrics (accuracy, precision, recall, F1-score) |
| **Pillow (PIL)** | Image file format handling (open, convert, save) |

### 9.2 Module Structure

```
ai_model/
├── model.py                        # Main DocumentValidator class (entry point)
├── requirements.txt                # AI/ML Python dependencies
│
├── preprocessing/                   # (Required) Image preprocessing pipeline
│   ├── __init__.py
│   ├── image_processor.py          # Resize, normalize, denoise, grayscale
│   └── augmentation.py             # Data augmentation for training (rotation, flip, noise)
│
├── cnn/                             # (Required) Convolutional Neural Network
│   ├── __init__.py
│   ├── architecture.py             # CNN model definition (layers, activation functions)
│   ├── train.py                    # Training script with train/validation split
│   ├── predict.py                  # Inference — load model and predict on new image
│   └── evaluate.py                 # Model evaluation (accuracy, confusion matrix, ROC)
│
├── ocr/                             # (Required) Optical Character Recognition
│   ├── __init__.py
│   ├── text_extractor.py           # OCR engine wrapper (Tesseract or EasyOCR)
│   ├── field_parser.py             # Parse raw OCR text into structured fields
│   └── confidence.py               # Calculate OCR confidence scores
│
├── verification/                    # (Required) Database cross-verification
│   ├── __init__.py
│   ├── db_matcher.py               # Compare extracted fields against DB records
│   └── score_calculator.py         # Combine all scores into final verdict
│
├── models/                          # (Generated) Saved model files
│   └── document_cnn_v1.h5         # Trained CNN model weights
│
├── data/                            # Training data directory
│   ├── real/                       # Genuine document images
│   ├── fake/                       # Forged document images
│   └── labels.csv                  # Image labels (filename, class)
│
└── tests/                           # (Required) Model tests
    ├── test_preprocessing.py
    ├── test_cnn.py
    └── test_ocr.py
```

### 9.3 Module Descriptions

#### `preprocessing/image_processor.py` — Image Preprocessing

Takes the raw uploaded image and prepares it for AI analysis:

| Step | Operation | Purpose |
|---|---|---|
| 1 | **Read Image** | Load image file using OpenCV or Pillow |
| 2 | **Resize** | Standardize to 224×224 pixels (CNN input size) |
| 3 | **Color Conversion** | Convert to RGB (for CNN) or Grayscale (for OCR) |
| 4 | **Normalize** | Scale pixel values from 0–255 to 0.0–1.0 |
| 5 | **Denoise** | Apply Gaussian blur or bilateral filter to reduce noise |
| 6 | **To Tensor** | Convert to NumPy array shaped (1, 224, 224, 3) for CNN input |

#### `cnn/architecture.py` — CNN Model Definition

The CNN architecture for document classification:

```
Input Layer (224 × 224 × 3)
        ↓
Conv2D (32 filters, 3×3) → ReLU → MaxPool (2×2)
        ↓
Conv2D (64 filters, 3×3) → ReLU → MaxPool (2×2)
        ↓
Conv2D (128 filters, 3×3) → ReLU → MaxPool (2×2)
        ↓
Conv2D (256 filters, 3×3) → ReLU → MaxPool (2×2)
        ↓
Flatten
        ↓
Dense (512) → ReLU → Dropout (0.5)
        ↓
Dense (256) → ReLU → Dropout (0.3)
        ↓
Dense (1) → Sigmoid → Output (0.0 to 1.0)
```

| Layer Type | What It Does |
|---|---|
| **Conv2D** | Slides small filters across the image to detect patterns (edges, shapes, textures) |
| **ReLU** | Activation function — introduces non-linearity so the model can learn complex patterns |
| **MaxPool** | Reduces spatial dimensions by keeping only the strongest signals — speeds up training |
| **Flatten** | Converts 2D feature maps into a 1D vector for the fully connected layers |
| **Dense** | Fully connected layers that make the final classification decision |
| **Dropout** | Randomly disables neurons during training to prevent overfitting |
| **Sigmoid** | Outputs a probability between 0 (fake) and 1 (real) |

#### `cnn/train.py` — Model Training

Training process:
1. **Load Dataset**: Read images from `data/real/` and `data/fake/` directories
2. **Augment Data**: Apply random rotations, flips, zoom, and brightness changes to increase dataset size
3. **Split Data**: 80% training, 10% validation, 10% testing
4. **Compile Model**: Adam optimizer, binary cross-entropy loss
5. **Train**: Run for 50–100 epochs with early stopping (stop if validation loss doesn't improve for 10 epochs)
6. **Save Model**: Export trained weights to `models/document_cnn_v1.h5`

#### `ocr/text_extractor.py` — OCR Engine

Uses Tesseract OCR or EasyOCR to extract text from document images:

```
Document Image → OCR Engine → Raw Text → Field Parser → Structured Data
```

**Example Output:**
```
Input: marksheet.jpg

Raw OCR Output:
"Mumbai University\nName: Rahul Sharma\nRoll No: 2022CSE1045\nCGPA: 8.5\nYear: 2024"

Parsed Output:
{
    "institution": "Mumbai University",
    "name": "Rahul Sharma",
    "roll_number": "2022CSE1045",
    "cgpa": "8.5",
    "year": "2024"
}
```

#### `ocr/field_parser.py` — Text Field Extraction
- Uses **regular expressions** and **keyword matching** to identify specific fields from raw OCR text
- Handles variations in field labels (e.g., "Name:", "Student Name:", "Candidate Name:")
- Returns confidence score for each extracted field based on OCR engine's character-level confidence

#### `verification/db_matcher.py` — Database Cross-Verification
- Takes the extracted fields and queries the trusted database
- Compares each field using **fuzzy string matching** (to handle minor OCR errors)
- Returns a per-field match result:

```
{
    "name": {"extracted": "Rahul Sharma", "db_value": "Rahul Sharma", "match": true, "confidence": 1.0},
    "roll_number": {"extracted": "2022CSE1045", "db_value": "2022CSE1045", "match": true, "confidence": 1.0},
    "cgpa": {"extracted": "8.5", "db_value": "7.2", "match": false, "confidence": 0.0}
}
```

#### `verification/score_calculator.py` — Final Scoring

Combines all three verification scores into a single verdict:

```
Final Score = (CNN Visual Score × 0.4) + (OCR Confidence × 0.2) + (DB Match Score × 0.4)

Verdict Thresholds:
  ≥ 0.90 → "AUTHENTIC"     (Green — document is genuine)
  ≥ 0.70 → "SUSPICIOUS"    (Orange — requires manual review)
  < 0.70 → "FAKE"          (Red — document is likely forged)
```

---

## 10. Database Design

### 10.1 Entity-Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    USERS     │       │    DOCUMENTS     │       │    RESULTS      │
├──────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (PK)      │──1:N──│ id (PK)          │──1:1──│ id (PK)         │
│ email        │       │ filename         │       │ document_id (FK)│
│ password_hash│       │ stored_name      │       │ cnn_score       │
│ name         │       │ file_type        │       │ ocr_confidence  │
│ role         │       │ user_id (FK)     │       │ db_match_score  │
│ created_at   │       │ uploaded_at      │       │ final_score     │
└──────────────┘       └──────────────────┘       │ verdict         │
                                                   │ extracted_data  │
                                                   │ field_matches   │
                                                   │ validated_at    │
                                                   └─────────────────┘

┌──────────────────────┐
│   TRUSTED_RECORDS    │
├──────────────────────┤
│ id (PK)              │
│ institution          │   (Pre-loaded trusted data for
│ record_type          │    cross-verification)
│ identifier           │
│ data (JSON)          │
│ created_at           │
└──────────────────────┘
```

### 10.2 Relationships

- **Users → Documents**: One-to-Many (a user can upload multiple documents)
- **Documents → Results**: One-to-One (each document has one validation result)
- **Trusted_Records**: Standalone table with institutional data for verification

---

## 11. API Specification

### 11.1 Complete API Endpoints

| # | Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|---|
| 1 | POST | `/api/auth/register` | No | `{email, password, name}` | `{user, token}` |
| 2 | POST | `/api/auth/login` | No | `{email, password}` | `{user, token}` |
| 3 | GET | `/api/auth/profile` | Yes | — | `{user}` |
| 4 | POST | `/api/upload` | Yes | `multipart/form-data (file)` | `{document_id, filename}` |
| 5 | GET | `/api/upload/list` | Yes | — | `{documents: [...]}` |
| 6 | DELETE | `/api/upload/<id>` | Yes | — | `{message}` |
| 7 | POST | `/api/validate/<doc_id>` | Yes | — | `{result}` |
| 8 | GET | `/api/results/<doc_id>` | Yes | — | `{result with scores}` |
| 9 | GET | `/api/history` | Yes | `?page=1&per_page=10` | `{results: [...], total}` |
| 10 | GET | `/api/health` | No | — | `{status: "healthy"}` |

### 11.2 Response Format (Standard)

All API responses follow this structure:

```json
// Success
{
    "success": true,
    "data": { ... },
    "message": "Operation completed successfully"
}

// Error
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "File type not supported. Allowed: pdf, jpg, png"
    }
}
```

---

## 12. Security Architecture

| Concern | Solution |
|---|---|
| **Authentication** | JWT tokens with 24-hour expiry, stored in `localStorage` |
| **Password Storage** | bcrypt hashing with salt (never store plain text) |
| **File Upload Safety** | `secure_filename()` + file type whitelist + size limit (16MB) |
| **CORS** | Flask-CORS configured to allow only the frontend origin |
| **Secret Management** | `.env` file for secrets, never committed to Git |
| **SQL Injection** | SQLAlchemy ORM with parameterized queries (no raw SQL) |
| **XSS Protection** | React auto-escapes rendered content by default |
| **Rate Limiting** | (Recommended) Flask-Limiter to prevent abuse |

---

## 13. Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Frontend   │  │   Backend    │  │  Database   │  │
│  │  Container  │  │  Container   │  │  Container  │  │
│  │             │  │              │  │             │  │
│  │  Nginx      │  │  Flask +     │  │  PostgreSQL │  │
│  │  (serves    │  │  Gunicorn    │  │             │  │
│  │   React     │  │  + AI Model  │  │             │  │
│  │   build)    │  │              │  │             │  │
│  │             │  │              │  │             │  │
│  │  Port 80    │  │  Port 5000   │  │  Port 5432  │  │
│  └─────────────┘  └──────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
```

| Component | Dev Environment | Production Environment |
|---|---|---|
| Frontend | `npm run dev` (Vite, port 5173) | Nginx serving static build |
| Backend | `python app.py` (Flask dev server, port 5000) | Gunicorn WSGI server |
| Database | SQLite (file-based, zero config) | PostgreSQL (containerized) |
| AI Model | Loaded into Flask process | Same, or separate inference microservice |

---

## 14. Future Scope

| Enhancement | Description |
|---|---|
| **Multi-Document Support** | Support additional document types (Aadhaar, PAN, Passport, Driving License) with type-specific CNN models |
| **Transfer Learning** | Use pre-trained models (ResNet, VGG16) as base and fine-tune on document-specific data for better accuracy with smaller datasets |
| **Cloud OCR Integration** | Option to use Google Vision API or AWS Textract for higher OCR accuracy |
| **Blockchain Verification** | Store document hashes on a blockchain for tamper-proof verification records |
| **Batch Processing** | Allow uploading multiple documents at once with a queue-based processing system |
| **Admin Dashboard** | Analytics page showing total verifications, fake detection rate, top institutions |
| **API Access** | Provide API keys for third-party institutions to integrate verification into their systems |
| **Mobile App** | React Native mobile application for on-the-go document scanning and verification |

---

*Document prepared: February 22, 2026*
*Project: Document-Validator — AI-Powered Document Authenticity Verification System*
