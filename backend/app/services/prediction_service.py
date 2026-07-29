"""
Prediction service — loads and caches the Predictor singleton.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ml.inference.predictor import Predictor, PredictionResult

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_ARTIFACT_DIR = _PROJECT_ROOT / "ml" / "artifacts"
_PROCESSED_DIR = _PROJECT_ROOT / "datasets" / "processed" / "CICIDS2017"

# Module-level singleton — instantiated on first call to get_predictor()
_predictor: Predictor | None = None


def get_predictor() -> Predictor:
    """
    Return the application-wide Predictor singleton.

    Loads from disk on first call (lazy init). Thread-safe for read access.
    Raises ``FileNotFoundError`` if no trained model exists.
    """
    global _predictor
    if _predictor is None:
        logger.info("Initialising Predictor from %s ...", _ARTIFACT_DIR)
        _predictor = Predictor(
            artifact_dir=_ARTIFACT_DIR,
            processed_dir=_PROCESSED_DIR,
            top_k=3,
        )
    return _predictor


def predict_single(features: dict) -> PredictionResult:
    """Run a single-flow prediction through the loaded model."""
    predictor = get_predictor()
    return predictor.predict(features)


def predict_batch(features_list: list[dict]) -> list[PredictionResult]:
    """Run batch prediction through the loaded model."""
    predictor = get_predictor()
    return predictor.predict_batch(features_list)


def is_model_loaded() -> bool:
    """Return True if the model has been loaded (without triggering load)."""
    return _predictor is not None
