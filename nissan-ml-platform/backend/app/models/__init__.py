# backend/app/models/__init__.py
from app.core.database import Base

# Import models in dependency order
from app.models.user import User
from app.models.file import File  
from app.models.ml_model import MLModel

# Ensure all models are available for relationship resolution
__all__ = ["Base", "User", "File", "MLModel"]