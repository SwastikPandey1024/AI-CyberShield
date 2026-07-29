# 🏗️ Architecture Overview

## High-Level Architecture

```
                    ┌──────────────┐
                    │    User /     │
                    │   Dashboard   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  REST API    │
                    │  (FastAPI)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Prediction  │
                    │   Service    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  ML Model    │
                    │  (XGBoost)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Preprocessing│
                    │   Pipeline   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  CICIDS2017  │
                    │   Dataset    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │  + Logging   │
                    └──────────────┘
```

## Layer Responsibilities

### 1. Presentation Layer (Frontend)
- HTML/CSS/JS threat detection dashboard
- Communicates with backend via REST API
- Visualizes predictions, history, and metrics
- Provides real-time threat monitoring interface

### 2. API Layer (Backend)
- FastAPI application with automatic OpenAPI documentation
- Route handlers for prediction, history, and metrics
- Pydantic schemas for request/response validation
- Middleware for logging, CORS, and error handling

### 3. Service Layer
- Business logic orchestrator
- Coordinates between API, ML inference, and database
- Handles data transformation and validation
- Manages prediction history storage

### 4. ML Inference Layer
- Loads trained model and preprocessor artifacts
- Performs feature transformation (same as training pipeline)
- Executes model prediction
- Returns prediction class and confidence scores

### 5. ML Pipeline Layer
- Offline training pipeline (not served in production)
- Data ingestion from CICIDS2017 dataset
- Feature engineering, selection, and scaling
- Model training with cross-validation and hyperparameter tuning
- Model evaluation with comprehensive metrics
- Artifact serialization (model + scaler + encoder)

### 6. Data Layer
- PostgreSQL for structured prediction history
- SQLAlchemy ORM for database abstraction
- Alembic for schema migrations
- Structured JSON logging for debugging and audit trails

## Backend Layering Pattern

```
Route Layer (FastAPI routers)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (database access via SQLAlchemy)
    ↓
ML Inference Layer (model loading + preprocessing)
```

## ML Pipeline Architecture

```
data/raw/ → data/processed/ → features/ → trained_model.pkl + scaler.pkl
                   ↓                              ↓
            (reused in inference)          loaded by API service
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI over Flask** | Native async support, automatic OpenAPI docs, Pydantic integration |
| **XGBoost over deep learning** | Better performance on tabular network flow data, faster training, explainability |
| **SQLAlchemy ORM** | Production-ready, migration support, database-agnostic |
| **Separate preprocessing pipeline** | Prevents data leakage between training and inference |
| **Docker Compose** | Single-command setup for development and deployment |

## Prevention of Data Leakage

The preprocessing pipeline is shared between training and inference:
1. During training: fit scalers, encoders, and feature selectors on training data only
2. Serialize fitted objects as artifacts alongside the model
3. During inference: load fitted artifacts and transform input data
4. Never re-fit scalers on inference data

## Database Schema

### `predictions` table
```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    features_hash VARCHAR(64) NOT NULL,
    predicted_class VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    actual_label VARCHAR(50) DEFAULT NULL,
    processing_time_ms FLOAT NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    raw_features JSONB NOT NULL
);

CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX idx_predictions_class ON predictions(predicted_class);
```

### `model_metrics` table
```sql
CREATE TABLE model_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_version VARCHAR(20) NOT NULL,
    evaluation_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    per_class_metrics JSONB NOT NULL,
    confusion_matrix JSONB NOT NULL
);
```

## Structured Logging

All system events are logged in structured JSON format:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "module": "predictor",
  "message": "Prediction completed",
  "extra": {
    "request_id": "abc-123",
    "processing_time_ms": 45.2,
    "predicted_class": "Benign",
    "confidence": 0.987
  }
}
```

Log levels:
- **DEBUG**: Development-only details
- **INFO**: Normal operational events
- **WARNING**: Anomalous but non-critical events
- **ERROR**: Failures requiring attention
