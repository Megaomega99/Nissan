from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class BatteryData(Base):
    __tablename__ = "battery_data"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    # Battery health metrics
    state_of_health = Column(Float, nullable=False)  # SOH (0-100%)
    state_of_charge = Column(Float)  # SOC (0-100%)
    voltage = Column(Float)  # Volts
    current = Column(Float)  # Amperes
    temperature = Column(Float)  # Celsius
    
    # Additional metrics
    cycle_count = Column(Integer)  # Number of charge cycles
    capacity_fade = Column(Float)  # Percentage capacity loss
    internal_resistance = Column(Float)  # Ohms
    
    # Metadata
    measurement_timestamp = Column(DateTime(timezone=True), nullable=False)
    data_source = Column(String(50))  # e.g., "OBD", "Manual", "Sensor"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="battery_data")