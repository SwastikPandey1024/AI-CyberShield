# 🔧 Development Guide

## Prerequisites

- Python 3.12+
- PostgreSQL 15+ (optional, SQLite for local development)
- Git
- Docker (recommended)
- VS Code (recommended)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-CyberShield.git
cd AI-CyberShield
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # Development tools (Black, Ruff)
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run the Application

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## Development Workflow

```
Requirement → Design → Implementation → Testing → Code Review → Documentation → Git Commit → Merge
```

Every feature should follow this lifecycle.

### 1. Create a Feature Branch

```bash
git checkout -b feat/your-feature-name
```

Branch naming convention:
- `feat/` — New features
- `fix/` — Bug fixes
- `refactor/` — Code restructuring
- `docs/` — Documentation updates
- `chore/` — Maintenance tasks

### 2. Implement Changes

- Follow the [coding standards](coding-standards.md)
- Write type hints and docstrings
- Keep functions focused and modular

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=ml tests/

# Run specific test file
pytest tests/test_api.py -v
```

### 4. Run Linters

```bash
# Format code
black .

# Sort imports
isort .

# Lint check
ruff check .

# Type check
mypy .
```

### 5. Commit Changes

Use conventional commits:

```bash
git commit -m "feat: add threat prediction endpoint"
git commit -m "fix: correct feature scaling in preprocessing"
git commit -m "docs: update API documentation"
git commit -m "refactor: extract prediction service from router"
```

### 6. Create a Pull Request

```bash
git push origin feat/your-feature-name
# Open a PR on GitHub
```

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configurations
├── test_api/            # API endpoint tests
├── test_services/       # Service layer tests
├── test_ml/             # ML pipeline tests
└── test_database/       # Database tests
```

### Writing Tests

```python
# tests/test_api/test_predict.py
import pytest
from httpx import AsyncClient

async def test_predict_endpoint(client: AsyncClient):
    response = await client.post("/api/v1/predict", json={
        "features": {...}
    })
    assert response.status_code == 200
    assert "prediction" in response.json()
```

### Test Coverage Requirements

- **Backend services**: 90%+ coverage
- **API endpoints**: 100% coverage for status codes
- **ML pipeline**: 80%+ coverage
- **Database operations**: 85%+ coverage

## Docker Workflow

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `backend` | 8000 | FastAPI application |
| `frontend` | 3000 | React dashboard |
| `database` | 5432 | PostgreSQL |

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

### Workflow: `ci.yml`

```yaml
Triggers: push to main, pull requests
Steps:
  1. Checkout code
  2. Set up Python 3.12
  3. Install dependencies
  4. Run linting (Black, Ruff, mypy)
  5. Run tests with pytest
  6. Check test coverage
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data.db` | Database connection string |
| `MODEL_PATH` | `./ml/artifacts/model.pkl` | Path to trained model |
| `SCALER_PATH` | `./ml/artifacts/scaler.pkl` | Path to fitted scaler |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

## Useful Commands

```bash
# Run development server
uvicorn backend.app.main:app --reload

# Run tests
pytest -v --tb=short

# Format code
black . && isort .

# Lint check
ruff check . --fix

# Type check
mypy backend/ ml/

# Build Docker images
docker-compose build

# View API docs
# Open http://localhost:8000/docs
