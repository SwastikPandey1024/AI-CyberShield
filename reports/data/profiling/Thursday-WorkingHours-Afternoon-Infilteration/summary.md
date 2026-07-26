# Dataset Profile: Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv

*Generated: 2026-07-26 15:19:57 UTC*

## Dataset Summary

| Metric | Value |
|--------|-------|
| Rows | 288,602 |
| Columns | 79 |
| Memory Usage | 186.88 MB |
| Missing Cells | 18 (0.00%) |
| Duplicate Rows | 35,630 (12.35%) |

## Target Analysis

| Metric | Value |
|--------|-------|
| Target Column | Label |
| Number of Classes | 2 |
| Class Balance Ratio | 0.0001 |

### Class Distribution

| Class | Count | Ratio |
|-------|-------|-------|
| BENIGN | 288,566 | 99.9875% |
| Infiltration | 36 | 0.0125% |

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

- ⚠️ Severe class imbalance detected: ratio=0.0001. Consider resampling techniques.
- ⚠️ Column 'Bwd PSH Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd URG Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Bytes/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Packets/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Bulk Rate' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Bytes/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Packets/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Bulk Rate' is constant (single value). Consider dropping for modeling.
