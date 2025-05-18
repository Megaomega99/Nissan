# backend/app/schemas/file.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class FileBase(BaseModel):
    """Esquema base para archivos."""
    filename: str


class FileCreate(FileBase):
    """Esquema para la creación de un nuevo archivo."""
    pass


class FileMetadata(BaseModel):
    """Esquema para metadatos de un archivo CSV."""
    columns: List[str]
    rows_count: int
    preview_data: Optional[List[Dict[str, Any]]] = None


class FileInDB(FileBase):
    """Esquema para archivo almacenado en la base de datos."""
    id: int
    original_filename: str
    file_path: str
    file_size: int
    is_processed: bool
    processing_status: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileResponse(FileBase):
    """Esquema para respuestas con información de archivos."""
    id: int
    original_filename: str
    file_size: int
    columns: Optional[List[str]] = None
    rows_count: Optional[int] = None
    is_processed: bool
    processing_status: str
    
    class Config:
        from_attributes = True