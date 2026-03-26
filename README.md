# VeriAcd (Document-Validator)

VeriAcd is a full-stack educational document validation platform.
It verifies uploaded marksheets/certificates using:

- CNN-based visual forgery detection
- OCR plus field extraction (Gemini + fallback parser)
- trusted institutional record cross-checking

The system returns a final verdict and a downloadable PDF report.

## Current Architecture

The project runs as 3 services:

- Frontend (React + Vite): Port 5173
- Backend API (Flask): Port 5000
- AI Model Service (FastAPI): Port 8001

Reference diagram: `Documentation/ieee_architecture_diagram.mmd`

## Repository Structure

```text
Document-Validator/
|- frontend/                    # React app (UI)
|  |- src/
|  |- package.json
|
|- backend/                     # Flask API + business logic
|  |- app.py
|  |- blueprints/
|  |- models/
|  |- services/
|  |- requirements.txt
|  |- start_backend.ps1
|
|- AI Model/                    # FastAPI AI microservice
|  |- app/                      # API entrypoint: app.main:app
|  |- src/                      # CNN, OCR, pipeline logic
|  |- saved_models/
|  |- requirements.txt
|  |- start_ai_model.ps1
|
|- Documentation/
|  |- run.txt
|  |- ieee_architecture_diagram.mmd
|
`- README.md
```

## Tech Stack (Actual)

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite 7, Tailwind CSS 4, React Router 7, Axios, Recharts |
| Backend | Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-Limiter, PyJWT, psycopg |
| AI Service | FastAPI, Uvicorn, PyTorch, Torchvision, OpenCV, Pillow, pdf2image, Gemini API |
| Database | PostgreSQL |
| Testing | pytest, pytest-cov |

## Core Workflow (End-to-End)

1. User logs in from the frontend.
2. Frontend sends auth request to backend authentication service.
3. Backend validates JWT/token state and user role.
4. User uploads document from frontend.
5. Backend upload service validates file, stores it, and saves upload metadata.
6. User requests validation/report.
7. Backend validation service:
    - reads uploaded document metadata,
    - cross-checks institutional records,
    - calls AI pipeline (`/api/pipeline/full`).
8. AI pipeline runs:
    - CNN forgery detection,
    - OCR extraction (Gemini + fallback parser).
9. Backend stores final result and generates PDF report.
10. Frontend shows validation output and allows PDF download.

## Environment Configuration

Create and configure:

1. `backend/.env`
2. `AI Model/.env`

Typical backend keys include:

```env
SECRET_KEY=your_strong_secret
JWT_SECRET_KEY=your_strong_jwt_secret
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/document_validator
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=16
```

Typical AI Model key:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

## Run Instructions

Use 3 terminals.

### 1) AI Model Service (Port 8001)

```powershell
cd "AI Model"
.\start_ai_model.ps1
```

### 2) Backend API (Port 5000)

```powershell
cd backend
.\start_backend.ps1
```

### 3) Frontend (Port 5173)

```powershell
cd frontend
npm install
npm run dev
```

## Health and Access

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:5000/api/health`
- AI docs: `http://localhost:8001/docs`

## Notes

- Backend and AI service use separate Python environments.
- If frontend `npm run dev` fails, check Node version and reinstall dependencies.
- If OCR/extraction fails, verify AI service and `GEMINI_API_KEY`.

## License

See `LICENSE`.
