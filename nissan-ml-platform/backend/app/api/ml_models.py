# backend/app/api/ml_models.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
import os
from enum import Enum

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.file import File
from app.models.ml_model import MLModel
from app.services.preprocessing import PreprocessingService
from app.services.file_service import FileService
from app.services.ml_service import MLService
from app.tasks.ml_tasks import train_model_task

router = APIRouter()


class ModelTypeEnum(str, Enum):
    """Enumeración de tipos de modelos ML soportados."""
    LINEAR_REGRESSION = "linear_regression"
    SVR = "svr"
    ELASTIC_NET = "elasticnet"
    SGD = "sgd"


@router.post("/train", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def train_model(
    training_config: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Inicia el entrenamiento asíncrono de un modelo ML.
    
    Args:
        training_config: Configuración de entrenamiento
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Dict[str, Any]: Información sobre el modelo creado y la tarea de entrenamiento
    """
    # Validar datos de entrada
    file_id = training_config.get("file_id")
    model_type = training_config.get("model_type")
    model_name = training_config.get("name", f"Modelo {model_type} - {file_id}")
    parameters = training_config.get("parameters", {})
    index_column = training_config.get("index_column")
    target_column = training_config.get("target_column")
    
    # Verificar datos obligatorios
    if not all([file_id, model_type, index_column, target_column]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faltan parámetros obligatorios: file_id, model_type, index_column, target_column"
        )
    
    # Validar tipo de modelo
    if model_type not in [m.value for m in ModelTypeEnum]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de modelo no soportado. Valores permitidos: {[m.value for m in ModelTypeEnum]}"
        )
    
    # Obtener archivo
    file = FileService.get_file_by_id(file_id, current_user.id, db)
    
    # Crear registro del modelo en la base de datos
    db_model = MLModel(
        name=model_name,
        model_type=model_type,
        parameters=parameters,
        index_column=index_column,
        target_column=target_column,
        file_id=file_id,
        user_id=current_user.id,
        is_trained=False,
        training_status="pending"
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    # Iniciar tarea de entrenamiento en segundo plano
    task_id = train_model_task.delay(
        model_id=db_model.id,
        file_path=file.file_path,
        model_type=model_type,
        index_column=index_column,
        target_column=target_column,
        parameters=parameters
    )
    
    return {
        "model_id": db_model.id,
        "task_id": str(task_id),
        "status": "pending",
        "message": "Entrenamiento iniciado, los resultados estarán disponibles pronto."
    }


@router.get("/list", response_model=List[Dict[str, Any]])
async def list_models(
    file_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Lista los modelos ML del usuario, opcionalmente filtrados por archivo.
    
    Args:
        file_id: ID del archivo para filtrar (opcional)
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        List[Dict[str, Any]]: Lista de modelos ML
    """
    # Construir query base
    query = db.query(MLModel).filter(MLModel.user_id == current_user.id)
    
    # Filtrar por archivo si se especifica
    if file_id:
        query = query.filter(MLModel.file_id == file_id)
    
    # Ejecutar consulta
    models = query.all()
    
    # Formatear resultados
    result = []
    for model in models:
        result.append({
            "id": model.id,
            "name": model.name,
            "model_type": model.model_type,
            "parameters": model.parameters,
            "index_column": model.index_column,
            "target_column": model.target_column,
            "is_trained": model.is_trained,
            "training_status": model.training_status,
            "metrics": {
                "mae": model.mae,
                "mse": model.mse,
                "rmse": model.rmse,
                "r2": model.r2
            },
            "file_id": model.file_id,
            "created_at": model.created_at.isoformat()
        })
    
    return result


@router.get("/{model_id}", response_model=Dict[str, Any])
async def get_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene detalles de un modelo ML específico.
    
    Args:
        model_id: ID del modelo ML
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Dict[str, Any]: Detalles del modelo ML
    """
    # Buscar modelo en la base de datos
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado o no tienes permiso para acceder"
        )
    
    # Formatear respuesta
    result = {
        "id": model.id,
        "name": model.name,
        "model_type": model.model_type,
        "parameters": model.parameters,
        "index_column": model.index_column,
        "target_column": model.target_column,
        "is_trained": model.is_trained,
        "training_status": model.training_status,
        "metrics": {
            "mae": model.mae,
            "mse": model.mse,
            "rmse": model.rmse,
            "r2": model.r2
        },
        "file_id": model.file_id,
        "created_at": model.created_at.isoformat(),
        "updated_at": model.updated_at.isoformat()
    }
    
    return result


@router.post("/{model_id}/predict", response_model=Dict[str, Any])
async def predict(
    model_id: int,
    prediction_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Realiza predicciones con un modelo entrenado.
    
    Args:
        model_id: ID del modelo ML
        prediction_data: Datos para la predicción
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Dict[str, Any]: Resultados de la predicción
    """
    # Buscar modelo en la base de datos
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado o no tienes permiso para acceder"
        )
    
    # Verificar que el modelo esté entrenado
    if not model.is_trained or model.training_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El modelo no está entrenado o el entrenamiento no ha terminado"
        )
    
    try:
        # Cargar modelo
        loaded_model = MLService.load_model(model.model_path)
        
        # Comprobar tipo de predicción
        if "indices" in prediction_data:
            # Predicción para valores específicos
            indices = prediction_data["indices"]
            predictions = MLService.predict(loaded_model, indices)
            
            # Formatear resultados
            result = {
                "indices": indices,
                "predictions": predictions.tolist()
            }
        else:
            # Predicción para el conjunto de datos completo
            # Obtener archivo asociado
            file = db.query(File).filter(File.id == model.file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Archivo no encontrado"
                )
            
            # Leer datos
            df = PreprocessingService.read_csv_file(file.file_path)
            
            # Preparar datos para predicción
            X = df[model.index_column].values.reshape(-1, 1)
            
            # Realizar predicción
            predictions = MLService.predict(loaded_model, X)
            
            # Proyectar valores futuros (doble del índice máximo)
            max_index = float(df[model.index_column].max())
            future_indices = np.linspace(max_index, max_index * 2, 50)
            future_predictions = MLService.predict(loaded_model, future_indices)
            
            # Formatear resultados
            result = {
                "original": {
                    "indices": df[model.index_column].tolist(),
                    "predictions": predictions.tolist(),
                    "actual_values": df[model.target_column].tolist()
                },
                "projection": {
                    "indices": future_indices.tolist(),
                    "predictions": future_predictions.tolist()
                }
            }
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar predicciones: {str(e)}"
        )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Elimina un modelo ML.
    
    Args:
        model_id: ID del modelo ML a eliminar
        current_user: Usuario autenticado
        db: Sesión de base de datos
    """
    # Buscar modelo en la base de datos
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado o no tienes permiso para eliminar"
        )
    
    try:
        # Eliminar archivo del modelo si existe
        if model.model_path and os.path.exists(model.model_path):
            os.remove(model.model_path)
        
        # Eliminar registro de la base de datos
        db.delete(model)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar modelo: {str(e)}"
        )