# Experiment Template

Use this template to document each ML experiment.

---

## Experiment {NUMBER}: {SHORT_DESCRIPTION}

**Date:** YYYY-MM-DD
**Author:** [Name]

---

### Objective

What are we trying to achieve or test?

### Configuration

- **Model:** XGBoost / Random Forest / etc.
- **Dataset:** CICIDS2017 (sample: 10% / 50% / 100%)
- **Features:** [number] features selected via [method]
- **Preprocessing:** Scaling, encoding, missing value handling
- **Class Imbalance Handling:** SMOTE / class_weight / none

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| `n_estimators` | |
| `max_depth` | |
| `learning_rate` | |
| `subsample` | |
| `colsample_bytree` | |
| `scale_pos_weight` | |
| `early_stopping_rounds` | |

### Results

| Metric | Value |
|--------|-------|
| **Accuracy** | |
| **Precision (macro)** | |
| **Recall (macro)** | |
| **F1-Score (macro)** | |
| **ROC AUC** | |

### Per-Class Metrics

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Benign | | | | |
| DDoS | | | | |
| Brute Force | | | | |
| Botnet | | | | |
| Port Scan | | | | |
| Web Attack | | | | |

### Observations

- Key findings
- Unexpected patterns
- Data quality issues

### Next Steps

- What to try next
- Hyperparameters to tune
- Features to add or remove

### Artifacts

- Model: `experiments/models/experiment_{NUMBER}_model.pkl`
- Scaler: `experiments/models/experiment_{NUMBER}_scaler.pkl`
- Metrics: `experiments/models/experiment_{NUMBER}_metrics.json`
