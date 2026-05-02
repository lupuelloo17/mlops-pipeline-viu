"""Tests de integración para src/api.py"""

import json
import os
import sys

import joblib
import pytest
import numpy as np
from fastapi.testclient import TestClient
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_model_and_metrics(tmp_path, monkeypatch):
    """Entrena un modelo real, parchea rutas y crea metrics.json."""
    iris = load_iris()
    X_train, _, y_train, _ = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_scaled, y_train)

    model_path = str(tmp_path / "model.pkl")
    scaler_path = str(tmp_path / "scaler.pkl")
    metrics_path = str(tmp_path / "metrics.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    metrics = {"accuracy": 0.9667, "classification_report": {}}
    with open(metrics_path, "w") as f:
        json.dump(metrics, f)

    import predict as predict_module
    monkeypatch.setattr(predict_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(predict_module, "SCALER_PATH", scaler_path)
    monkeypatch.setattr(predict_module, "_model", None)
    monkeypatch.setattr(predict_module, "_scaler", None)

    import api as api_module
    monkeypatch.setattr(api_module, "METRICS_PATH", metrics_path)


@pytest.fixture
def client():
    import api
    return TestClient(api.app)


# ── GET / ──────────────────────────────────────────────────────────────────────

def test_root_returns_200(client):
    r = client.get("/")
    assert r.status_code == 200


def test_root_message(client):
    r = client.get("/")
    assert "message" in r.json()


# ── GET /health ────────────────────────────────────────────────────────────────

def test_health_status_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_model_loaded(client):
    r = client.get("/health")
    assert r.json()["model_loaded"] is True


# ── POST /predict ──────────────────────────────────────────────────────────────

VALID_SETOSA = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2,
}

VALID_VIRGINICA = {
    "sepal_length": 6.3,
    "sepal_width": 3.3,
    "petal_length": 6.0,
    "petal_width": 2.5,
}


def test_predict_returns_200(client):
    r = client.post("/predict", json=VALID_SETOSA)
    assert r.status_code == 200


def test_predict_response_keys(client):
    r = client.post("/predict", json=VALID_SETOSA)
    data = r.json()
    assert "class_index" in data
    assert "class_name" in data
    assert "confidence" in data
    assert "probabilities" in data


def test_predict_class_name_valid(client):
    r = client.post("/predict", json=VALID_SETOSA)
    assert r.json()["class_name"] in ["setosa", "versicolor", "virginica"]


def test_predict_confidence_between_0_and_1(client):
    r = client.post("/predict", json=VALID_SETOSA)
    assert 0.0 <= r.json()["confidence"] <= 1.0


def test_predict_probabilities_three_classes(client):
    r = client.post("/predict", json=VALID_SETOSA)
    probs = r.json()["probabilities"]
    assert set(probs.keys()) == {"setosa", "versicolor", "virginica"}


def test_predict_missing_field_returns_422(client):
    r = client.post("/predict", json={"sepal_length": 5.1})
    assert r.status_code == 422


def test_predict_negative_value_returns_422(client):
    bad = {**VALID_SETOSA, "sepal_length": -1.0}
    r = client.post("/predict", json=bad)
    assert r.status_code == 422


def test_predict_virginica_not_setosa(client):
    r = client.post("/predict", json=VALID_VIRGINICA)
    assert r.json()["class_index"] != 0


# ── GET /metrics ───────────────────────────────────────────────────────────────

def test_metrics_returns_200(client):
    r = client.get("/metrics")
    assert r.status_code == 200


def test_metrics_has_accuracy(client):
    r = client.get("/metrics")
    assert "accuracy" in r.json()


def test_metrics_accuracy_value(client):
    r = client.get("/metrics")
    assert r.json()["accuracy"] == pytest.approx(0.9667)
