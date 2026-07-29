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
    manifest.json            (Phase 2.7 data versioning — checksums + stats)
    preprocessing_stats.json (detailed pipeline statistics)
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
        data.to_frame() if isinstance(data, pd.Series) else data
        if isinstance(data, pd.Series):
            data.to_frame(name=name).to_parquet(path, index=False)
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

    # ── summary ───────────────────────────────
    logger.info("=" * 60)
    logger.info("PREPROCESSING COMPLETE")
    logger.info("  Raw rows:          %d", result.stats["raw_rows"])
    logger.info("  Dropped NaN rows:  %d", result.stats["rows_dropped_nan"])
    logger.info("  Dropped dup rows:  %d", result.stats["rows_dropped_duplicates"])
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
