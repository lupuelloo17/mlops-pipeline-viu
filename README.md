# 🌸 Iris MLOps Pipeline — VIU 20GIAR

Pipeline MLOps completo para clasificación de flores Iris, implementado con FastAPI, Docker, GitHub Actions y AWS.

**Asignatura:** Metodologías de Desarrollo y Despliegue de Aplicaciones para Ciencia de Datos  
**Código:** 20GIAR — Máster en Data Analytics, Universidad Internacional de Valencia  
**Autor:** Luis [apellido]

---

## Arquitectura

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Dataset     │───▶│  train.py    │───▶│  model.pkl   │───▶│  FastAPI     │
│  (Iris CSV)  │    │  sklearn RF  │    │  scaler.pkl  │    │  /predict    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                    │
                    ┌──────────────┐    ┌──────────────┐           │
                    │  AWS EC2     │◀───│   Docker     │◀──────────┘
                    │  t2.micro    │    │  Container   │
                    └──────────────┘    └──────────────┘
                           ▲
                    ┌──────┴───────┐
                    │ GitHub       │
                    │ Actions CD   │
                    └──────────────┘
```

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Modelo | scikit-learn — Random Forest Classifier |
| API | FastAPI + Uvicorn |
| Tests | pytest + pytest-cov |
| Contenedor | Docker (multi-stage build) |
| CI/CD | GitHub Actions |
| IaC | Terraform |
| Cloud | AWS EC2 t2.micro (Free Tier) |

---

## Requisitos previos

- Python 3.11+
- Docker y Docker Compose
- Terraform >= 1.7 (para despliegue en AWS)
- Cuenta AWS con Free Tier activo

---

## Ejecución en local

### 1. Clonar y preparar entorno

```bash
git clone https://github.com/TU_USUARIO/mlops-pipeline.git
cd mlops-pipeline

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Entrenar el modelo

```bash
python src/train.py
# Output: models/model.pkl, models/scaler.pkl, models/metrics.json
# [train] Accuracy: 0.9333
```

### 3. Arrancar la API

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

La API queda disponible en:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 4. Probar un endpoint

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

Respuesta esperada:
```json
{
  "class_index": 0,
  "class_name": "setosa",
  "confidence": 1.0,
  "probabilities": {
    "setosa": 1.0,
    "versicolor": 0.0,
    "virginica": 0.0
  }
}
```

---

## Ejecución con Docker

```bash
# Build y arrancar la API
docker compose up --build

# Entrenar modelo dentro de Docker
docker compose --profile train up trainer

# Verificar que la API responde
curl http://localhost:8000/health
```

---

## Tests

```bash
# Entrenar modelo primero (necesario para tests de integración)
python src/train.py

# Ejecutar tests con reporte de cobertura
pytest tests/ --cov=src --cov-report=term-missing -v
```

Cobertura actual: **86.82%** (mínimo requerido: 70%)

| Módulo | Cobertura |
|--------|-----------|
| src/predict.py | 100% |
| src/train.py | 87% |
| src/api.py | 79% |

---

## Despliegue en AWS con Terraform

### 1. Configurar credenciales AWS

```bash
aws configure
# AWS Access Key ID: [tu key]
# AWS Secret Access Key: [tu secret]
# Default region: eu-west-1
```

### 2. Inicializar y aplicar Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Terraform crea:
- Security Group con puertos 80 y 22 abiertos
- Key Pair SSH
- Instancia EC2 t2.micro con Docker instalado automáticamente

### 3. Obtener IP y conectar

```bash
terraform output instance_public_ip
terraform output ssh_command
```

---

## CI/CD con GitHub Actions

El repositorio tiene dos workflows activos:

### `ci.yml` — Integración continua
Se ejecuta en **cada push** a cualquier rama:
1. Instala dependencias
2. Entrena el modelo
3. Corre los 37 tests con pytest
4. Verifica cobertura ≥ 70%

### `cd.yml` — Despliegue continuo
Se ejecuta en **merge a main**:
1. Build de imagen Docker
2. Push a Docker Hub
3. SSH a EC2 → pull imagen → restart contenedor

### Secrets necesarios en GitHub

| Secret | Descripción |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Tu usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Token de acceso de Docker Hub |
| `EC2_HOST` | IP pública de la instancia EC2 |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | Contenido de tu clave privada SSH |

---

## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Mensaje de bienvenida |
| GET | `/health` | Estado del servicio y del modelo |
| POST | `/predict` | Clasificación de una flor Iris |
| GET | `/metrics` | Métricas del modelo entrenado |

---

## Estructura del proyecto

```
mlops-pipeline/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Tests automáticos
│       └── cd.yml          # Deploy a AWS
├── src/
│   ├── train.py            # Entrenamiento del modelo
│   ├── predict.py          # Lógica de predicción
│   └── api.py              # FastAPI REST API
├── tests/
│   ├── test_train.py       # 10 tests del módulo de entrenamiento
│   ├── test_predict.py     # 11 tests del módulo de predicción
│   └── test_api.py         # 16 tests de integración de la API
├── terraform/
│   ├── main.tf             # Infraestructura AWS
│   └── variables.tf        # Variables configurables
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Orquestación local
├── requirements.txt
└── README.md
```

---

## Reproducibilidad

El pipeline es completamente reproducible:

```bash
git clone https://github.com/TU_USUARIO/mlops-pipeline.git
cd mlops-pipeline
pip install -r requirements.txt
python src/train.py
pytest tests/
uvicorn src.api:app --port 8000
```

Todo el código es determinista (`random_state=42` en train/test split y RandomForest).
