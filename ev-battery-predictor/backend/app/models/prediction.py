from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    
    # Prediction input and output
    input_data = Column(JSON)  # Input features used for prediction
    predicted_soh = Column(Float, nullable=False)  # Predicted State of Health
    confidence_interval = Column(JSON)  # [lower_bound, upper_bound]
    
    # Failure prediction
    estimated_failure_date = Column(DateTime(timezone=True))
    failure_probability = Column(Float)  # 0-1 probability of failure within timeframe
    
    # Metadata
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    prediction_type = Column(String(50))  # "current", "future", "failure_analysis"
    
    # Relationships
    model = relationship("MLModel", back_populates="predictions")