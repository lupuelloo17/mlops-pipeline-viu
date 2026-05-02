"""
train.py — Entrena un clasificador Random Forest sobre el dataset Iris
y guarda el modelo en models/model.pkl junto con métricas en metrics.json.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")


def load_data() -> tuple:
    """Carga el dataset Iris y lo devuelve como DataFrame."""
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name="target")
    return X, y, iris.target_names.tolist()


def train(X_train, y_train) -> tuple:
    """Entrena el scaler y el clasificador. Devuelve ambos objetos."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )
    model.fit(X_scaled, y_train)
    return model, scaler


def evaluate(model, scaler, X_test, y_test, target_names: list) -> dict:
    """Evalúa el modelo y devuelve un dict con las métricas."""
    X_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_scaled)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
    return {"accuracy": round(float(acc), 4), "classification_report": report}


def save_artifacts(model, scaler, metrics: dict) -> None:
    """Persiste modelo, scaler y métricas en disco."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[train] Modelo guardado en {MODEL_PATH}")
    print(f"[train] Accuracy: {metrics['accuracy']}")


def main():
    X, y, target_names = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model, scaler = train(X_train, y_train)
    metrics = evaluate(model, scaler, X_test, y_test, target_names)
    save_artifacts(model, scaler, metrics)


if __name__ == "__main__":
    main()
