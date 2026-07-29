# Phase 2.5 — Evidence-Driven EDA Findings
# AI CyberShield - CICIDS2017

**Generated:** 2026-07-29
**Script:** `_eda_diagnostics.py` (run with `PYTHONUTF8=1`, output captured to `eda_raw_output.txt`)
**Data source:** 8 real CICIDS2017 CSVs in `datasets/raw/CICIDS2017/`
**Profiling source:** per-file `summary.json` reports in `reports/data/profiling/`

All numbers in this document were computed fresh in this session against the real data.
No number is restated from conversation history without independent verification.

---

## Dataset Overview (from profiling reports)

| File | Rows | Columns | Duplicates | Dup % | Missing Cells |
|------|------|---------|------------|-------|---------------|
| Friday-WorkingHours-Afternoon-DDos | 225,745 | 79 | 2,633 | 1.17% | 4 |
| Friday-WorkingHours-Afternoon-PortScan | 286,467 | 79 | 72,353 | 25.26% | 15 |
| Friday-WorkingHours-Morning | 191,033 | 79 | 6,888 | 3.61% | 28 |
| Monday-WorkingHours | 529,918 | 79 | 26,935 | 5.08% | 64 |
| Thursday-WorkingHours-Afternoon-Infilteration | 288,602 | 79 | 35,630 | 12.35% | 18 |
| Thursday-WorkingHours-Morning-WebAttacks | 170,366 | 79 | 6,066 | 3.56% | 20 |
| Tuesday-WorkingHours | 445,909 | 79 | 24,065 | 5.40% | 201 |
| Wednesday-workingHours | 692,703 | 79 | 81,909 | 11.82% | 1,008 |
| **TOTAL** | **2,830,743** | **79** | **256,479** | **9.06%** | **1,358** |

---

## Step 0 — Attack Label Mapping Verification (Blocking Check)

**Method:** `_eda_diagnostics.py` reads every row of all 8 CSVs with `errors="replace"` via
`csv.reader`, extracts the label column index by case-insensitive "label" search, and
compares each value (repr + codepoints) against `attack_mapping.yaml` keys.

### YAML keys and their codepoints (from `attack_mapping.yaml`)

All 17 keys in `label_to_category` are pure ASCII. No em-dash, no separator other than
plain space (0x20). The `Web Attack` keys are: `Web Attack Brute Force`,
`Web Attack XSS`, `Web Attack Sql Injection` — with plain spaces between all words.

### Unique label values found in the raw CSVs

**Total rows scanned:** 2,830,743
**Unique label values:** 15

| Label (repr) | Count | % | Mapped? | Note |
|---|---:|---:|---|---|
| BENIGN | 2,273,097 | 80.30% | YES | |
| DoS Hulk | 231,073 | 8.16% | YES | |
| PortScan | 158,930 | 5.61% | YES | |
| DDoS | 128,027 | 4.52% | YES | |
| DoS GoldenEye | 10,293 | 0.36% | YES | |
| FTP-Patator | 7,938 | 0.28% | YES | |
| SSH-Patator | 5,897 | 0.21% | YES | |
| DoS slowloris | 5,796 | 0.20% | **NO** | lowercase 's' — YAML has `DoS Slowloris` |
| DoS Slowhttptest | 5,499 | 0.19% | YES | |
| Bot | 1,966 | 0.07% | **NO** | YAML has `Botnet`, not `Bot` |
| Web Attack [U+FFFD] Brute Force | 1,507 | 0.05% | **NO** | separator is non-UTF-8 byte |
| Web Attack [U+FFFD] XSS | 652 | 0.02% | **NO** | same encoding issue |
| Infiltration | 36 | 0.00% | YES | |
| Web Attack [U+FFFD] Sql Injection | 21 | 0.00% | **NO** | same encoding issue |
| Heartbleed | 11 | 0.00% | YES | |

**Total unmatched rows: 9,942 (0.35%)**

### Confirmed mismatches — three distinct root causes

**1. Case mismatch — `DoS slowloris` (5,796 rows)**
- CSV codepoints: 0x44 0x6f 0x53 0x20 0x73 0x6c 0x6f 0x77 0x6c 0x6f 0x72 0x69 0x73
- That is literally `DoS slowloris` — lowercase 's' in `slowloris`
- YAML key: `DoS Slowloris` — capital 'S'
- Fix required: add `DoS slowloris` as a key in `attack_mapping.yaml`, or normalise
  to title-case before lookup. **A decision is needed here.**

**2. Name mismatch — `Bot` (1,966 rows)**
- CSV codepoints: 0x42 0x6f 0x74 — literally `Bot`
- YAML key: `Botnet`
- Fix required: add `Bot` as a key mapping to `Botnet` category, or rename YAML key.
  **A decision is needed here.**

**3. Encoding issue — Web Attack labels (2,180 rows total)**
- The raw CSV bytes for the separator between "Web Attack" and "Brute Force"/"XSS"/
  "Sql Injection" are not valid UTF-8. Reading with `errors="replace"` produces U+FFFD.
- The actual byte(s) are not yet identified from this read alone. Most likely this is
  an em-dash (U+2014, encoded as 0xe2 0x80 0x94 in UTF-8, or 0x97 in Windows-1252).
- The YAML keys use plain spaces only (`Web Attack Brute Force`).
- **Two sub-questions need answering before fixing:**
  a. What are the exact raw bytes in the CSV for this separator?
  b. Should YAML be updated to match CSV, or should the loader normalise the separator?

> **BLOCKING:** `attack_mapping.yaml` cannot be treated as reliable for `DoS slowloris`,
> `Bot`, or any Web Attack label until these three mismatches are resolved. Any pipeline
> using `label_to_category` mapping today will silently drop 9,942 rows (0.35%) with
> no error raised.

---

## Step 1 — Constant / Near-Constant Column Investigation

**Method:** Pulled `unique_count` from each file's `summary.json`. A column is flagged
constant if `unique_count <= 1` in that file.

### Columns constant in ALL 8 files (feature_type: bulk)

| Column | Feature Type |
|--------|-------------|
| Bwd Avg Bulk Rate | bulk |
| Bwd Avg Bytes/Bulk | bulk |
| Bwd Avg Packets/Bulk | bulk |
| Fwd Avg Bulk Rate | bulk |
| Fwd Avg Bytes/Bulk | bulk |
| Fwd Avg Packets/Bulk | bulk |

### Columns constant in ALL 8 files (feature_type: flag)

| Column | Feature Type |
|--------|-------------|
| Bwd PSH Flags | flag |
| Bwd URG Flags | flag |

### Columns constant in 7/8 files

| Column | Feature Type |
|--------|-------------|
| CWE Flag Count | flag |
| Fwd URG Flags | flag |

### Note: Label constant in 1/8 files
Monday-WorkingHours is 100% BENIGN traffic — Label has unique_count=1 in that file only.
This is expected and not a data quality issue.

### Plausible explanations
- **Bulk stat columns (6):** CICFlowMeter only populates bulk stats when TCP bulk transfer
  mode triggers. CICIDS2017 capture conditions appear to never have triggered this code
  path, leaving all 6 columns zero throughout. This is a CICFlowMeter extraction artefact.
- **Bwd PSH Flags / Bwd URG Flags:** URG is rarely set in practice; PSH in the backward
  direction being universally zero is consistent with CICFlowMeter session direction
  conventions.
- **CWE Flag Count / Fwd URG Flags (7/8):** One file has a non-zero value, confirming
  these columns are not permanently broken — they occasionally capture real data.

> **Preprocessing consideration (not a decision):** The 8 columns constant across all
> 8 files are candidates for removal before model training. `CWE Flag Count` and
> `Fwd URG Flags` are non-constant in at least one file and need separate treatment.
> No action taken in this phase.

---

## Step 2 — Missing Value Pattern Analysis

**Method:** Per-column `missing_count` and `missing_ratio` from each file's `summary.json`.

### Finding: Missing values are in ONE column only — `Flow Bytes/s`

All other 78 columns are complete across all 8 files.

| File | Flow Bytes/s missing | Missing ratio |
|------|----------------------:|---------------|
| Friday-WorkingHours-Afternoon-DDos | 4 | 0.0018% |
| Friday-WorkingHours-Afternoon-PortScan | 15 | 0.0052% |
| Friday-WorkingHours-Morning | 28 | 0.0147% |
| Monday-WorkingHours | 64 | 0.0121% |
| Thursday-WorkingHours-Afternoon-Infilteration | 18 | 0.0062% |
| Thursday-WorkingHours-Morning-WebAttacks | 20 | 0.0117% |
| Tuesday-WorkingHours | 201 | 0.0451% |
| Wednesday-workingHours | 1,008 | 0.1455% |
| **Total** | **1,358** | **0.048% of all rows** |

Missing values appear in all 8 files, concentrated in `Flow Bytes/s`. This column also
has infinity values (see Step 4). The formula `Flow Bytes/s = Total Bytes / Flow Duration`
produces Inf when duration=0 and NaN when both numerator and denominator are 0 — both
anomaly types share the same root cause.

> **Preprocessing consideration:** 1,358 missing rows are trivially small (0.048%).
> Imputation or row-dropping are both defensible. The right choice depends on whether
> this column is retained after the Step 4 Infinity analysis.

---

## Step 3 — Duplicate Row Investigation

**Method:** Per-file duplicate counts from `summary.json` (`total_duplicate_rows` uses
pandas `keep='first'` semantics). Class breakdown computed by loading Friday-DDos via
pandas with `keep=False`.

### Per-file duplicate counts

| File | Rows | Duplicate Rows | Dup % |
|------|------|---------------|-------|
| Friday-WorkingHours-Afternoon-DDos | 225,745 | 2,633 | 1.17% |
| Friday-WorkingHours-Afternoon-PortScan | 286,467 | 72,353 | **25.26%** |
| Friday-WorkingHours-Morning | 191,033 | 6,888 | 3.61% |
| Monday-WorkingHours | 529,918 | 26,935 | 5.08% |
| Thursday-WorkingHours-Afternoon-Infilteration | 288,602 | 35,630 | **12.35%** |
| Thursday-WorkingHours-Morning-WebAttacks | 170,366 | 6,066 | 3.56% |
| Tuesday-WorkingHours | 445,909 | 24,065 | 5.40% |
| Wednesday-workingHours | 692,703 | 81,909 | **11.82%** |
| **TOTAL** | **2,830,743** | **256,479** | **9.06%** |

### Class breakdown — Friday-DDos file (keep=False: all copies counted)

Total duplicate rows: 3,940 (1.75% of file)

| Class | Total rows | Duplicated rows | % of class duplicated |
|-------|---:|---:|---:|
| BENIGN | 97,718 | 3,920 | 4.0% |
| DDoS | 128,027 | 20 | 0.0% |

### Observations
- Duplicate rates range from 1.17% to 25.26% — the PortScan file is a major outlier.
- In the Friday-DDos file, 99.5% of duplicate rows are BENIGN. DDoS attack rows are
  essentially never duplicated (20 of 128,027). This suggests duplicates arise from
  repeated baseline traffic captures, not labelling artefacts.
- The overall 9.06% aggregate rate (256,479 rows) is much higher than the single-file
  figure mentioned in earlier profiling work — that reflected one file only.

> **Preprocessing consideration:** Whether to drop duplicates depends on whether they
> represent genuine repeated flows (valid training signal) or measurement artefacts.
> Given BENIGN concentration, dropping all duplicates would reduce class imbalance
> slightly. This is a decision for the Tech Lead. No de-duplication is performed here.

---

## Step 4 — Infinity and Negative Value Root Cause

**Method:** pandas load of each file; `isin([inf, -inf])` on `Flow Bytes/s`;
`Flow Duration == 0` mask; co-occurrence count; negative value check on all numeric cols.

### Infinity co-occurrence with Flow Duration == 0

**Finding: 100% co-occurrence in every single file.**

| File | Inf in Flow Bytes/s | Flow Duration==0 rows | Co-occurrence % |
|------|-----------------------:|------------------------:|---:|
| Friday-WorkingHours-Afternoon-DDos | 30 | 34 | 100% |
| Friday-WorkingHours-Afternoon-PortScan | 356 | 371 | 100% |
| Friday-WorkingHours-Morning | 94 | 122 | 100% |
| Monday-WorkingHours | 373 | 437 | 100% |
| Thursday-WorkingHours-Afternoon-Infilteration | 189 | 207 | 100% |
| Thursday-WorkingHours-Morning-WebAttacks | 115 | 135 | 100% |
| Tuesday-WorkingHours | 63 | 264 | 100% |
| Wednesday-workingHours | 289 | 1,297 | 100% |

Root cause confirmed: `Flow Bytes/s = Total Bytes / Flow Duration`. Division by zero in
floating-point produces Inf. CICFlowMeter generates zero-duration flows for packets where
start and end timestamps are identical (instantaneous captures).

Note: `Flow Duration==0` rows exceed Inf rows in several files (e.g. Wednesday: 1,297 vs
289). Zero-duration flows with zero bytes produce NaN — these are the 1,358 missing values
in `Flow Bytes/s` (Step 2). Both anomalies share the same root cause.

### Negative values — dominant pattern: `Init_Win_bytes_*`

| File | Init_Win_bytes_backward neg % | Init_Win_bytes_forward neg % |
|------|---:|---:|
| Friday-WorkingHours-Afternoon-DDos | 39.1% | 14.6% |
| Friday-WorkingHours-Afternoon-PortScan | 26.9% | 21.0% |
| Friday-WorkingHours-Morning | 62.0% | 50.2% |
| Monday-WorkingHours | 56.4% | 42.4% |
| Thursday-WorkingHours-Afternoon-Infilteration | 56.9% | 35.5% |
| Thursday-WorkingHours-Morning-WebAttacks | 60.1% | 48.1% |
| Tuesday-WorkingHours | 57.5% | 44.9% |
| Wednesday-workingHours | 48.4% | 29.3% |

These represent TCP initial window size. CICFlowMeter stores `-1` as a sentinel for
"window size not observed" (no SYN captured, or non-TCP flow). This is a feature semantics
issue — `-1` is an intentional sentinel, not corruption.

### Negative values — minor columns (small counts, consistent across files)

- `Flow IAT Min`: up to 749 rows per file — physically impossible negative IAT,
  likely a CICFlowMeter timestamp precision bug
- `Fwd Header Length`, `Fwd Header Length.1`, `min_seg_size_forward`, `Bwd Header Length`:
  1–23 rows per file — likely CICFlowMeter measurement artefacts
- `Flow Duration`, `Flow Packets/s`, `Flow IAT Mean`, `Flow IAT Max`, `Flow Bytes/s`:
  2–36 rows per file — likely overflow or sign-bit artefacts in duration computation

> **Preprocessing considerations (not decisions):**
> 1. `Init_Win_bytes_*` sentinel (-1): Options include keeping as-is, treating -1 as a
>    categorical indicator (TCP vs non-TCP flows), or imputing. Dropping rows would
>    eliminate 30-62% of some files.
> 2. Infinity in `Flow Bytes/s`/`Flow Packets/s`: These rows correspond to zero-duration
>    flows. The column could be dropped, capped, or these rows filtered.
> 3. Minor negative columns: Likely safe to clip to 0, but the root cause should confirm
>    whether the column is worth retaining at all.
> No imputation, clipping, or dropping is performed in this phase.

---

## Step 5 — Correlation Findings

**Method:** Pearson correlation matrix on numeric columns of Friday-DDos file only (first
file, by script design). Upper triangle filtered to |r| > 0.9.

**Friday-WorkingHours-Afternoon-DDos: 89 highly correlated pairs (|r| > 0.9)**

Top 15 by |r|:

| Column A | Column B | r | Classification |
|---|---|---:|---|
| Total Fwd Packets | Subflow Fwd Packets | 1.0000 | EXPLAINABLE: exact duplicate |
| Total Backward Packets | Subflow Bwd Packets | 1.0000 | EXPLAINABLE: exact duplicate |
| Total Length of Fwd Packets | Subflow Fwd Bytes | 1.0000 | EXPLAINABLE: exact duplicate |
| Total Length of Bwd Packets | Subflow Bwd Bytes | 1.0000 | EXPLAINABLE: exact duplicate |
| Fwd Packet Length Mean | Avg Fwd Segment Size | 1.0000 | EXPLAINABLE: exact duplicate |
| Bwd Packet Length Mean | Avg Bwd Segment Size | 1.0000 | EXPLAINABLE: exact duplicate |
| Fwd PSH Flags | SYN Flag Count | 1.0000 | NOT OBVIOUS: possible DDoS traffic artefact |
| Fwd Header Length | Fwd Header Length.1 | 1.0000 | EXPLAINABLE: CICFlowMeter duplicate column |
| RST Flag Count | ECE Flag Count | 1.0000 | NOT OBVIOUS: possible DDoS traffic artefact |
| Packet Length Mean | Average Packet Size | 0.9994 | NOT OBVIOUS: likely definitionally equivalent |
| Flow IAT Max | Idle Max | 0.9973 | NOT OBVIOUS: timing relationship |
| Flow Duration | Fwd IAT Total | 0.9971 | NOT OBVIOUS: total IAT ~ duration |
| Flow IAT Max | Fwd IAT Max | 0.9953 | NOT OBVIOUS |
| Fwd IAT Max | Idle Max | 0.9930 | NOT OBVIOUS |
| Bwd Packet Length Max | Bwd Packet Length Std | 0.9927 | NOT OBVIOUS |

### Confirmed exact duplicate columns (r = 1.0000, CICFlowMeter definition)
1. Subflow Fwd Packets = Total Fwd Packets
2. Subflow Bwd Packets = Total Backward Packets
3. Subflow Fwd Bytes = Total Length of Fwd Packets
4. Subflow Bwd Bytes = Total Length of Bwd Packets
5. Avg Fwd Segment Size = Fwd Packet Length Mean
6. Avg Bwd Segment Size = Bwd Packet Length Mean
7. Fwd Header Length.1 = Fwd Header Length (literal CICFlowMeter duplicate column bug)

### Caveat on scope
Correlation analysis ran on Friday-DDos only (the script has `break` after the first file).
DDoS traffic is highly homogeneous — r=1.0 pairs like `Fwd PSH Flags` vs `SYN Flag Count`
are specific to DDoS attack behaviour in this file. These pairs may not hold across files
with more diverse traffic. The 89 pairs here should not be treated as a dataset-wide claim.

> **Preprocessing consideration:** 7 confirmed exact duplicate columns can be removed
> without information loss. Decisions about non-obvious pairs should wait for a full-
> dataset correlation analysis. No feature removal is performed in this phase.

---

## Step 6 — Class Imbalance Characterization

**Method:** Aggregate `Label` value counts across all 8 files via pandas `value_counts()`.
Imbalance ratio = majority count / minority count.

**Note:** Counts include 9,942 currently-unmapped rows (Step 0).

### Aggregate class distribution — all 8 files

| Class (raw label) | Count | Ratio |
|---|---:|---:|
| BENIGN | 2,273,097 | 80.30% |
| DoS Hulk | 231,073 | 8.16% |
| PortScan | 158,930 | 5.61% |
| DDoS | 128,027 | 4.52% |
| DoS GoldenEye | 10,293 | 0.36% |
| FTP-Patator | 7,938 | 0.28% |
| SSH-Patator | 5,897 | 0.21% |
| DoS slowloris [UNMAPPED] | 5,796 | 0.20% |
| DoS Slowhttptest | 5,499 | 0.19% |
| Bot [UNMAPPED] | 1,966 | 0.07% |
| Web Attack Brute Force [UNMAPPED - encoding] | 1,507 | 0.05% |
| Web Attack XSS [UNMAPPED - encoding] | 652 | 0.02% |
| Infiltration | 36 | 0.00% |
| Web Attack Sql Injection [UNMAPPED - encoding] | 21 | 0.00% |
| Heartbleed | 11 | 0.00% |

**Imbalance ratio (majority / minority):** 2,273,097 / 11 = **206,645x**

### Classes with < 1,000 samples — stratified splitting concern

| Class | Count | % |
|---|---:|---:|
| Heartbleed | 11 | 0.0004% |
| Web Attack Sql Injection | 21 | 0.0007% |
| Infiltration | 36 | 0.0013% |
| Web Attack XSS | 652 | 0.0230% |

### Observations
- BENIGN dominates at 80.3%. Accuracy is not a useful metric — a naive all-BENIGN
  classifier scores 80%.
- Top 4 attack classes (DoS Hulk, PortScan, DDoS, DoS GoldenEye) = 18.7% of all rows.
- Heartbleed (11 rows) and Infiltration (36 rows) are functionally unlearnable at this
  sample size. Stratified splitting would produce 2-7 test samples of these classes.
- The 206,645x imbalance ratio is extreme. Standard splitting without stratification has
  meaningful probability of zero Heartbleed samples in either split.

> **Preprocessing consideration:** Class imbalance requires deliberate handling before
> model training. Options: SMOTE/oversampling, BENIGN undersampling, class-weighted loss,
> or merging very small classes into a catch-all. The choice is a modeling decision
> deferred to Tech Lead review. No resampling performed in this phase.

---

## Summary of Blocking Items

The following require Tech Lead decisions before Phase 2.6 can start:

| # | Issue | Rows Affected | Action Required |
|---|-------|---:|---|
| 1 | `DoS slowloris` case mismatch — lowercase 's' in CSV, uppercase in YAML | 5,796 | Decision: add alias to YAML or normalise at load time |
| 2 | `Bot` label not in YAML (YAML has `Botnet`) | 1,966 | Decision: add `Bot` alias or rename YAML key |
| 3 | Web Attack labels contain non-UTF-8 byte separator; YAML uses plain spaces | 2,180 | Prerequisite: identify actual raw bytes; then decide YAML vs loader fix |
| 4 | Web Attack byte identification | prerequisite for #3 | One targeted hexdump of Thursday-WebAttacks CSV is sufficient |

**Total rows currently unmapped and silently failing: 9,942 (0.35%)**

## Summary of Non-Blocking Findings (for preprocessing planning)

| Finding | Key Number | Preprocessing Consideration |
|---------|-----------|------------------------------|
| 8 columns constant across all 8 files | 6 bulk + 2 flag | Candidates for removal; CWE Flag Count and Fwd URG Flags need separate treatment |
| Missing values | 1,358 rows, Flow Bytes/s only | Trivially small; impute or drop per column retention decision |
| Duplicates | 256,479 rows (9.06% overall); PortScan 25.26% worst | BENIGN-concentrated; decision on whether to drop needed |
| Infinity in Flow Bytes/s | 100% co-occurrence with Flow Duration==0 (causal) | Cap, impute, or drop the column |
| Init_Win_bytes_* negative sentinel (-1) | 30-62% of rows per file | Semantically valid sentinel; needs explicit handling strategy |
| Minor negative columns (Flow IAT Min etc.) | < 0.15% of rows | Likely safe to clip to 0 |
| 7 confirmed exact duplicate columns | r=1.0000, CICFlowMeter definition | Safe to remove; Tech Lead sign-off needed |
| 206,645x class imbalance | 4 classes < 1,000 samples | Technique choice is a modeling decision |

---

*Phase 2.5 complete. Phase 2.6 (Preprocessing Pipeline) is BLOCKED pending Tech Lead
review of this document and resolution of the 4 blocking items listed above.*

---

## Addendum — Web Attack Separator Byte Identification (Step 0 follow-up)

**Verified:** 2026-07-29 via direct binary read of Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv

Raw bytes of label field at first Web Attack row (row 12,637):
  hex: 57 65 62 20 41 74 74 61 63 6b 20 ef bf bd 20 42 72 75 74 65 20 46 6f 72 63 65

The separator bytes are `0xef 0xbf 0xbd` — which is the UTF-8 encoding of **U+FFFD**
(Unicode Replacement Character, displayed as `▓`).

**Critical finding:** The CSV file was **already corrupted at source**. The CICIDS2017
dataset was generated with a character that was itself already the Unicode replacement
character at the time the CSV was written. This is not an encoding mismatch between the
file and our reader — the file literally contains U+FFFD as a separator.

This means the YAML keys (`Web Attack Brute Force`, etc.) are wrong *in their current
form* — they assume plain spaces only. The actual label values in the file are
`Web Attack \ufffd Brute Force`, `Web Attack \ufffd XSS`, `Web Attack \ufffd Sql Injection`.

**Two options for resolution (decision required):**

Option A — Update `attack_mapping.yaml` keys to include the U+FFFD character:
  ```yaml
  Web Attack \ufffd Brute Force: WebAttack
  Web Attack \ufffd XSS: WebAttack
  Web Attack \ufffd Sql Injection: WebAttack
  ```
  Pro: YAML exactly matches what is in the CSV. Con: YAML file contains a non-printing
  character that is confusing to humans editing it.

Option B — Add a normalisation step in the data loading or label-mapping pipeline that
  strips or replaces U+FFFD in label values before mapping:
  ```python
  label = label.replace('\ufffd', '').strip()
  # or: label = label.replace('\ufffd', '-')
  ```
  Pro: YAML stays human-readable. Con: adds label-specific logic to the loader.

Either option is valid. A third option — treating these as a separate "Web Attack" category
with their own YAML keys using the actual character — is equivalent to Option A.

The Tech Lead must decide which approach to use before `attack_mapping.yaml` is patched.
