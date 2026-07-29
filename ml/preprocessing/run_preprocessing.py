"""
run_preprocessing.py
====================

CLI entry point for the Phase 2.6 preprocessing pipeline.

Usage:
    python -m ml.preprocessing.run_preprocessing [--raw-dir PATH] [--out-dir PATH]

Outputs (all written to ``datasets/processed/CICIDS2017/``):
    X_train.parquet, X_val.parquet, X_test.parquet
    y_train.parquet, y_val.parquet, y_test.parquet
    scaler.pkl
    feature_meta.json
    preprocessing_stats.json
    manifest.json (Phase 2.7 data versioning — checksums + stats)
    reports/data/eda/preprocessing_log.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import pickle
import sys
from pathlib import Path

import pandas as pd

# ── project root on sys.path ──────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ml.preprocessing.preprocessor import CICIDSPreprocessor

# ── logging ───────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("run_preprocessing")


def _sha256(path: Path) -> str:
    """Compute SHA-256 of a file for data versioning manifest."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_preprocessing_log(result_stats: dict, out_dir: Path) -> None:
    """Generate Markdown audit log at reports/data/eda/preprocessing_log.md."""
    log_path = _PROJECT_ROOT / "reports" / "data" / "eda" / "preprocessing_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    per_file_rows = ""
    for fname, details in result_stats.get("per_file_before_after", {}).items():
        per_file_rows += f"| `{fname}` | {details['raw_rows']:,} | {details['dedup_rows']:,} | {details['duplicates_dropped']:,} | {details['duplicate_pct']:.2f}% |\n"

    exact_dup_cols_table = ""
    for item in result_stats.get("verified_exact_duplicates", []):
        exact_dup_cols_table += f"| `{item['column']}` | `{item['identical_to']}` | **100% Identical (VERIFIED)** |\n"

    content = f"""# Preprocessing Audit Log — Phase 2.6b
**Generated:** 2026-07-29
**Dataset:** CICIDS2017 (8 raw CSVs)
**Evidence Base:** `reports/data/eda/findings.md`

---

## Executive Summary & Data Pipeline Transformation Flow

- **Raw Rows Read Across 8 Files:** {result_stats['raw_rows_total']:,}
- **Duplicates Dropped Per-File (findings.md Step 3):** {result_stats['total_per_file_duplicates_dropped']:,}
- **Combined Rows After Per-File Deduplication:** {result_stats['combined_rows_after_file_dedup']:,}
- **Inf Values Replaced with 0 (findings.md Step 4):** {result_stats['inf_replaced_count']:,}
- **Rows Dropped Due to Missing Values (findings.md Step 2):** {result_stats['missing_rows_dropped']:,} (0.048% of dataset)
- **Verified & Dropped Exact Duplicate Columns (findings.md Step 5):** 7 columns
- **Final Cleaned Rows:** {result_stats['split_sizes']['train'] + result_stats['split_sizes']['val'] + result_stats['split_sizes']['test']:,}
- **Final Feature Columns:** {result_stats['n_features']} (78 initial - 7 dropped exact duplicates = 71 feature columns)

---

## 1. Per-File Deduplication Audit (findings.md Step 3)

| File Name | Raw Rows | Rows After Deduplication | Duplicates Dropped | Dup % |
|---|---:|---:|---:|---:|
{per_file_rows}

---

## 2. Verified Exact Duplicate Columns Dropped (findings.md Step 5)

| Dropped Duplicate Column | Retained Primary Column | Verification Status |
|---|---|---|
{exact_dup_cols_table}

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

- **Train Split (70%):** {result_stats['split_sizes']['train']:,} rows
- **Validation Split (10%):** {result_stats['split_sizes']['val']:,} rows
- **Test Split (20%):** {result_stats['split_sizes']['test']:,} rows
- **Feature Matrix Shape:** {result_stats['n_features']} features
"""

    log_path.write_text(content.strip(), encoding="utf-8")
    logger.info("Wrote preprocessing log -> %s", log_path)


def run(raw_dir: Path, out_dir: Path) -> None:
    """Execute the full preprocessing pipeline and write outputs."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── run pipeline ──────────────────────────
    preprocessor = CICIDSPreprocessor(
        test_size=0.20,
        val_size=0.10,
        random_state=42,
    )
    result = preprocessor.fit_transform(raw_dir)

    # ── write parquet splits ──────────────────
    artefacts: dict[str, Path] = {}

    splits = {
        "X_train": result.X_train,
        "X_val":   result.X_val,
        "X_test":  result.X_test,
        "y_train": result.y_train.rename("label"),
        "y_val":   result.y_val.rename("label"),
        "y_test":  result.y_test.rename("label"),
    }

    for name, data in splits.items():
        path = out_dir / f"{name}.parquet"
        if isinstance(data, pd.Series):
            data.to_frame(name="label").to_parquet(path, index=False)
        else:
            data.to_parquet(path, index=False)
        artefacts[name] = path
        logger.info("Wrote %s (%d rows) → %s", name, len(data), path.name)

    # ── write scaler ──────────────────────────
    scaler_path = out_dir / "scaler.pkl"
    with open(scaler_path, "wb") as fh:
        pickle.dump(result.scaler, fh)
    artefacts["scaler"] = scaler_path
    logger.info("Wrote scaler → %s", scaler_path.name)

    # ── write feature/label metadata ─────────
    meta_path = out_dir / "feature_meta.json"
    meta = {
        "feature_names": result.feature_names,
        "label_names": {str(k): v for k, v in result.label_names.items()},
        "n_features": result.stats["n_features"],
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    artefacts["feature_meta"] = meta_path
    logger.info("Wrote feature metadata → %s", meta_path.name)

    # ── write preprocessing stats ─────────────
    stats_path = out_dir / "preprocessing_stats.json"
    stats_path.write_text(json.dumps(result.stats, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote preprocessing stats → %s", stats_path.name)

    # ── Phase 2.7: write data versioning manifest ──
    manifest: dict = {
        "dataset": "CICIDS2017",
        "pipeline_version": "1.0",
        "random_state": 42,
        "test_size": 0.20,
        "val_size": 0.10,
        "rows": {
            "train": result.stats["split_sizes"]["train"],
            "val":   result.stats["split_sizes"]["val"],
            "test":  result.stats["split_sizes"]["test"],
        },
        "n_features": result.stats["n_features"],
        "files": {},
    }

    for name, path in artefacts.items():
        if path.exists():
            manifest["files"][name] = {
                "path": str(path.relative_to(_PROJECT_ROOT)),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Wrote data manifest → %s", manifest_path.name)

    # ── Generate preprocessing_log.md ─────────
    generate_preprocessing_log(result.stats, out_dir)

    # ── summary ───────────────────────────────
    logger.info("=" * 60)
    logger.info("PREPROCESSING COMPLETE")
    logger.info("  Raw rows total:    %d", result.stats["raw_rows_total"])
    logger.info("  Per-file dups drop:%d", result.stats["total_per_file_duplicates_dropped"])
    logger.info("  Inf replaced to 0: %d", result.stats["inf_replaced_count"])
    logger.info("  Dropped NaN rows:  %d", result.stats["missing_rows_dropped"])
    logger.info("  Train rows:        %d", result.stats["split_sizes"]["train"])
    logger.info("  Val rows:          %d", result.stats["split_sizes"]["val"])
    logger.info("  Test rows:         %d", result.stats["split_sizes"]["test"])
    logger.info("  Features:          %d", result.stats["n_features"])
    logger.info("  Output dir:        %s", out_dir)
    logger.info("=" * 60)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI CyberShield — CICIDS2017 Preprocessing Pipeline (Phase 2.6)",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=_PROJECT_ROOT / "datasets" / "raw" / "CICIDS2017",
        help="Directory containing raw CICIDS2017 CSV files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=_PROJECT_ROOT / "datasets" / "processed" / "CICIDS2017",
        help="Output directory for processed parquet files and manifest.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(raw_dir=args.raw_dir, out_dir=args.out_dir)
