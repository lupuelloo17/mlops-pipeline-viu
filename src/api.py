"""
api.py — API REST con FastAPI para servir predicciones del modelo Iris.

Endpoints:
  GET  /          → health check
  GET  /health    → estado del servicio
  POST /predict   → predicción a partir de 4 features
  GET  /metrics   → métricas del modelo entrenado
"""

import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from predict import predict, reload_model

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "metrics.json")


# ── Schemas ────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    sepal_length: float = Field(..., gt=0, description="Longitud del sépalo en cm")
    sepal_width: float  = Field(..., gt=0, description="Anchura del sépalo en cm")
    petal_length: float = Field(..., gt=0, description="Longitud del pétalo en cm")
    petal_width: float  = Field(..., gt=0, description="Anchura del pétalo en cm")

    model_config = {"json_schema_extra": {
        "example": {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
    }}


class PredictResponse(BaseModel):
    class_index: int
    class_name: str
    confidence: float
    probabilities: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo al arrancar la API."""
    try:
        reload_model()
        print("[api] Modelo cargado correctamente.")
    except FileNotFoundError as e:
        print(f"[api] ADVERTENCIA: {e}")
    yield


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Iris MLOps API",
    description="Pipeline MLOps para clasificación de flores Iris — VIU 20GIAR",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["root"])
def root():
    return {"message": "Iris MLOps API — usa /docs para explorar los endpoints."}


@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
def health():
    model_loaded = os.path.exists(METRICS_PATH)
    return HealthResponse(status="ok", model_loaded=model_loaded)


@app.post("/predict", response_model=PredictResponse, tags=["inference"])
def predict_endpoint(request: PredictRequest):
    features = [
        request.sepal_length,
        request.sepal_width,
        request.petal_length,
        request.petal_width,
    ]
    try:
        result = predict(features)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return PredictResponse(**result)


@app.get("/metrics", tags=["monitoring"])
def metrics():
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(
            status_code=404,
            detail="Métricas no encontradas. Entrena el modelo primero.",
        )
    with open(METRICS_PATH) as f:
        return json.load(f)
