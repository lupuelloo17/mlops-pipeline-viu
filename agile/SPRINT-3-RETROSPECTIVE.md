# Sprint 3 — Retrospective

**Sprint**: 3 (Despliegue continuo y AWS)
**Periodo**: 27 de abril – 3 de mayo de 2026
**Participante**: Luis Carlos Puello Fuentes
**Fecha de la retrospective**: 3 de mayo de 2026

---

## Lo que fue bien

- **Separación CI / CD**: tener dos workflows diferenciados permitió iterar el CD sin tocar el CI. Los 37 tests siguieron pasando mientras yo rompía y arreglaba la conexión SSH a la EC2.
- **Docker multi-stage**: la imagen final pesa 250 MB en lugar de los 1,5 GB de un PyTorch base. Eso recortó el tiempo de `docker push` y `docker pull` en cada despliegue.
- **Terraform reproducible**: la infraestructura quedó definida en `main.tf`. Si tuviera que recrearla mañana en otra cuenta de AWS, sería un `terraform apply` y listo.
- **Smoke test al final del CD**: incluir un `curl /health` desde el runner de GitHub me ahorró ir a la EC2 a comprobar manualmente que la API estaba arriba.

## Lo que no fue bien

- **Clave SSH mal pegada al secret**: el primer intento de despliegue falló con un error críptico (`ssh: handshake failed: unable to authenticate, attempted methods [none publickey]`). Tardé 5 commits en darme cuenta de que el problema estaba en cómo se había pegado la clave en el secret de GitHub: el portapapeles del navegador añadía caracteres invisibles que rompían el parser.
- **Usé `key_path` en vez de `key`**: la primera versión del workflow usaba `key_path: /github/workspace/ec2_key.pem` con la action `appleboy/ssh-action`. El path no se montaba correctamente dentro del contenedor de la action y la conexión se quedaba en silencio.
- **Probé soluciones sin diagnosticar primero**: las primeras tres iteraciones fueron a ciegas (probar base64, probar otra forma de escribir la clave). Hubiera sido más rápido leer los logs completos al principio y entender qué pasaba en el handshake.
- **Mezclé dos instancias EC2**: durante el desarrollo creé una segunda EC2 (`mlops-ec2`) por error, con otra key pair. Eso confundió la depuración hasta que la terminé.

## Acciones para el próximo sprint

1. **Usar `gh secret set < archivo.pem`** en lugar del portapapeles para subir secrets binarios o multilínea. Evita los caracteres invisibles.
2. **Empezar por el log antes que por el código**: en cualquier fallo del CD, leer el log completo del paso fallido antes de tocar el YAML.
3. **No crear recursos AWS de prueba sin etiquetar**: cualquier EC2 de prueba debe tener un tag `purpose=temporary` y una fecha de expiración. Así no se acumulan instancias dormidas que cuestan dinero y confunden la depuración.
4. **Añadir un endpoint `/reload`** que recargue el modelo desde disco sin reiniciar el contenedor. Útil para futuros cambios de modelo sin downtime.
5. **Documentar HTTPS con Let's Encrypt** en el siguiente sprint para servir la API por puerto 443.

## Métricas del sprint

| Métrica | Valor |
|---|---|
| Puntos planificados | 10 |
| Puntos completados | 10 |
| Commits | 32 |
| Pull requests | 4 |
| Workflow runs (CI) | 12 |
| Workflow runs (CD) | 12 |
| CD failures antes del primer verde | 9 |
| Tiempo desperdiciado en el bug del SSH | ≈ 4 horas |

## Lección clave del sprint

En un proyecto MLOps, **el modelo no es el problema**: el problema es la cadena de automatización. Una clave SSH mal pegada al secret de GitHub puede hacer perder más tiempo que entrenar y validar el modelo entero. Invertir en herramientas de diagnóstico (logs claros, smoke tests, verificación temprana de secrets) compensa con creces el tiempo dedicado.
