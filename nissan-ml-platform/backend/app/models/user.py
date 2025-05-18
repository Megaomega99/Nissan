# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    Modelo SQLAlchemy para representar usuarios en la base de datos.
    
    Almacena información básica de autenticación y perfil del usuario.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        """Representación de string para depuración."""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


# backend/app/models/file.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class File(Base):
    """
    Modelo SQLAlchemy para representar archivos CSV subidos.
    
    Almacena metadatos del archivo y su relación con el usuario propietario.
    """
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Tamaño en bytes
    
    # Metadatos del CSV
    columns = Column(Text, nullable=True)  # JSON serializado de columnas
    rows_count = Column(Integer, nullable=True)
    
    # Estado de procesamiento
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")
    
    # Relación con el usuario
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="files")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        """Representación de string para depuración."""
        return f"<File(id={self.id}, filename={self.original_filename}, user_id={self.user_id})>"


# backend/app/models/ml_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MLModel(Base):
    """
    Modelo SQLAlchemy para representar modelos de ML entrenados.
    
    Almacena información sobre el tipo de modelo, parámetros, métricas y estado.
    """
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # 'linear_regression', 'svr', 'elasticnet', 'sgd'
    
    # Parámetros utilizados para entrenar el modelo (JSON)
    parameters = Column(JSON, nullable=False, default={})
    
    # Columnas utilizadas para entrenar
    index_column = Column(String, nullable=False)
    target_column = Column(String, nullable=False)
    
    # Métricas de rendimiento
    mae = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)
    
    # Serialización del modelo (alternativamente, se podría guardar en disco)
    model_path = Column(String, nullable=True)
    
    # Estado del entrenamiento
    is_trained = Column(Boolean, default=False)
    training_status = Column(String, default="pending")  # pending, training, completed, failed
    
    # Relaciones
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    file = relationship("File", backref="models")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="models")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        """Representación de string para depuración."""
        return f"<MLModel(id={self.id}, type={self.model_type}, file_id={self.file_id})>"