# Changelog

All notable changes to AI CyberShield will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2024

### Added

- Project scaffold with modular architecture (`backend/`, `ml/`, `frontend/`)
- Python 3.12 development environment with Black, Ruff, isort, and pytest
- Pydantic-settings configuration loader (`backend/app/config.py`)
- Configuration files for application, model, training, and logging (`configs/`)
- Comprehensive `.gitignore` with Python, ML, dataset, and IDE rules
- Environment template (`.env.example`)
- Dataset directory structure (`raw/`, `processed/`, `external/`)
- Structured logging package (`backend/app/logging/`)
- Database migrations scaffold (`backend/migrations/`)
- GitHub templates for issues, pull requests, and code owners
- Architecture Decision Records (ADR): tech stack, dataset, FastAPI, XGBoost
- Documentation: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- Documentation: `docs/architecture.md`, `docs/development-guide.md`, `docs/coding-standards.md`, `docs/roadmap.md`
- Documentation: `docs/PRD.md`, `docs/BRD.md`
- API documentation scaffold (`docs/api/`)
- Experiment tracking scaffold (`experiments/`)
- VS Code workspace settings and recommended extensions
- Assets folder for images, diagrams, screenshots, and logo
- Model registry structure (`ml/artifacts/models/`, `ml/artifacts/metadata/`)
- GitHub labels configuration (`.github/labels.yml`)
- Docker configuration placeholder (`docker/`)
- CI/CD scaffold (`.github/`)
- `Makefile` with common development commands
- `pyproject.toml` with build and tool configuration
