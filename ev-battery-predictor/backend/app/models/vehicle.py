from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    make = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    battery_capacity = Column(Float)  # kWh
    battery_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="vehicles")
    battery_data = relationship("BatteryData", back_populates="vehicle", cascade="all, delete-orphan")
    ml_models = relationship("MLModel", back_populates="vehicle", cascade="all, delete-orphan")