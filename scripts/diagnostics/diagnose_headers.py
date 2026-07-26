"""Step 1 — Diagnose raw header variations across all 8 CICIDS2017 CSV files."""
import csv
from pathlib import Path

dataset_dir = Path("datasets/raw/CICIDS2017")
files = sorted(dataset_dir.glob("*.csv"))

print("=" * 90)
print("STEP 1 — RAW HEADER DIAGNOSTIC")
print("=" * 90)
print()
print(f"{'File':<55} {'Raw \"Label\"-like header (repr)':<35}")
print("-" * 90)

for f in files:
    with open(f, "r", encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            header = []

    # Find any column that looks like 'Label' (case-insensitive, with possible whitespace)
    label_cols = [repr(col) for col in header if "label" in col.lower()]
    label_repr = label_cols[0] if label_cols else "NOT FOUND"

    print(f"{f.name:<55} {label_repr:<35}")

    # Also check ALL columns for variations
    print(f"  All columns ({len(header)} total):")
    for col in header:
        r = repr(col)
        # Flag anything with whitespace, odd casing, or non-standard chars
        flags = []
        if col != col.strip():
            flags.append("LEADING/TRAILING SPACE")
        if col != col.strip().lower().replace(" ", "_").replace(".", "_").replace("-", "_"):
            flags.append("NON-CANONICAL")
        if flags:
            print(f"    {r}  <-- {' | '.join(flags)}")
    print()
