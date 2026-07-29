"""
Pydantic schemas — Prediction request/response
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class FlowFeatures(BaseModel):
    """
    Network flow feature vector for a single connection.

    All features are canonical names (post-ColumnNormalizer).
    Any missing features are filled with 0.0 by the predictor.
    """

    model_config = {"extra": "allow"}  # accept additional fields for forward-compat

    # Common high-signal features (document the most important ones)
    destination_port: Optional[float] = Field(None, alias="Destination Port")
    flow_duration: Optional[float] = Field(None, alias="Flow Duration")
    total_fwd_packets: Optional[float] = Field(None, alias="Total Fwd Packets")
    total_backward_packets: Optional[float] = Field(None, alias="Total Backward Packets")
    total_length_of_fwd_packets: Optional[float] = Field(None, alias="Total Length of Fwd Packets")
    total_length_of_bwd_packets: Optional[float] = Field(None, alias="Total Length of Bwd Packets")
    fwd_packet_length_max: Optional[float] = Field(None, alias="Fwd Packet Length Max")
    fwd_packet_length_min: Optional[float] = Field(None, alias="Fwd Packet Length Min")
    fwd_packet_length_mean: Optional[float] = Field(None, alias="Fwd Packet Length Mean")
    bwd_packet_length_max: Optional[float] = Field(None, alias="Bwd Packet Length Max")
    flow_bytes_per_s: Optional[float] = Field(None, alias="Flow Bytes/s")
    flow_packets_per_s: Optional[float] = Field(None, alias="Flow Packets/s")
    flow_iat_mean: Optional[float] = Field(None, alias="Flow IAT Mean")
    flow_iat_std: Optional[float] = Field(None, alias="Flow IAT Std")
    flow_iat_max: Optional[float] = Field(None, alias="Flow IAT Max")
    flow_iat_min: Optional[float] = Field(None, alias="Flow IAT Min")
    syn_flag_count: Optional[float] = Field(None, alias="SYN Flag Count")
    rst_flag_count: Optional[float] = Field(None, alias="RST Flag Count")
    psh_flag_count: Optional[float] = Field(None, alias="PSH Flag Count")
    ack_flag_count: Optional[float] = Field(None, alias="ACK Flag Count")
    init_win_bytes_forward: Optional[float] = Field(None, alias="Init_Win_bytes_forward")
    init_win_bytes_backward: Optional[float] = Field(None, alias="Init_Win_bytes_backward")

    def to_feature_dict(self) -> dict[str, Any]:
        """Return all fields (named + extra) as a flat dict."""
        result = {}
        # Named fields
        for field_name, field_info in self.__class__.model_fields.items():
            val = getattr(self, field_name)
            if val is not None:
                alias = field_info.alias or field_name
                result[alias] = val
        # Extra fields (pass-through)
        result.update(self.model_extra or {})
        return result


class PredictRequest(BaseModel):
    """Single-flow prediction request."""

    features: FlowFeatures = Field(..., description="Network flow feature vector")
    source_ip: Optional[str] = Field(None, description="Source IP for audit logging")
    request_id: Optional[str] = Field(None, description="Caller-supplied idempotency key")


class BatchPredictRequest(BaseModel):
    """Batch prediction request (up to 1000 flows)."""

    flows: list[FlowFeatures] = Field(..., min_length=1, max_length=1000)
    source_ip: Optional[str] = None


class TopKResult(BaseModel):
    """Single top-k class + probability."""

    class_name: str
    probability: float


class PredictResponse(BaseModel):
    """Single-flow prediction response."""

    predicted_class: str = Field(..., description="Predicted attack category name")
    predicted_index: int = Field(..., description="Integer class index")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Probability of predicted class")
    is_attack: bool = Field(..., description="True if predicted_class != BENIGN")
    top_k: list[TopKResult] = Field(..., description="Top-k classes by probability")
    all_probabilities: dict[str, float] = Field(..., description="All class probabilities")
    model_run_id: str = Field(..., description="Model run identifier for reproducibility")
    request_id: Optional[str] = None


class BatchPredictResponse(BaseModel):
    """Batch prediction response."""

    results: list[PredictResponse]
    total: int
    model_run_id: str


class ModelInfoResponse(BaseModel):
    """Model metadata for the /model/info endpoint."""

    run_id: str
    n_classes: int
    n_features: int
    label_names: dict[str, str]
    feature_names: list[str]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_run_id: Optional[str] = None
    version: str
