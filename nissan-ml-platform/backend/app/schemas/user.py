# backend/app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum 

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
        from_attributes = True


class UserResponse(UserBase):
    """Esquema para respuestas con información de usuario."""
    id: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Esquema para token de acceso."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Esquema para el payload del token JWT."""
    sub: Optional[int] = None


