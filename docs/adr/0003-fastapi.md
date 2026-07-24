# ADR 0003: FastAPI as Backend Framework

**Status:** Accepted
**Date:** 2026
**Deciders:** Engineering Team

---

## Context

The backend service must:
- Serve ML predictions via REST API
- Handle concurrent requests efficiently
- Provide automatic API documentation
- Support request validation with clear error messages
- Integrate with SQLAlchemy for database operations
- Be maintainable and well-structured for future extensions

## Decision

**Framework:** FastAPI (Python 3.12+)

### Key Features Used
- **Starlette** for ASGI server and async support
- **Pydantic** for request/response validation
- **Dependency Injection** for database sessions and model loading
- **Auto-generated OpenAPI docs** at `/docs` and `/redoc`
- **Background tasks** for non-blocking operations

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| **Flask** | Simple, widely known | No native async; manual OpenAPI; older ecosystem |
| **Django REST Framework** | Full-featured, ORM built-in | Heavy; opinionated; steeper learning curve |
| **Starlette** | Lightweight, fast | Too low-level; requires manual structure |

## Consequences

### Positive
- Automatic interactive API documentation (Swagger UI + ReDoc)
- Native async support for concurrent request handling
- Pydantic validation ensures data integrity with clear error messages
- Dependency injection makes testing easy (swap dependencies)
- High performance (on par with Node.js and Go)

### Negative
- FastAPI is newer; smaller community than Flask/Django
- Async SQLAlchemy requires additional setup
- Dependency injection pattern takes time to learn

### Structure
```
backend/app/
├── api/        # Route handlers (thin layer)
├── services/   # Business logic
├── models/     # SQLAlchemy ORM models
├── schemas/    # Pydantic models
├── core/       # Configuration
├── database/   # Session management
└── utils/      # Helper functions
