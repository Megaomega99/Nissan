# backend/app/api/auth.py
from typing import Any
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user
)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        user_in: Datos del nuevo usuario
        db: Sesión de base de datos
        
    Returns:
        UserResponse: Datos del usuario creado
    """
    # Verificar si el email ya existe
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este correo electrónico ya está registrado"
        )
    
    # Verificar si el username ya existe
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este nombre de usuario ya está registrado"
        )
    
    # Crear hash de la contraseña
    hashed_password = get_password_hash(user_in.password)
    
    # Crear nuevo usuario
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False
    )
    
    # Guardar en la base de datos
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Autentica un usuario y genera un token JWT.
    
    Args:
        form_data: Formulario con credenciales
        db: Sesión de base de datos
        
    Returns:
        Token: Token de acceso JWT
    """
    # Buscar usuario por email o username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    # Verificar credenciales
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Generar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene información del usuario actual.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        UserResponse: Datos del usuario actual
    """
    return current_user