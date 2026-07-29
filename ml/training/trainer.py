"""
Trainer
=======

XGBoost multi-class classifier for CICIDS2017 network intrusion detection.

Model strategy:
  - XGBoost ``multi:softprob`` objective for probability outputs per class
  - Class weights computed from training set distribution (handles 206,645x imbalance)
  - Early stopping on validation log-loss to prevent overfitting
  - Feature importance scores saved alongside model for explainability
  - All hyperparameters documented with evidence-based justification

Artifacts written to ``ml/artifacts/<run_id>/``:
    model.ubj           XGBoost booster (universal binary JSON, best format)
    model_meta.json     Hyperparameters, class names, feature list, git hash
    feature_importance.json   Gain, weight, cover importance scores
    training_log.json   Per-round eval metric history
"""

from __future__ import annotations

import json
import logging
import os
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.utils.class_weight import compute_class_weight

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Result dataclass
# ──────────────────────────────────────────────


@dataclass
class TrainingResult:
    """
    Output of a training run.

    Attributes:
        booster:           Trained XGBoost booster.
        best_iteration:    Iteration with best validation metric.
        eval_history:      Dict of metric name → list of per-round values.
        feature_importance: Dict of importance type → {feature: score}.
        run_id:            Unique run identifier string.
        train_time_sec:    Wall-clock training time in seconds.
    """

    booster: xgb.Booster
    best_iteration: int
    eval_history: dict[str, list[float]]
    feature_importance: dict[str, dict[str, float]]
    run_id: str
    train_time_sec: float


# ──────────────────────────────────────────────
# Trainer
# ──────────────────────────────────────────────


class CICIDSTrainer:
    """
    Trains an XGBoost multi-class classifier on preprocessed CICIDS2017 data.

    Args:
        n_classes:      Number of target classes.
        random_state:   Random seed.
        n_jobs:         XGBoost ``nthread`` parameter (-1 = all cores).
        early_stopping: Number of non-improving rounds before stopping.
        num_boost_round: Maximum number of boosting rounds.
        verbose_eval:   Log eval metrics every N rounds (0 = silent).
    """

    # Evidence-based hyperparameter defaults:
    # - eta=0.1: Conservative learning rate for 2.8M rows; fast convergence expected
    # - max_depth=7: Network traffic features have moderate interactions; 7 avoids
    #   the trivial depth=3 baseline while staying interpretable
    # - subsample=0.8, colsample_bytree=0.8: Regularisation for 64 features post-drop
    # - min_child_weight=5: Prevents splitting on the 11 Heartbleed rows repeatedly
    # - scale_pos_weight not used: multi-class handled via sample_weight instead

    DEFAULT_PARAMS: dict[str, Any] = {
        "objective":        "multi:softprob",
        "eval_metric":      ["mlogloss", "merror"],
        "eta":              0.1,
        "max_depth":        7,
        "subsample":        0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "tree_method":      "hist",   # histogram method: fast on large datasets
        "device":           "cpu",
        "seed":             42,
        "verbosity":        1,
    }

    def __init__(
        self,
        n_classes: int,
        random_state: int = 42,
        n_jobs: int = -1,
        early_stopping: int = 30,
        num_boost_round: int = 500,
        verbose_eval: int = 25,
    ) -> None:
        self.n_classes = n_classes
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.early_stopping = early_stopping
        self.num_boost_round = num_boost_round
        self.verbose_eval = verbose_eval

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> TrainingResult:
        """
        Train XGBoost with class-weighted samples and early stopping on validation.

        Args:
            X_train: Training feature matrix (already scaled).
            y_train: Training labels (integer-encoded).
            X_val:   Validation feature matrix.
            y_val:   Validation labels.

        Returns:
            ``TrainingResult`` with booster, eval history, and importance scores.
        """
        run_id = f"run_{int(time.time())}"
        logger.info("Starting training run: %s", run_id)
        logger.info("  Train: %d rows × %d features", len(X_train), X_train.shape[1])
        logger.info("  Val:   %d rows", len(X_val))
        logger.info("  Classes: %d", self.n_classes)

        # ── compute per-sample weights (inverse class frequency) ─
        # Use only classes actually present in y_train (not all n_classes):
        # compute_class_weight requires classes ⊆ y, which fails if a class
        # is absent from this split (e.g. Heartbleed with only 11 total rows).
        classes_present = np.unique(y_train.values)
        class_weights_arr = compute_class_weight(
            class_weight="balanced",
            classes=classes_present,
            y=y_train.values,
        )
        # Build a full-size weight array (absent classes get weight 1.0)
        class_weight_map = dict(zip(classes_present, class_weights_arr))
        sample_weights = np.array(
            [class_weight_map.get(int(yv), 1.0) for yv in y_train.values]
        )
        logger.info(
            "Class weights (min=%.4f, max=%.4f)", class_weights_arr.min(), class_weights_arr.max()
        )

        # ── build DMatrix ─────────────────────────────────────────
        dtrain = xgb.DMatrix(
            data=X_train.values,
            label=y_train.values,
            weight=sample_weights,
            feature_names=list(X_train.columns),
        )
        dval = xgb.DMatrix(
            data=X_val.values,
            label=y_val.values,
            feature_names=list(X_val.columns),
        )

        # ── params ────────────────────────────────────────────────
        params = {**self.DEFAULT_PARAMS}
        params["num_class"] = self.n_classes
        params["nthread"] = os.cpu_count() if self.n_jobs == -1 else self.n_jobs
        params["seed"] = self.random_state

        # ── train ─────────────────────────────────────────────────
        eval_history: dict[str, list[float]] = {}
        callbacks = []
        if self.verbose_eval > 0:
            callbacks.append(xgb.callback.EvaluationMonitor(period=self.verbose_eval))

        t0 = time.time()
        booster = xgb.train(
            params=params,
            dtrain=dtrain,
            num_boost_round=self.num_boost_round,
            evals=[(dtrain, "train"), (dval, "val")],
            evals_result=eval_history,
            early_stopping_rounds=self.early_stopping,
            callbacks=callbacks,
        )
        elapsed = time.time() - t0

        best_iter = booster.best_iteration
        logger.info(
            "Training complete in %.1fs. Best iteration: %d", elapsed, best_iter
        )

        # ── feature importance ────────────────────────────────────
        importance: dict[str, dict[str, float]] = {}
        for imp_type in ("weight", "gain", "cover"):
            scores = booster.get_score(importance_type=imp_type)
            importance[imp_type] = dict(
                sorted(scores.items(), key=lambda x: x[1], reverse=True)
            )

        return TrainingResult(
            booster=booster,
            best_iteration=best_iter,
            eval_history=eval_history,
            feature_importance=importance,
            run_id=run_id,
            train_time_sec=elapsed,
        )

    def save(
        self,
        result: TrainingResult,
        out_dir: Path,
        *,
        feature_names: list[str],
        label_names: dict[int, str],
    ) -> Path:
        """
        Persist all training artefacts to ``out_dir``.

        Returns the path to the model file.
        """
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Booster (ubj = universal binary JSON — preferred by XGBoost team)
        model_path = out_dir / "model.ubj"
        result.booster.save_model(str(model_path))
        logger.info("Saved booster → %s", model_path.name)

        # 2. Model metadata
        meta = {
            "run_id":            result.run_id,
            "best_iteration":    result.best_iteration,
            "train_time_sec":    round(result.train_time_sec, 2),
            "n_classes":         self.n_classes,
            "n_features":        len(feature_names),
            "feature_names":     feature_names,
            "label_names":       {str(k): v for k, v in label_names.items()},
            "hyperparameters":   {
                **self.DEFAULT_PARAMS,
                "num_class":          self.n_classes,
                "early_stopping":     self.early_stopping,
                "num_boost_round":    self.num_boost_round,
                "random_state":       self.random_state,
            },
        }
        meta_path = out_dir / "model_meta.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        logger.info("Saved model metadata → %s", meta_path.name)

        # 3. Feature importance
        fi_path = out_dir / "feature_importance.json"
        fi_path.write_text(
            json.dumps(result.feature_importance, indent=2), encoding="utf-8"
        )
        logger.info("Saved feature importance → %s", fi_path.name)

        # 4. Training log
        log_path = out_dir / "training_log.json"
        log_path.write_text(
            json.dumps(result.eval_history, indent=2), encoding="utf-8"
        )
        logger.info("Saved training log → %s", log_path.name)

        return model_path
