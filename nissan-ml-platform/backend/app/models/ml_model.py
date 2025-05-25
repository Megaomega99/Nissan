# backend/app/models/ml_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func

from app.core.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False, default={})
    index_column = Column(String, nullable=False)
    target_column = Column(String, nullable=False)
    mae = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)
    model_path = Column(String, nullable=True)
    is_trained = Column(Boolean, default=False)
    training_status = Column(String, default="pending")
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<MLModel(id={self.id}, type={self.model_type}, file_id={self.file_id})>"