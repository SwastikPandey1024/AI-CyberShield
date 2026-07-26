# Dataset Profile: Wednesday-workingHours.pcap_ISCX.csv

*Generated: 2026-07-26 15:18:44 UTC*

## Dataset Summary

| Metric | Value |
|--------|-------|
| Rows | 692,703 |
| Columns | 79 |
| Memory Usage | 449.16 MB |
| Missing Cells | 1,008 (0.00%) |
| Duplicate Rows | 81,909 (11.82%) |

## Target Analysis

| Metric | Value |
|--------|-------|
| Target Column | Label |
| Number of Classes | 6 |
| Class Balance Ratio | 0.0000 |

### Class Distribution

| Class | Count | Ratio |
|-------|-------|-------|
| BENIGN | 440,031 | 63.5238% |
| DoS Hulk | 231,073 | 33.3582% |
| DoS GoldenEye | 10,293 | 1.4859% |
| DoS slowloris | 5,796 | 0.8367% |
| DoS Slowhttptest | 5,499 | 0.7938% |
| Heartbleed | 11 | 0.0016% |

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

- ⚠️ Severe class imbalance detected: ratio=0.0000. Consider resampling techniques.
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
