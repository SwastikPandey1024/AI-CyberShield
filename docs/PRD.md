# 📋 Product Requirements Document — AI CyberShield

**Version:** 1.0
**Status:** Draft
**Date:** 2024

---

## 1. Executive Summary

AI CyberShield is an AI-powered network threat detection and analysis platform that uses machine learning to identify malicious network traffic in real time. The platform provides threat predictions, explainable AI insights, monitoring dashboards, and REST APIs to help security analysts identify cyber attacks efficiently.

---

## 2. Product Overview

### 2.1 Product Vision

To build an adaptive, intelligent intrusion detection system that learns from network traffic patterns, detects evolving cyber threats with high accuracy, and minimizes false positives — making cybersecurity accessible and actionable for organizations of all sizes.

### 2.2 Target Users

**Primary:**
- Security Operations Center (SOC) Analysts
- Cybersecurity Engineers
- Incident Response Teams

**Secondary:**
- Students and researchers in cybersecurity
- Universities for academic and research purposes

**Future:**
- Financial institutions
- Healthcare organizations
- Cloud service providers
- Government agencies

### 2.3 Problem Statement

Traditional Intrusion Detection Systems (IDS) rely on predefined signatures and struggle to identify novel or evolving cyber threats. Organizations require an adaptive, AI-driven system capable of analyzing network traffic patterns and detecting malicious behavior with high accuracy while minimizing false positives.

---

## 3. MVP Scope

### 3.1 In Scope (MVP)

| Category | Features |
|----------|----------|
| **Data Processing** | CICIDS2017 dataset import, cleaning, preprocessing, feature engineering |
| **Machine Learning** | Model training (XGBoost), hyperparameter tuning, cross-validation |
| **Inference** | Single prediction, batch prediction, confidence scoring |
| **API** | RESTful endpoints for prediction, history, metrics, health check |
| **Dashboard** | Threat detection visualization, prediction history, statistics |
| **Storage** | PostgreSQL-backed prediction history and model metrics |
| **Evaluation** | Accuracy, precision, recall, F1-score, confusion matrix, ROC curves |
| **Logging** | Structured JSON logging for all system events |
| **Documentation** | API docs, architecture docs, setup guide, development guide |

### 3.2 Out of Scope (Future Versions)

- Live packet sniffing and real-time network capture
- Kafka streaming for high-throughput data ingestion
- SIEM integration (Splunk, Elastic, QRadar)
- Threat intelligence feed enrichment
- Multi-model ensemble (Random Forest + XGBoost + LightGBM)
- User authentication and role-based access control
- Kubernetes deployment and horizontal scaling

---

## 4. Functional Requirements

### 4.1 Data Ingestion & Preprocessing

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01 | The system shall import the CICIDS2017 dataset from CSV files | P0 |
| FR-02 | The system shall clean data by handling missing values, infinite values, and duplicates | P0 |
| FR-03 | The system shall encode categorical variables (e.g., protocol types, labels) | P0 |
| FR-04 | The system shall scale numerical features using StandardScaler | P0 |
| FR-05 | The system shall perform feature selection to reduce dimensionality | P1 |
| FR-06 | The system shall handle class imbalance using SMOTE or class weighting | P1 |
| FR-07 | The system shall split data into training, validation, and test sets | P0 |

### 4.2 Model Training

| ID | Requirement | Priority |
|----|------------|----------|
| FR-08 | The system shall train an XGBoost classifier on the processed dataset | P0 |
| FR-09 | The system shall support hyperparameter tuning using GridSearchCV or Optuna | P1 |
| FR-10 | The system shall perform k-fold cross-validation during training | P0 |
| FR-11 | The system shall save trained model artifacts (model, scaler, encoder) | P0 |
| FR-12 | The system shall log all training metrics and parameters | P1 |

### 4.3 Prediction & Inference

| ID | Requirement | Priority |
|----|------------|----------|
| FR-13 | The system shall accept network flow features via REST API and return a threat prediction | P0 |
| FR-14 | The system shall return prediction confidence scores alongside the predicted class | P0 |
| FR-15 | The system shall support batch predictions for multiple network flows | P1 |
| FR-16 | The system shall return processing time per prediction | P1 |
| FR-17 | The system shall load the latest trained model on startup | P0 |

### 4.4 Prediction History

| ID | Requirement | Priority |
|----|------------|----------|
| FR-18 | The system shall store every prediction in PostgreSQL with timestamp | P0 |
| FR-19 | The system shall allow retrieving prediction history with pagination | P1 |
| FR-20 | The system shall allow filtering history by predicted class, date range, or confidence | P2 |

### 4.5 Model Evaluation

| ID | Requirement | Priority |
|----|------------|----------|
| FR-21 | The system shall compute accuracy, precision, recall, and F1-score | P0 |
| FR-22 | The system shall generate per-class metrics for all attack categories | P1 |
| FR-23 | The system shall generate a confusion matrix | P1 |
| FR-24 | The system shall generate ROC curves and precision-recall curves | P2 |

### 4.6 Dashboard

| ID | Requirement | Priority |
|----|------------|----------|
| FR-25 | The dashboard shall display a form to input network flow features and get predictions | P1 |
| FR-26 | The dashboard shall display prediction results with confidence visualization | P1 |
| FR-27 | The dashboard shall show prediction history in a sortable, filterable table | P1 |
| FR-28 | The dashboard shall display charts showing attack distribution and confidence trends | P2 |

### 4.7 Logging

| ID | Requirement | Priority |
|----|------------|----------|
| FR-29 | The system shall log all API requests and responses with timestamps | P1 |
| FR-30 | The system shall log model loading and prediction events | P1 |
| FR-31 | The system shall log errors and warnings with stack traces | P1 |
| FR-32 | The system shall support configurable log levels (DEBUG, INFO, WARNING, ERROR) | P1 |

---

## 5. Non-Functional Requirements

| ID | Requirement | Target | Priority |
|----|------------|--------|----------|
| NFR-01 | Classification accuracy | > 95% on test set | P0 |
| NFR-02 | Balanced F1-score | > 0.90 (macro average) | P0 |
| NFR-03 | API response time (single prediction) | < 500ms (95th percentile) | P1 |
| NFR-04 | API response time (batch prediction) | < 2s for 100 flows | P2 |
| NFR-05 | Dashboard load time | < 3 seconds | P2 |
| NFR-06 | Test coverage | > 85% | P1 |
| NFR-07 | Deployment | Single `docker-compose up` command | P0 |
| NFR-08 | API documentation | Auto-generated OpenAPI/Swagger | P0 |
| NFR-09 | Code quality | Zero Ruff errors, all type hints | P1 |

---

## 6. User Stories

### Epic 1: ML Pipeline

| Story | Description | Priority |
|-------|-------------|----------|
| US-01 | As a data scientist, I want to import the CICIDS2017 dataset so that I can train models on realistic network traffic data | P0 |
| US-02 | As a data scientist, I want to preprocess and clean the data so that the model trains on high-quality features | P0 |
| US-03 | As a data scientist, I want to train an XGBoost model with cross-validation so that I can evaluate its performance reliably | P0 |
| US-04 | As a data scientist, I want to tune hyperparameters automatically so that the model achieves optimal performance | P1 |
| US-05 | As a data scientist, I want to save trained model artifacts so that they can be loaded for inference | P0 |

### Epic 2: API

| Story | Description | Priority |
|-------|-------------|----------|
| US-06 | As a developer, I want to send network flow features to an API endpoint and receive a threat prediction so that I can integrate with other systems | P0 |
| US-07 | As a developer, I want to send multiple flows in a single request so that I can process data efficiently | P1 |
| US-08 | As a developer, I want to retrieve prediction history with pagination so that I can audit past predictions | P1 |
| US-09 | As a developer, I want to check API health so that I can monitor system availability | P1 |

### Epic 3: Dashboard

| Story | Description | Priority |
|-------|-------------|----------|
| US-10 | As a SOC analyst, I want to input network flow features and see a prediction instantly so that I can investigate suspicious traffic | P1 |
| US-11 | As a SOC analyst, I want to see the confidence level of each prediction so that I can prioritize my response | P1 |
| US-12 | As a SOC analyst, I want to browse past predictions in a table so that I can review historical threat activity | P1 |
| US-13 | As a SOC analyst, I want to see charts of attack type distribution so that I can understand threat patterns | P2 |

---

## 7. Release Criteria

### MVP Release Checklist

- [ ] All P0 functional requirements implemented and tested
- [ ] ML model achieves > 95% accuracy and > 0.90 F1-score
- [ ] All API endpoints documented in Swagger/OpenAPI
- [ ] Dashboard displays predictions and history
- [ ] Docker Compose starts all services with one command
- [ ] Test coverage ≥ 85%
- [ ] All linters pass with zero errors
- [ ] README and API documentation complete

---

## 8. Glossary

| Term | Definition |
|------|------------|
| **CICIDS2017** | A public cybersecurity dataset containing benign and malicious network traffic flows |
| **XGBoost** | An optimized gradient boosting machine learning algorithm |
| **Confidence Score** | The probability (0–1) assigned to a prediction by the model |
| **False Positive** | Benign traffic incorrectly classified as malicious |
| **False Negative** | Malicious traffic incorrectly classified as benign |
| **F1-Score** | The harmonic mean of precision and recall |
| **SMOTE** | Synthetic Minority Over-sampling Technique for handling class imbalance |
| **SIEM** | Security Information and Event Management system |
