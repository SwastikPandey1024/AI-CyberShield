"""
Evaluator
=========

Evaluation suite for the CICIDS2017 multi-class classifier.

Produces:
  - Per-class precision / recall / F1 / support
  - Macro + weighted averages
  - Overall accuracy
  - Confusion matrix (raw counts + normalised)
  - Per-class ROC-AUC (OVR)
  - Feature importance ranking from model artefact

Design note on metrics:
  Accuracy is included but NOT the primary metric — at 80% BENIGN base rate a
  trivial classifier scores 80%. Macro-F1 is the headline metric because it
  weights all classes equally, penalising models that ignore Heartbleed (11 rows).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.preprocessing import label_binarize

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """
    Full evaluation report for a single split (test or val).

    Attributes:
        accuracy:           Overall accuracy (0–1).
        macro_f1:           Unweighted macro-averaged F1.
        weighted_f1:        Support-weighted F1.
        macro_roc_auc:      Macro OVR ROC-AUC.
        per_class:          Dict of class name → {precision, recall, f1, support, roc_auc}.
        confusion_matrix:   Raw confusion matrix (list of lists, row=true, col=pred).
        confusion_matrix_normalised: Row-normalised confusion matrix.
        classification_report_str: sklearn classification_report string.
    """

    accuracy: float
    macro_f1: float
    weighted_f1: float
    macro_roc_auc: float
    per_class: dict[str, dict[str, float]]
    confusion_matrix: list[list[int]]
    confusion_matrix_normalised: list[list[float]]
    classification_report_str: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "accuracy":            round(self.accuracy, 6),
            "macro_f1":            round(self.macro_f1, 6),
            "weighted_f1":         round(self.weighted_f1, 6),
            "macro_roc_auc":       round(self.macro_roc_auc, 6),
            "per_class":           {
                cls: {k: round(v, 6) if isinstance(v, float) else v
                      for k, v in metrics.items()}
                for cls, metrics in self.per_class.items()
            },
            "confusion_matrix":            self.confusion_matrix,
            "confusion_matrix_normalised": self.confusion_matrix_normalised,
        }


class CICIDSEvaluator:
    """
    Evaluates a trained XGBoost booster on labelled data.

    Args:
        label_names: Dict mapping integer class index to class name string.
    """

    def __init__(self, label_names: dict[int, str]) -> None:
        self.label_names = label_names
        self.n_classes = len(label_names)

    def evaluate(
        self,
        booster: xgb.Booster,
        X: pd.DataFrame,
        y_true: pd.Series,
    ) -> EvaluationResult:
        """
        Run full evaluation suite on a dataset split.

        Args:
            booster: Trained XGBoost booster.
            X:       Feature matrix.
            y_true:  Ground-truth integer labels.

        Returns:
            ``EvaluationResult`` with all metrics populated.
        """
        dmatrix = xgb.DMatrix(data=X.values, feature_names=list(X.columns))
        proba = booster.predict(dmatrix)  # shape: (n_samples, n_classes)
        y_pred = np.argmax(proba, axis=1)
        y_true_arr = y_true.values

        # ── scalar metrics ────────────────────────────────────────
        accuracy   = float(accuracy_score(y_true_arr, y_pred))
        macro_f1   = float(f1_score(y_true_arr, y_pred, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_true_arr, y_pred, average="weighted", zero_division=0))

        # ── ROC-AUC (OVR) ────────────────────────────────────────
        classes_present = sorted(np.unique(np.concatenate([y_true_arr, y_pred])))
        try:
            y_bin = label_binarize(y_true_arr, classes=list(range(self.n_classes)))
            if self.n_classes == 2:
                macro_roc_auc = float(roc_auc_score(y_true_arr, proba[:, 1]))
            else:
                macro_roc_auc = float(
                    roc_auc_score(y_bin, proba, average="macro", multi_class="ovr")
                )
        except ValueError as exc:
            logger.warning("ROC-AUC computation failed (%s). Setting to 0.0.", exc)
            macro_roc_auc = 0.0

        # ── per-class metrics ─────────────────────────────────────
        report_dict = classification_report(
            y_true_arr,
            y_pred,
            labels=list(range(self.n_classes)),
            target_names=[self.label_names.get(i, str(i)) for i in range(self.n_classes)],
            zero_division=0,
            output_dict=True,
        )
        report_str = classification_report(
            y_true_arr,
            y_pred,
            labels=list(range(self.n_classes)),
            target_names=[self.label_names.get(i, str(i)) for i in range(self.n_classes)],
            zero_division=0,
        )

        per_class: dict[str, dict[str, float]] = {}
        for i in range(self.n_classes):
            cls_name = self.label_names.get(i, str(i))
            cls_data = report_dict.get(cls_name, {})
            # per-class OVR ROC-AUC
            try:
                y_bin_cls = (y_true_arr == i).astype(int)
                cls_proba = proba[:, i]
                cls_auc = float(roc_auc_score(y_bin_cls, cls_proba))
            except ValueError:
                cls_auc = float("nan")

            per_class[cls_name] = {
                "precision": cls_data.get("precision", 0.0),
                "recall":    cls_data.get("recall", 0.0),
                "f1":        cls_data.get("f1-score", 0.0),
                "support":   int(cls_data.get("support", 0)),
                "roc_auc":   cls_auc,
            }

        # ── confusion matrix ──────────────────────────────────────
        cm = confusion_matrix(y_true_arr, y_pred, labels=list(range(self.n_classes)))
        cm_norm = cm.astype(float)
        row_sums = cm_norm.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # avoid division by zero for absent classes
        cm_norm = (cm_norm / row_sums).round(4)

        logger.info(
            "Evaluation: accuracy=%.4f  macro_f1=%.4f  macro_auc=%.4f",
            accuracy, macro_f1, macro_roc_auc,
        )

        return EvaluationResult(
            accuracy=accuracy,
            macro_f1=macro_f1,
            weighted_f1=weighted_f1,
            macro_roc_auc=macro_roc_auc,
            per_class=per_class,
            confusion_matrix=cm.tolist(),
            confusion_matrix_normalised=cm_norm.tolist(),
            classification_report_str=report_str,
        )

    def save_report(
        self,
        result: EvaluationResult,
        out_dir: Path,
        *,
        split_name: str = "test",
    ) -> Path:
        """Write evaluation report JSON and text classification report."""
        out_dir.mkdir(parents=True, exist_ok=True)

        json_path = out_dir / f"eval_{split_name}.json"
        json_path.write_text(
            json.dumps(result.to_dict(), indent=2), encoding="utf-8"
        )

        txt_path = out_dir / f"eval_{split_name}_report.txt"
        txt_path.write_text(result.classification_report_str, encoding="utf-8")

        logger.info("Saved %s evaluation → %s", split_name, out_dir)
        return json_path
