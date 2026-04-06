---
name: document-validator-ai-model-update
description: 'Update AI model workflows for this project. Use when changing data prep, training, model artifacts, inference API behavior, or AI-model tests.'
argument-hint: 'Model change objective (training, inference, dataset, threshold, or endpoint behavior)'
---

# Document Validator AI Model Update

## When to Use
- Modify model training or inference behavior.
- Adjust preprocessing, dataset handling, or saved model usage.
- Align AI API output with backend expectations.

## Procedure
1. Define change scope
- Specify whether the change is training-time, inference-time, or both.

2. Trace pipeline impact
- Review AI app entrypoints, pipeline modules, CNN or OCR components, and model artifacts.

3. Implement the change
- Update processing logic, model loading, or prediction output shape.

4. Validate compatibility
- Ensure AI endpoint payloads and outputs remain compatible with backend consumers.

5. Update tests or notebooks
- Add or adjust tests and reproducible evaluation steps.

6. Run verification
- Execute relevant checks to confirm inference behavior and error handling.

## Quality Gates
- Inference output is deterministic for known test inputs.
- Contract changes are explicit and documented.
- Model file paths and environment assumptions are valid.

## Completion Criteria
- AI pipeline change is implemented and scoped.
- Integration contract implications are handled.
- Validation evidence exists (tests or reproducible run steps).
