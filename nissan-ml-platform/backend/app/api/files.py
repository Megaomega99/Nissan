# backend/app/api/files.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.file import File
from app.schemas.file import FileResponse, FileMetadata
from app.services.file_service import FileService

router = APIRouter()


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Sube un archivo CSV para procesamiento y análisis ML.
    
    Args:
        file: Archivo CSV a subir
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        FileResponse: Metadatos del archivo subido
    """
    db_file = await FileService.save_upload_file(file, current_user.id, db)
    return db_file


@router.get("/list", response_model=List[FileResponse])
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Lista todos los archivos CSV del usuario actual.
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        List[FileResponse]: Lista de archivos del usuario
    """
    files = FileService.get_user_files(current_user.id, db)
    return files


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene información de un archivo específico.
    
    Args:
        file_id: ID del archivo
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        FileResponse: Metadatos del archivo
    """
    file = FileService.get_file_by_id(file_id, current_user.id, db)
    return file


@router.get("/{file_id}/preview", response_model=FileMetadata)
async def get_file_preview(
    file_id: int,
    max_rows: Optional[int] = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene una vista previa del contenido del archivo.
    
    Args:
        file_id: ID del archivo
        max_rows: Número máximo de filas a devolver
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        FileMetadata: Metadatos y vista previa del archivo
    """
    preview = FileService.get_file_preview(file_id, current_user.id, db, max_rows)
    return preview


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Elimina un archivo del sistema.
    
    Args:
        file_id: ID del archivo a eliminar
        current_user: Usuario autenticado
        db: Sesión de base de datos
    """
    FileService.delete_file(file_id, current_user.id, db)