# 📊 Business Requirements Document — AI CyberShield

**Version:** 1.0
**Status:** Accepted
**Date:** 2026

---

## 1. Business Overview

### 1.1 Business Context

The cybersecurity landscape is evolving rapidly. Organizations face an increasing volume and sophistication of cyber attacks, including DDoS, ransomware, brute force attacks, botnets, and zero-day exploits. Traditional signature-based Intrusion Detection Systems (IDS) are reactive — they can only detect attacks that match known signatures. This leaves organizations vulnerable to novel and evolving threats.

AI CyberShield addresses this gap by using machine learning to detect malicious patterns in network traffic, adapting to new threats without requiring signature updates.

### 1.2 Business Opportunity

The global intrusion detection and prevention systems market was valued at **$5.2 billion in 2023** and is projected to reach **$11.8 billion by 2030**, growing at a CAGR of 12.4% (source: Grand View Research). Organizations are actively seeking AI-driven security solutions that can:

- Detect unknown and zero-day attacks
- Reduce alert fatigue from false positives
- Provide actionable threat intelligence
- Scale with growing network traffic volumes

AI CyberShield targets this growing market with a modern, ML-first approach.

### 1.3 Business Objectives

| Objective | Metric | Target | Timeline |
|-----------|--------|--------|----------|
| Launch MVP with core threat detection | Functional MVP release | v1.0 | Month 4 |
| Achieve high detection accuracy | Balanced F1-score | > 0.90 | Month 3 |
| Enable easy deployment for organizations | Docker one-command setup | Complete | Month 4 |
| Build an extensible platform for future features | Modular architecture | Complete | Month 1 |
| Establish open-source community | GitHub stars, contributors | 100+ stars | Month 6 |

---

## 2. Stakeholder Analysis

### 2.1 Stakeholder Map

| Stakeholder | Role | Interest | Pain Points | Success Criteria |
|-------------|------|----------|-------------|-----------------|
| **SOC Analysts** | End users | High — daily tool | Alert fatigue, false positives | Accurate, fast predictions with confidence scores |
| **Security Engineers** | Implementers | High — integration | Complex deployment, lack of APIs | Clean REST API, easy Docker deployment |
| **Incident Responders** | End users | Medium — investigation | Slow threat analysis | Quick access to prediction history and patterns |
| **Data Scientists** | Contributors | High — model improvement | Poor data quality, hard to retrain | Reproducible pipeline, clear metrics |
| **Researchers** | Community | Medium — academic use | Lack of accessible tools | Open-source, well-documented, example notebooks |
| **Students** | Learners | Low — education | Complex setup | Clear documentation, easy local setup |
| **Investors / Leadership** | Decision makers | Medium — ROI | High security costs | Cost-effective, scalable solution |

### 2.2 Stakeholder Requirements

| Stakeholder | Requirement | Priority |
|-------------|-------------|----------|
| SOC Analysts | Real-time threat predictions with confidence scores | P0 |
| SOC Analysts | Historical prediction data for audit and review | P1 |
| Security Engineers | Well-documented REST API for integration | P0 |
| Security Engineers | Docker-based deployment for consistency | P0 |
| Incident Responders | Filter and search past predictions by threat type | P1 |
| Data Scientists | Reproducible ML pipeline with saved artifacts | P0 |
| Data Scientists | Evaluation metrics including per-class performance | P1 |
| Researchers | Accessible open-source code with documentation | P1 |
| Leadership | Clear metrics on detection accuracy and coverage | P2 |

---

## 3. Market Analysis

### 3.1 Competitive Landscape

| Competitor | Type | Strengths | Weaknesses | Differentiation |
|------------|------|-----------|------------|-----------------|
| **Snort** | Open-source signature-based | Mature, widely adopted | Signature-only, no ML | ML-based adaptive detection |
| **Suricata** | Open-source IDS/IPS | Multi-threaded, protocol detection | No built-in ML | AI-powered with confidence scoring |
| **Zeek (Bro)** | Open-source network monitor | Deep protocol analysis | No real-time blocking | ML-first architecture |
| **Cisco Secure IDS** | Commercial | Enterprise support, SIEM integration | Expensive, closed source | Open-source, cost-effective |
| **Darktrace** | Commercial AI-based | Enterprise AI, self-learning | Very expensive, black box | Transparent, explainable predictions |

### 3.2 Market Positioning

AI CyberShield occupies the **open-source, ML-native IDS** position — combining the accessibility of open-source tools like Snort with the intelligence of ML models like Darktrace.

```
Cost:              Free (open-source)
Approach:          ML-first (not signature-based)
Transparency:      Fully explainable predictions
Deployment:        Docker-based, single command
Target:            SMBs, researchers, students
```

### 3.3 Total Addressable Market

- **Global IDS/IPS Market:** $5.2B (2023) → $11.8B (2030)
- **AI in Cybersecurity Market:** $15.1B (2023) → $38.2B (2028)
- **Open-source Security Tools Market:** Growing at 18% CAGR

AI CyberShield targets the **AI-driven, open-source segment** of this market.

---

## 4. Business Model

### 4.1 Model (MVP Phase)

- **Open-source** (MIT License)
- Community-driven development
- Free for all users

### 4.2 Future Monetization Options

| Option | Description | Timeline |
|--------|-------------|----------|
| **Managed Cloud Service** | Hosted AI CyberShield with SLA | Post-MVP |
| **Enterprise Support** | Priority support, custom SLAs | Post-MVP |
| **Advanced Features** | SIEM integration, threat feeds (paid add-ons) | v2.0+ |
| **Training & Consulting** | Custom model training, deployment assistance | v2.0+ |

---

## 5. Functional Requirements (Business View)

### 5.1 Core Business Capabilities

| Capability | Business Value | Priority |
|------------|----------------|----------|
| **Threat Detection** | Identify malicious traffic automatically | P0 |
| **Confidence Scoring** | Prioritize high-confidence threats for immediate action | P0 |
| **Prediction History** | Audit trail for compliance and investigation | P1 |
| **Performance Metrics** | Demonstrate detection effectiveness to stakeholders | P1 |
| **REST API** | Integrate with existing security tools and workflows | P0 |
| **Dashboard** | Visual interface for analysts without CLI skills | P1 |

### 5.2 Business Rules

| Rule | Description |
|------|-------------|
| BR-01 | All predictions must be logged with a timestamp for auditability |
| BR-02 | The system must return a confidence score for every prediction |
| BR-03 | Model metrics must be computed on a held-out test set — never on training data |
| BR-04 | The system must maintain backward compatibility of the prediction API |
| BR-05 | All configuration must be externalized via environment variables |

---

## 6. Success Metrics

### 6.1 MVP Success Criteria

| Metric | Target | Measurement Method | Why It Matters |
|--------|--------|--------------------|----------------|
| Classification Accuracy | > 95% | Test set evaluation | General detection capability |
| Balanced F1-Score | > 0.90 | Per-class metrics | Fair detection across all attack types |
| False Positive Rate | < 5% | Confusion matrix analysis | Minimize analyst alert fatigue |
| API Response Time | < 500ms | 95th percentile latency | Real-time usability for analysts |
| Deployment Time | < 15 minutes | Docker setup from scratch | Adoption barrier reduction |
| Test Coverage | > 85% | pytest-cov report | Code reliability and maintainability |

### 6.2 Business Impact Metrics (Post-MVP)

| Metric | Description |
|--------|-------------|
| **Time to Detection** | Average time from attack to detection |
| **False Positive Reduction** | % reduction vs. signature-based IDS |
| **Analyst Productivity** | Alerts reviewed per hour |
| **Threat Coverage** | % of MITRE ATT&CK techniques detected |
| **Adoption Rate** | Number of active deployments |

---

## 7. Constraints & Assumptions

### 7.1 Constraints

| Constraint | Impact |
|------------|--------|
| MVP uses offline dataset (CICIDS2017) only | No real-time packet capture in v1 |
| Single model (XGBoost) in MVP | No ensemble or deep learning initially |
| No user authentication in MVP | Suitable for local/internal deployments only |
| SQLite default, PostgreSQL optional | Limits concurrent users without setup |

### 7.2 Assumptions

| Assumption | Risk if False |
|------------|---------------|
| CICIDS2017 dataset is representative of real network traffic | Model may not generalize to production environments |
| XGBoost is sufficient for MVP accuracy targets | May need ensemble or deep learning for some attack types |
| Users have basic Python/Docker knowledge | Documentation must be clear for non-developer users |
| Network flow features are available for prediction | Integration with packet capture tools needed in future |

---

## 8. Risk Assessment

### 8.1 Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Poor model accuracy on real traffic** | Medium | High | Extensive testing on multiple datasets; implement retraining pipeline |
| **Class imbalance skewing results** | High | Medium | SMOTE, class weighting, stratified splits, per-class metrics |
| **Data leakage between train and test** | Medium | High | Isolated preprocessing pipeline; fitted scalers saved as artifacts |
| **Large dataset size hindering development** | Medium | Low | Stratified sampling for quick iteration; scale up progressively |
| **Scope creep delaying MVP delivery** | High | Medium | Strict MVP scope enforcement; features prioritized as P0/P1/P2 |
| **Low adoption due to complexity** | Medium | Medium | Docker one-command setup; comprehensive documentation |

### 8.2 Risk Response Plan

| Risk | Response Strategy | Owner |
|------|-------------------|-------|
| Poor accuracy | Run systematic hyperparameter tuning; evaluate multiple feature sets | ML Engineer |
| Class imbalance | Implement SMOTE and weighted training from day one | Data Scientist |
| Data leakage | Build unified preprocessing pipeline used by both training and inference | ML Engineer |
| Scope creep | Use GitHub Projects with clear MVP milestone | Product Manager |

---

## 9. Milestone Roadmap

The project follows a milestone-based roadmap. Milestones are completed sequentially; each milestone builds on the previous one. There are no fixed calendar dates — progress depends on resource availability and scope adjustments.

```
Milestone 1: Project Foundation
    ↓
Milestone 2: Data Engineering
    ↓
Milestone 3: Machine Learning
    ↓
Milestone 4: Backend API & Services
    ↓
Milestone 5: Frontend Dashboard
    ↓
Milestone 6: Deployment & Polish
    ↓
Post-MVP Releases (v1.1, v1.2, v2.0)
```

### Milestone 1 — Project Foundation
**Goal:** Establish project infrastructure, tooling, and development environment.

**Deliverables:**
- Project scaffold with modular architecture
- Python 3.12 development environment (Black, Ruff, isort, pytest)
- Configuration-driven design (config.py + YAML configs)
- Docker Compose setup for local development
- CI/CD pipeline with GitHub Actions
- Comprehensive documentation (README, architecture, coding standards, contributing)

**Success Criteria:** Developer can clone, set up, and run the project in under 15 minutes.

---

### Milestone 2 — Data Engineering
**Goal:** Build a reproducible data pipeline for ingesting and preprocessing network traffic data.

**Deliverables:**
- Dataset downloader for CICIDS2017
- Data cleaning pipeline (missing values, duplicates, infinite values)
- Feature engineering and selection
- Handling class imbalance (SMOTE, class weighting)
- Train/validation/test split with stratification
- Exploratory Data Analysis (EDA) notebook

**Success Criteria:** Clean, preprocessed dataset ready for model training with reproducible pipeline.

---

### Milestone 3 — Machine Learning
**Goal:** Train, evaluate, and export a production-ready ML model.

**Deliverables:**
- XGBoost model training with cross-validation
- Hyperparameter tuning (GridSearchCV or Optuna)
- Model evaluation (accuracy, precision, recall, F1, confusion matrix, ROC)
- Per-class metrics for all attack categories
- Artifact serialization (model, scaler, encoder, feature names)
- Inference module for prediction serving

**Success Criteria:** Model achieves > 95% accuracy and > 0.90 balanced F1-score on held-out test set.

---

### Milestone 4 — Backend API & Services
**Goal:** Expose ML predictions and history through a well-documented REST API.

**Deliverables:**
- FastAPI application with modular route structure
- Endpoints: predict, predict/batch, history, metrics, health
- Pydantic schemas for request/response validation
- PostgreSQL-backed prediction history storage
- Structured JSON logging
- Unit tests and integration tests

**Success Criteria:** All endpoints functional, documented in Swagger, and tested with Pytest.

---

### Milestone 5 — Frontend Dashboard
**Goal:** Provide an interactive dashboard for non-technical users.

**Deliverables:**
- React + TypeScript + Tailwind CSS application
- Prediction form with real-time results
- Prediction history table with filters and pagination
- Charts (attack distribution, confidence trends)
- Responsive design

**Success Criteria:** Dashboard loads in < 3 seconds; all dashboard features functional.

---

### Milestone 6 — Deployment & Polish
**Goal:** Production-ready deployment with comprehensive documentation.

**Deliverables:**
- Optimized Dockerfiles (multi-stage builds)
- Docker Compose with all services
- CI/CD pipeline with automated testing and deployment
- API documentation with request/response examples
- Postman collection
- Performance optimization and edge case hardening

**Success Criteria:** One-command `docker-compose up` launches the full stack.

---

### Post-MVP Releases

| Release | Focus Areas |
|---------|-------------|
| **v1.1** | Real-time packet capture, WebSocket dashboard updates |
| **v1.2** | Kafka streaming, threat intelligence feed enrichment |
| **v2.0** | User authentication (JWT), SIEM integration, Kubernetes deployment |

---

## 10. Budget & Resources (MVP)

### 10.1 Development Resources

| Resource | Quantity | Duration |
|----------|----------|----------|
| Senior ML Engineer | 1 | 14 weeks |
| Backend Engineer | 1 | 10 weeks |
| Frontend Engineer | 1 | 6 weeks |
| Infrastructure (Docker, CI/CD) | Shared | Ongoing |

### 10.2 Infrastructure Costs (MVP)

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| **Development** | — | Local development, no cloud costs |
| **PostgreSQL** | — | Local or free-tier (Render, Railway) |
| **CI/CD (GitHub Actions)** | Free | Public repository |
| **Docker Hosting** | $5–$15/month | VPS for demo deployment |
| **Domain (optional)** | $10–$15/year | For hosted demo |

**Total estimated monthly cost:** $5–$30 (MVP)

---

## 11. Compliance & Legal

| Area | Consideration | Status |
|------|---------------|--------|
| **License** | MIT License — permissive, allows commercial use | ✅ Selected |
| **Dataset License** | CICIDS2017 is publicly available for research | ✅ Verified |
| **Data Privacy** | No PII collected; network flow statistics only | ✅ Low risk |
| **Export Control** | Cybersecurity tools may have export restrictions | ⚠️ Review needed |

---

## 12. Appendix

### 12.1 Key Performance Indicators (KPIs)

| KPI | Target | Tracking |
|-----|--------|----------|
| Model Accuracy | > 95% | Post-training evaluation |
| Inference Latency | < 500ms | API monitoring |
| GitHub Stars | 100+ | GitHub analytics |
| Active Contributors | 3+ | GitHub insights |
| Documentation Coverage | 100% of endpoints | Manual review |
| Time to First Prediction (new user) | < 5 minutes | User testing |

### 12.2 Open Questions

1. Should the MVP include a simple feedback loop (users submit actual labels)?
2. What is the target accuracy for zero-day attack detection?
3. Should we support custom model uploads in v1 or v2?
