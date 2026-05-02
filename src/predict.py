"""
predict.py — Carga el modelo entrenado y expone la función predict().
"""

import os
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

TARGET_NAMES = ["setosa", "versicolor", "virginica"]

_model = None
_scaler = None


def _load_artifacts():
    """Carga modelo y scaler una sola vez (lazy loading)."""
    global _model, _scaler
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Modelo no encontrado en {MODEL_PATH}. "
                "Ejecuta src/train.py primero."
            )
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)


def predict(features: list[float]) -> dict:
    """
    Recibe una lista de 4 features [sepal_length, sepal_width,
    petal_length, petal_width] y devuelve la clase predicha
    con su probabilidad máxima.
    """
    if len(features) != 4:
        raise ValueError(f"Se esperan 4 features, se recibieron {len(features)}.")

    _load_artifacts()

    X = np.array(features).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    class_idx = int(_model.predict(X_scaled)[0])
    probabilities = _model.predict_proba(X_scaled)[0].tolist()
    confidence = round(max(probabilities), 4)

    return {
        "class_index": class_idx,
        "class_name": TARGET_NAMES[class_idx],
        "confidence": confidence,
        "probabilities": {
            name: round(prob, 4)
            for name, prob in zip(TARGET_NAMES, probabilities)
        },
    }


def reload_model():
    """Fuerza recarga del modelo (útil tras reentrenamiento)."""
    global _model, _scaler
    _model = None
    _scaler = None
    _load_artifacts()
