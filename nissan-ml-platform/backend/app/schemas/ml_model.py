# backend/app/schemas/ml_model.py
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ModelTypeEnum(str, Enum):
    """Enumeración de tipos de modelos ML soportados."""
    LINEAR_REGRESSION = "linear_regression"
    SVR = "svr"
    ELASTIC_NET = "elasticnet"
    SGD = "sgd"


class MLModelBase(BaseModel):
    """Esquema base para modelos ML."""
    name: str = Field(..., min_length=1, max_length=100)
    model_type: ModelTypeEnum
    parameters: Dict[str, Any] = {}
    index_column: str
    target_column: str


class MLModelCreate(MLModelBase):
    """Esquema para la creación de un nuevo modelo ML."""
    file_id: int


class MLModelInDB(MLModelBase):
    """Esquema para modelo ML almacenado en la base de datos."""
    id: int
    mae: Optional[float] = None
    mse: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None
    model_path: Optional[str] = None
    is_trained: bool
    training_status: str
    file_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MLModelResponse(MLModelBase):
    """Esquema para respuestas con información del modelo ML."""
    id: int
    mae: Optional[float] = None
    mse: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None
    is_trained: bool
    training_status: str
    file_id: int
    
    class Config:
        from_attributes = True


class MLPrediction(BaseModel):
    """Esquema para las predicciones del modelo ML."""
    indices: List[float]
    predictions: List[float]
    actual_values: Optional[List[float]] = None