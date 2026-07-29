"""
FastAPI API router — Prediction endpoints
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.prediction import (
    BatchPredictRequest,
    BatchPredictResponse,
    ModelInfoResponse,
    PredictRequest,
    PredictResponse,
    TopKResult,
)
from backend.app.services.prediction_service import (
    get_predictor,
    is_model_loaded,
    predict_batch,
    predict_single,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Prediction"])


def _make_response(result, request_id: str | None, run_id: str) -> PredictResponse:
    return PredictResponse(
        predicted_class=result.predicted_class,
        predicted_index=result.predicted_index,
        confidence=round(result.confidence, 6),
        is_attack=result.is_attack,
        top_k=[TopKResult(class_name=c, probability=round(p, 6)) for c, p in result.top_k],
        all_probabilities={k: round(v, 6) for k, v in result.all_probabilities.items()},
        model_run_id=run_id,
        request_id=request_id,
    )


@router.post(
    "/single",
    response_model=PredictResponse,
    summary="Classify a single network flow",
    description=(
        "Accepts a single network flow feature vector and returns the predicted "
        "attack category, confidence score, and per-class probabilities."
    ),
)
async def predict_single_endpoint(request: PredictRequest) -> PredictResponse:
    """Single-flow prediction."""
    try:
        predictor = get_predictor()
        features = request.features.to_feature_dict()
        result = predict_single(features)
        req_id = request.request_id or str(uuid.uuid4())
        logger.info(
            "Prediction: class=%s confidence=%.4f request_id=%s",
            result.predicted_class, result.confidence, req_id,
        )
        return _make_response(result, req_id, predictor.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model not available: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post(
    "/batch",
    response_model=BatchPredictResponse,
    summary="Classify a batch of network flows",
)
async def predict_batch_endpoint(request: BatchPredictRequest) -> BatchPredictResponse:
    """Batch prediction for up to 1,000 flows."""
    try:
        predictor = get_predictor()
        features_list = [f.to_feature_dict() for f in request.flows]
        results = predict_batch(features_list)
        responses = [_make_response(r, None, predictor.run_id) for r in results]
        return BatchPredictResponse(
            results=responses,
            total=len(responses),
            model_run_id=predictor.run_id,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Batch prediction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Get loaded model metadata",
)
async def model_info() -> ModelInfoResponse:
    """Return metadata about the currently-loaded model."""
    try:
        predictor = get_predictor()
        return ModelInfoResponse(
            run_id=predictor.run_id,
            n_classes=predictor.n_classes,
            n_features=len(predictor.feature_names),
            label_names={str(k): v for k, v in predictor.label_names.items()},
            feature_names=predictor.feature_names,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
