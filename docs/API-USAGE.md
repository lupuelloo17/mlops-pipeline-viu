# Cómo usar la API — Iris MLOps

> URL pública: **http://3.14.14.225**
> Documentación interactiva: **http://3.14.14.225/docs**
> Esquema OpenAPI 3.1: **http://3.14.14.225/openapi.json**

La API expone cuatro endpoints. Para hacer una predicción solo necesitas el `POST /predict`; los demás son utilitarios.

---

## 1. Endpoints disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Mensaje de bienvenida |
| `GET` | `/health` | Estado del servicio y si el modelo está cargado |
| `GET` | `/metrics` | Accuracy del modelo entrenado |
| `POST` | `/predict` | Clasifica una flor a partir de sus 4 medidas |

---

## 2. Probar desde el navegador (forma más rápida)

Abre directamente:

- http://3.14.14.225/docs

Verás el Swagger UI. Despliega `POST /predict`, pulsa **"Try it out"**, edita el JSON con tus medidas y pulsa **"Execute"**. La respuesta aparece debajo en JSON.

---

## 3. Probar desde la terminal con `curl`

### 3.1. Comprobar que la API está viva

```bash
curl http://3.14.14.225/health
# {"status":"ok","model_loaded":true}
```

### 3.2. Hacer una predicción

```bash
curl -X POST http://3.14.14.225/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

Respuesta:

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

### 3.3. Ver las métricas del entrenamiento

```bash
curl http://3.14.14.225/metrics
```

---

## 4. Probar desde Python

```python
import requests

URL = "http://3.14.14.225/predict"

flor = {
    "sepal_length": 6.7,
    "sepal_width": 3.0,
    "petal_length": 5.2,
    "petal_width": 2.3,
}

resp = requests.post(URL, json=flor, timeout=5)
resp.raise_for_status()

data = resp.json()
print(f"Clase predicha: {data['class_name']}")
print(f"Confianza: {data['confidence']:.2%}")
print("Probabilidades por clase:")
for clase, p in data["probabilities"].items():
    print(f"  {clase:11s}: {p:.2%}")
```

Salida esperada:

```
Clase predicha: virginica
Confianza: 99.00%
Probabilidades por clase:
  setosa     : 0.00%
  versicolor : 1.00%
  virginica  : 99.00%
```

---

## 5. Probar desde Postman

1. Crea una nueva request con método `POST` y URL `http://3.14.14.225/predict`.
2. Pestaña **Headers**: añade `Content-Type: application/json`.
3. Pestaña **Body** → **raw** → **JSON**, pega:

```json
{
  "sepal_length": 5.9,
  "sepal_width": 3.0,
  "petal_length": 4.2,
  "petal_width": 1.5
}
```

4. Pulsa **Send**. La respuesta aparece en la mitad inferior con la clase predicha.

---

## 6. Datos de ejemplo para cada clase

Estos son ejemplos típicos del dataset Iris para que puedas probar las tres clases:

### Iris setosa
```json
{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
```

### Iris versicolor
```json
{"sepal_length": 5.9, "sepal_width": 3.0, "petal_length": 4.2, "petal_width": 1.5}
```

### Iris virginica
```json
{"sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3}
```

---

## 7. Validación de entradas

La API valida los rangos con Pydantic. Si envías un valor fuera de rango, devuelve **HTTP 422 Unprocessable Entity** con un mensaje claro.

| Campo | Mín | Máx |
|-------|-----|-----|
| `sepal_length` | 0 | 30 |
| `sepal_width`  | 0 | 30 |
| `petal_length` | 0 | 30 |
| `petal_width`  | 0 | 30 |

Ejemplo de error:

```bash
curl -X POST http://3.14.14.225/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":-1,"sepal_width":3,"petal_length":4,"petal_width":1}'
```

```json
{
  "detail": [
    {
      "loc": ["body", "sepal_length"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

---

## 8. Códigos de estado HTTP

| Código | Significado | Cuándo |
|--------|-------------|--------|
| `200 OK` | Predicción correcta | El JSON era válido |
| `422 Unprocessable Entity` | Validación fallida | Falta un campo o el valor está fuera de rango |
| `500 Internal Server Error` | Error en el servidor | El modelo no está cargado o hubo una excepción |
| `502 / 504` | Sin respuesta del servidor | El contenedor está reiniciándose o la EC2 no responde |

---

## 9. Rendimiento esperado

- **Latencia media** de `/predict`: < 100 ms (modelo en memoria, sin carga remota).
- **Throughput** estimado en la t3.micro: ~50 req/s en una sola instancia (no probado bajo carga real).
- **Disponibilidad**: el contenedor tiene `--restart unless-stopped`, así que sobrevive a reinicios. La instancia EC2 no tiene HA: si AWS para la zona, la API cae.

---

## 10. ¿Cómo se actualiza el modelo en producción?

El flujo automatizado (CI/CD) es:

1. Cambias `src/train.py` o cualquier código.
2. `git push origin main`.
3. GitHub Actions ejecuta CI (tests + cobertura).
4. Si pasa, el CD hace build de la imagen, push a Docker Hub, SSH a EC2, pull y restart.
5. En ~1 min 35 s la nueva versión está sirviendo tráfico.

No hay paso manual. Si modificas el modelo, sube el código y espera al despliegue.

---

## 11. Casos de uso típicos

### 11.1. Integración en una app web

```javascript
// React + fetch
async function predecirIris(medidas) {
  const r = await fetch("http://3.14.14.225/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(medidas),
  });
  return r.json();
}
```

### 11.2. Procesamiento por lotes

```python
import requests, pandas as pd

df = pd.read_csv("flores_a_clasificar.csv")
URL = "http://3.14.14.225/predict"

resultados = []
for _, fila in df.iterrows():
    r = requests.post(URL, json=fila.to_dict()).json()
    resultados.append(r["class_name"])

df["clase_predicha"] = resultados
df.to_csv("flores_clasificadas.csv", index=False)
```

### 11.3. Test rápido desde el smartphone

Abre Safari/Chrome en el móvil y entra en `http://3.14.14.225/docs`. El Swagger es responsive y permite probar `/predict` directamente desde el teléfono.

---

## 12. Limitaciones actuales

- **Sin HTTPS**: la API se sirve por HTTP plano (puerto 80). En un escenario real añadiría Let's Encrypt y nginx en frente.
- **Sin autenticación**: cualquiera con la IP puede llamar. Para uso académico es aceptable; para producción añadiría una API key como header.
- **Sin rate limiting**: no hay protección contra abuso.
- **Modelo congelado**: el modelo se entrena en cada build de imagen. No hay endpoint `/reload` para recargar sin reiniciar el contenedor.
- **Una sola instancia**: si la EC2 cae, no hay failover.

Estas limitaciones están listadas como trabajo futuro en la memoria del proyecto.
