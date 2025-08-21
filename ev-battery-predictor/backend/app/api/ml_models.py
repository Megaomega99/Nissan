from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import pandas as pd
import os
from datetime import datetime

from ..core.database import get_db
from ..models.user import User
from ..models.vehicle import Vehicle
from ..models.ml_model import MLModel
from ..models.battery_data import BatteryData
from ..ml.models import MLModelFactory, ModelTrainer
from .auth import get_current_user

router = APIRouter()

class MLModelCreate(BaseModel):
    vehicle_id: int
    name: str
    model_type: str  # linear, polynomial, svm, sgd, neural_network, rnn
    description: str | None = None
    parameters: Dict[str, Any] | None = None
    feature_columns: List[str] | None = None
    target_column: str = "state_of_health"

class MLModelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    parameters: Dict[str, Any] | None = None

class MLModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    vehicle_id: int
    name: str
    model_type: str
    description: str | None
    parameters: Dict[str, Any] | None
    is_trained: bool
    training_score: float | None
    validation_score: float | None
    test_score: float | None
    feature_columns: List[str] | None
    target_column: str
    created_at: datetime
    updated_at: datetime | None
    last_trained_at: datetime | None

class TrainingRequest(BaseModel):
    test_size: float = 0.2

class TrainingResponse(BaseModel):
    success: bool
    message: str
    training_score: float | None = None
    test_score: float | None = None

@router.post("/", response_model=MLModelResponse)
async def create_ml_model(
    model_data: MLModelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify vehicle belongs to user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == model_data.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Validate model type
    valid_types = ["linear", "polynomial", "svm", "sgd", "neural_network", "rnn"]
    if model_data.model_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model type. Must be one of: {valid_types}"
        )
    
    # Create model
    ml_model = MLModel(
        user_id=current_user.id,
        vehicle_id=model_data.vehicle_id,
        name=model_data.name,
        model_type=model_data.model_type,
        description=model_data.description,
        parameters=model_data.parameters or {},
        feature_columns=model_data.feature_columns,
        target_column=model_data.target_column
    )
    
    db.add(ml_model)
    db.commit()
    db.refresh(ml_model)
    return ml_model

@router.get("/", response_model=List[MLModelResponse])
async def get_ml_models(
    vehicle_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(MLModel).filter(MLModel.user_id == current_user.id)
    
    if vehicle_id:
        # Verify vehicle belongs to user
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == vehicle_id,
            Vehicle.user_id == current_user.id
        ).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        query = query.filter(MLModel.vehicle_id == vehicle_id)
    
    models = query.all()
    return models

@router.get("/{model_id}", response_model=MLModelResponse)
async def get_ml_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model

@router.put("/{model_id}", response_model=MLModelResponse)
async def update_ml_model(
    model_id: int,
    model_update: MLModelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    update_data = model_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    return model

@router.post("/{model_id}/train", response_model=TrainingResponse)
async def train_ml_model(
    model_id: int,
    training_request: TrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get model
    ml_model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Get battery data for the vehicle
    battery_data = db.query(BatteryData).filter(
        BatteryData.vehicle_id == ml_model.vehicle_id
    ).all()
    
    if len(battery_data) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 10 data points to train a model"
        )
    
    # Convert to DataFrame
    data_dicts = []
    for data in battery_data:
        data_dict = {
            'state_of_health': data.state_of_health,
            'state_of_charge': data.state_of_charge,
            'voltage': data.voltage,
            'current': data.current,
            'temperature': data.temperature,
            'cycle_count': data.cycle_count,
            'capacity_fade': data.capacity_fade,
            'internal_resistance': data.internal_resistance,
            'measurement_timestamp': data.measurement_timestamp
        }
        data_dicts.append(data_dict)
    
    df = pd.DataFrame(data_dicts)
    
    try:
        # Train model in background
        background_tasks.add_task(
            train_model_task,
            ml_model.id,
            df,
            ml_model.model_type,
            ml_model.parameters or {},
            ml_model.feature_columns,
            ml_model.target_column,
            training_request.test_size
        )
        
        return TrainingResponse(
            success=True,
            message="Training started. Check model status for completion."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )

@router.delete("/{model_id}")
async def delete_ml_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Delete model file if exists
    if model.model_file_path and os.path.exists(model.model_file_path):
        os.remove(model.model_file_path)
    
    db.delete(model)
    db.commit()
    return {"message": "Model deleted successfully"}

def train_model_task(model_id: int, df: pd.DataFrame, model_type: str, 
                    parameters: Dict[str, Any], feature_columns: List[str] | None,
                    target_column: str, test_size: float):
    """Background task for training models"""
    from ..core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get the model
        ml_model = db.query(MLModel).filter(MLModel.id == model_id).first()
        if not ml_model:
            return
        
        # Initialize trainer
        trainer = ModelTrainer()
        
        # Prepare data
        X, y, feature_cols = trainer.prepare_data(df, target_column, feature_columns)
        
        if len(X) < 5:
            ml_model.is_trained = False
            db.commit()
            return
        
        # Create model
        model = MLModelFactory.create_model(model_type, parameters)
        
        # Train model
        results = trainer.train_model(model, X, y, test_size)
        
        # Save model
        model_dir = f"models/user_{ml_model.user_id}/vehicle_{ml_model.vehicle_id}"
        os.makedirs(model_dir, exist_ok=True)
        model_path = f"{model_dir}/model_{model_id}"
        
        trainer.save_model(model, model_path, trainer.scaler if hasattr(trainer, 'scaler') else None)
        
        # Update model in database
        ml_model.is_trained = True
        ml_model.training_score = results["train_score"]
        ml_model.test_score = results["test_score"]
        ml_model.validation_score = results["test_score"]  # Using test as validation for simplicity
        ml_model.model_file_path = model_path
        ml_model.feature_columns = feature_cols
        ml_model.last_trained_at = datetime.now()
        
        db.commit()
        
    except Exception as e:
        # Mark training as failed
        ml_model = db.query(MLModel).filter(MLModel.id == model_id).first()
        if ml_model:
            ml_model.is_trained = False
            db.commit()
        print(f"Training failed for model {model_id}: {str(e)}")
        
    finally:
        db.close()