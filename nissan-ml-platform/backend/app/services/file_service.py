# backend/app/services/file_service.py
from typing import Dict, List, Optional, Tuple, Any, Union, BinaryIO
import pandas as pd
import os
import json
import shutil
from pathlib import Path
import logging
from datetime import datetime
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file import File
from app.models.user import User
from app.services.preprocessing import PreprocessingService

# Configurar logging
logger = logging.getLogger(__name__)


class FileService:
    """
    Servicio para la gestión de archivos CSV.
    
    Proporciona funcionalidades para subir, leer, analizar y eliminar
    archivos CSV para el entrenamiento de modelos ML.
    """
    
    @staticmethod
    async def save_upload_file(
        upload_file: UploadFile, 
        user_id: int,
        db: Session
    ) -> File:
        """
        Guarda un archivo subido por el usuario y registra sus metadatos.
        
        Args:
            upload_file: Archivo subido por el usuario
            user_id: ID del usuario que sube el archivo
            db: Sesión de base de datos
            
        Returns:
            File: Objeto del modelo File con los metadatos del archivo
            
        Raises:
            HTTPException: Si hay error al guardar el archivo
        """
        try:
            # Verificar extensión del archivo
            if not upload_file.filename or not upload_file.filename.lower().endswith('.csv'):
                raise HTTPException(
                    status_code=400,
                    detail="Solo se permiten archivos CSV"
                )
            
            # Crear directorio para archivos del usuario si no existe
            user_upload_dir = os.path.join(settings.UPLOAD_DIRECTORY, str(user_id))
            os.makedirs(user_upload_dir, exist_ok=True)
            
            # Generar nombre único para el archivo
            original_filename = upload_file.filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            safe_filename = f"{timestamp}_{unique_id}_{original_filename}"
            file_path = os.path.join(user_upload_dir, safe_filename)
            
            # Guardar archivo en disco
            contents = await upload_file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Determinar tamaño del archivo
            file_size = os.path.getsize(file_path)
            
            # Leer archivo para obtener metadatos básicos
            try:
                df = PreprocessingService.read_csv_file(file_path)
                columns_json = json.dumps(df.columns.tolist())
                rows_count = len(df)
            except Exception as e:
                logger.warning(f"Error al extraer metadatos del CSV: {str(e)}")
                columns_json = "[]"
                rows_count = 0
            
            # Crear registro en la base de datos
            db_file = File(
                filename=safe_filename,
                original_filename=original_filename,
                file_path=file_path,
                file_size=file_size,
                columns=columns_json,
                rows_count=rows_count,
                user_id=user_id
            )
            
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            return db_file
            
        except HTTPException:
            # Re-lanzar excepciones HTTP
            raise
        except Exception as e:
            logger.error(f"Error al guardar archivo: {str(e)}")
            # Limpiar archivo si se creó
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar el archivo: {str(e)}"
            )

    @staticmethod
    def delete_file(file_id: int, user_id: int, db: Session) -> bool:
        """
        Elimina un archivo y su registro en la base de datos.
        
        Args:
            file_id: ID del archivo a eliminar
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            HTTPException: Si el archivo no existe o no pertenece al usuario
        """
        # Buscar archivo en la base de datos
        db_file = db.query(File).filter(File.id == file_id, File.user_id == user_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado o no tienes permiso para eliminarlo"
            )
        
        try:
            # Eliminar archivo físico
            if os.path.exists(db_file.file_path):
                os.remove(db_file.file_path)
            
            # Eliminar registro de la base de datos
            db.delete(db_file)
            db.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar archivo {file_id}: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar archivo: {str(e)}"
            )

    @staticmethod
    def get_file_preview(file_id: int, user_id: int, db: Session, max_rows: int = 10) -> Dict[str, Any]:
        """
        Obtiene una vista previa de los datos del archivo.
        
        Args:
            file_id: ID del archivo
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            max_rows: Número máximo de filas a devolver
            
        Returns:
            Dict: Diccionario con metadatos y vista previa
            
        Raises:
            HTTPException: Si el archivo no existe o hay error al leerlo
        """
        # Buscar archivo en la base de datos
        db_file = db.query(File).filter(File.id == file_id, File.user_id == user_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado o no tienes permiso para acceder"
            )
        
        try:
            # Leer archivo CSV
            df = PreprocessingService.read_csv_file(db_file.file_path)
            
            # Obtener metadatos
            metadata = PreprocessingService.get_file_metadata(df)
            
            # Limitar vista previa
            preview_df = df.head(max_rows)
            metadata['preview_data'] = preview_df.to_dict(orient='records')
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error al obtener vista previa de {file_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al leer archivo: {str(e)}"
            )

    @staticmethod
    def get_user_files(user_id: int, db: Session) -> List[File]:
        """
        Obtiene todos los archivos del usuario.
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            List[File]: Lista de archivos del usuario
        """
        return db.query(File).filter(File.user_id == user_id).all()

    @staticmethod
    def get_file_by_id(file_id: int, user_id: int, db: Session) -> File:
        """
        Obtiene un archivo por su ID.
        
        Args:
            file_id: ID del archivo
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            File: Objeto del modelo File
            
        Raises:
            HTTPException: Si el archivo no existe o no pertenece al usuario
        """
        db_file = db.query(File).filter(File.id == file_id, File.user_id == user_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado o no tienes permiso para acceder"
            )
        
        return db_file