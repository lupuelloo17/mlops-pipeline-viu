# Guion del vídeo individual — Defensa 20GIAR

> Duración objetivo: **17 minutos** (rango permitido: 15-20)
> Formato: vídeo individual grabado, entrega antes del 6 de mayo a las 23:59
> Estructura: una intervención por cada una de las 10 slides en Gamma
> Tono: profesional, en primera persona, sin leer literal. Personaliza con tus muletillas naturales.

---

## Antes de empezar

- Coloca la cámara a la altura de los ojos.
- Ten dos pestañas abiertas: la presentación de Gamma y `http://3.14.14.225/docs` para la demo.
- Lleva un terminal listo con un `curl` de ejemplo por si la red falla.
- Habla mirando a cámara, no a la pantalla.
- Si te equivocas, no rebobines: corrige en directo, suena más humano.

---

## Slide 1 — Portada (≈ 30 s)

> Buenos días. Soy **Luis Carlos Puello Fuentes**, alumno del Grado en Ciencia de Datos e Inteligencia Artificial de la Universidad Internacional de Valencia.
>
> En este vídeo voy a presentar el trabajo de la asignatura 20GIAR, **Metodologías de Desarrollo y Despliegue de Aplicaciones para Ciencia de Datos**.
>
> El proyecto se titula **Pipeline MLOps para la clasificación de flores Iris con despliegue automatizado en AWS**, y lo que voy a enseñar es un sistema completo, end-to-end, que ahora mismo está en producción y respondiendo peticiones reales.

---

## Slide 2 — Por qué MLOps + objetivos (≈ 2 min)

> El punto de partida es un dato incómodo: según Algorithmia, **el 87 % de los modelos de machine learning que se desarrollan nunca llegan a producción**. Y los pocos que llegan se mantienen a mano: sin tests, sin versionado, sin posibilidad de hacer rollback. Cambiar una línea de código en ese mundo es prácticamente cruzar los dedos.
>
> **MLOps** es la respuesta a ese problema. Es aplicar las prácticas que llevan quince años funcionando en DevOps —integración continua, despliegue continuo, infraestructura como código— al ciclo de vida específico del machine learning.
>
> Para este proyecto me marqué cinco objetivos, todos con criterios de aceptación verificables:
>
> 1. Construir un **pipeline end-to-end** que cubra desde el entrenamiento hasta el despliegue.
> 2. Garantizar la **reproducibilidad** mediante contenedores, semillas fijas y dependencias versionadas.
> 3. Tener **integración continua** que valide cada commit con una cobertura mínima del 70 %.
> 4. Tener **despliegue continuo** que entregue cada cambio en AWS sin intervención manual.
> 5. Definir la **infraestructura como código** para que se pueda recrear en cualquier cuenta.
>
> El caso de uso elegido es la clasificación de flores Iris con un Random Forest. Iris es deliberadamente sencillo: si el problema fuera más complejo, la atención se iría al modelo y no al pipeline, que es lo que estamos aprendiendo a hacer.

---

## Slide 3 — Arquitectura (≈ 2 min)

> La arquitectura es un **microservicio contenerizado**. Tiene un único servicio responsable de servir predicciones, y lo expongo a través de una API REST.
>
> El flujo es muy directo. El script `train.py` carga el dataset Iris embebido en scikit-learn, entrena un Random Forest de cien árboles, y serializa el modelo y el escalador con joblib en la carpeta `models`.
>
> Esos artefactos los recoge un servidor **FastAPI** que expone el endpoint `/predict`. Cuando llega una petición, el módulo `predict.py` valida la entrada, normaliza las cuatro medidas de la flor con el escalador, y llama al `model.predict_proba` del Random Forest.
>
> Todo este servicio vive dentro de un **contenedor Docker** que corre en una instancia EC2 t3.micro de AWS, en la región us-east-2 (Ohio). Sólo hay una imagen, una instancia y una API. El modelo viaja embebido dentro de la imagen, así que no necesito S3 ni volúmenes externos. La imagen final pesa unos 250 megas en lugar de los 1,5 gigas que tendría si hubiera elegido PyTorch con CUDA.
>
> Un detalle: cada imagen que subo a Docker Hub lleva dos etiquetas, `latest` para el deploy y otra con el SHA del commit, lo que me permite hacer rollback a una versión concreta si algo falla.

---

## Slide 4 — Pipeline en 6 pasos (≈ 2 min)

> Lo que enseño en esta slide es lo que pasa entre que pulso `git push` y la nueva versión está sirviendo tráfico real.
>
> Son seis pasos automatizados:
>
> 1. **Git push** a la rama main.
> 2. **CI**: GitHub Actions ejecuta los 37 tests con pytest y verifica que la cobertura no haya bajado del 70 por ciento. Tarda unos 35 segundos.
> 3. **Build** de la imagen Docker multi-stage con Buildx. Otros 30 segundos.
> 4. **Push** de la imagen a Docker Hub con sus dos tags. Quince segundos.
> 5. **SSH** desde el runner de GitHub a la EC2. Allí se hace `docker pull`, se para el contenedor anterior, se arranca el nuevo y se monta el volumen del modelo. Treinta segundos.
> 6. **Smoke test**: el propio runner hace un `curl` al endpoint `/health` para confirmar que la API responde.
>
> El total son **un minuto y treinta y cinco segundos** desde el commit hasta que la nueva versión está en producción. Y durante ese tiempo el contenedor anterior sigue vivo, así que el cliente no nota ningún corte.

---

## Slide 5 — Stack y API (≈ 2 min)

> En cuanto al stack, la decisión consciente fue **no usar nada exótico**. Python 3.11, scikit-learn para el modelo, FastAPI con Uvicorn para la API, Pydantic versión 2 para la validación, pytest con pytest-cov para los tests, Docker multi-stage, GitHub Actions y Terraform.
>
> Las decisiones más relevantes están justificadas en la memoria, pero las resumo:
>
> **scikit-learn** sobre PyTorch porque Iris es un problema lineal-tabular con tres clases muy separables. PyTorch sería sobre-ingeniería y la imagen pesaría seis veces más.
>
> **FastAPI** sobre Flask porque la validación con Pydantic y la documentación OpenAPI son automáticas. Eso me ahorra escribir código de validación a mano.
>
> **EC2** sobre Lambda porque para un proyecto académico la simplicidad de hacer SSH y ver los logs vale más que el autoscaling.
>
> La API tiene cuatro endpoints. `GET /` con un mensaje de bienvenida. `GET /health` que devuelve si el modelo está cargado en memoria. `GET /metrics` con la accuracy del entrenamiento. Y `POST /predict` que recibe las cuatro medidas de una flor y devuelve la clase con sus probabilidades.
>
> La parte interesante es que toda la documentación interactiva, el Swagger, está disponible en `/docs` sin haber escrito una línea de código para generarla.

---

## Slide 6 — CI y CD (≈ 2 min 30 s)

> La **integración continua** y el **despliegue continuo** están separados a propósito.
>
> El workflow de **CI** se llama `ci.yml` y se dispara en cada push a cualquier rama, no sólo a main. Configura Python 3.11, instala dependencias con caché, entrena el modelo, ejecuta los 37 tests y comprueba la cobertura. Si la cobertura baja del 70 por ciento, el workflow falla automáticamente. La cobertura actual del proyecto es **86,82 por ciento**.
>
> El workflow de **CD** se llama `cd.yml` y se dispara únicamente cuando hay un push a main, así que cualquier commit que rompa los tests no llega a producción. Tiene cinco pasos:
>
> Primero, **verifica que existen los cinco secrets** que necesita: las dos credenciales de Docker Hub y las tres de la EC2. Esto fue una lección aprendida que cuento en un momento.
>
> Después, **login a Docker Hub**, build de la imagen multi-stage, push con las dos etiquetas, conexión SSH a la EC2 y, finalmente, **smoke test** desde el runner contra `/health`.
>
> Sobre el detalle de verificar los secrets como primer paso: el primer despliegue falló cinco veces seguidas porque el secret de la clave SSH se había pegado mal en GitHub. El portapapeles del navegador metía caracteres invisibles que rompían el parser de la action. Como el error sólo aparecía en el último paso, perdía un minuto entero de build cada vez que probaba. Ahora el workflow falla en el primer paso si algún secret está vacío y eso ahorra tiempo de debug.

---

## Slide 7 — AWS y Terraform (≈ 1 min 30 s)

> La **infraestructura está definida con Terraform** en el fichero `main.tf`. Crea tres recursos: la instancia EC2 t3.micro, el grupo de seguridad con los puertos 22 y 80 abiertos, y la pareja de claves SSH.
>
> Además, el `user_data` de la instancia instala Docker automáticamente al primer arranque, así que cuando la máquina termina de inicializarse ya tiene todo lo necesario para correr el contenedor.
>
> El comando es `terraform init` seguido de `terraform apply`, y en unos noventa segundos tengo toda la infraestructura creada desde cero. Sin clicks en la consola de AWS, sin pasos manuales, sin "funciona en mi cuenta pero no en la tuya".
>
> Eso es lo que diferencia un proyecto reproducible de uno que sólo funciona en la máquina del autor.

---

## Slide 8 — Metodología ágil y resultados (≈ 2 min)

> El proyecto se ha organizado siguiendo **SCRUM ligero adaptado a un equipo unipersonal** con sprints de una semana.
>
> El **Sprint 1**, del 13 al 19 de abril, se centró en el modelo y en la API local. El resultado fueron los 37 tests verdes y la cobertura del 86,82 por ciento.
>
> El **Sprint 2**, del 20 al 26 de abril, se dedicó a la contenerización y al CI. Conseguí reducir la imagen de 1,5 gigas a 250 megas con el patrón multi-stage y el CI pasaba en GitHub Actions.
>
> El **Sprint 3**, del 27 de abril al 3 de mayo, fue el más complejo. Implementar el CD, configurar Terraform y desplegar en AWS. Es el sprint donde apareció el bug de la clave SSH que comentaba antes.
>
> La gestión visual la llevé en un **tablero Kanban público en GitHub Projects**, con seis User Stories como issues del repositorio. El Sprint 3 tiene su retrospective documentada en la carpeta `agile/`.
>
> Los **resultados** son los esperados:
>
> - Accuracy del modelo: **0,9333**
> - Cobertura de tests: **86,82 por ciento**
> - Tiempo desde push hasta producción: **un minuto y 35 segundos**
> - Latencia del endpoint `/predict`: **menos de 100 milisegundos**

---

## Slide 9 — Demo en vivo (≈ 2 min 30 s)

> Y ahora la demo en vivo.

[Cambia de pantalla y abre `http://3.14.14.225/docs` en el navegador]

> Estoy abriendo la URL pública de la API: `http://3.14.14.225/docs`. Esta IP corresponde a mi instancia EC2 en la región Ohio. Lo que veis es el Swagger UI generado automáticamente por FastAPI a partir del esquema OpenAPI 3.1. No he escrito ni una línea para que se vea así.

[Click en `/health`, click en "Try it out", click en "Execute"]

> Llamo al endpoint `/health`. La respuesta es `status ok` y `model_loaded true`. Eso confirma que el contenedor está vivo y el modelo serializado se ha cargado correctamente en memoria.

[Click en `/predict`, click en "Try it out"]

> Ahora hago una predicción real con los datos canónicos de una flor Iris setosa: longitud y anchura de sépalo de 5,1 y 3,5, longitud y anchura de pétalo de 1,4 y 0,2.

[Click en "Execute"]

> La respuesta llega en menos de cien milisegundos. La clase predicha es **setosa** con confianza del cien por cien. Las probabilidades por clase son setosa al uno, versicolor y virginica al cero. El modelo está perfectamente seguro de la predicción, lo cual tiene sentido porque la setosa es linealmente separable de las otras dos clases en el espacio de características.

[Si te da tiempo, abre un terminal y ejecuta `ssh -i mlops-deploy-key ec2-user@3.14.14.225 "docker logs --tail 5 iris-mlops-api"`]

> Y por último, si entro por SSH a la máquina y miro los logs del contenedor, puedo ver la petición que acabo de hacer registrada en tiempo real.

---

## Slide 10 — Lecciones y trabajo futuro (≈ 1 min)

> Cierro con dos bloques.
>
> Las **lecciones aprendidas** han sido tres principalmente. La primera es que en MLOps **el modelo apenas ocupa esfuerzo**: lo costoso es la cadena de automatización, los secrets, las claves SSH y los logs opacos de los workflows. La segunda es que cinco commits de prueba y error por una clave mal pegada me hicieron perder más tiempo que entrenar y validar el modelo entero. Y la tercera es que verificar los secrets como primer paso del CD ahorra horas de depuración.
>
> Como **trabajo futuro** dejaría cuatro mejoras concretas: añadir HTTPS con Let's Encrypt para servir por el puerto 443, montar monitorización con Prometheus y Grafana, gestionar el versionado de modelos con MLflow, y migrar a ECS Fargate con balanceador y despliegues blue/green sin downtime.
>
> El código y la documentación completa están públicos en mi repositorio de GitHub: **github.com/lupuelloo17/mlops-pipeline-viu**.
>
> Muchas gracias por su atención.

---

## Checklist final antes de grabar

- [ ] Audio: micrófono cerca, sin eco, sin ruido de fondo.
- [ ] Vídeo: cámara estable, fondo neutro, buena iluminación.
- [ ] Pantalla: resolución 1080p o superior, ventana del navegador con tema claro y zoom 110-125 % para que el código se lea.
- [ ] Pestañas: Gamma + `/docs` + terminal listo.
- [ ] Conexión: si vas a hacer la demo en vivo, comprueba que la API responde dos minutos antes de grabar.
- [ ] Plan B: ten captura de pantalla del Swagger y de una predicción correcta por si la red cae a mitad.
- [ ] Tiempo: cronometra al grabar; objetivo 17 min, no más de 20.
- [ ] Subtítulos: si el formato lo permite, añade subtítulos quemados o transcripción.
- [ ] Formato de salida: MP4 H.264, 1080p, audio AAC. Tamaño objetivo < 500 MB para enviar por correo o nube.
