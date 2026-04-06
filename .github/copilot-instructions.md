# Document Validator Workspace Instructions

## Project Shape
This repository contains three services that should be treated as separate layers:
- `frontend/`: React 19 + Vite UI
- `backend/`: Flask API, business logic, database models, migrations, and background worker
- `AI Model/`: FastAPI AI microservice for OCR, CNN forgery detection, and pipeline orchestration

## Core Rules
- Keep changes focused to the layer that owns the behavior.
- Preserve the existing request/response contracts between frontend, backend, and AI service unless the user explicitly asks for a breaking change.
- Prefer minimal edits over broad refactors.
- Update tests and validation steps together with code changes.
- Do not introduce Redis or RabbitMQ for validation queueing; this project uses the database-backed job queue already in `backend/validation_worker.py`.

## Backend Changes
When changing backend behavior:
- Update blueprints, services, models, and migrations together when schema or contract changes are involved.
- Keep auth, upload, validation, institution, and admin logic aligned with existing route structure.
- Verify health and startup behavior through the Flask app and `/api/health`.
- Add or update pytest coverage for affected endpoints and service paths.

## AI Model Changes
When changing the AI service:
- Keep preprocessing, inference, and response shapes compatible with backend consumers.
- Treat `AI Model/app/main.py` as the service entrypoint and `AI Model/src/` as the main pipeline area.
- Verify model loading, pipeline execution, and `/health` behavior.
- Update or add tests for inference and parsing behavior when outputs change.

## Frontend Changes
When changing the UI:
- Keep the React + Vite structure simple and consistent with the existing routing and component layout.
- Preserve API integration contracts used by the frontend.
- Run lint and build checks for UI changes when practical.

## Validation Workflow
For cross-layer changes:
- Validate backend, AI service, and frontend in the same change set when the behavior spans multiple services.
- Start services using the repo scripts when possible: `backend/start_backend.ps1`, `AI Model/start_ai_model.ps1`, and `frontend/npm run dev`.
- Confirm health endpoints and the primary upload-to-validation flow before considering the change complete.

## Editing Expectations
- Prefer existing project patterns and naming over introducing new abstractions.
- Do not remove or rename public routes, files, or configuration keys without a clear reason.
- If a change touches a user flow such as upload, validation, auth, admin, or institution management, trace the full path through all affected layers before editing.

## Good Completion Standard
A change is complete when:
- The targeted behavior is implemented.
- Related tests or checks are updated.
- Cross-service impact has been reviewed.
- Any contract change is explicit and intentional.
