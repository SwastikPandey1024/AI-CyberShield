# Datasets — AI CyberShield

This directory manages all datasets used for training, validation, and external evaluation.

---

## Directory Structure

```
datasets/
├── raw/              # Original, unmodified source datasets
│   └── CICIDS2017/   # Primary dataset: CICIDS2017
├── processed/        # Cleaned, preprocessed, ready-for-training datasets
├── external/         # Alternative/future datasets for evaluation
└── README.md         # This file
```

---

## Directory Purposes

### `raw/`

Contains **original, unmodified** datasets exactly as downloaded from their source. Files in this directory are treated as immutable — no edits, cleaning, or transformations are applied here.

| Subdirectory | Dataset | Purpose |
|-------------|---------|---------|
| `CICIDS2017/` | CICIDS2017 | Primary training/validation dataset |

**Naming convention:** `<DatasetName>/` with the canonical dataset name.

### `processed/`

Contains **cleaned and preprocessed** datasets that are ready for model consumption. Output of the ML preprocessing pipeline (`ml/preprocessing/`). Each processed dataset should have a corresponding source in `raw/`.

**Naming convention:** `<dataset_name>_<stage>_<timestamp>.parquet`

Examples: `cicids2017_clean_20240101.parquet`, `cicids2017_train_20240101.parquet`

### `external/`

Contains **alternative datasets** used for cross-validation or future training expansion. These are not the primary dataset but may be used to test model generalisation.

Candidates: UNSW-NB15, CSE-CIC-IDS2018, TON-IoT

---

## Dataset Versioning Strategy

| Component | Strategy | Example |
|-----------|----------|---------|
| **Raw datasets** | Immutable; identified by dataset name + download date | `CICIDS2017/` (folder) |
| **Processed datasets** | File-level versioning via timestamps in filename | `cicids2017_v2_train_20240101.parquet` |
| **Artifact metadata** | JSON metadata saved alongside processed files | See `ml/artifacts/metadata/` |
| **Experiment linkage** | Experiment config references exact dataset filename | See `experiments/` |

**Version format:** `v<major>.<minor>` where major bumps indicate breaking schema changes and minor bumps indicate additive changes (new features, bug fixes).

---

## Expected File Formats

| Format | Usage | Reader Library |
|--------|-------|----------------|
| `.csv` | Raw source data (CICIDS2017) | `pandas.read_csv()` |
| `.parquet` | Processed/cleaned data (preferred) | `pandas.read_parquet()` |
| `.pcap` | Raw packet captures (future) | `scapy` |
| `.json` | Metadata and schema definitions | `json` module |
| `.yaml` | Dataset configuration | `pyyaml` |

`.parquet` is the **preferred format** for processed data due to its columnar storage, compression, and schema preservation.

---

## Which Datasets Go Where

| Dataset | Directory | Rationale |
|---------|-----------|-----------|
| CICIDS2017 Monday-Friday CSVs | `raw/CICIDS2017/` | Original source — immutable |
| Cleaned + encoded CICIDS2017 | `processed/` | Pipeline output — mutable |
| UNSW-NB15 (downloaded) | `external/` | Not the primary dataset |
| CSE-CIC-IDS2018 (downloaded) | `external/` | Reserved for future expansion |

---

## Data Integrity Rules

1. **Never** modify files inside `raw/` in place. All transformations go to `processed/`.
2. **Never** commit large dataset files to Git. They are ignored via `.gitignore`.
3. **Always** document dataset schema changes in the corresponding experiment or ADR.
4. **Always** use the same preprocessing pipeline for both training and inference to prevent data leakage.

---

## Quick Reference

```python
# Loading raw data (CICIDS2017)
import pandas as pd
df = pd.read_csv("datasets/raw/CICIDS2017/MachineLearningCVE/Monday-WorkingHours.pcap_ISCX.csv")

# Loading processed data
df = pd.read_parquet("datasets/processed/cicids2017_v1_clean.parquet")
```

> See `ml/preprocessing/dataset_loader.py` for the production data loader.

---

## Processed Dataset SHA256 Checksums (Phase 2.7 Versioning)

**Manifest File:** `datasets/processed/CICIDS2017/manifest.json`  
**Pipeline Version:** `1.0`  
**Preprocessing Audit Log:** `reports/data/eda/preprocessing_log.md`

| Output File | Size | SHA256 Checksum |
|---|---:|---|
| `datasets/processed/CICIDS2017/X_train.parquet` | 273,066,516 bytes | `16daeccfd04d63bddd86ffe68503ecb6b9e0af63c2676c429e381b9e88498e92` |
| `datasets/processed/CICIDS2017/X_val.parquet` | 38,916,465 bytes | `b0042c05cffd5e5ee74905e31447267cbb5cb1c43bec0facede042ea3dac1131` |
| `datasets/processed/CICIDS2017/X_test.parquet` | 77,676,266 bytes | `d4995878f0f7d16bab18c0db91872a2f463df6405f7d7835f1669f69d0954e3f` |
| `datasets/processed/CICIDS2017/y_train.parquet` | 503,021 bytes | `1e3ae13c942e7c293bbd84fa47c71beb2b564eb800f944d716e21e687238f7c7` |
| `datasets/processed/CICIDS2017/y_val.parquet` | 76,371 bytes | `de09155fd02fc66b35b6456db8becca7787af08eff9099933eb80cd1546d1252` |
| `datasets/processed/CICIDS2017/y_test.parquet` | 147,817 bytes | `907fdb6c0e399082cf584c4cb82b6ce3272451b03e0ac58cb9de1b13551cbd6a` |
| `datasets/processed/CICIDS2017/scaler.pkl` | 3,081 bytes | `901d7c28a9dd311c50e5b10425fc5519c6b12f9637942083e30ed5a1263c32d5` |

