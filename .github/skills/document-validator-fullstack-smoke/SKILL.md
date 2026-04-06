---
name: document-validator-fullstack-smoke
description: 'Run full-stack smoke validation for this project. Use when verifying frontend, backend, and AI model integration after changes.'
argument-hint: 'What changed and which user flow to validate (upload, validation, auth, admin, institution)'
---

# Document Validator Full-Stack Smoke

## When to Use
- After cross-layer changes.
- Before merging high-impact features.
- When diagnosing integration regressions.

## Procedure
1. Start required services
- Start backend, AI model service, and frontend in their project folders.

2. Verify health and connectivity
- Confirm each service starts without startup errors.
- Confirm frontend can call backend and backend can call AI service.

3. Execute critical user flows
- Validate auth flow.
- Validate document upload and validation flow.
- Validate role-based views (user/institution/admin when applicable).

4. Check error paths
- Submit invalid input and confirm safe error responses.

5. Run targeted tests
- Run backend and frontend tests related to changed flows.

6. Report results
- Summarize pass/fail by flow and note follow-up fixes.

## Quality Gates
- All required services boot successfully.
- Core end-to-end flow works for changed feature area.
- Failures include actionable root-cause notes.

## Completion Criteria
- Smoke checks executed across frontend, backend, and AI model.
- Critical flow outcomes documented.
- Regressions are identified with next actions.
