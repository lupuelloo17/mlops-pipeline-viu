# Product Backlog — Iris MLOps Pipeline

> Trabajo grupal de la asignatura **20GIAR — Metodologías de Desarrollo y Despliegue de Aplicaciones para Ciencia de Datos** (VIU, 2025-26).
> Autor: Luis Carlos Puello Fuentes.

Cada User Story sigue el formato **Como [rol] quiero [acción] para [beneficio]** y tiene criterios de aceptación verificables. Las historias están priorizadas según valor entregado y agrupadas por sprint.

---

## US-01 — Endpoint de predicción

**Como** usuario de la API
**quiero** un endpoint `POST /predict` que reciba las cuatro medidas de una flor Iris y devuelva la clase predicha
**para** automatizar la clasificación sin tener que ejecutar el modelo a mano.

**Criterios de aceptación**
- [x] La petición acepta JSON con `sepal_length`, `sepal_width`, `petal_length`, `petal_width`.
- [x] La respuesta incluye `class_name`, `confidence` y `probabilities` por clase.
- [x] Valores fuera de rango (negativos o > 30 cm) devuelven HTTP 422 con mensaje claro.
- [x] Una predicción tarda menos de 100 ms.

**Estimación**: 3 puntos · **Sprint**: 1 · **Estado**: Done

---

## US-02 — API en local con un solo comando

**Como** desarrollador del proyecto
**quiero** poder arrancar la API en local con `docker compose up --build`
**para** acelerar el ciclo de desarrollo sin instalar Python ni dependencias en mi máquina.

**Criterios de aceptación**
- [x] El `docker-compose.yml` arranca el contenedor y deja la API en `http://localhost:8000`.
- [x] El endpoint `/health` responde `{"status":"ok","model_loaded":true}`.
- [x] `docker compose --profile train up trainer` permite reentrenar el modelo en el contenedor.

**Estimación**: 2 puntos · **Sprint**: 2 · **Estado**: Done

---

## US-03 — Tests automáticos con cobertura mínima

**Como** responsable de calidad del proyecto
**quiero** que cada commit ejecute automáticamente la batería de pruebas y verifique una cobertura ≥ 70 %
**para** detectar regresiones antes de que lleguen a la rama principal.

**Criterios de aceptación**
- [x] El workflow `ci.yml` se dispara en cada push a cualquier rama y en cada PR a `main`.
- [x] Pytest ejecuta los 37 tests y todos pasan.
- [x] La cobertura medida está por encima del 70 % (objetivo final: 86,82 %).
- [x] El workflow falla si la cobertura baja del umbral.

**Estimación**: 3 puntos · **Sprint**: 2 · **Estado**: Done

---

## US-04 — Despliegue continuo a AWS

**Como** SRE del proyecto
**quiero** que cada merge a `main` despliegue automáticamente la nueva versión en AWS EC2
**para** reducir el time-to-market y eliminar los errores de despliegue manual.

**Criterios de aceptación**
- [x] El workflow `cd.yml` se dispara en push a `main` y también puede lanzarse a mano (workflow_dispatch).
- [x] Construye la imagen Docker multi-stage y la sube a Docker Hub con dos tags (latest y SHA).
- [x] Conecta por SSH a la EC2 y reinicia el contenedor.
- [x] Hace un smoke test contra `/health` desde el runner y falla si la API no responde.
- [x] El tiempo total entre push y nueva versión sirviendo tráfico es menor de 2 minutos.

**Estimación**: 5 puntos · **Sprint**: 3 · **Estado**: Done

---

## US-05 — Infraestructura como código

**Como** auditor o nuevo miembro del equipo
**quiero** que la infraestructura de AWS esté definida con Terraform
**para** poder recrearla en cualquier cuenta o región sin pasos manuales.

**Criterios de aceptación**
- [x] La carpeta `terraform/` contiene `main.tf` y `variables.tf`.
- [x] `terraform plan` muestra los recursos que se crearían: EC2, Security Group, Key Pair.
- [x] `terraform apply` crea la infraestructura completa desde cero.
- [x] Las variables (región, tipo de instancia, CIDR SSH) están parametrizadas.

**Estimación**: 3 puntos · **Sprint**: 3 · **Estado**: Done

---

## US-06 — Documentación reproducible

**Como** profesor que evalúa el trabajo
**quiero** un README claro con todos los pasos para reproducir el sistema en local y en AWS
**para** verificar que el proyecto funciona sin tener que preguntar al autor.

**Criterios de aceptación**
- [x] El README incluye comandos para clonar, instalar, entrenar, testear y arrancar la API.
- [x] Documenta los 5 secrets necesarios para el CD.
- [x] Lista los 4 endpoints con ejemplos de petición y respuesta.
- [x] Incluye un diagrama de la arquitectura.

**Estimación**: 2 puntos · **Sprint**: 3 · **Estado**: Done

---

## Resumen del backlog

| ID | Historia | Sprint | Estimación | Estado |
|---|---|---|---|---|
| US-01 | Endpoint `/predict` | 1 | 3 | ✅ Done |
| US-02 | API en local con Docker Compose | 2 | 2 | ✅ Done |
| US-03 | CI con cobertura mínima | 2 | 3 | ✅ Done |
| US-04 | CD a AWS EC2 | 3 | 5 | ✅ Done |
| US-05 | IaC con Terraform | 3 | 3 | ✅ Done |
| US-06 | Documentación reproducible | 3 | 2 | ✅ Done |

**Total**: 18 puntos repartidos en 3 sprints.
