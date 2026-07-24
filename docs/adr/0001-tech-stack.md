# ADR 0001: Technology Stack Selection

**Status:** Accepted
**Date:** 2024
**Deciders:** Engineering Team

---

## Context

The project requires a technology stack that supports:
- High-performance REST API with automatic documentation
- Machine learning model training and inference
- Relational database storage for prediction history
- Interactive dashboard for data visualization
- Containerized deployment for reproducibility

## Decision

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | FastAPI | ≥ 0.110 |
| **ML Framework** | scikit-learn + XGBoost | ≥ 1.4 / ≥ 2.0 |
| **Database** | PostgreSQL + SQLAlchemy | 15+ / 2.0+ |
| **Frontend** | React + TypeScript + Tailwind CSS | Latest |
| **Visualization** | Recharts | Latest |
| **Containerization** | Docker + Docker Compose | Latest |
| **Testing** | Pytest | ≥ 8.0 |
| **Linting** | Black + Ruff + isort + mypy | Latest |

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|----------------------|
| **Flask** | Lacks native async support; requires manual OpenAPI setup |
| **Django REST Framework** | Too heavy for an ML service; steep learning curve |
| **TensorFlow / PyTorch** | Overkill for tabular network flow data; XGBoost performs better |
| **MongoDB** | Relational data with strict schema fits PostgreSQL better |
| **Streamlit** | Good for demos but lacks flexibility for production dashboards |

## Consequences

### Positive
- FastAPI provides automatic OpenAPI/Swagger documentation
- XGBoost gives state-of-the-art performance on tabular data
- PostgreSQL ensures ACID compliance for audit trails
- Docker ensures reproducible environments across team members

### Negative
- Team must learn FastAPI patterns (dependency injection, Pydantic)
- XGBoost training can be memory-intensive on large datasets
- PostgreSQL requires connection pooling configuration for production

### Neutral
- Migrating to a different ML framework later is possible via scikit-learn API
- Frontend can be replaced or upgraded without affecting backend
