# ADR-0001: Project Structure & Architecture

## Status
Accepted

## Date
2026-07-26

## Context
AI CyberShield requires a modular, maintainable, and scalable project structure that separates concerns across backend (FastAPI), machine learning pipeline, and frontend (React). The initial project skeleton needed to support independent development of each layer while maintaining clear boundaries.

## Decision
Adopt a layered monorepo structure:

```
backend/app/
├── api/          — Route handlers (controllers)
├── core/          — Configuration, settings, security
├── models/        — SQLAlchemy ORM models
├── services/      — Business logic layer
├── schemas/       — Pydantic request/response schemas
├── database/      — Connection, session management
└── utils/         — Shared utilities

ml/
├── preprocessing/ — Feature engineering, cleaning
├── training/      — Model training & hyperparameter tuning
├── inference/     — Prediction serving
├── evaluation/    — Metrics & validation
└── artifacts/     — Serialized models + metadata
```

FastAPI was chosen for the backend due to its automatic OpenAPI documentation, Pydantic integration, and async support. The ML pipeline is isolated as a separate top-level package to prevent coupling between model logic and API routing.

## Alternatives Considered
- **Single monolithic backend**: Rejected — would couple ML logic with API routes, making testing and iteration on models harder.
- **Django**: Rejected — heavier than needed for a prediction API; FastAPI's async performance is better suited for real-time inference.
- **Flat structure**: Rejected — would become unmanageable as the codebase grows.

## Consequences
- Clear separation enables independent development and testing of each layer.
- New developers can quickly locate relevant code.
- ML pipeline is isolated from API logic, preventing accidental coupling during model iteration.
