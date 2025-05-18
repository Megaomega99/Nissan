# backend/app/models/ml_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List

from app.core.database import Base


class MLModel(Base):
    """
    Model for trained ML models.
    
    Attributes:
        id: Unique identifier for the model
        name: Human-readable name for the model
        model_type: Type of ML algorithm used
        parameters: JSON containing training parameters
        index_column: Column used as input features
        target_column: Column being predicted
        mae: Mean Absolute Error metric
        mse: Mean Squared Error metric
        rmse: Root Mean Squared Error metric
        r2: R-squared coefficient of determination
        model_path: Path to the serialized model file
        is_trained: Flag indicating if training is complete
        training_status: Current state of training process
        file_id: Foreign key to the source file
        user_id: Foreign key to the user who owns this model
        created_at: Timestamp when the model was created
        updated_at: Timestamp when the model was last updated
    """
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # 'linear_regression', 'svr', 'elasticnet', 'sgd'
    
    # Parameters used for training (JSON format)
    parameters = Column(JSON, nullable=False, default={})
    
    # Columns used for training
    index_column = Column(String, nullable=False)
    target_column = Column(String, nullable=False)
    
    # Performance metrics
    mae = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)
    
    # Model serialization (file path)
    model_path = Column(String, nullable=True)
    
    # Training status
    is_trained = Column(Boolean, default=False)
    training_status = Column(String, default="pending")  # pending, training, completed, failed
    
    # Relationships
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    file = relationship("File", backref="models")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="models")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<MLModel(id={self.id}, type={self.model_type}, file_id={self.file_id})>"