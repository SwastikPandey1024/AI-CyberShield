"""
run_training.py
===============

CLI entry point for Phase 3 model training.

Usage:
    python -m ml.training.run_training [--processed-dir PATH] [--artifact-dir PATH]

Loads preprocessed parquet splits produced by run_preprocessing.py, trains
an XGBoost classifier, evaluates on the validation set, and writes all
artefacts to ``ml/artifacts/<run_id>/``.
"""

from __future__ import annotations

import argparse
import json
import logging
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ml.training.trainer import CICIDSTrainer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("run_training")


def run(processed_dir: Path, artifact_dir: Path) -> None:
    """Load preprocessed data, train, and save artefacts."""

    # ── load splits ───────────────────────────
    logger.info("Loading splits from %s ...", processed_dir)
    X_train = pd.read_parquet(processed_dir / "X_train.parquet")
    X_val   = pd.read_parquet(processed_dir / "X_val.parquet")
    y_train = pd.read_parquet(processed_dir / "y_train.parquet").squeeze()
    y_val   = pd.read_parquet(processed_dir / "y_val.parquet").squeeze()

    with open(processed_dir / "feature_meta.json", encoding="utf-8") as fh:
        meta = json.load(fh)

    feature_names: list[str] = meta["feature_names"]
    label_names: dict[int, str] = {int(k): v for k, v in meta["label_names"].items()}
    n_classes = len(label_names)

    logger.info(
        "Splits loaded. Train: %d rows  Val: %d rows  Features: %d  Classes: %d",
        len(X_train), len(X_val), len(feature_names), n_classes,
    )

    # ── train ─────────────────────────────────
    trainer = CICIDSTrainer(
        n_classes=n_classes,
        random_state=42,
        n_jobs=-1,
        early_stopping=30,
        num_boost_round=500,
        verbose_eval=25,
    )

    result = trainer.train(X_train, y_train, X_val, y_val)

    # ── save artefacts ────────────────────────
    run_artifact_dir = artifact_dir / result.run_id
    model_path = trainer.save(
        result,
        out_dir=run_artifact_dir,
        feature_names=feature_names,
        label_names=label_names,
    )

    # Write a ``latest`` symlink-style redirect: a JSON pointer file
    latest_path = artifact_dir / "latest.json"
    latest_path.write_text(
        json.dumps({"run_id": result.run_id, "model_path": str(model_path)}, indent=2),
        encoding="utf-8",
    )

    # ── summary ───────────────────────────────
    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("  Run ID:           %s", result.run_id)
    logger.info("  Best iteration:   %d", result.best_iteration)
    logger.info("  Train time:       %.1fs", result.train_time_sec)
    logger.info("  Artifacts dir:    %s", run_artifact_dir)
    logger.info("=" * 60)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI CyberShield — CICIDS2017 Model Training (Phase 3)",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=_PROJECT_ROOT / "datasets" / "processed" / "CICIDS2017",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=_PROJECT_ROOT / "ml" / "artifacts",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(processed_dir=args.processed_dir, artifact_dir=args.artifact_dir)
