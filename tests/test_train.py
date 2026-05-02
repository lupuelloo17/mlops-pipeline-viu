"""Tests para src/train.py"""

import json
import os
import sys

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from train import load_data, train, evaluate, save_artifacts


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def iris_data():
    return load_data()


@pytest.fixture
def trained_artifacts(iris_data):
    X, y, target_names = iris_data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model, scaler = train(X_train, y_train)
    return model, scaler, X_test, y_test, target_names


# ── load_data ──────────────────────────────────────────────────────────────────

def test_load_data_shape(iris_data):
    X, y, target_names = iris_data
    assert X.shape == (150, 4)
    assert len(y) == 150


def test_load_data_target_names(iris_data):
    _, _, target_names = iris_data
    assert len(target_names) == 3


def test_load_data_no_nulls(iris_data):
    X, y, _ = iris_data
    assert X.isnull().sum().sum() == 0
    assert y.isnull().sum() == 0


def test_load_data_columns(iris_data):
    X, _, _ = iris_data
    expected_cols = [
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
    ]
    assert list(X.columns) == expected_cols


# ── train ──────────────────────────────────────────────────────────────────────

def test_train_returns_correct_types(trained_artifacts):
    model, scaler, *_ = trained_artifacts
    assert isinstance(model, RandomForestClassifier)
    assert isinstance(scaler, StandardScaler)


def test_train_model_is_fitted(trained_artifacts):
    model, scaler, X_test, _, _ = trained_artifacts
    X_scaled = scaler.transform(X_test)
    preds = model.predict(X_scaled)
    assert len(preds) == len(X_test)


# ── evaluate ───────────────────────────────────────────────────────────────────

def test_evaluate_accuracy_above_threshold(trained_artifacts):
    model, scaler, X_test, y_test, target_names = trained_artifacts
    metrics = evaluate(model, scaler, X_test, y_test, target_names)
    assert metrics["accuracy"] >= 0.90, "Se espera accuracy ≥ 90% en Iris"


def test_evaluate_returns_dict_keys(trained_artifacts):
    model, scaler, X_test, y_test, target_names = trained_artifacts
    metrics = evaluate(model, scaler, X_test, y_test, target_names)
    assert "accuracy" in metrics
    assert "classification_report" in metrics


def test_evaluate_accuracy_range(trained_artifacts):
    model, scaler, X_test, y_test, target_names = trained_artifacts
    metrics = evaluate(model, scaler, X_test, y_test, target_names)
    assert 0.0 <= metrics["accuracy"] <= 1.0


# ── save_artifacts ─────────────────────────────────────────────────────────────

def test_save_artifacts_creates_files(tmp_path, monkeypatch, trained_artifacts):
    model, scaler, X_test, y_test, target_names = trained_artifacts
    metrics = evaluate(model, scaler, X_test, y_test, target_names)

    monkeypatch.setattr("train.MODEL_DIR", str(tmp_path))
    monkeypatch.setattr("train.MODEL_PATH", str(tmp_path / "model.pkl"))
    monkeypatch.setattr("train.SCALER_PATH", str(tmp_path / "scaler.pkl"))
    monkeypatch.setattr("train.METRICS_PATH", str(tmp_path / "metrics.json"))

    save_artifacts(model, scaler, metrics)

    assert (tmp_path / "model.pkl").exists()
    assert (tmp_path / "scaler.pkl").exists()
    assert (tmp_path / "metrics.json").exists()


def test_save_artifacts_metrics_content(tmp_path, monkeypatch, trained_artifacts):
    model, scaler, X_test, y_test, target_names = trained_artifacts
    metrics = evaluate(model, scaler, X_test, y_test, target_names)

    monkeypatch.setattr("train.MODEL_DIR", str(tmp_path))
    monkeypatch.setattr("train.MODEL_PATH", str(tmp_path / "model.pkl"))
    monkeypatch.setattr("train.SCALER_PATH", str(tmp_path / "scaler.pkl"))
    monkeypatch.setattr("train.METRICS_PATH", str(tmp_path / "metrics.json"))

    save_artifacts(model, scaler, metrics)

    with open(tmp_path / "metrics.json") as f:
        saved = json.load(f)
    assert saved["accuracy"] == metrics["accuracy"]
