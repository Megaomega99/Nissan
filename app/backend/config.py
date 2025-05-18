from pydantic import BaseSettings, PostgresDsn
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    # Database settings
    DATABASE_URL: PostgresDsn = "postgresql://user:password@localhost/nissan_db"
    
    # Security settings
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Application settings
    DEBUG: bool = True
    UPLOAD_DIR: str = "uploaded_files"
    MODELS_DIR: str = "models"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()
