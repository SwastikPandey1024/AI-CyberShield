# 📐 Coding Standards

## General Principles

- **Readability over cleverness** — Write code that is easy to understand
- **Consistency** — Follow established patterns throughout the codebase
- **Defense in depth** — Validate inputs, handle errors, log appropriately
- **Modularity** — Small, focused functions and classes with single responsibilities
- **Testability** — Write code that can be easily tested in isolation

## Python Standards

### Version
- Python 3.12+
- Use new-style type hints and features

### Formatting (Black)

All code is formatted with **Black** at 88 characters per line:

```python
# ✅ Good — Black-formatted
def predict_threat(
    features: pd.DataFrame,
    model: BaseEstimator,
    threshold: float = 0.5,
) -> PredictionResult:
    probabilities = model.predict_proba(features)
    return classify_prediction(probabilities, threshold)


# ❌ Bad — Non-compliant formatting
def predict_threat(features, model, threshold=0.5):
    probabilities=model.predict_proba(features)
    return classify_prediction(probabilities,threshold)
```

### Linting (Ruff)

Ruff enforces Python best practices. Key rules:

| Rule | Description |
|------|-------------|
| `E` | PEP 8 errors |
| `F` | Pyflakes (logic errors) |
| `I` | isort (import order) |
| `W` | PEP 8 warnings |
| `UP` | Pyupgrade (modern syntax) |
| `N` | Naming conventions |
| `D` | Docstring conventions |

### Import Ordering (isort)

```python
# ✅ Correct order
# 1. Standard library
import json
import logging
from typing import Optional

# 2. Third-party
import numpy as np
import pandas as pd
from fastapi import APIRouter
from sqlalchemy.orm import Session

# 3. Local application
from backend.app.core.config import settings
from backend.app.models.prediction import Prediction
```

### Type Hints

Always use type hints for function signatures:

```python
# ✅ Good
def preprocess_data(
    df: pd.DataFrame,
    scaler: StandardScaler,
    feature_columns: list[str],
) -> pd.DataFrame:
    ...


# ❌ Bad
def preprocess_data(df, scaler, feature_columns):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def predict_from_features(
    features: dict[str, float],
    model: BaseEstimator,
    threshold: float = 0.5,
) -> PredictionResult:
    """Classify network flow features as benign or malicious.

    Args:
        features: Dictionary of network flow feature values.
        model: Trained classifier with predict_proba method.
        threshold: Confidence threshold for positive classification.

    Returns:
        PredictionResult containing predicted class and confidence.

    Raises:
        ValueError: If features contain missing or invalid values.
        ModelNotLoadedError: If the model is not loaded.
    """
    ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Packages | `snake_case` | `preprocessing`, `training` |
| Modules | `snake_case` | `data_loader.py`, `model_trainer.py` |
| Classes | `PascalCase` | `DataPreprocessor`, `ModelTrainer` |
| Functions | `snake_case` | `predict_threat()`, `load_model()` |
| Variables | `snake_case` | `feature_columns`, `prediction_result` |
| Constants | `UPPER_CASE` | `DEFAULT_THRESHOLD`, `MODEL_VERSION` |
| Private | `_prefix` | `_validate_features()`, `_cached_model` |

### Error Handling

```python
# ✅ Good — Specific exception handling
try:
    result = model.predict(features)
except ModelNotLoadedError:
    logger.error("Model is not loaded, reloading...")
    model = load_model()
    result = model.predict(features)
except ValueError as e:
    logger.error(f"Invalid features: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected prediction error: {e}")
    raise PredictionError("Prediction failed") from e


# ❌ Bad — Bare except
try:
    result = model.predict(features)
except:
    pass
```

## Project Structure Standards

### Backend Layering

```
Route Layer (FastAPI routers)
    → Service Layer (business logic)
        → Repository Layer (database access)
            → ML Inference Layer (model + preprocessing)
```

Each layer should only interact with the layer immediately below it.

### Module Responsibilities

| Module | Responsibility | Should NOT |
|--------|---------------|-----------|
| `api/` | HTTP route handlers, request parsing | Access database directly |
| `services/` | Business logic, orchestration | Import FastAPI objects |
| `models/` | SQLAlchemy ORM models | Contain business logic |
| `schemas/` | Pydantic request/response models | Reference ORM models directly |
| `database/` | Connection management, sessions | Contain business logic |
| `core/` | Configuration, constants | Import from other modules |
| `utils/` | Helper functions | Depend on app-specific modules |

## Testing Standards

### Test File Naming

- `test_<module_name>.py` for unit tests
- `test_<feature>.py` for integration tests

### Test Structure

```python
# Arrange: Set up test data
features = get_sample_features()
expected_class = "Benign"

# Act: Execute the function
result = predictor.predict(features)

# Assert: Verify the result
assert result.predicted_class == expected_class
assert result.confidence > 0.95
```

### What to Test

- ✅ Happy paths (normal operation)
- ✅ Edge cases (empty input, boundary values)
- ✅ Error cases (invalid input, missing data)
- ✅ Performance (response time within limits)

## Git Commit Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `refactor` | Code restructuring |
| `test` | Adding or modifying tests |
| `chore` | Maintenance, dependencies |
| `style` | Formatting, linting |

### Examples

```
feat(api): add batch prediction endpoint
fix(preprocessing): correct NaN handling in feature scaling
docs: update API documentation with examples
refactor(services): extract prediction logic from router
test: add unit tests for prediction service
```

## Code Review Checklist

- [ ] Code follows Black formatting
- [ ] Ruff linter passes with no errors
- [ ] Type hints are complete and correct
- [ ] Docstrings are present for public functions
- [ ] Error handling is appropriate
- [ ] Tests cover the new code
- [ ] No hardcoded credentials or secrets
- [ ] Logging is at the appropriate level
- [ ] No unnecessary dependencies added
- [ ] Database queries are indexed where needed
