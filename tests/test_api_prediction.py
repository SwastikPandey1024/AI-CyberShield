"""
Integration & End-to-End API Tests — FastAPI Endpoints
======================================================
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI CyberShield"
    assert "version" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_model_info_endpoint(client):
    response = client.get("/api/v1/predict/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["n_classes"] >= 8
    assert data["n_features"] == 75
    assert "BENIGN" in data["label_names"].values()


def test_predict_single_benign(client):
    payload = {
        "features": {
            "Destination Port": 80,
            "Flow Duration": 1000,
            "Total Fwd Packets": 2,
            "Total Backward Packets": 2,
            "Flow Bytes/s": 500.0,
        }
    }
    response = client.post("/api/v1/predict/single", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["top_k"]) > 0


def test_predict_batch(client):
    payload = {
        "flows": [
            {
                "Destination Port": 80,
                "Flow Duration": 500,
            },
            {
                "Destination Port": 22,
                "Flow Duration": 90000,
            },
        ]
    }
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2
