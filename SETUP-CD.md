# Guía rápida — Hacer funcionar el CD en GitHub Actions

> Sigue los pasos **en orden**. Cada paso tiene un comando para verificar.

---

## 0. Lo que ya tienes ✅

- EC2 corriendo en AWS con IP pública
- Cuenta Docker Hub con token
- AWS CLI configurado en local
- Repo en GitHub: `lupuelloo17/mlops-pipeline-viu`
- Clave privada local: `mlops-key.pem`

---

## 1. Verifica que puedes entrar a la EC2 desde tu Mac

```bash
cd ~/Documents/Universidad_VIU_2025-26/VIU_CDIAI/01_ASIGNATURAS/20GIAR_Dev_Deploy/02_Ejercicios

# Ajustar permisos del .pem (obligatorio en macOS)
chmod 400 mlops-key.pem

# Sustituye <IP_EC2> por tu IP pública
ssh -i mlops-key.pem ec2-user@<IP_EC2>
```

Si te dice **"Permission denied"** → la key no es la correcta o el usuario no es `ec2-user` (en Ubuntu sería `ubuntu`).
Si te dice **"Connection timed out"** → el Security Group no tiene el puerto 22 abierto a tu IP.

---

## 2. Una vez dentro de la EC2, instala Docker

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Comprueba
sudo docker --version
exit
```

> El `cd.yml` nuevo también lo intenta instalar si no está, pero hacerlo a mano evita que el primer deploy tarde minutos.

---

## 3. Abre el puerto 80 en el Security Group de la EC2

En la **consola AWS → EC2 → Security Groups → tu SG → Inbound rules → Edit**:

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | My IP (o 0.0.0.0/0 si quieres) |
| HTTP | TCP | 80 | 0.0.0.0/0 |

---

## 4. Configura los **5 secrets** en GitHub

Ve a:
```
https://github.com/lupuelloo17/mlops-pipeline-viu/settings/secrets/actions
```

Pulsa **"New repository secret"** cinco veces:

| Nombre | Valor |
|--------|-------|
| `DOCKERHUB_USERNAME` | Tu usuario de Docker Hub (ej: `lupuelloo17`) |
| `DOCKERHUB_TOKEN` | El **Access Token** generado en `https://hub.docker.com/settings/security` (NO la contraseña) |
| `EC2_HOST` | La IP pública de tu EC2 (ej: `54.123.45.67`, **sin** `http://`) |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | El contenido **completo** del `mlops-key.pem`, incluyendo las líneas `-----BEGIN ... PRIVATE KEY-----` y `-----END ... PRIVATE KEY-----` |

Para obtener el contenido del .pem listo para pegar:

```bash
cat mlops-key.pem | pbcopy   # ya está en tu portapapeles (macOS)
```

> ⚠️ **Importante**: el cd.yml nuevo NO usa base64. Pega el .pem **tal cual**.

---

## 5. Crea el repositorio en Docker Hub

Ve a `https://hub.docker.com/repositories` → **Create Repository**:

- Name: `iris-mlops-api`
- Visibility: Public

(Si no lo creas, el push del workflow falla con `denied: requested access to the resource is denied`.)

---

## 6. Sube el cd.yml actualizado y dispara el workflow

```bash
cd ~/Documents/Universidad_VIU_2025-26/VIU_CDIAI/01_ASIGNATURAS/20GIAR_Dev_Deploy/02_Ejercicios/mlops-pipeline

git add .github/workflows/cd.yml SETUP-CD.md verify-ec2.sh
git commit -m "fix(cd): use direct ssh key, add diagnostics and smoke test"
git push origin main
```

Después abre:
```
https://github.com/lupuelloo17/mlops-pipeline-viu/actions
```

Y mira el último run de **CD — Deploy a AWS EC2**.

---

## 7. Si vuelve a fallar, mira el primer paso que dé X roja

| Paso que falla | Causa más probable | Solución |
|----------------|---------------------|----------|
| `Verificar que existen los secrets` | Te falta algún secret | Vuelve al paso 4 |
| `Login a Docker Hub` | Token mal pegado o caducado | Genera otro en hub.docker.com |
| `Build y Push imagen` | No existe el repo `iris-mlops-api` en Docker Hub | Paso 5 |
| `Deploy a EC2` → `dial tcp ... timeout` | Puerto 22 cerrado o IP mala | Revisa SG y EC2_HOST |
| `Deploy a EC2` → `Permission denied (publickey)` | Key mal copiada o usuario incorrecto | Revisa EC2_SSH_KEY y EC2_USER |
| `Smoke test público` | Puerto 80 cerrado o app no arranca | Revisa SG y mira logs con `sudo docker logs iris-mlops-api` |

---

## 8. Comprobación final

Cuando el workflow esté verde, abre en el navegador:

```
http://<IP_EC2>/docs
```

Deberías ver el Swagger de FastAPI con el endpoint `/predict`.

Y para probar el modelo:

```bash
curl -X POST http://<IP_EC2>/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```
