"""
run_evaluation.py
=================

CLI entry point for Phase 3 model evaluation.

Usage:
    python -m ml.evaluation.run_evaluation [--processed-dir PATH] [--artifact-dir PATH]

Evaluates the current ``latest`` model against both val and test splits.
Writes JSON reports and text classification reports to the artifact directory.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd
import xgboost as xgb

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ml.evaluation.evaluator import CICIDSEvaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("run_evaluation")


def run(processed_dir: Path, artifact_dir: Path) -> None:
    """Load model + test data, run full evaluation suite."""

    # ── find latest model ────────────────────
    latest_path = artifact_dir / "latest.json"
    if not latest_path.exists():
        logger.error("No latest.json found in %s. Run training first.", artifact_dir)
        sys.exit(1)

    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    model_path = Path(latest["model_path"])
    run_id = latest["run_id"]
    run_dir = artifact_dir / run_id

    logger.info("Loading model: %s", model_path)
    booster = xgb.Booster()
    booster.load_model(str(model_path))

    # ── load meta ─────────────────────────────
    meta = json.loads((run_dir / "model_meta.json").read_text(encoding="utf-8"))
    label_names: dict[int, str] = {int(k): v for k, v in meta["label_names"].items()}

    # ── load splits ───────────────────────────
    logger.info("Loading processed splits from %s ...", processed_dir)
    X_val  = pd.read_parquet(processed_dir / "X_val.parquet")
    X_test = pd.read_parquet(processed_dir / "X_test.parquet")
    y_val  = pd.read_parquet(processed_dir / "y_val.parquet").squeeze()
    y_test = pd.read_parquet(processed_dir / "y_test.parquet").squeeze()

    evaluator = CICIDSEvaluator(label_names=label_names)

    # ── evaluate val ──────────────────────────
    logger.info("Evaluating on validation split ...")
    val_result = evaluator.evaluate(booster, X_val, y_val)
    evaluator.save_report(val_result, out_dir=run_dir, split_name="val")

    # ── evaluate test ─────────────────────────
    logger.info("Evaluating on test split ...")
    test_result = evaluator.evaluate(booster, X_test, y_test)
    evaluator.save_report(test_result, out_dir=run_dir, split_name="test")

    # ── print summary ─────────────────────────
    logger.info("=" * 60)
    logger.info("EVALUATION COMPLETE — Run: %s", run_id)
    logger.info("  Val  macro-F1:  %.4f   accuracy: %.4f", val_result.macro_f1, val_result.accuracy)
    logger.info("  Test macro-F1: %.4f   accuracy: %.4f", test_result.macro_f1, test_result.accuracy)
    logger.info("")
    logger.info("Per-class test results:")
    for cls_name, m in test_result.per_class.items():
        if m["support"] > 0:
            logger.info(
                "  %-30s  P=%.3f  R=%.3f  F1=%.3f  n=%d",
                cls_name, m["precision"], m["recall"], m["f1"], m["support"],
            )
    logger.info("=" * 60)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI CyberShield — Model Evaluation (Phase 3)",
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
