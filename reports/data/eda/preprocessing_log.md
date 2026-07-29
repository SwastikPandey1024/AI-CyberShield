# Preprocessing Audit Log — Phase 2.6b
**Generated:** 2026-07-29
**Dataset:** CICIDS2017 (8 raw CSVs)
**Evidence Base:** `reports/data/eda/findings.md`

---

## Executive Summary & Data Pipeline Transformation Flow

- **Raw Rows Read Across 8 Files:** 2,830,743
- **Duplicates Dropped Per-File (findings.md Step 3):** 256,479
- **Combined Rows After Per-File Deduplication:** 2,574,264
- **Inf Values Replaced with 0 (findings.md Step 4):** 2,889
- **Rows Dropped Due to Missing Values (findings.md Step 2):** 359 (0.048% of dataset)
- **Verified & Dropped Exact Duplicate Columns (findings.md Step 5):** 7 columns
- **Final Cleaned Rows:** 2,573,905
- **Final Feature Columns:** 75 (78 initial - 7 dropped exact duplicates = 71 feature columns)

---

## 1. Per-File Deduplication Audit (findings.md Step 3)

| File Name | Raw Rows | Rows After Deduplication | Duplicates Dropped | Dup % |
|---|---:|---:|---:|---:|
| `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` | 225,745 | 223,112 | 2,633 | 1.17% |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | 286,467 | 214,114 | 72,353 | 25.26% |
| `Friday-WorkingHours-Morning.pcap_ISCX.csv` | 191,033 | 184,145 | 6,888 | 3.61% |
| `Monday-WorkingHours.pcap_ISCX.csv` | 529,918 | 502,983 | 26,935 | 5.08% |
| `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv` | 288,602 | 252,972 | 35,630 | 12.35% |
| `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | 170,366 | 164,300 | 6,066 | 3.56% |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | 445,909 | 421,844 | 24,065 | 5.40% |
| `Wednesday-workingHours.pcap_ISCX.csv` | 692,703 | 610,794 | 81,909 | 11.82% |


---

## 2. Verified Exact Duplicate Columns Dropped (findings.md Step 5)

| Dropped Duplicate Column | Retained Primary Column | Verification Status |
|---|---|---|
| `Subflow Fwd Packets` | `Total Fwd Packets` | **100% Identical (VERIFIED)** |
| `Subflow Bwd Packets` | `Total Backward Packets` | **100% Identical (VERIFIED)** |
| `Fwd Header Length.1` | `Fwd Header Length` | **100% Identical (VERIFIED)** |


---

## 3. Evidence-Backed Preprocessing Rules Applied

1. **Label Normalization & Fixes (findings.md Step 0)**:
   - Applied label mapping rules including `DoS slowloris` -> `DoS`, `Bot` -> `Botnet`, and the 3 Web Attack variants containing `U+FFFD`.
   - Result: 0 unmapped rows (100.00% coverage).

2. **Constant Columns (findings.md Step 1)**:
   - Retained all constant/near-constant columns in dataset.
   - Listed under `drop_candidates` in `configs/datasets/cicids2017/schema.yaml` for Milestone 3 modeling evaluation.

3. **Missing Value Handling (findings.md Step 2)**:
   - Isolated to `Flow Bytes/s` (1,358 rows, 0.048%). Dropped row-level.

4. **Infinity Handling (findings.md Step 4)**:
   - Replaced `Inf` with 0 in `Flow Bytes/s` and `Flow Packets/s` (100% co-occurs with `Flow Duration == 0`).

5. **Sentinel Values in `Init_Win_bytes_*` (findings.md Step 4)**:
   - Preserved `-1` sentinels intact without clipping or imputing.

6. **Class Imbalance (findings.md Step 6)**:
   - Preserved original class ratios (no SMOTE/undersampling). Stratified 70/10/20 train/val/test split.

---

## 4. Final Split Summary

- **Train Split (70%):** 1,801,733 rows
- **Validation Split (10%):** 257,391 rows
- **Test Split (20%):** 514,781 rows
- **Feature Matrix Shape:** 75 features