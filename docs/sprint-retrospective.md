# Sprint Retrospective — Sprint 3

**Fecha:** Mayo 2026  
**Sprint:** 3 — Despliegue continuo y AWS

## ¿Qué fue bien?

- La separación entre CI y CD funcionó exactamente como se esperaba: los tests validan cada commit antes de que llegue a producción.
- El Dockerfile multi-stage redujo el tamaño de la imagen un 60% frente al primer borrador.
- Terraform permitió recrear la infraestructura en minutos desde cero.

## ¿Qué se puede mejorar?

- El secret EC2_SSH_KEY se pegó mal en GitHub la primera vez, lo que causó cinco commits de depuración innecesarios. En el futuro usaré `gh secret set < archivo.pem` desde la CLI en lugar del portapapeles.
- No se configuró HTTPS, la API sirve por HTTP en puerto 80.

## Acciones para el próximo sprint

- Añadir HTTPS con Let's Encrypt
- Configurar monitorización con Prometheus y Grafana
- Migrar el despliegue a ECS Fargate para soportar blue/green deploys
