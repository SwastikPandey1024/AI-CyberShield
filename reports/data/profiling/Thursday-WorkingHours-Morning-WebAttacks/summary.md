# Dataset Profile: Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv

*Generated: 2026-07-26 15:19:30 UTC*

## Dataset Summary

| Metric | Value |
|--------|-------|
| Rows | 170,366 |
| Columns | 79 |
| Memory Usage | 110.48 MB |
| Missing Cells | 20 (0.00%) |
| Duplicate Rows | 6,066 (3.56%) |

## Target Analysis

| Metric | Value |
|--------|-------|
| Target Column | Label |
| Number of Classes | 4 |
| Class Balance Ratio | 0.0001 |

### Class Distribution

| Class | Count | Ratio |
|-------|-------|-------|
| BENIGN | 168,186 | 98.7204% |
| Web Attack � Brute Force | 1,507 | 0.8846% |
| Web Attack � XSS | 652 | 0.3827% |
| Web Attack � Sql Injection | 21 | 0.0123% |

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
- ⚠️ Column 'Fwd URG Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd URG Flags' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'CWE Flag Count' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Bytes/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Packets/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Fwd Avg Bulk Rate' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Bytes/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Packets/Bulk' is constant (single value). Consider dropping for modeling.
- ⚠️ Column 'Bwd Avg Bulk Rate' is constant (single value). Consider dropping for modeling.
