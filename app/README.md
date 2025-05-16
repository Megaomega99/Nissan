# Proyecto Nissan

Este proyecto es una aplicación web que permite a los usuarios:

1. Registrarse e iniciar sesión.
2. Subir y gestionar archivos CSV.
3. Preprocesar datos (eliminar valores nulos, vacíos o infinitos).
4. Entrenar modelos de Machine Learning (Regresión Lineal, SVR, ElasticNet, SDG).
5. Visualizar métricas y gráficos de los modelos entrenados.

## Tecnologías utilizadas

- **Backend**: FastAPI
- **Frontend**: Flet
- **Base de datos**: PostgreSQL
- **Tareas en segundo plano**: Celery
- **Servidor**: Uvicorn

## Estructura del proyecto

- `backend/`: Contiene el código del backend.
- `frontend/`: Contiene el código del frontend.
- `database/`: Configuración y scripts para la base de datos.

## Configuración inicial

1. Clona este repositorio.
2. Instala las dependencias necesarias.
3. Configura las variables de entorno para la base de datos y Celery.
4. Ejecuta el servidor con Uvicorn.
