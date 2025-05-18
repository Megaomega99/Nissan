# backend/app/tasks/ml_tasks.py
from typing import Dict, Any, Optional, Union
from celery import Celery, Task
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
import os
import pandas as pd
import numpy as np
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.ml_model import MLModel
from app.services.preprocessing import PreprocessingService
from app.services.ml_service import MLService

# Configurar Celery
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configurar logging
logger = get_task_logger(__name__)


class SQLAlchemyTask(Task):
    """Clase base para tareas Celery que requieren una sesión de base de datos."""
    
    _db: Optional[Session] = None
    
    @property
    def db(self) -> Session:
        """
        Obtiene una sesión de base de datos.
        
        Returns:
            Session: Sesión de SQLAlchemy
        """
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args: Any, **kwargs: Any) -> None:
        """
        Cierra la sesión de base de datos después de que la tarea termine.
        
        Esta función se llama después de que la tarea se complete,
        sin importar si fue exitosa o falló.
        """
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=SQLAlchemyTask, name="train_model")
def train_model_task(
    self: SQLAlchemyTask,
    model_id: int,
    file_path: str,
    model_type: str,
    index_column: str,
    target_column: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Tarea asíncrona para entrenar un modelo ML.
    
    Args:
        self: Instancia de la tarea Celery
        model_id: ID del modelo en la base de datos
        file_path: Ruta al archivo CSV de entrenamiento
        model_type: Tipo de modelo a entrenar
        index_column: Columna a usar como índice/feature
        target_column: Columna objetivo a predecir
        parameters: Parámetros para el modelo
        
    Returns:
        Dict[str, Any]: Resultados del entrenamiento
    """
    logger.info(f"Iniciando entrenamiento de modelo {model_id} de tipo {model_type}")
    
    # Obtener modelo de la base de datos
    db_model = self.db.query(MLModel).filter(MLModel.id == model_id).first()
    
    if not db_model:
        logger.error(f"Modelo {model_id} no encontrado en la base de datos")
        return {"status": "error", "message": "Modelo no encontrado"}
    
    try:
        # Actualizar estado
        db_model.training_status = "training"
        self.db.commit()
        
        # Cargar datos
        df = PreprocessingService.read_csv_file(file_path)
        
        # Generar ruta para guardar el modelo
        model_path = MLService.generate_model_path(
            model_type=model_type,
            file_id=db_model.file_id,
            user_id=db_model.user_id
        )
        
        # Entrenar modelo
        trained_model, metrics, y_pred, projections = MLService.train_model(
            df=df,
            model_type=model_type,
            index_column=index_column,
            target_column=target_column,
            params=parameters,
            save_path=model_path
        )
        
        # Actualizar modelo en la base de datos
        db_model.is_trained = True
        db_model.training_status = "completed"
        db_model.model_path = model_path
        db_model.mae = metrics["mae"]
        db_model.mse = metrics["mse"]
        db_model.rmse = metrics["rmse"]
        db_model.r2 = metrics["r2"]
        
        self.db.commit()
        
        logger.info(f"Entrenamiento del modelo {model_id} completado con éxito")
        
        return {
            "status": "success",
            "model_id": model_id,
            "metrics": metrics,
            "model_path": model_path
        }
    
    except Exception as e:
        logger.error(f"Error en entrenamiento del modelo {model_id}: {str(e)}")
        
        # Actualizar estado en caso de error
        db_model.training_status = "failed"
        self.db.commit()
        
        return {
            "status": "error",
            "model_id": model_id,
            "message": f"Error en entrenamiento: {str(e)}"
        }