# Phase 2.4.1 — Ingestion Normalization: Implementation Steps

## Step 1 — Diagnose ✅ (already done, results below)
```
File                                                    | Raw "Label"-like header (repr)
Monday-WorkingHours.pcap_ISCX.csv                       | ' Label'
Tuesday-WorkingHours.pcap_ISCX.csv                      | ' Label'
Wednesday-workingHours.pcap_ISCX.csv                    | ' Label'
Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv  | ' Label'
Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv | ' Label'
Friday-WorkingHours-Morning.pcap_ISCX.csv               | ' Label'
Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv        | ' Label'
Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv    | ' Label'
```
All 8 files have identical header structure: some columns have leading space, some don't. No case differences across files.

## Step 2 — Create `ml/preprocessing/column_normalizer.py`
- [x] Create `ColumnNormalizer` class with:
  - `normalize_column_name(name)`: strip whitespace, collapse internal whitespace runs
  - `normalize_columns(columns)`: apply to list
  - `build_column_mapping(columns)`: return {raw: canonical} dict
- [x] Remove `_canonical_name()` from `data_dictionary.py` and update callers

## Step 3 — Wire into `DatasetLoader.load()`
- [x] Apply `ColumnNormalizer().normalize_columns()` after `pd.read_csv()` in `_read_file()`
- [x] Log `build_column_mapping()` at DEBUG level

## Step 4 — Simplify `DatasetValidator`
- [x] Remove any fuzzy/multi-name matching for target column
- [x] Use exact lookup since loader now guarantees canonical names

## Step 5 — Audit `DataProfiler`
- [x] Verify no raw/uncanonicalized column name references (clean — uses `self._target_column` only)

## Step 6 — Regression test
- [x] Create `tests/test_column_normalization.py` with 4-header test

## Step 7 — Relocate diagnostic script
- [x] Create `scripts/diagnostics/` directory
- [x] Move `_diagnose_headers.py` → `scripts/diagnostics/diagnose_headers.py`

## Step 8 — Full regression validation
- [x] `python -m py_compile` on every touched file (all 7 files PASSED)
- [x] Run regression tests (ColumnNormalizer unit tests + integration tests PASSED)
- [ ] Run `run_profiling.py` against all 8 files (IN PROGRESS — 1/8 complete)
- [ ] Report findings
