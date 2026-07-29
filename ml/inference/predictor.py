"""
Predictor
=========

Production inference layer for the AI CyberShield model.

Wraps the trained model (RandomForest/XGBoost) + fitted RobustScaler into a single
``Predictor`` object that the FastAPI backend instantiates once at startup
and reuses for all requests.

Thread-safety: Model prediction is read-only (no state mutation).
The ``Predictor`` instance is safe to share across async request handlers.
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
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """
    Output of a single-sample prediction.

    Attributes:
        predicted_class:   String name of the predicted attack category.
        predicted_index:   Integer class index.
        confidence:        Probability of the predicted class (0–1).
        top_k:             List of (class_name, probability) for top-k classes.
        all_probabilities: Dict mapping class name → probability for all classes.
        is_attack:         True if predicted_class != 'BENIGN'.
    """

    predicted_class: str
    predicted_index: int
    confidence: float
    top_k: list[tuple[str, float]]
    all_probabilities: dict[str, float]
    is_attack: bool


class Predictor:
    """
    Production-ready inference wrapper combining model + scaler + metadata.

    Loads artifacts from ``ml/artifacts/models/`` and ``datasets/processed/CICIDS2017/``,
    applies the fitted RobustScaler, and returns structured ``PredictionResult`` objects.
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
        models_dir = artifact_dir / "models"
        model_path = models_dir / "model.pkl"
        feature_names_path = models_dir / "feature_names.json"
        meta_path = processed_dir / "feature_meta.json"
        scaler_path = processed_dir / "scaler.pkl"

        if not model_path.exists():
            # Check latest.json fallback if available
            latest_path = artifact_dir / "latest.json"
            if latest_path.exists():
                latest = json.loads(latest_path.read_text(encoding="utf-8"))
                model_path = Path(latest["model_path"])

        if not model_path.exists():
            raise FileNotFoundError(
                f"No trained model found at {model_path}. "
                "Run `python -m ml.training.train_ensembles` to train and save the model."
            )

        logger.info("Loading model from: %s", model_path)
        with open(model_path, "rb") as fh:
            self._model = pickle.load(fh)

        # Load feature names
        if feature_names_path.exists():
            fn_payload = json.loads(feature_names_path.read_text(encoding="utf-8"))
            self._feature_names: list[str] = fn_payload["feature_names"]
        else:
            raise FileNotFoundError(f"Feature names file missing: {feature_names_path}")

        # Load metadata / label names
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self._label_names: dict[int, str] = {
                int(k): v for k, v in meta["label_names"].items()
            }
        else:
            # Default CICIDS2017 8-class mapping
            self._label_names = {
                0: "BENIGN", 1: "DoS", 2: "DDoS", 3: "PortScan",
                4: "BruteForce", 5: "WebAttack", 6: "Botnet", 7: "Infiltration"
            }

        self._n_classes: int = len(self._label_names)
        self.run_id = "randomforest_milestone3"

        # Load scaler
        logger.info("Loading scaler from: %s", scaler_path)
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler file missing: {scaler_path}")
        with open(scaler_path, "rb") as fh:
            self._scaler: RobustScaler = pickle.load(fh)

        logger.info(
            "Predictor ready. Run=%s  Classes=%d  Features=%d",
            self.run_id, self._n_classes, len(self._feature_names),
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
        row = {col: features.get(col, 0.0) for col in self._feature_names}
        X = pd.DataFrame([row], columns=self._feature_names)
        X_scaled = self._scaler.transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=self._feature_names)

        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(X_scaled_df)[0]
        else:
            pred = self._model.predict(X_scaled_df)[0]
            proba = np.zeros(self._n_classes)
            proba[pred] = 1.0

        pred_idx = int(np.argmax(proba))
        pred_class = self._label_names.get(pred_idx, "Unknown")
        confidence = float(proba[pred_idx])

        all_probs = {
            self._label_names.get(i, str(i)): float(p)
            for i, p in enumerate(proba)
        }
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
        """
        rows = [
            {col: f.get(col, 0.0) for col in self._feature_names}
            for f in features_list
        ]
        X = pd.DataFrame(rows, columns=self._feature_names)
        X_scaled = self._scaler.transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=self._feature_names)

        if hasattr(self._model, "predict_proba"):
            proba_batch = self._model.predict_proba(X_scaled_df)
        else:
            preds = self._model.predict(X_scaled_df)
            proba_batch = np.zeros((len(preds), self._n_classes))
            for i, p in enumerate(preds):
                proba_batch[i, p] = 1.0

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
