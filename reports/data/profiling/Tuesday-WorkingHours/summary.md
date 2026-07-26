# Dataset Profile: Tuesday-WorkingHours.pcap_ISCX.csv

*Generated: 2026-07-26 15:17:40 UTC*

## Dataset Summary

| Metric | Value |
|--------|-------|
| Rows | 445,909 |
| Columns | 79 |
| Memory Usage | 288.81 MB |
| Missing Cells | 201 (0.00%) |
| Duplicate Rows | 24,065 (5.40%) |

## Target Analysis

| Metric | Value |
|--------|-------|
| Target Column | Label |
| Number of Classes | 3 |
| Class Balance Ratio | 0.0136 |

### Class Distribution

| Class | Count | Ratio |
|-------|-------|-------|
| BENIGN | 432,074 | 96.8973% |
| FTP-Patator | 7,938 | 1.7802% |
| SSH-Patator | 5,897 | 1.3225% |

## Data Quality Flags

| Flag | Status |
|------|--------|
| Missing Values | ⚠️ |
| Duplicates | ⚠️ |
| Infinite Values | ⚠️ |
| Negative Values | ⚠️ |
| Constant Columns | ⚠️ |
| High Cardinality | ✅ |

## Warnings

- ⚠️ Severe class imbalance detected: ratio=0.0136. Consider resampling techniques.
- ⚠️ Column 'Bwd PSH Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd URG Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd URG Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'CWE Flag Count' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Bytes/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Packets/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Bulk Rate' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Bytes/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Packets/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Bulk Rate' is constant (single value). Consider dropping for modeling.
