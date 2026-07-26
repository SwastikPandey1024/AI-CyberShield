# AI CyberShield — Refactoring Progress

## REFACTOR 1: Externalize Feature & Label Metadata into Config ✅ COMPLETE

- [x] Create `configs/data_dictionary/features.yaml` — 29 feature definitions
- [x] Create `configs/data_dictionary/attack_mapping.yaml` — 17 label mappings + 9 category indices
- [x] Rewrite `ml/preprocessing/data_dictionary.py` to load from YAML at import time
- [x] Preserve backward compatibility: `CICIDS2017_FEATURES`, `CICIDS2017_LABEL_MAPPING`, `CATEGORY_TO_INDEX`
- [x] All 7 verification tests passed

## REFACTOR 2: Config-Driven Preprocessing Pipeline (In Progress)

### Step 1: Config paths updated ✅
- [x] Update `data_dictionary.py` default paths to `configs/datasets/cicids2017/`
- [x] Copy config files to new location

### Step 2: Complete features YAML ✅
- [x] Generate complete `features.yaml` with all 79 columns from actual CSV data
- [x] Auto-classify feature types (flow, time, flag, payload, subflow, etc.)
- [x] Auto-generate descriptions for each feature
- [x] Verify all 79 features load correctly

### Step 3: Update dataset_loader.py ✅
- [x] Add `load_with_standardisation()` method for config-driven column renaming
- [x] Add `load_and_validate()` convenience method
- [x] Integrate with `get_raw_to_canonical_mapping()` from data_dictionary

### Step 4: Update dataset_validator.py ✅
- [x] Add `use_catalogue=True` parameter to `validate()` method
- [x] Auto-build expected_columns and schema from feature catalogue
- [x] Ensure validation is always consistent with data dictionary

### Step 5: Create preprocessing configs ✅
- [x] Create `configs/preprocessing/cleaning.yaml` — NaN handling, infinite value strategy
- [x] Create `configs/preprocessing/feature_selection.yaml` — feature groups, correlation thresholds
- [x] Create `configs/preprocessing/scaling.yaml` — scaler type per feature group
- [x] Create `configs/preprocessing/__init__.py` — config loader with `load_config()` helper
- [x] Verify all 3 config files load correctly via `load_config()`

## REFACTOR 3: Config-Driven Model Training (Pending)

- [ ] Create `configs/training/model_params.yaml` — XGBoost hyperparameters
- [ ] Create `configs/training/cv.yaml` — cross-validation strategy
- [ ] Refactor `ml/training/` to be config-driven

## REFACTOR 4: Config-Driven Evaluation (Pending)

- [ ] Create `configs/evaluation/metrics.yaml` — metric definitions
- [ ] Create `configs/evaluation/thresholds.yaml` — pass/fail thresholds
- [ ] Refactor `ml/evaluation/` to be config-driven
