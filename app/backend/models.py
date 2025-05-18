from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Base class for SQLAlchemy models
Base = declarative_base()

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    files = relationship("FileRecord", back_populates="user", cascade="all, delete-orphan")
    models = relationship("ModelRecord", back_populates="user", cascade="all, delete-orphan")

class FileRecord(Base):
    """File record model to track uploaded files."""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    content_type = Column(String)
    status = Column(String, default="uploaded")  # uploaded, preprocessing, preprocessed, training, etc.
    
    # Relationships
    user = relationship("User", back_populates="files")
    models = relationship("ModelRecord", back_populates="file", cascade="all, delete-orphan")

class ModelRecord(Base):
    """Model record to track trained ML models."""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    model_type = Column(String, nullable=False)
    model_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    visualization_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="models")
    file = relationship("FileRecord", back_populates="models")