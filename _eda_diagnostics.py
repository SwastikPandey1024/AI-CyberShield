"""Phase 2.5 — Evidence-Driven EDA: All diagnostic steps."""
import csv, yaml, json
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_ROOT / "datasets" / "raw" / "CICIDS2017"
REPORT_DIR = PROJECT_ROOT / "reports" / "data" / "profiling"
MAPPING_PATH = PROJECT_ROOT / "configs" / "datasets" / "cicids2017" / "attack_mapping.yaml"
FEATURES_PATH = PROJECT_ROOT / "configs" / "datasets" / "cicids2017" / "features.yaml"

files = sorted(DATASET_DIR.glob("*.csv"))

# Load mapping
with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    mapping = yaml.safe_load(f)
mapped_labels = set(mapping["label_to_category"].keys())

# Load features
with open(FEATURES_PATH, "r", encoding="utf-8") as f:
    features_config = yaml.safe_load(f)
feature_names = {f["name"] for f in features_config["features"]}

# ──────────────────────────────────────────────
# STEP 0 — Attack Label Mapping Verification
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 0 — ATTACK LABEL MAPPING VERIFICATION (byte-level)")
print("=" * 90)
print()

print("Mapping file keys (repr):")
for k in sorted(mapping["label_to_category"].keys()):
    codepoints = [hex(ord(c)) for c in k]
    print(f"  {repr(k):40s} codepoints: {codepoints}")
print()

all_labels = Counter()
total_rows = 0
file_label_counts = defaultdict(Counter)

for f in files:
    with open(f, "r", encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(fh)
        header = next(reader)
    label_idx = next((i for i, c in enumerate(header) if "label" in c.lower()), None)
    if label_idx is None:
        continue
    with open(f, "r", encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            if len(row) > label_idx:
                val = row[label_idx]
                all_labels[val] += 1
                file_label_counts[f.name][val] += 1
                total_rows += 1

print(f"Unique label values across ALL 8 files: {len(all_labels)}")
print()

unmatched_labels = {}
for val, cnt in sorted(all_labels.items(), key=lambda x: -x[1]):
    codepoints = [hex(ord(c)) for c in val]
    matched = val in mapped_labels
    if not matched:
        unmatched_labels[val] = cnt
    print(f"  {repr(val):45s} count={cnt:>8,} ({cnt/total_rows*100:5.2f}%)  mapped={matched}  codepoints={codepoints}")

total_unmatched = sum(unmatched_labels.values())
print(f"\nTotal rows: {total_rows:,}")
print(f"Total unmatched rows: {total_unmatched:,} ({total_unmatched/total_rows*100:.2f}%)")
if total_unmatched > 0:
    print("*** BLOCKING FINDING: Unmapped label values detected ***")
    for val, cnt in unmatched_labels.items():
        print(f"  {repr(val)}: {cnt:,} rows ({cnt/total_rows*100:.2f}%)")
else:
    print("All label values have exact matches in attack_mapping.yaml")
print()

# ──────────────────────────────────────────────
# STEP 1 — Constant / Near-Constant Column Investigation
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 1 — CONSTANT / NEAR-CONSTANT COLUMN INVESTIGATION")
print("=" * 90)
print()

# Load profiling summaries to find constant columns
constant_cols_across_files = defaultdict(list)
for f in files:
    file_name = f.stem
    summary_path = REPORT_DIR / file_name / "summary.json"
    if not summary_path.exists():
        # Try matching by file name pattern
        for subdir in REPORT_DIR.iterdir():
            if subdir.is_dir() and (subdir / "summary.json").exists():
                s = json.loads(open(subdir / "summary.json").read())
                if s.get("file_name", "").startswith(f.stem.split(".")[0]):
                    break
        else:
            continue
    else:
        s = json.loads(open(summary_path).read())

    for col in s.get("columns", []):
        if col.get("unique_count", 0) <= 1:
            constant_cols_across_files[col["column_name"]].append(file_name)

print("Columns that are constant (unique_count <= 1) in at least one file:")
for col_name, file_list in sorted(constant_cols_across_files.items()):
    num_files = len(file_list)
    all_files_flag = "ALL 8 FILES" if num_files == 8 else f"{num_files}/8 files"
    print(f"  {col_name:<35s} constant in {all_files_flag}")
    # Cross-reference with features.yaml
    if col_name in feature_names:
        feat = [f for f in features_config["features"] if f["name"] == col_name][0]
        print(f"    Description: {feat['description']}")
        print(f"    Feature type: {feat['feature_type']}")
    else:
        print(f"    NOT FOUND in features.yaml")
    print()

# ──────────────────────────────────────────────
# STEP 2 — Missing Value Pattern Analysis
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 2 — MISSING VALUE PATTERN ANALYSIS")
print("=" * 90)
print()

for f in files:
    file_name = f.stem
    summary_path = REPORT_DIR / file_name / "summary.json"
    if not summary_path.exists():
        continue
    s = json.loads(open(summary_path).read())

    missing_cols = [(c["column_name"], c["missing_count"], c["missing_ratio"])
                    for c in s.get("columns", []) if c["missing_count"] > 0]

    if missing_cols:
        print(f"{f.name}:")
        for col_name, mcount, mratio in missing_cols:
            print(f"  {col_name:<30s} missing={mcount:>8,} ({mratio*100:.4f}%)")
        print()

# ──────────────────────────────────────────────
# STEP 3 — Duplicate Row Investigation
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 3 — DUPLICATE ROW INVESTIGATION")
print("=" * 90)
print()

for f in files:
    file_name = f.stem
    summary_path = REPORT_DIR / file_name / "summary.json"
    if not summary_path.exists():
        continue
    s = json.loads(open(summary_path).read())

    dup_count = s.get("total_duplicate_rows", 0)
    dup_ratio = s.get("total_duplicate_ratio", 0)
    print(f"{f.name}: {dup_count:,} duplicate rows ({dup_ratio*100:.2f}%)")

# Load actual data to check duplicate class breakdown
print("\nDuplicate class breakdown (sampling first file with >0 duplicates):")
for f in files:
    df = pd.read_csv(f, low_memory=False)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    if "Label" not in df.columns:
        continue

    dup_mask = df.duplicated(keep=False)
    dup_count = dup_mask.sum()
    if dup_count > 0:
        dup_df = df[dup_mask]
        dup_class_dist = dup_df["Label"].value_counts()
        total_class_dist = df["Label"].value_counts()

        print(f"\n{f.name}:")
        print(f"  Total duplicate rows (keep=False): {dup_count:,} ({dup_count/len(df)*100:.2f}%)")
        print(f"  Class distribution of ALL rows:")
        for cls, cnt in total_class_dist.items():
            print(f"    {repr(cls):30s} {cnt:>8,}")
        print(f"  Class distribution of DUPLICATED rows:")
        for cls, cnt in dup_class_dist.items():
            pct = cnt / total_class_dist.get(cls, 1) * 100
            print(f"    {repr(cls):30s} {cnt:>8,} ({pct:.1f}% of this class)")
        break  # Just one file for detailed analysis
print()

# ──────────────────────────────────────────────
# STEP 4 — Infinity and Negative Value Root Cause
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 4 — INFINITY AND NEGATIVE VALUE ROOT CAUSE")
print("=" * 90)
print()

for f in files:
    df = pd.read_csv(f, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    if "Flow Bytes/s" not in df.columns or "Flow Duration" not in df.columns:
        continue

    # Check co-occurrence of infinity in Flow Bytes/s with Flow Duration == 0
    inf_mask = df["Flow Bytes/s"].isin([np.inf, -np.inf])
    zero_dur_mask = df["Flow Duration"] == 0

    inf_count = inf_mask.sum()
    inf_and_zero_dur = (inf_mask & zero_dur_mask).sum()
    cooccurrence_rate = inf_and_zero_dur / inf_count * 100 if inf_count > 0 else 0

    print(f"{f.name}:")
    print(f"  Flow Bytes/s infinity count: {inf_count:,}")
    print(f"  Flow Duration == 0 count: {zero_dur_mask.sum():,}")
    print(f"  Co-occurrence (infinity AND Flow Duration==0): {inf_and_zero_dur:,} ({cooccurrence_rate:.2f}%)")

    # Check negative values
    neg_cols = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                neg_cols.append((col, neg_count, neg_count/len(df)*100))

    if neg_cols:
        print(f"  Columns with negative values:")
        for col, ncount, npct in sorted(neg_cols, key=lambda x: -x[1]):
            print(f"    {col:<35s} {ncount:>8,} rows ({npct:.4f}%)")
    print()

# ──────────────────────────────────────────────
# STEP 5 — Correlation Findings
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 5 — CORRELATION FINDINGS (|r| > 0.9)")
print("=" * 90)
print()

for f in files:
    df = pd.read_csv(f, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        continue

    corr_matrix = numeric_df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    high_corr = [(col1, col2, upper.loc[col1, col2])
                 for col1 in upper.columns
                 for col2 in upper.index
                 if upper.loc[col1, col2] > 0.9 and not pd.isna(upper.loc[col1, col2])]

    if high_corr:
        print(f"{f.name}: {len(high_corr)} highly correlated pairs (|r| > 0.9)")
        for col1, col2, r in sorted(high_corr, key=lambda x: -x[2])[:15]:
            # Check if relationship is explainable by definition
            explainable = False
            # Check for arithmetic relationships
            if col1.replace(" ", "").replace(".", "") in col2.replace(" ", "").replace(".", "") or \
               col2.replace(" ", "").replace(".", "") in col1.replace(" ", "").replace(".", ""):
                explainable = True
            # Check for known derived pairs
            derived_pairs = [
                ("Fwd Packet Length Mean", "Avg Fwd Segment Size"),
                ("Bwd Packet Length Mean", "Avg Bwd Segment Size"),
                ("Total Fwd Packets", "Subflow Fwd Packets"),
                ("Total Backward Packets", "Subflow Bwd Packets"),
                ("Total Length of Fwd Packets", "Subflow Fwd Bytes"),
                ("Total Length of Bwd Packets", "Subflow Bwd Bytes"),
                ("Fwd Header Length", "Fwd Header Length.1"),
            ]
            for a, b in derived_pairs:
                if (col1 == a and col2 == b) or (col1 == b and col2 == a):
                    explainable = True
                    break

            flag = " [EXPLAINABLE - derived/duplicate feature]" if explainable else " [NOT OBVIOUSLY EXPLAINABLE]"
            print(f"    {col1:<35s} vs {col2:<35s} r={r:.4f}{flag}")
        print()
    break  # Just first file for correlation analysis
print()

# ──────────────────────────────────────────────
# STEP 6 — Class Imbalance Characterization
# ──────────────────────────────────────────────
print("=" * 90)
print("STEP 6 — CLASS IMBALANCE CHARACTERIZATION")
print("=" * 90)
print()

all_class_dist = Counter()
for f in files:
    df = pd.read_csv(f, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    if "Label" in df.columns:
        for val, cnt in df["Label"].value_counts().items():
            all_class_dist[val] += cnt

print("Aggregate class distribution across ALL 8 files:")
print(f"{'Class':<35s} {'Count':>10s} {'Ratio':>10s}")
print("-" * 55)
total = sum(all_class_dist.values())
for val, cnt in sorted(all_class_dist.items(), key=lambda x: -x[1]):
    ratio = cnt / total
    print(f"{repr(val):<35s} {cnt:>10,} {ratio:>10.4f}")

# Imbalance ratio
if all_class_dist:
    max_class = max(all_class_dist.values())
    min_class = min(all_class_dist.values())
    imbalance_ratio = max_class / min_class if min_class > 0 else float('inf')
    print(f"\nImbalance ratio (majority/minority): {imbalance_ratio:.2f}")
    print(f"Majority class count: {max_class:,}")
    print(f"Minority class count: {min_class:,}")

    # Flag classes with very few samples
    print(f"\nClasses with < 1000 samples (potential stratified splitting concern):")
    for val, cnt in sorted(all_class_dist.items(), key=lambda x: x[1]):
        if cnt < 1000:
            print(f"  {repr(val):35s} {cnt:>8,} ({cnt/total*100:.4f}%)")
print()
