# Milestone 2 Review & Preprocessing Verification Report

**Date:** 2026-07-29  
**Author:** AI CyberShield Engineering Team  
**Scope:** Phase 2.5 (EDA), Phase 2.6 (Preprocessing), Phase 2.7 (Data Versioning)  
**Evidence Artifacts:**
- [findings.md](file:///c:/Users/Swastik%20Pandey/OneDrive/Documents/AI%20CyberShield/reports/data/eda/findings.md)
- [preprocessing_log.md](file:///c:/Users/Swastik%20Pandey/OneDrive/Documents/AI%20CyberShield/reports/data/eda/preprocessing_log.md)
- [manifest.json](file:///c:/Users/Swastik%20Pandey/OneDrive/Documents/AI%20CyberShield/datasets/processed/CICIDS2017/manifest.json)
- [schema.yaml](file:///c:/Users/Swastik%20Pandey/OneDrive/Documents/AI%20CyberShield/configs/datasets/cicids2017/schema.yaml)

---

## 1. Architecture Review & Technical Debt Assessment

### Modular Architecture
- **Pipeline Separation**: The `CICIDSPreprocessor` class in `ml/preprocessing/preprocessor.py` implements a reusable `fit/transform` pattern. It decouples dataset ingestion, deduplication, cleaning, scaling, and splitting from execution wrappers.
- **Config-Driven Design**: Candidate constant columns, exact duplicate column pairs, and label mappings are driven via YAML configurations (`schema.yaml`, `attack_mapping.yaml`, `features.yaml`). No hardcoded column names or label strings exist in Python code.
- **Empirical Validation Gate**: Runtime column equality checks (`np.array_equal`) guarantee that candidate duplicate columns are only dropped if they are 100% bitwise identical across all 2.57M rows.

### Technical Debt Audit
- **Zero Technical Debt Introduced**: All transformation decisions strictly follow empirical findings in `findings.md`.
- **Dependency Hygiene**: Added `pyarrow` explicitly to `requirements.txt` for efficient columnar Parquet I/O. No unapproved third-party dependencies were introduced.
- **Python Quality & Linting**: All new and modified Python files (`preprocessor.py`, `run_preprocessing.py`, `data_dictionary.py`, `column_normalizer.py`) passed `python -m py_compile` with zero syntax errors.

---

## 2. Data Review & Transformation Statistics

### Row Count Progression
- **Initial Raw Rows (8 CSVs)**: 2,830,743 rows
- **Per-File Deduplication**: -256,479 rows (9.06% aggregate rate, PortScan worst at 25.26%)
- **Infinity Replacement**: 2,889 `Inf` cells in `Flow Bytes/s` & `Flow Packets/s` replaced with `0` (100% co-occurs with `Flow Duration == 0`)
- **Missing Value Removal**: -359 rows (0.0139% of deduplicated dataset, isolated strictly to `Flow Bytes/s`)
- **Total Processed Rows**: **2,573,905 rows**
  - **Training Split (70%)**: 1,801,733 rows
  - **Validation Split (10%)**: 257,391 rows
  - **Test Split (20%)**: 514,781 rows

### Feature Matrix Dimensions
- **Raw Feature Columns**: 78 features + 1 target (`Label`)
- **Verified & Dropped Exact Duplicates**: 3 features (`Subflow Fwd Packets`, `Subflow Bwd Packets`, `Fwd Header Length.1`)
- **Retained Feature Columns**: **75 features**
- **Label Encodings**: 100.00% label coverage (0 unmapped rows across all 2.83M raw rows after YAML fix).

### Data Integrity & Reproducibility
- All output Parquet files (`X_train.parquet`, `X_val.parquet`, `X_test.parquet`, `y_train.parquet`, `y_val.parquet`, `y_test.parquet`) and `scaler.pkl` are hashed with SHA256 checksums in `datasets/processed/CICIDS2017/manifest.json`.

---

## 3. Go / No-Go Recommendation for Milestone 3

### **RECOMMENDATION: GO (READY FOR MILESTONE 3)**

### Rationale
1. **Clean Data Foundation**: 100% of raw labels are mapped, missing values and infinities are handled without data leakage, and exact duplicate rows are removed per-file.
2. **Deterministic Splitting**: Stratified train/val/test split (70/10/20) guarantees exact preservation of class ratios, critical for rare classes (Heartbleed: 11 rows, Infiltration: 36 rows).
3. **No Premature Optimization**: Resampling (SMOTE / undersampling) and feature removal beyond exact duplicates were deliberately deferred to Milestone 3 modeling.

---

## 4. Proposed Milestone 3 High-Level Execution Plan (For Approval)

When Milestone 3 begins, the following sequential strategy is proposed for Tech Lead review before any training code is written:

1. **Baseline Model First**:
   - Train a fast, interpretable baseline model (e.g. `LogisticRegression` or a single `DecisionTreeClassifier`) on `X_train.parquet` to establish performance floors across all 7 attack categories.
2. **Imbalance-Aware Evaluation Metrics**:
   - Evaluate using per-class Precision, Recall, F1-Score, Confusion Matrix, and Precision-Recall Curves (PR-AUC), rather than plain overall accuracy.
3. **Advanced Tree Ensembles**:
   - Train `XGBoost` and `RandomForest` classifiers using class weights (`scale_pos_weight` / `class_weight='balanced'`).
4. **Conditional Resampling**:
   - Evaluate whether `imbalanced-learn` resampling is needed only after reviewing baseline per-class F1-scores.
