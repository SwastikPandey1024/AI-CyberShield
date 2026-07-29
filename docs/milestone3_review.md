# Milestone 3 Review & Machine Learning Model Selection Report

**Date:** 2026-07-29  
**Dataset:** CICIDS2017 Preprocessed Test Split (514,781 rows, 75 features)  
**Selected Model:** `RandomForest`  
**Model Artifact Path:** `ml/artifacts/models/model.pkl`  

---

## 1. Executive Summary & Model Comparison

Three candidate models were trained and evaluated on the held-out test split using the preprocessed stratified splits (`datasets/processed/CICIDS2017/`):

1. **Unweighted Decision Tree Baseline** (`max_depth=15`)
2. **RandomForest Classifier** (`n_estimators=100`, `class_weight='balanced'`)
3. **XGBoost Classifier** (`n_estimators=100`, `max_depth=8`, `sample_weight='balanced'`)

### Overall Performance Matrix

| Model | Accuracy | Macro F1-Score | Weighted F1-Score | Training Time |
|---|---:|---:|---:|---:|
| **Baseline (DecisionTree)** | 99.77% | 0.8071 | 0.9973 | 174s |
| **RandomForest (Balanced)** | **99.93%** | **0.9637** | **0.9993** | 77.91s |
| **XGBoost (Sample Weighted)** | 99.88% | 0.9483 | 0.9988 | 158.65s |

---

## 2. Per-Class F1-Score & Recall Comparison Across Models

| Class Name | Baseline F1 | RandomForest F1 (Recall) | XGBoost F1 (Recall) | Test Support |
|---|---:|---:|---:|---:|
| `BENIGN` | 0.9986 | 0.9993 (0.9987 Rec) | 0.9993 (0.9986 Rec) | 429,606 |
| `DoS` | 0.9944 | 0.9975 (0.9992 Rec) | 0.9980 (0.9997 Rec) | 38,749 |
| `DDoS` | 0.9989 | 0.9999 (0.9999 Rec) | 0.9997 (0.9999 Rec) | 25,603 |
| `PortScan` | 0.9928 | 0.9939 (0.9994 Rec) | 0.9938 (0.9994 Rec) | 18,164 |
| `BruteForce` | 0.9967 | 0.9997 (1.0000 Rec) | 0.9978 (1.0000 Rec) | 1,830 |
| `WebAttack` | 0.9456 | 0.9837 (0.9860 Rec) | 0.9793 (0.9930 Rec) | 429 |
| `Botnet` | 0.0296 | 0.7945 (0.9540 Rec) | 0.7610 (0.9974 Rec) | 391 |
| `Infiltration` | 0.5000 | 0.9412 (0.8889 Rec) | 0.8571 (1.0000 Rec) | 9 |
| `Unknown` | 0.0000 | 0.0000 (0.0000 Rec) | 0.0000 (0.0000 Rec) | 0 |

---

## 3. Selected Model & Justification

### Recommended Model: `RandomForest` (with `class_weight='balanced'`)

**Justification:**
1. **Highest Macro F1-Score**: RandomForest achieved a Macro F1-score of **0.9637**, outperforming XGBoost (0.9483) and the Baseline (0.8071).
2. **Dramatic Recovery on Rare Classes**:
   - **`Botnet` (391 test samples)**: Baseline F1 was **0.0296** (1.53% Recall). RandomForest balanced class weighting boosted `Botnet` Recall to **95.40%** and F1 to **0.7945** — a massive improvement in threat detection capability.
   - **`WebAttack` (429 test samples)**: F1 improved from **0.9456** (Baseline) to **0.9837** (RandomForest) with **98.60% Recall**.
   - **`Infiltration` (9 test samples)**: Achieved **88.89% Recall** (8 out of 9 test samples detected), yielding an F1-score of **0.9412** compared to Baseline's 0.5000.
3. **Near-Perfect Protection on Dominant Traffic**: Achieved **99.93% F1** on `BENIGN` traffic and $\ge 99.3\%$ F1 across `DoS`, `DDoS`, `PortScan`, and `BruteForce`.

---

## 4. Honest Statement of Model Performance Limitations

While RandomForest with balanced class weights significantly elevates threat detection across rare classes, empirical evaluation reveals the following remaining limitations:

1. **Infiltration Sample Size**: `Infiltration` contains only 36 total rows across the 2.83M dataset (9 test samples). While RandomForest detected 8 out of 9 test instances (0.8889 recall), precision is 1.0000. Production deployment should flag `Infiltration` alerts as high-priority candidates for analyst verification due to low overall sample support in training.
2. **Botnet Precision vs. Recall**: `Botnet` recall is high at 95.40%, but precision is 0.6807 (F1 = 0.7945). Approximately 175 benign flows were misclassified as `Botnet` due to overlapping TCP statistical characteristics in baseline network activity.

---

## 5. Artifact Export Verification

- **Trained Model**: `ml/artifacts/models/model.pkl`
- **Model Metrics**: `ml/artifacts/models/metrics.json`
- **Feature Names**: `ml/artifacts/models/feature_names.json`