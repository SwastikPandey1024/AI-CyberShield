"""
Predictor
=========

Production inference layer for the AI CyberShield model.

Wraps the trained XGBoost booster + fitted RobustScaler into a single
``Predictor`` object that the FastAPI backend instantiates once at startup
and reuses for all requests.

Thread-safety: XGBoost prediction is read-only (no state mutation).
The ``Predictor`` instance is safe to share across async request handlers.

Args flow:
    raw feature dict  →  DataFrame  →  scale  →  DMatrix  →  predict
                      ↓
    PredictionResult(predicted_class, confidence, top_k_probs)
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """
    Output of a single-sample prediction.

    Attributes:
        predicted_class:  String name of the predicted attack category.
        predicted_index:  Integer class index.
        confidence:       Probability of the predicted class (0–1).
        top_k:            List of (class_name, probability) for top-k classes.
        all_probabilities: Dict mapping class name → probability for all classes.
        is_attack:        True if predicted_class != 'BENIGN'.
    """

    predicted_class: str
    predicted_index: int
    confidence: float
    top_k: list[tuple[str, float]]
    all_probabilities: dict[str, float]
    is_attack: bool


class Predictor:
    """
    Production-ready inference wrapper combining booster + scaler + metadata.

    Loads all artefacts from the ``artifact_dir`` (using ``latest.json`` to
    locate the current run), applies the fitted RobustScaler, and returns
    structured ``PredictionResult`` objects.

    Args:
        artifact_dir:  Root of ``ml/artifacts/``.
        processed_dir: Root of ``datasets/processed/CICIDS2017/`` (for scaler).
        top_k:         Number of top classes to include in result.
    """

    def __init__(
        self,
        artifact_dir: Path,
        processed_dir: Path,
        top_k: int = 3,
    ) -> None:
        self.top_k = top_k
        self._load(artifact_dir, processed_dir)

    def _load(self, artifact_dir: Path, processed_dir: Path) -> None:
        """Load model, scaler, and metadata from disk."""
        # Resolve run directory from latest.json
        latest_path = artifact_dir / "latest.json"
        if not latest_path.exists():
            raise FileNotFoundError(
                f"No trained model found. Run `python -m ml.training.run_training` first. "
                f"Expected: {latest_path}"
            )

        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        run_id = latest["run_id"]
        run_dir = artifact_dir / run_id
        model_path = Path(latest["model_path"])

        logger.info("Loading model from: %s", model_path)
        self._booster = xgb.Booster()
        self._booster.load_model(str(model_path))

        # Load metadata
        meta = json.loads((run_dir / "model_meta.json").read_text(encoding="utf-8"))
        self._feature_names: list[str] = meta["feature_names"]
        self._label_names: dict[int, str] = {
            int(k): v for k, v in meta["label_names"].items()
        }
        self._n_classes: int = meta["n_classes"]
        self.run_id = run_id
        self.model_version = meta.get("hyperparameters", {}).get("num_boost_round", "?")

        # Load scaler
        scaler_path = processed_dir / "scaler.pkl"
        logger.info("Loading scaler from: %s", scaler_path)
        with open(scaler_path, "rb") as fh:
            self._scaler: RobustScaler = pickle.load(fh)

        logger.info(
            "Predictor ready. Run=%s  Classes=%d  Features=%d",
            run_id, self._n_classes, len(self._feature_names),
        )

    def predict(self, features: dict[str, Any]) -> PredictionResult:
        """
        Predict the attack category for a single network flow.

        Args:
            features: Dict mapping canonical feature names to numeric values.
                      Missing features will be filled with 0.0.

        Returns:
            ``PredictionResult`` with predicted class and probabilities.
        """
        # Build DataFrame aligned to training feature order
        row = {col: features.get(col, 0.0) for col in self._feature_names}
        X = pd.DataFrame([row], columns=self._feature_names)

        # Scale
        X_scaled = self._scaler.transform(X)

        # Predict
        dmatrix = xgb.DMatrix(data=X_scaled, feature_names=self._feature_names)
        proba = self._booster.predict(dmatrix)[0]  # shape: (n_classes,)

        pred_idx = int(np.argmax(proba))
        pred_class = self._label_names.get(pred_idx, "Unknown")
        confidence = float(proba[pred_idx])

        # All probabilities
        all_probs = {
            self._label_names.get(i, str(i)): float(p)
            for i, p in enumerate(proba)
        }

        # Top-k
        sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        top_k = sorted_probs[: self.top_k]

        return PredictionResult(
            predicted_class=pred_class,
            predicted_index=pred_idx,
            confidence=confidence,
            top_k=top_k,
            all_probabilities=all_probs,
            is_attack=(pred_class != "BENIGN"),
        )

    def predict_batch(
        self,
        features_list: list[dict[str, Any]],
    ) -> list[PredictionResult]:
        """
        Predict attack categories for a batch of network flows.

        Args:
            features_list: List of feature dicts, one per flow.

        Returns:
            List of ``PredictionResult`` in the same order.
        """
        rows = [
            {col: f.get(col, 0.0) for col in self._feature_names}
            for f in features_list
        ]
        X = pd.DataFrame(rows, columns=self._feature_names)
        X_scaled = self._scaler.transform(X)
        dmatrix = xgb.DMatrix(data=X_scaled, feature_names=self._feature_names)
        proba_batch = self._booster.predict(dmatrix)  # shape: (n_samples, n_classes)

        results: list[PredictionResult] = []
        for proba in proba_batch:
            pred_idx = int(np.argmax(proba))
            pred_class = self._label_names.get(pred_idx, "Unknown")
            confidence = float(proba[pred_idx])
            all_probs = {
                self._label_names.get(i, str(i)): float(p)
                for i, p in enumerate(proba)
            }
            top_k = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)[: self.top_k]
            results.append(
                PredictionResult(
                    predicted_class=pred_class,
                    predicted_index=pred_idx,
                    confidence=confidence,
                    top_k=top_k,
                    all_probabilities=all_probs,
                    is_attack=(pred_class != "BENIGN"),
                )
            )
        return results

    @property
    def feature_names(self) -> list[str]:
        return self._feature_names

    @property
    def label_names(self) -> dict[int, str]:
        return self._label_names

    @property
    def n_classes(self) -> int:
        return self._n_classes
