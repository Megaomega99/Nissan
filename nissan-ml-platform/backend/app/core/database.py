# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator, Any

from app.core.config import settings

# Crear el motor de SQLAlchemy para PostgreSQL
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_size=10,  # Tamaño del pool de conexiones
    max_overflow=20,  # Conexiones adicionales permitidas
    pool_recycle=3600,  # Reciclar conexiones después de 1 hora
)

# Sesión local para operaciones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para modelos ORM
Base = declarative_base()


def get_db() -> Generator[Any, None, None]:
    """
    Dependency injection para obtener una sesión de base de datos.
    
    Yields:
        Session: Sesión de SQLAlchemy para interactuar con la base de datos
        
    Example:
        @app.get("/users/")
        def read_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit automático si no hay excepciones
    except Exception:
        db.rollback()  # Rollback en caso de error
        raise
    finally:
        db.close()  # Garantizar que la sesión se cierre