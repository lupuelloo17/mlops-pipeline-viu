# Sprints — Iris MLOps Pipeline

> Tres sprints de una semana cada uno. Equipo unipersonal (Luis Carlos Puello Fuentes). Marco SCRUM ligero.

---

## Sprint 1 — Modelo y API local

**Periodo**: 13-19 de abril de 2026 · **Duración**: 1 semana · **Capacidad**: 5 puntos

### Sprint Goal
Tener un modelo Iris entrenado y servido localmente con FastAPI, ejecutable desde la línea de comandos.

### Sprint Backlog
- US-01 — Endpoint `/predict` (3 pts)
- Tarea técnica: estructura de carpetas (`src/`, `tests/`, `models/`)
- Tarea técnica: `requirements.txt` con versiones fijas
- Tarea técnica: validación de entradas con Pydantic v2
- Tarea técnica: 16 tests de integración para la API

### Resultado
- API funcionando en `http://localhost:8000` con Swagger en `/docs`.
- Modelo Random Forest serializado en `models/model.pkl` con accuracy 0,9333.
- 37 tests verdes (10 train + 11 predict + 16 api).
- Cobertura inicial: 86,82 %.

### Burndown
Empezó con 5 puntos, terminó con 0. Sin desviación.

---

## Sprint 2 — Contenedorización y CI

**Periodo**: 20-26 de abril de 2026 · **Duración**: 1 semana · **Capacidad**: 5 puntos

### Sprint Goal
Empaquetar la API en un contenedor Docker reproducible y validar cada commit con un workflow de CI en GitHub Actions.

### Sprint Backlog
- US-02 — API en local con Docker Compose (2 pts)
- US-03 — CI con cobertura mínima (3 pts)
- Tarea técnica: Dockerfile multi-stage de tres etapas (builder → trainer → runtime)
- Tarea técnica: optimización de la imagen final (de 1,5 GB a 250 MB)
- Tarea técnica: workflow `ci.yml` con Python 3.11 y cache de pip

### Resultado
- Imagen Docker en Docker Hub: `lupuelloo17/iris-mlops-api:latest`.
- CI verde en GitHub Actions, ejecuta tests + cobertura en ~35 segundos.
- `docker compose up --build` arranca la API en menos de 30 segundos.

### Burndown
Empezó con 5 puntos, terminó con 0.

---

## Sprint 3 — Despliegue continuo y AWS

**Periodo**: 27 de abril – 3 de mayo de 2026 · **Duración**: 1 semana · **Capacidad**: 10 puntos

### Sprint Goal
Conseguir que cada merge a `main` despliegue la nueva versión en una EC2 de AWS sin intervención manual.

### Sprint Backlog
- US-04 — CD a AWS EC2 (5 pts)
- US-05 — IaC con Terraform (3 pts)
- US-06 — Documentación reproducible (2 pts)
- Tarea técnica: workflow `cd.yml` con build + push + SSH
- Tarea técnica: configuración de los 5 secrets en GitHub
- Tarea técnica: smoke test contra `/health` desde el runner
- Tarea técnica: depuración del problema de la clave SSH (5 commits)

### Resultado
- API desplegada y operativa en `http://3.14.14.225/docs`.
- Tiempo entre push y producción: 1 min 35 s.
- Terraform define EC2, Security Group y Key Pair de forma reproducible.
- README con comandos de despliegue paso a paso.

### Burndown
Empezó con 10 puntos. Hubo un pico de tiempo invertido en depurar la clave SSH (problema con el portapapeles del navegador). Se terminaron los 10 puntos antes de que cerrara el sprint.

### Retrospective
Documentada en `agile/SPRINT-3-RETROSPECTIVE.md`.
