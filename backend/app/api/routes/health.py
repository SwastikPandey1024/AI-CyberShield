"""
Health and readiness endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.config import settings
from backend.app.schemas.prediction import HealthResponse
from backend.app.services.prediction_service import get_predictor, is_model_loaded

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """Liveness probe — always returns 200 if the server is up."""
    model_loaded = is_model_loaded()
    run_id = None
    if model_loaded:
        try:
            run_id = get_predictor().run_id
        except Exception:
            pass
    return HealthResponse(
        status="ok",
        model_loaded=model_loaded,
        model_run_id=run_id,
        version=settings.api_version,
    )


@router.get("/ready", summary="Readiness probe")
async def ready():
    """
    Readiness probe — returns 200 only when the model is loaded and ready.
    Kubernetes/Docker health checks should use this endpoint.
    """
    try:
        predictor = get_predictor()
        return {"status": "ready", "model_run_id": predictor.run_id}
    except FileNotFoundError:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Model not loaded")
