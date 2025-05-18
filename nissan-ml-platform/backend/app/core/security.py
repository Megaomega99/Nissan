# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.core.database import get_db

# Configuración del contexto de encriptación para passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de autenticación OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Algoritmo para JWT
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que la contraseña plana coincida con el hash almacenado.
    
    Args:
        plain_password: Contraseña en texto plano proporcionada por el usuario
        hashed_password: Hash de contraseña almacenado en la base de datos
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de contraseña usando bcrypt
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un token JWT de acceso.
    
    Args:
        subject: Identificador del usuario (normalmente user_id)
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        str: Token JWT firmado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency que valida el token JWT y devuelve el usuario actual.
    
    Args:
        db: Sesión de base de datos
        token: Token JWT de autenticación
        
    Returns:
        User: Instancia del modelo de usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    return user