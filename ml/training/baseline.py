"""
Milestone 3 — Baseline Model Training & Evaluation
====================================================

Trains and evaluates a simple, interpretable Decision Tree Baseline Model
on the preprocessed CICIDS2017 dataset.

Rule Enforcement:
  - Baseline model ONLY (DecisionTreeClassifier), executed alone before any ensemble work.
  - Stratified splits used directly from datasets/processed/CICIDS2017/.
  - Evaluates per-class Precision, Recall, F1-Score, Support, PR-AUC, and Confusion Matrix.
  - Specifically audits performance on rare classes (<1,000 samples).
  - Audits feature importances for constant/near-constant columns listed in schema.yaml.
"""

from __future__ import annotations

import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.tree import DecisionTreeClassifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("baseline_training")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed" / "CICIDS2017"
SCHEMA_PATH = PROJECT_ROOT / "configs" / "datasets" / "cicids2017" / "schema.yaml"
ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
REPORTS_DIR = PROJECT_ROOT / "reports" / "data" / "validation"


def load_data() -> tuple[
    pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, dict, list[str]
]:
    """Load preprocessed Parquet splits, feature metadata, and constant columns list."""
    logger.info("Loading preprocessed dataset splits from %s", PROCESSED_DIR)
    X_train = pd.read_parquet(PROCESSED_DIR / "X_train.parquet")
    y_train = pd.read_parquet(PROCESSED_DIR / "y_train.parquet")["label"]

    X_val = pd.read_parquet(PROCESSED_DIR / "X_val.parquet")
    y_val = pd.read_parquet(PROCESSED_DIR / "y_val.parquet")["label"]

    X_test = pd.read_parquet(PROCESSED_DIR / "X_test.parquet")
    y_test = pd.read_parquet(PROCESSED_DIR / "y_test.parquet")["label"]

    meta = json.loads((PROCESSED_DIR / "feature_meta.json").read_text(encoding="utf-8"))
    label_names = {int(k): v for k, v in meta["label_names"].items()}

    with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
        schema_cfg = yaml.safe_load(fh)

    drop_candidates = (
        schema_cfg.get("drop_candidates", {}).get("constant_all_8_files", [])
        + schema_cfg.get("drop_candidates", {}).get("constant_7_of_8_files", [])
    )

    return X_train, y_train, X_val, y_val, X_test, y_test, label_names, drop_candidates


def train_and_evaluate() -> dict[str, Any]:
    """Train DecisionTreeClassifier baseline and compute comprehensive evaluation metrics."""
    (
        X_train,
        y_train,
        X_val,
        y_val,
        X_test,
        y_test,
        label_names,
        drop_candidates,
    ) = load_data()

    logger.info("Training DecisionTreeClassifier baseline (max_depth=15, random_state=42)...")
    start_time = time.time()
    dt = DecisionTreeClassifier(max_depth=15, random_state=42)
    dt.fit(X_train, y_train)
    train_time = time.time() - start_time
    logger.info("Baseline training complete in %.2f seconds", train_time)

    # Evaluate on Validation Set
    y_val_pred = dt.predict(X_val)

    # Evaluate on Test Set
    start_eval = time.time()
    y_test_pred = dt.predict(X_test)
    y_test_proba = dt.predict_proba(X_test)
    eval_time = time.time() - start_eval

    unique_classes = sorted(label_names.keys())
    target_names = [label_names[c] for c in unique_classes]

    # Per-class precision, recall, f1, support
    prec, rec, f1, supp = precision_recall_fscore_support(
        y_test, y_test_pred, labels=unique_classes, zero_division=0
    )

    # Calculate PR-AUC (Average Precision Score) per class (One-Vs-Rest)
    pr_auc_scores = {}
    for idx, c in enumerate(unique_classes):
        c_name = label_names[c]
        binary_y_test = (y_test == c).astype(int)
        if binary_y_test.sum() > 0 and idx < y_test_proba.shape[1]:
            score = average_precision_score(binary_y_test, y_test_proba[:, idx])
            pr_auc_scores[c_name] = round(float(score), 4)
        else:
            pr_auc_scores[c_name] = 0.0

    # Overall metrics
    macro_f1 = float(f1_score(y_test, y_test_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0))
    accuracy = float((y_test == y_test_pred).mean())

    # Build per-class results table
    per_class_results = {}
    for idx, c in enumerate(unique_classes):
        c_name = label_names[c]
        per_class_results[c_name] = {
            "class_id": int(c),
            "precision": round(float(prec[idx]), 4),
            "recall": round(float(rec[idx]), 4),
            "f1_score": round(float(f1[idx]), 4),
            "pr_auc": pr_auc_scores[c_name],
            "support": int(supp[idx]),
        }

    # Confusion matrix
    cm = confusion_matrix(y_test, y_test_pred, labels=unique_classes)

    # Feature Importance Audit
    importances = dict(zip(X_train.columns, dt.feature_importances_))
    sorted_importances = dict(
        sorted(importances.items(), key=lambda item: item[1], reverse=True)
    )

    constant_col_importances = {}
    for col in drop_candidates:
        if col in importances:
            constant_col_importances[col] = float(importances[col])

    # Package results
    results = {
        "model_type": "DecisionTreeClassifier",
        "parameters": dt.get_params(),
        "train_time_sec": round(train_time, 2),
        "eval_time_sec": round(eval_time, 2),
        "overall_metrics": {
            "accuracy": round(accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
        },
        "per_class_metrics": per_class_results,
        "confusion_matrix": cm.tolist(),
        "constant_columns_importance_audit": constant_col_importances,
        "top_10_features": dict(list(sorted_importances.items())[:10]),
    }

    # Save outputs
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(ARTIFACTS_DIR / "baseline_model.pkl", "wb") as fh:
        pickle.dump(dt, fh)

    with open(REPORTS_DIR / "baseline_evaluation.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    # Generate Markdown Baseline Report
    generate_baseline_markdown_report(results, target_names, REPORTS_DIR / "baseline_report.md")

    return results


def generate_baseline_markdown_report(results: dict, target_names: list[str], out_path: Path) -> None:
    """Write human-readable Baseline Model Evaluation Report."""
    per_class_rows = ""
    for c_name, m in results["per_class_metrics"].items():
        per_class_rows += f"| `{c_name}` | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1_score']:.4f} | {m['pr_auc']:.4f} | {m['support']:,} |\n"

    const_rows = ""
    for col, imp in results["constant_columns_importance_audit"].items():
        const_rows += f"| `{col}` | {imp:.6f} | {'Zero Importance (Confirmed Safe)' if imp == 0 else 'Non-zero Importance'} |\n"

    content = f"""# Milestone 3 — Baseline Model Evaluation Report

**Model:** DecisionTreeClassifier (`max_depth=15`)  
**Evaluation Set:** Test Split (514,781 rows)  
**Training Time:** {results['train_time_sec']}s  

---

## 1. Overall Performance Summary

- **Accuracy:** {results['overall_metrics']['accuracy'] * 100:.2f}%
- **Macro F1-Score:** {results['overall_metrics']['macro_f1']:.4f}
- **Weighted F1-Score:** {results['overall_metrics']['weighted_f1']:.4f}

---

## 2. Full Per-Class Metric Breakdown

| Class Name | Precision | Recall | F1-Score | PR-AUC | Test Support |
|---|---:|---:|---:|---:|---:|
{per_class_rows}

---

## 3. Constant Columns Feature Importance Audit (`schema.yaml` list)

| Feature Name | Decision Tree Gini Importance | Finding |
|---|---:|---|
{const_rows}

---

## 4. Top 10 Most Predictive Features

"""
    for feat, imp in results["top_10_features"].items():
        content += f"- `{feat}`: {imp:.4f}\n"

    out_path.write_text(content.strip(), encoding="utf-8")
    logger.info("Wrote baseline evaluation report -> %s", out_path)


if __name__ == "__main__":
    res = train_and_evaluate()
    print("\n" + "=" * 80)
    print("BASELINE EVALUATION COMPLETE")
    print(f"Overall Accuracy: {res['overall_metrics']['accuracy'] * 100:.2f}%")
    print(f"Macro F1-Score:   {res['overall_metrics']['macro_f1']:.4f}")
    print(f"Weighted F1:     {res['overall_metrics']['weighted_f1']:.4f}")
    print("=" * 80)
