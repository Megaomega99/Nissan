from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    """Base schema for user data."""
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(UserBase):
    """Schema for user login."""
    password: str

class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Token schemas
class TokenResponse(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str

# File schemas
class FileResponse(BaseModel):
    """Schema for file response data."""
    id: int
    filename: str
    upload_date: datetime
    status: str
    file_size: Optional[int] = None
    
    class Config:
        orm_mode = True

# Model schemas
class ModelParamsBase(BaseModel):
    """Base schema for model parameters."""
    pass

class LinearRegressionParams(ModelParamsBase):
    """Schema for LinearRegression parameters."""
    fit_intercept: Optional[bool] = True
    normalize: Optional[bool] = False

class SVRParams(ModelParamsBase):
    """Schema for SVR parameters."""
    C: Optional[float] = 1.0
    epsilon: Optional[float] = 0.1
    kernel: Optional[str] = 'rbf'

class ElasticNetParams(ModelParamsBase):
    """Schema for ElasticNet parameters."""
    alpha: Optional[float] = 1.0
    l1_ratio: Optional[float] = 0.5
    fit_intercept: Optional[bool] = True

class SGDParams(ModelParamsBase):
    """Schema for SGD parameters."""
    loss: Optional[str] = 'squared_loss'
    penalty: Optional[str] = 'l2'
    alpha: Optional[float] = 0.0001
    l1_ratio: Optional[float] = 0.15

class TrainModelRequest(BaseModel):
    """Schema for model training request."""
    model_type: str
    params: Dict[str, Any] = {}
    polynomial_degree: int = 1

class ModelResponse(BaseModel):
    """Schema for model response data."""
    id: int
    file_id: int
    model_type: str
    created_at: datetime
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True

# Task schemas
class TaskResponse(BaseModel):
    """Schema for task status response."""
    state: str
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None