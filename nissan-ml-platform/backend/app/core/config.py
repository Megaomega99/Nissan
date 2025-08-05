# backend/app/core/config.py - Versión modificada para GCP
import logging
import sys
import os
from typing import Optional, Dict, Any, Union, cast
from functools import lru_cache
from pathlib import Path

# Updated import for BaseSettings from pydantic-settings package
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, validator


class LogConfig:
    """Logging configuration to be set for the application."""
    LOGGER_NAME: str = "nissan_ml"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL: str = "INFO"

    @classmethod
    def setup_logging(cls) -> logging.Logger:
        """
        Configure and return a logger with the specified settings.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(cls.LOGGER_NAME)
        logger.setLevel(getattr(logging, cls.LOG_LEVEL))
        
        # Avoid duplicate handlers in case of module reloading
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
            logger.addHandler(handler)
        
        logger.propagate = False
        return logger


logger = LogConfig.setup_logging()


class Settings(BaseSettings):
    """
    Application configuration with environment variable support.
    
    This class centralizes all configuration settings for the application,
    with reasonable defaults that can be overridden by environment variables.
    """
    # Application metadata
    PROJECT_NAME: str = "Nissan ML Platform"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    
    # Security settings
    SECRET_KEY: str = "superclavesecreta123456789"  # Should be overridden in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database settings - Modificado para GCP Cloud SQL
    POSTGRES_SERVER: str = "localhost"  # Para Cloud SQL: /cloudsql/PROJECT:REGION:INSTANCE
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "nissan_ml"
    POSTGRES_PORT: str = "5432"
    
    # File storage settings - Modificado para Cloud Run
    UPLOAD_DIRECTORY: str = "/tmp/uploads"  # Cloud Run usa /tmp para archivos temporales
    
    # Celery configuration for asynchronous tasks - Modificado para Redis Memorystore
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"  # Para GCP: redis://REDIS_IP:6379/0
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Variables específicas para GCP
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GCP_REGION: str = "us-central1"
    CLOUD_SQL_CONNECTION_NAME: Optional[str] = None
    
    @validator("UPLOAD_DIRECTORY")
    def validate_upload_directory(cls, v: str) -> str:
        """
        Ensure the upload directory exists and is writable.
        
        Args:
            v (str): Directory path
            
        Returns:
            str: Validated directory path
        """
        directory = Path(v)
        directory.mkdir(parents=True, exist_ok=True)
        
        if not directory.is_dir():
            raise ValueError(f"UPLOAD_DIRECTORY must be a directory: {v}")
        
        # Check if directory is writable by trying to create a temporary file
        try:
            test_file = directory / ".test_write_permission"
            test_file.touch()
            test_file.unlink()
        except (IOError, PermissionError):
            logger.warning(f"UPLOAD_DIRECTORY might not be writable: {v}")
            # En Cloud Run esto es normal para /tmp, así que solo advertimos
        
        return v
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Construct and return the PostgreSQL database URI.
        
        Para GCP Cloud SQL, detecta automáticamente si estamos usando Cloud SQL Proxy.
        
        Returns:
            str: Complete database connection URI
        """
        try:
            # Detectar si estamos en Cloud Run con Cloud SQL
            if self.POSTGRES_SERVER.startswith('/cloudsql/'):
                # Conexión vía Unix socket para Cloud SQL
                connection_uri = (
                    f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                    f"/{self.POSTGRES_DB}?host={self.POSTGRES_SERVER}"
                )
            else:
                # Conexión TCP estándar
                connection_uri = (
                    f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                    f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
                )
            return connection_uri
        except Exception as e:
            logger.error(f"Error building database URI: {str(e)}")
            raise RuntimeError(f"Failed to build database URI: {str(e)}") from e

    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        case_sensitive = True
        # Validate all fields during assignment
        validate_assignment = True


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached instance of the settings.
    
    This function uses lru_cache for performance, avoiding
    reloading the environment variables on each call.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Application settings instance
settings = get_settings()
