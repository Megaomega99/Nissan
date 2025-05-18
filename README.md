# README.md
# Plataforma ML para Nissan

Plataforma de Machine Learning para Nissan que permite a los usuarios subir archivos CSV, preprocesar datos y entrenar modelos predictivos.

## Características Principales

- **Autenticación de usuarios**: Sistema completo de registro y login.
- **Gestión de archivos CSV**: Carga, visualización y eliminación de archivos.
- **Preprocesamiento de datos**: Limpieza, manejo de valores nulos y normalización.
- **Entrenamiento de modelos ML**: Soporte para Regresión Lineal, SVR, ElasticNet y SGD.
- **Visualización de resultados**: Gráficas y métricas de evaluación.
- **Predicciones**: Proyección de nuevos valores con los modelos entrenados.

## Arquitectura

Este proyecto sigue una arquitectura de microservicios con separación clara entre frontend, backend y base de datos:

- **Frontend**: React con Material-UI
- **Backend**: FastAPI (Python)
- **Base de datos**: PostgreSQL
- **Tareas asíncronas**: Celery con Redis
- **Contenedores**: Docker y Docker Compose

## Requisitos

- Docker y Docker Compose
- Git

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tuusuario/nissan-ml-platform.git
   cd nissan-ml-platform
   ```

2. Iniciar los servicios con Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Acceder a la aplicación:
   - Frontend: http://localhost:3000
   - API Backend: http://localhost:8000/api/v1/docs

## Estructura del Proyecto

```
nissan-ml-platform/
├── backend/               # API FastAPI 
│   ├── app/               # Código principal
│   ├── Dockerfile         # Contenedor para FastAPI
│   └── Dockerfile.celery  # Contenedor para worker Celery
├── frontend/              # Aplicación React
│   ├── src/               # Código fuente
│   └── Dockerfile         # Contenedor para React
├── database/              # Configuración PostgreSQL
│   ├── init.sql           # Script de inicialización
│   └── Dockerfile         # Contenedor para PostgreSQL
└── docker-compose.yml     # Configuración de servicios
```
## Estructura del Backend

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py           # Endpoints de autenticación
│   │   ├── files.py          # Gestión de archivos CSV
│   │   ├── preprocessing.py  # Endpoints de preprocesamiento
│   │   └── ml_models.py      # Endpoints para modelos ML
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuraciones
│   │   ├── security.py       # JWT y seguridad
│   │   └── database.py       # Conexión a PostgreSQL
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # Modelo de usuario
│   │   ├── file.py           # Modelo de archivos
│   │   └── ml_model.py       # Modelo para ML
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py           # Esquemas Pydantic
│   │   └── file.py           # Esquemas para archivos
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py   # Lógica de negocio para archivos
│   │   ├── preprocessing.py  # Preprocesamiento datos
│   │   └── ml_service.py     # Entrenamiento y predicción
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── ml_tasks.py       # Tareas asíncronas Celery
│   └── main.py               # Punto de entrada principal
├── Dockerfile
└── requirements.txt

```
## Uso

1. Crear una cuenta o iniciar sesión.
2. Subir un archivo CSV desde la interfaz.
3. Realizar preprocesamiento de datos según sea necesario.
4. Entrenar un modelo ML seleccionando columnas y parámetros.
5. Visualizar resultados y realizar predicciones.

## Modelos ML Disponibles

- **Regresión Lineal**: Soporta transformación polinómica.
- **SVR (Support Vector Regression)**: Con distintos kernels.
- **ElasticNet**: Combinación de regularización L1 y L2.
- **SGD (Stochastic Gradient Descent)**: Con distintas funciones de pérdida.

## Contribuir

1. Hacer fork del repositorio
2. Crear una rama para nuevas características: `git checkout -b feature/nueva-caracteristica`
3. Hacer commit de los cambios: `git commit -am 'Añadir nueva característica'`
4. Hacer push a la rama: `git push origin feature/nueva-caracteristica`
5. Enviar Pull Request

## Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE).