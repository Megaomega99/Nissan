# backend/app/core/config.py
import logging
import sys
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
    
    # Database settings
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "nissan_ml"
    POSTGRES_PORT: str = "5432"
    
    # File storage settings
    UPLOAD_DIRECTORY: str = "/app/uploads"
    
    # Celery configuration for asynchronous tasks
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
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
            raise ValueError(f"UPLOAD_DIRECTORY is not writable: {v}")
        
        return v
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Construct and return the PostgreSQL database URI.
        
        Pydantic v2 compatibility: we use direct string formatting instead
        of PostgresDsn.build() which has changed its API.
        
        Returns:
            str: Complete database connection URI
        """
        try:
            # Create connection string using direct formatting
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