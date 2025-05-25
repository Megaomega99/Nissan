# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

from app.core.config import settings
from app.api import auth, files, preprocessing, ml_models
from app.core.database import Base, engine
from app.models import user, file, ml_model

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear directorios de almacenamiento
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"],
)
app.include_router(
    files.router,
    prefix=f"{settings.API_V1_STR}/files",
    tags=["files"],
)
app.include_router(
    preprocessing.router,
    prefix=f"{settings.API_V1_STR}/preprocessing",
    tags=["preprocessing"],
)
app.include_router(
    ml_models.router,
    prefix=f"{settings.API_V1_STR}/models",
    tags=["ml-models"],
)


@app.get("/")
async def root():
    """Ruta raíz para verificar que la API está funcionando."""
    return {"message": "Nissan ML Platform API", "status": "online"}


@app.get("/healthcheck")
async def healthcheck():
    """Endpoint para verificar el estado de la API."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # Iniciar servidor con uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )