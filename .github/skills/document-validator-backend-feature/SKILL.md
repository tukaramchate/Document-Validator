---
name: document-validator-backend-feature
description: 'Implement or modify backend API features in this project. Use when adding Flask blueprints, service logic, database models, migrations, and backend tests.'
argument-hint: 'Feature goal, endpoint(s), and affected backend modules'
---

# Document Validator Backend Feature

## When to Use
- Add or update backend endpoints.
- Extend validation, upload, auth, or institution workflows.
- Keep blueprint, service, model, and tests aligned.

## Procedure
1. Locate affected modules
- Identify relevant files in backend blueprints, services, models, and tests.

2. Implement API and business logic
- Update route handlers in blueprints.
- Add or modify service-layer methods.

3. Update data model and migration needs
- If schema changes are needed, update model definitions and migration plan.

4. Keep contracts consistent
- Ensure request and response shapes remain consistent across endpoints.

5. Add or update tests
- Add focused tests for success and failure paths in backend tests.

6. Validate
- Run backend tests and fix regressions caused by the change.

## Quality Gates
- Endpoint behavior matches requirements.
- Service logic handles validation and error paths.
- Tests cover core behavior and edge cases.
- No unrelated refactors are mixed in.

## Completion Criteria
- Code changes are implemented in route and service layers.
- Required model/migration updates are included.
- Backend tests for changed behavior are passing.
