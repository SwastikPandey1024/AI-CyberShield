<p align="center">
  <img src="https://img.shields.io/badge/status-in--development-yellow" alt="Status">
  <img src="https://img.shields.io/badge/python-3.13-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
</p>

<h1 align="center">🛡️ AI CyberShield</h1>
<p align="center"><em>AI-Powered Network Threat Detection & Analysis Platform</em></p>

<p align="center">
  A machine learning-powered cybersecurity platform that detects malicious network traffic,<br/>
  provides explainable threat predictions, and helps security analysts identify cyber attacks efficiently.
</p>

---

## 📋 Overview

AI CyberShield is an intelligent intrusion detection system that leverages machine learning to identify malicious network activity. Unlike traditional signature-based IDS solutions, CyberShield adapts to evolving threats by learning from network traffic patterns, reducing false positives while maintaining high detection accuracy.

The platform is built as a modular, production-ready system with:
- A **FastAPI** backend serving RESTful prediction APIs
- A **scikit-learn / XGBoost** ML pipeline for training and inference
- A **glassmorphic dashboard** (HTML/CSS/JS) for real-time threat visualization
- **Docker** containerization for reproducible deployment

---

## 🚨 Problem Statement

Traditional Intrusion Detection Systems (IDS) rely on predefined signatures and struggle to identify novel or evolving cyber threats.

Organizations require an adaptive, AI-driven system capable of:
- Analyzing network traffic patterns in real time
- Detecting malicious behavior with high accuracy
- Minimizing false positives that overwhelm analysts
- Providing explainable predictions for informed decision-making

AI CyberShield addresses these challenges by combining modern machine learning techniques with a clean, deployable architecture.

---

## ✨ Features

### Currently Implemented
- ✅ Project scaffolding and modular architecture (Python 3.13)
- ✅ Complete CICIDS2017 EDA, data profiling, and schema validation
- ✅ Evidence-driven preprocessing pipeline (2.57M clean rows, 75 features, zero unmapped labels)
- ✅ Stratified train/val/test data versioning with SHA256 checksum manifests
- ✅ DecisionTree baseline model evaluation
- ✅ RandomForest (class-balanced) & XGBoost ensemble models trained & evaluated
- ✅ Selected RandomForest model (99.93% accuracy, 0.9637 Macro F1) exported to `ml/artifacts/models/`
- ✅ REST API for single and batch predictions (FastAPI backend)
- ✅ Threat detection dashboard with interactive preset simulator
- ✅ Docker containerization for one-command deployment

### Future
- 📋 Live packet sniffing and real-time detection
- 📋 PostgreSQL storage for prediction history and security event logging
- 📋 Kafka streaming for high-throughput data ingestion
- 📋 SIEM integration (Splunk, Elastic, etc.)
- 📋 Threat intelligence feed enrichment
- 📋 User authentication and role-based access
- 📋 Kubernetes deployment for horizontal scaling

---

## 🏗️ Architecture

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
                    │(RandomForest)│
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
                    └──────────────┘
```

For detailed architecture documentation, see [`docs/architecture.md`](docs/architecture.md).

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------| --------|
| **Frontend** | HTML + CSS + JavaScript | Glassmorphic threat detection dashboard |
| **Backend** | FastAPI (Python 3.13) | High-performance REST API |
| **Machine Learning** | scikit-learn, XGBoost | Model training & inference |
| **Containerization** | Docker + Docker Compose | Reproducible deployment |
| **Testing** | Pytest, pytest-cov | Unit & integration testing |
| **Linting** | Black, Ruff, isort | Code quality enforcement |

---

## 📁 Folder Structure

```
AI-CyberShield/
│
├── backend/              # FastAPI application
│   └── app/
│       ├── api/          # Route handlers
│       ├── config.py     # Pydantic-settings configuration
│       ├── schemas/      # Pydantic request/response schemas
│       ├── services/     # Business logic layer
│       ├── logging/      # Structured logging
│       └── main.py       # Application entry point
│
├── ml/                   # Machine learning pipeline
│   ├── preprocessing/    # Data cleaning & feature engineering
│   ├── training/         # Model training & hyperparameter tuning
│   ├── inference/        # Prediction serving
│   ├── evaluation/       # Model performance metrics
│   ├── profiling/        # Dataset profiling & visualization
│   └── artifacts/        # Serialized models & scalers
│
├── frontend/             # Threat detection dashboard (HTML/CSS/JS)
├── configs/              # YAML configuration files
├── datasets/             # Dataset storage (raw & processed)
├── tests/                # Unit & integration tests
├── docs/                 # Architecture, ADRs, milestone reviews
├── scripts/              # Utility & diagnostic scripts
├── docker/               # Docker configuration files
├── .github/              # Issue templates, PR templates, labels
│
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Build & tool configuration
├── Makefile              # Development workflow commands
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── LICENSE               # MIT License
```

---

## 📦 Installation

### Prerequisites

- **Python 3.12+** (developed on 3.13)
- **Docker** (recommended for containerized setup)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/SwastikPandey1024/AI-CyberShield.git
cd AI-CyberShield

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development tools (optional)
pip install -e ".[dev]"

# 5. Set up environment variables
cp .env.example .env

# 6. Train the model (if model.pkl is not present)
python -m ml.training.train_ensembles

# 7. Run the application
uvicorn backend.app.main:app --reload
```

### Docker Setup

```bash
# Build and start all services
docker-compose up --build

# Services:
# - API: http://localhost:8000
# - Dashboard: http://localhost:3000
```

---

## 🚀 Usage

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/predict/single` | Classify a single network flow |
| `POST` | `/api/v1/predict/batch` | Batch prediction (up to 1,000 flows) |
| `GET`  | `/api/v1/predict/model/info` | Get loaded model metadata |
| `GET`  | `/health` | Health check (liveness probe) |
| `GET`  | `/ready` | Readiness probe (model loaded) |

### Example Prediction Request

```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "Destination Port": 443,
      "Flow Duration": 123456,
      "Total Fwd Packets": 10,
      "Total Backward Packets": 8,
      "Flow Bytes/s": 4500.0,
      "Flow Packets/s": 12.5,
      "SYN Flag Count": 1,
      "ACK Flag Count": 1
    }
  }'
```

### Example Response

```json
{
  "predicted_class": "BENIGN",
  "predicted_index": 0,
  "confidence": 0.987,
  "is_attack": false,
  "top_k": [
    {"class_name": "BENIGN", "probability": 0.987},
    {"class_name": "DoS", "probability": 0.008},
    {"class_name": "PortScan", "probability": 0.003}
  ],
  "all_probabilities": { ... },
  "model_run_id": "randomforest_milestone3"
}
```

---

## 🗺️ Roadmap

### Phase 0 — Foundation ✅
- [x] Project scaffolding and structure
- [x] Development environment configuration
- [x] Documentation framework

### Phase 1 — ML Pipeline ✅
- [x] Dataset preprocessing and cleaning
- [x] Feature engineering and selection
- [x] Model training (RandomForest + XGBoost)
- [x] Model evaluation and artifact export

### Phase 2 — API & Services ✅
- [x] Prediction endpoints (single & batch)
- [x] Model info and health endpoints
- [x] Unit tests and integration tests

### Phase 3 — Dashboard ✅
- [x] Threat detection dashboard
- [x] Prediction form with preset attack vectors
- [x] Real-time classification verdict display
- [x] Security event audit log

### Phase 4 — Polish (In Progress)
- [x] Docker Compose for one-command setup
- [x] Comprehensive documentation
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Live packet sniffing and PCAP extraction

See the full roadmap at [`docs/roadmap.md`](docs/roadmap.md).

---

## 🔮 Future Improvements

- **Real-time packet sniffing** — Capture live network traffic for on-the-fly analysis
- **Kafka streaming** — Handle high-throughput data ingestion with message queuing
- **SIEM integration** — Export alerts to Splunk, Elastic, or QRadar
- **Threat intelligence feeds** — Enrich predictions with external threat data
- **Authentication & RBAC** — Secure API access with JWT-based authentication
- **Kubernetes deployment** — Scale horizontally with container orchestration
- **PostgreSQL** — Persistent storage for prediction history and metrics

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Swastik Pandey**

- GitHub: [@SwastikPandey1024](https://github.com/SwastikPandey1024)
- Project Link: [https://github.com/SwastikPandey1024/AI-CyberShield](https://github.com/SwastikPandey1024/AI-CyberShield)

---

<p align="center">
  Made with ❤️ for cybersecurity researchers and practitioners
</p>
