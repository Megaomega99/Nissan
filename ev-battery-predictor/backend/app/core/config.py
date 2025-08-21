from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://evuser:evpass123@db:5432/evbattery"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis (for caching and task queue)
    REDIS_URL: str = "redis://redis:6379"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EV Battery Predictor"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://frontend:3000"]
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()