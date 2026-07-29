"""
FastAPI Application — AI CyberShield Backend
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import health, prediction
from backend.app.config import settings

# ── logging ────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("cybershield.api")


# ── lifespan (startup / shutdown) ──────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    On startup: eagerly load the ML model so the first request
    is not penalised by cold-start latency.
    """
    logger.info("AI CyberShield API starting up (%s) ...", settings.app_env)
    try:
        from backend.app.services.prediction_service import get_predictor
        predictor = get_predictor()
        logger.info(
            "Model loaded on startup. run_id=%s  classes=%d  features=%d",
            predictor.run_id, predictor.n_classes, len(predictor.feature_names),
        )
    except FileNotFoundError:
        logger.warning(
            "No trained model found at startup. "
            "Run `python -m ml.training.run_training` to train a model. "
            "Prediction endpoints will return 503 until a model is available."
        )
    except Exception as exc:
        logger.exception("Unexpected error loading model on startup: %s", exc)

    yield  # application runs here

    logger.info("AI CyberShield API shutting down.")


# ── app factory ────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI CyberShield",
        description=(
            "ML-powered network intrusion detection API. "
            "Classifies network flow features into BENIGN or one of 8 attack categories "
            "trained on the CICIDS2017 dataset."
        ),
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "*"]
        if settings.app_env == "development"
        else ["https://cybershield.example.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── request timing middleware ───────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
        return response

    # ── global exception handler ────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
        )

    # ── routers ────────────────────────────────
    app.include_router(health.router)
    app.include_router(prediction.router, prefix="/api/v1")

    # ── root ───────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": "AI CyberShield",
            "version": settings.api_version,
            "docs": "/docs",
        }

    return app


app = create_app()
