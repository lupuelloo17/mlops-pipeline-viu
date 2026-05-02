"""Tests para src/predict.py"""

import os
import sys

import joblib
import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def patch_model_paths(tmp_path, monkeypatch):
    """Entrena un modelo real y parchea las rutas para cada test."""
    iris = load_iris()
    X_train, X_test, y_train, _ = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_scaled, y_train)

    model_path = str(tmp_path / "model.pkl")
    scaler_path = str(tmp_path / "scaler.pkl")
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    import predict as predict_module
    monkeypatch.setattr(predict_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(predict_module, "SCALER_PATH", scaler_path)
    monkeypatch.setattr(predict_module, "_model", None)
    monkeypatch.setattr(predict_module, "_scaler", None)


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_predict_returns_dict():
    from predict import predict
    result = predict([5.1, 3.5, 1.4, 0.2])
    assert isinstance(result, dict)


def test_predict_keys():
    from predict import predict
    result = predict([5.1, 3.5, 1.4, 0.2])
    assert "class_index" in result
    assert "class_name" in result
    assert "confidence" in result
    assert "probabilities" in result


def test_predict_class_index_valid():
    from predict import predict
    result = predict([5.1, 3.5, 1.4, 0.2])
    assert result["class_index"] in [0, 1, 2]


def test_predict_class_name_valid():
    from predict import predict
    result = predict([5.1, 3.5, 1.4, 0.2])
    assert result["class_name"] in ["setosa", "versicolor", "virginica"]


def test_predict_confidence_range():
    from predict import predict
    result = predict([5.1, 3.5, 1.4, 0.2])
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_probabilities_sum_to_one():
    from predict import predict
    result = predict([6.3, 3.3, 6.0, 2.5])
    total = sum(result["probabilities"].values())
    assert abs(total - 1.0) < 1e-4


def test_predict_wrong_features_raises():
    from predict import predict
    with pytest.raises(ValueError):
        predict([5.1, 3.5, 1.4])


def test_predict_wrong_features_too_many():
    from predict import predict
    with pytest.raises(ValueError):
        predict([5.1, 3.5, 1.4, 0.2, 99.0])


def test_predict_virginica_sample():
    """Una muestra típica de virginica debe predecirse como clase 2."""
    from predict import predict
    result = predict([6.3, 3.3, 6.0, 2.5])
    # No forzamos la clase exacta pero sí que no sea setosa
    assert result["class_index"] != 0


def test_reload_model():
    from predict import reload_model, _model
    reload_model()
    import predict as m
    assert m._model is not None


def test_model_not_found_raises(monkeypatch):
    import predict as predict_module
    monkeypatch.setattr(predict_module, "MODEL_PATH", "/nonexistent/model.pkl")
    monkeypatch.setattr(predict_module, "_model", None)
    monkeypatch.setattr(predict_module, "_scaler", None)
    with pytest.raises(FileNotFoundError):
        predict_module.predict([5.1, 3.5, 1.4, 0.2])
