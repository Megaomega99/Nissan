# backend/app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class UserBase(BaseModel):
    """Esquema base para usuarios con campos comunes."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Esquema para creación de usuarios."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Valida que la contraseña cumpla con requisitos mínimos de seguridad."""
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un dígito')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        return v


class UserLogin(BaseModel):
    """Esquema para autenticación de usuarios."""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Esquema para usuario almacenado en la base de datos."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class UserResponse(UserBase):
    """Esquema para respuestas con información de usuario."""
    id: int
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    """Esquema para token de acceso."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Esquema para el payload del token JWT."""
    sub: Optional[int] = None


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
        orm_mode = True


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
        orm_mode = True


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
        orm_mode = True


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
        orm_mode = True


class MLPrediction(BaseModel):
    """Esquema para las predicciones del modelo ML."""
    indices: List[float]
    predictions: List[float]
    actual_values: Optional[List[float]] = None