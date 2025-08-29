from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    # Model info
    name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # linear, polynomial, svm, sgd, neural_network, rnn
    description = Column(String(500))
    
    # Model parameters (stored as JSON)
    parameters = Column(JSON)
    
    # Training info
    is_trained = Column(Boolean, default=False)
    training_score = Column(Float)
    validation_score = Column(Float)
    test_score = Column(Float)
    
    # Model storage
    model_file_path = Column(String(255))  # Path to saved model file
    feature_columns = Column(JSON)  # List of feature column names
    target_column = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_trained_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="models")
    vehicle = relationship("Vehicle", back_populates="ml_models")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")