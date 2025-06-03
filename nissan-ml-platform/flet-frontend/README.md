# Plataforma ML Nissan - Flet Frontend

Este frontend en Flet permite probar todos los endpoints del backend de la plataforma Nissan ML.

## Uso local

1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta la app:
   ```bash
   python main.py
   ```

## Uso con Docker Compose

El servicio `flet-frontend` ya está integrado en el `docker-compose.yml` principal. Para levantar todo el stack:

```bash
docker compose up --build
```

La app Flet estará disponible en: http://localhost:8501

## Endpoints cubiertos
- Login y registro
- Healthcheck
- Perfil de usuario
- Subida y listado de archivos
- Preprocesamiento y análisis de archivos

Puedes modificar o ampliar el frontend en `main.py` para cubrir más endpoints.
