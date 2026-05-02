# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Instala dependencias primero (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: trainer ──────────────────────────────────────────────────────────
FROM builder AS trainer

COPY src/ ./src/
COPY data/ ./data/

# Entrena el modelo y genera artifacts en models/
RUN python src/train.py

# ── Stage 3: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Solo copiamos lo necesario para producción
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=trainer /app/models ./models
COPY src/ ./src/

EXPOSE 8000

# Usuario no-root por seguridad
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
