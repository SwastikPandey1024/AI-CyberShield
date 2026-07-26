# AI CyberShield — Engineering Log

## Overview
This file chronicles all engineering decisions, architecture choices, and rationale behind the construction of the AI CyberShield platform. Every non‑trivial change that impacts the project structure, tooling, or development process is recorded here.

---

## Entry: 2026-07-26 — Project Bootstrap

### Change
Initialized the entire project structure.

### Rationale
- Established a clean, modular layout with separation of concerns (backend, ml, frontend, tests, docs, scripts, reports).
- Added placeholder `__init__.py` files in all Python packages to make them import‑ready.
- Configured a modern Python toolchain (`pyproject.toml` with Black, Ruff, mypy, pytest).
- Created a comprehensive `.gitignore` to prevent leaking artifacts, datasets, virtual environments, and IDE clutter.
- Added a `.vscode/settings.json` tailored for Python development with Black formatting and Ruff linting.
- All ML artifacts (models, scalers, encoders) are excluded from version control.
- Dataset directories (`raw/`, `processed/`) are ignored; only `.gitkeep` files are tracked.

### Files Affected
- `pyproject.toml`
- `.gitignore`
- `.vscode/settings.json`
- `README.md`
- `LICENSE`
- `requirements.txt`
- All `__init__.py` files under `backend/app/`, `ml/`, `tests/`
- `.gitkeep` files under `frontend/`, `datasets/`, `notebooks/`, `docs/`, `scripts/`, `docker/`, `.github/`

---

## Entry: 2026-07-26 — Data Science Reports Directory

### Change
Added `reports/data/` subtree with `profiling/`, `eda/`, and `validation/` subdirectories.

### Rationale
- Provides a dedicated home for profiling reports, EDA notebooks/figures, and data quality validation outputs.
- Prevents clutter in the root and keeps analytical artifacts separate from source code.
- `profiling/figures/feature_distributions/` allows for organized storage of per‑feature histograms and box plots.

### Files Affected
- `reports/data/profiling/.gitkeep`
- `reports/data/profiling/figures/feature_distributions/.gitkeep`
- `reports/data/eda/.gitkeep`
- `reports/data/validation/.gitkeep`

---

## Entry: 2026-07-26 — Dataset & ML Artifact Directory Expansion

### Change
- Added `datasets/raw/CICIDS2017/`, `datasets/processed/`, `datasets/external/` subdirectories.
- Added `ml/artifacts/models/` and `ml/artifacts/metadata/` subdirectories.
- Added `logs/` directory for application logs.
- Added `docs/decisions/` directory for Architecture Decision Records (ADRs).
- Created `.env.example` for environment variable documentation.

### Rationale
- **CICIDS2017 subdirectory**: The primary dataset deserves its own folder under `datasets/raw/` to keep multiple dataset sources organized.
- **Processed & external**: Separates cleaned training data from third-party datasets used for evaluation or augmentation.
- **models/ vs metadata/**: Physical model files (`.pkl`, `.joblib`, `.onnx`) should live separately from their evaluation metrics and config metadata to avoid confusion during inference.
- **logs/**: Centralized logging output directory; `.gitignore` already ignores all `.log` files but tracks the directory via `.gitkeep`.
- **docs/decisions/**: Architectural Decision Records (ADRs) are a standard practice for documenting design rationale. This directory will hold timestamped ADR files.
- **`.env.example`**: Provides a documented template for developers to configure local environment variables without hardcoding secrets.

### Files Affected
- `datasets/raw/CICIDS2017/.gitkeep`
- `datasets/processed/.gitkeep`
- `datasets/external/.gitkeep`
- `ml/artifacts/models/.gitkeep`
- `ml/artifacts/metadata/.gitkeep`
- `logs/.gitkeep`
- `docs/decisions/.gitkeep`
- `.env.example`

---

## Entry: 2026-07-26 — Documentation Restructure (ADR Migration)

### Change
- Removed `docs/decisions/` directory and migrated content to `docs/adr/` with standardized ADR numbering (0001-0004).
- Created ADR-0001 (project structure), ADR-0002 (YAML configuration), ADR-0003 (CICIDS2017 selection), ADR-0004 (profiling as a package).
- Moved `ANALYSIS.md` to `docs/research/cicids2017-analysis.md`.
- Created `docs/roadmap.md` as the authoritative status tracker for all phases.
- Updated `CHANGELOG.md` with [0.2.0] release entries.

### Rationale
- **ADR numbering**: Zero-padded sequential IDs (`0001`) are standard in ADR practice and sort correctly in filesystems.
- **ADR-0002**: The YAML migration is a real architectural decision from this project's history — replacing hardcoded configs with hierarchical YAML files.
- **ADR-0004**: Profiling was intentionally designed as a package (not a single module) to keep univariate, bivariate, missing, and report generation separate and testable.
- **ANALYSIS.md move**: Project analysis belongs under `docs/research/`, not the repo root.
- **roadmap.md**: Consolidates milestone tracking from informal conversation into a single authoritative file.

### Files Created
- `docs/adr/0001-project-structure.md`
- `docs/adr/0002-yaml-configuration.md`
- `docs/adr/0003-cicids2017-selection.md`
- `docs/adr/0004-profiling-as-a-package.md`
- `docs/roadmap.md`

### Files Deleted
- `docs/decisions/` (entire directory)
- `docs/decisions/.gitkeep`
- `docs/decisions/ADR-001-project-structure.md`

### Files Moved
- `ANALYSIS.md` → `docs/research/cicids2017-analysis.md`

### Files Modified
- `CHANGELOG.md` (added [0.2.0] section)
