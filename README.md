# VeriAcd (Document-Validator)

**Project Name:** VeriAcd  
**Team Name:** Error-404  
**Location:** Pune, MH  
**Contact:** 9322942240 | tukaramchate397@gmail.com  

A full-stack AI-powered educational document validation system that verifies document authenticity using Visual Analysis (CNN), OCR text extraction (Gemini 1.5), and database cross-verification.

## Overview

Final year project that combines AI-based document analysis with database verification. The system processes uploaded educational certificates and marksheets through a multi-stage pipeline — visual authenticity checks, AI OCR text extraction, and fuzzy matching against trusted institution records — to produce a confidence score and verdict.

## Project Structure (Microservices Architecture)

```
Document-Validator/
├── backend/                    # Flask REST API (Core Business Logic)
│   ├── app.py                  # Application factory
│   ├── blueprints/             # Routes (auth, validation, institution, admin)
│   ├── models/                 # SQLAlchemy models (User, Document, Result)
│   └── services/               # Pipeline orchestration & DB matching
├── frontend/                   # React + Vite SPA (User Interface)
│   └── src/                    # Pages, Contexts, Hooks, and API wrappers
├── AI Model/                   # AI Microservices
│   ├── OCR_api/                # FastAPI service (Gemini Vision OCR)
│   ├── forge_detection/        # FastAPI service (CNN visual forgery detection)
│   └── model.py                # Shared AI pipeline interfaces
└── Documentation/              # Project diagrams & run instructions
```

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS v4, Recharts, Axios |
| **Backend** | Flask, Flask-SQLAlchemy, Flask-Migrate, PyJWT, psycopg |
| **AI/ML** | FastAPI, Google Generative AI (Gemini Flash), OpenCV, TensorFlow/Keras |
| **Database** | PostgreSQL |
| **Testing** | pytest, pytest-cov |

## Features

- **🔐 Security-First Authentication** — JWT-based access with token blacklisting, fail-fast SECRETS validation, and strict route guards.
- **🏢 Institution Workflows** — Institutions can register (pending Admin approval) and bulk-upload trusted graduate records (max 500/request).
- **📤 Document Verification** — Drag-and-drop file uploads with dynamic status polling and PDF report generation.
- **🧠 3-Stage AI Pipeline** — Coordinates visual forgery analysis, Gemini-driven OCR data extraction, and PostgreSQL fuzzy matching.
- **🛡️ Admin Dashboard** — System-wide analytics, recent activity logs, and pending institution approval management.

## Environment Setup

You need to configure two `.env` files for the system to work.

### 1. Backend (`backend/.env`)
Must be created from `backend/.env.example`. *Note: The API will refuse to start if you use weak default secrets!*
```env
SECRET_KEY=generate_a_strong_random_secret_here
JWT_SECRET_KEY=generate_a_strong_random_jwt_secret_here
DATABASE_URL=postgresql+psycopg://postgres:yourpassword@localhost:5432/document_validator
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=16
```

### 2. OCR Service (`AI Model/OCR_api/.env`)
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

## Running the Project

The system requires **4 separate terminal windows** to run all microservices concurrently.

### 1. Backend API (Port 5000)
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 2. Frontend App (Port 5173)
```bash
cd frontend
npm install
npm run dev
```

### 3. AI OCR Service (Port 8001)
```bash
cd "AI Model\OCR_api"
..\..\backend\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8001
# (Note: Use --port 8001 without --reload if using Python 3.14 to avoid watchdog issues)
```

### 4. AI Forge Detection Service (Port 8002)
```bash
cd "AI Model\forge_detection"
..\..\backend\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8002
```

## How Validation Works

```
Upload → Preprocess → CNN Analysis → Gemini OCR → DB Fuzzy Match → Score & Verdict
                          (10%)          (40%)         (50%)
```

1. **User** uploads an educational certificate via the React frontend.
2. **Backend API** stores the file and dispatches async requests to the AI microservices.
3. **Forge API (Port 8002)** analyzes for visual tampering artifacts.
4. **OCR API (Port 8001)** sends the image to Gemini 1.5 Flash to extract structured JSON (Name, Roll No, Branch, CGPA).
5. **Backend Database** performs Levenshtein fuzzy matching on the extracted fields against trusted `InstitutionRecords`.
6. A weighted final score is calculated → verdict: **AUTHENTIC** (≥90%), **SUSPICIOUS** (≥70%), or **FAKE** (<70%).
7. The user can view a detailed breakdown and download a dynamically generated PDF report.

## License

See [LICENSE](LICENSE) file for details.
