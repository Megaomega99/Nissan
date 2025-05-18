from celery import Celery
from typing import Dict, Any, Optional, Tuple, List
import os
import json
import logging
from sqlalchemy.orm import Session
from contextlib import contextmanager

# Local imports (with conditional imports to avoid circular dependencies)
from .config import settings
from .ml_utils import preprocess_data, train_model
from .database import db_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "nissan_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Task configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(bind=True, name="preprocess_data_task")
def preprocess_data_task(self, file_path: str) -> Dict[str, Any]:
    """
    Celery task to preprocess data asynchronously.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with preprocessing results
    """
    logger.info(f"Starting preprocessing task for file: {file_path}")
    
    try:
        # Preprocess data
        preprocessed_path = preprocess_data(file_path)
        
        # Update file status in database
        original_filename = os.path.basename(file_path)
        
        with db_session() as db:
            from .models import FileRecord
            file_record = db.query(FileRecord).filter(FileRecord.filename == original_filename).first()
            
            if file_record:
                file_record.status = "preprocessed"
        
        # Return result
        return {
            "status": "success",
            "message": "File preprocessed successfully",
            "preprocessed_path": preprocessed_path
        }
    
    except Exception as e:
        logger.error(f"Error in preprocessing task: {e}")
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise

@celery_app.task(bind=True, name="train_model_task")
def train_model_task(
    self,
    file_path: str, 
    model_type: str, 
    params: Dict[str, Any], 
    polynomial_degree: int = 1,
    user_id: Optional[int] = None,
    file_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Celery task to train ML model asynchronously.
    
    Args:
        file_path: Path to preprocessed CSV file
        model_type: Type of ML model to train
        params: Model parameters
        polynomial_degree: Degree of polynomial features (for regression)
        user_id: ID of user training the model
        file_id: ID of file used for training
        
    Returns:
        Dictionary with model metrics and prediction data
    """
    logger.info(f"Starting model training task: {model_type}")
    
    try:
        # Train model
        result = train_model(
            file_path, 
            model_type, 
            params, 
            polynomial_degree,
            user_id,
            file_id
        )
        
        # Update database with model information
        if user_id and file_id:
            with db_session() as db:
                from .models import ModelRecord, FileRecord
                
                # Create model record
                model_record = ModelRecord(
                    user_id=user_id,
                    file_id=file_id,
                    model_type=model_type,
                    model_path=result["model_path"],
                    parameters=params,
                    metrics=result["metrics"],
                    visualization_data=result["visualization_data"]
                )
                
                db.add(model_record)
                
                # Update file status
                file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
                if file_record:
                    file_record.status = "processed"
        
        # Return result with visualization data
        return {
            "status": "success",
            "message": "Model trained successfully",
            "model_type": model_type,
            "metrics": result["metrics"],
            "visualization_data": result["visualization_data"]
        }
    
    except Exception as e:
        logger.error(f"Error in model training task: {e}")
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise