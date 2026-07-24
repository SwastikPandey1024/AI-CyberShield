# 🗺️ Roadmap

## Project Status

**Current Phase:** Phase 0 — Foundation
**Target Version:** 1.0.0 (MVP)

---

## Phase 0 — Foundation ✅ (Current)

> **Goal:** Establish project structure, tooling, and documentation.

| Task | Status |
|------|--------|
| Project scaffolding and folder structure | ✅ Complete |
| Python 3.12 development environment | ✅ Complete |
| Black, Ruff, isort, pytest configuration | ✅ Complete |
| .gitignore with comprehensive rules | ✅ Complete |
| Project documentation (README, architecture, standards, roadmap) | ✅ Complete |
| Docker Compose setup | ⬜ Not started |
| CI/CD pipeline (GitHub Actions) | ⬜ Not started |

---

## Phase 1 — ML Pipeline 🎯 (Next)

> **Goal:** Build a reproducible ML pipeline for training and evaluating threat detection models.

| Task | Status | Estimated Effort |
|------|--------|-----------------|
| CICIDS2017 dataset downloader and parser | ⬜ Not started | 2 days |
| Data cleaning and preprocessing pipeline | ⬜ Not started | 3 days |
| Exploratory Data Analysis (EDA) notebook | ⬜ Not started | 2 days |
| Feature engineering and selection | ⬜ Not started | 3 days |
| Handle class imbalance (SMOTE, weighting) | ⬜ Not started | 2 days |
| XGBoost model training with cross-validation | ⬜ Not started | 3 days |
| Hyperparameter tuning (GridSearchCV / Optuna) | ⬜ Not started | 2 days |
| Model evaluation (per-class metrics, confusion matrix, ROC) | ⬜ Not started | 2 days |
| Artifact serialization (model + scaler + encoder) | ⬜ Not started | 1 day |
| Inference module for prediction serving | ⬜ Not started | 2 days |

**Milestone:** Reproducible ML pipeline with trained model artifacts.

---

## Phase 2 — API & Services 🚀

> **Goal:** Expose ML predictions and history through a well-documented REST API.

| Task | Status | Estimated Effort |
|------|--------|-----------------|
| FastAPI application bootstrap | ⬜ Not started | 1 day |
| Core configuration and settings module | ⬜ Not started | 1 day |
| Database models (predictions, metrics) | ⬜ Not started | 1 day |
| Alembic migrations | ⬜ Not started | 1 day |
| Pydantic schemas for request/response | ⬜ Not started | 1 day |
| POST /api/v1/predict endpoint | ⬜ Not started | 2 days |
| POST /api/v1/predict/batch endpoint | ⬜ Not started | 1 day |
| GET /api/v1/history endpoint | ⬜ Not started | 1 day |
| GET /api/v1/metrics endpoint | ⬜ Not started | 1 day |
| GET /api/v1/health endpoint | ⬜ Not started | 0.5 day |
| Structured JSON logging | ⬜ Not started | 1 day |
| Error handling and middleware | ⬜ Not started | 1 day |
| Unit tests for all endpoints | ⬜ Not started | 2 days |
| Integration tests | ⬜ Not started | 2 days |

**Milestone:** Fully functional REST API with OpenAPI documentation.

---

## Phase 3 — Dashboard 📊

> **Goal:** Build an interactive React dashboard for real-time threat monitoring.

| Task | Status | Estimated Effort |
|------|--------|-----------------|
| React + TypeScript + Tailwind CSS scaffold | ⬜ Not started | 1 day |
| API client module | ⬜ Not started | 1 day |
| Prediction form with feature input | ⬜ Not started | 2 days |
| Real-time prediction results display | ⬜ Not started | 1 day |
| Prediction confidence visualization | ⬜ Not started | 1 day |
| Prediction history table with filters | ⬜ Not started | 2 days |
| Charts: attack distribution, confidence trends | ⬜ Not started | 2 days |
| Dashboard layout and navigation | ⬜ Not started | 1 day |
| Loading states and error handling | ⬜ Not started | 1 day |
| Responsive design | ⬜ Not started | 1 day |

**Milestone:** Interactive dashboard with real-time prediction capabilities.

---

## Phase 4 — Polish & Deploy 🚢

> **Goal:** Production-ready deployment with documentation and CI/CD.

| Task | Status | Estimated Effort |
|------|--------|-----------------|
| Docker Compose with all services | ⬜ Not started | 2 days |
| Dockerfile optimization (multi-stage builds) | ⬜ Not started | 1 day |
| CI/CD pipeline (GitHub Actions) | ⬜ Not started | 2 days |
| API documentation with examples | ⬜ Not started | 1 day |
| Postman collection | ⬜ Not started | 1 day |
| Environment variable documentation | ⬜ Not started | 0.5 day |
| Deployment guide | ⬜ Not started | 1 day |
| Performance testing and optimization | ⬜ Not started | 2 days |
| Edge case handling and hardening | ⬜ Not started | 2 days |

**Milestone:** Production-ready MVP deployable with a single command.

---

## Future Releases (Post-MVP)

### v1.1 — Real-Time Detection
- Live packet capture and analysis (pcap/pyshark)
- Streaming prediction pipeline
- WebSocket-based real-time dashboard updates

### v1.2 — Advanced Features
- Kafka integration for high-throughput data ingestion
- Threat intelligence feed enrichment
- Multi-model ensemble (Random Forest + XGBoost + LightGBM)

### v2.0 — Enterprise Ready
- User authentication and role-based access control (JWT)
- SIEM integration (Splunk, Elastic, QRadar)
- Alerting and notification system
- Kubernetes deployment with Helm charts
- Horizontal scaling for production workloads

### v2.1 — Enhanced Analytics
- Explainable AI (SHAP, LIME) for prediction interpretability
- Automated retraining pipeline
- A/B testing framework for model comparison
- Custom rule engine for hybrid detection

---

## Timeline (Estimated)

```
Phase 0: Foundation       ████████░░░░░░░░░░░░  2 weeks
Phase 1: ML Pipeline      ████████████████░░░░  4 weeks
Phase 2: API & Services   ██████████████░░░░░░  3 weeks
Phase 3: Dashboard        ██████████████░░░░░░  3 weeks
Phase 4: Polish & Deploy  ██████████░░░░░░░░░░  2 weeks
                                     ──────────
                            Total: 14 weeks (3.5 months)
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Classification Accuracy | > 95% | Test set evaluation |
| Balanced F1-Score | > 0.90 | Per-class F1 macro average |
| API Response Time | < 500ms | 95th percentile latency |
| Dashboard Load Time | < 3 seconds | Lighthouse performance |
| Test Coverage | > 85% | pytest-cov report |
| Docker Setup | Single command | `docker-compose up` |
