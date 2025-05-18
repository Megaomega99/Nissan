# backend/app/core/config.py
from pydantic import BaseSettings, PostgresDsn
from typing import Optional, Dict, Any, Union


class Settings(BaseSettings):
    """
    Configuración centralizada para la aplicación.
    Utiliza variables de entorno con valores predeterminados.
    """
    PROJECT_NAME: str = "Nissan ML Platform"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad
    SECRET_KEY: str = "superclavesecreta123456789"  # Cambiar en producción
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    
    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "nissan_ml"
    POSTGRES_PORT: str = "5432"
    
    # Directorio para almacenar archivos CSV
    UPLOAD_DIRECTORY: str = "/app/uploads"
    
    # Configuración Celery para tareas asíncronas
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """Construye la URL de conexión a la base de datos PostgreSQL."""
        return PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia singleton de configuración
settings = Settings()