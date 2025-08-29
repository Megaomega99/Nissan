from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import pandas as pd
import io

from ..core.database import get_db
from ..models.user import User
from ..models.vehicle import Vehicle
from ..models.battery_data import BatteryData
from .auth import get_current_user

router = APIRouter()

class BatteryDataCreate(BaseModel):
    vehicle_id: int
    state_of_health: float
    state_of_charge: float | None = None
    voltage: float | None = None
    current: float | None = None
    temperature: float | None = None
    cycle_count: int | None = None
    capacity_fade: float | None = None
    internal_resistance: float | None = None
    measurement_timestamp: datetime
    data_source: str | None = "Manual"

class BatteryDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    vehicle_id: int
    state_of_health: float
    state_of_charge: float | None
    voltage: float | None
    current: float | None
    temperature: float | None
    cycle_count: int | None
    capacity_fade: float | None
    internal_resistance: float | None
    measurement_timestamp: datetime
    data_source: str | None
    created_at: datetime

@router.post("/", response_model=BatteryDataResponse)
async def create_battery_data(
    data: BatteryDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify vehicle belongs to user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == data.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    battery_data = BatteryData(**data.model_dump())
    db.add(battery_data)
    db.commit()
    db.refresh(battery_data)
    return battery_data

@router.get("/vehicle/{vehicle_id}", response_model=List[BatteryDataResponse])
async def get_battery_data_by_vehicle(
    vehicle_id: int,
    skip: int = 0,
    limit: int = 1000,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify vehicle belongs to user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    data = db.query(BatteryData).filter(
        BatteryData.vehicle_id == vehicle_id
    ).order_by(BatteryData.measurement_timestamp.desc()).offset(skip).limit(limit).all()
    
    return data

@router.post("/upload/{vehicle_id}")
async def upload_battery_data(
    vehicle_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify vehicle belongs to user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check file format
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and Excel files are supported"
        )
    
    try:
        # Read file
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Expected columns mapping
        required_columns = {
            'state_of_health': ['soh', 'state_of_health', 'health'],
            'measurement_timestamp': ['timestamp', 'time', 'date', 'measurement_timestamp']
        }
        
        # Map columns
        column_mapping = {}
        for target_col, possible_names in required_columns.items():
            for col in df.columns:
                if col.lower() in [name.lower() for name in possible_names]:
                    column_mapping[col] = target_col
                    break
        
        if 'state_of_health' not in column_mapping.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required column: state_of_health"
            )
        
        # Process data
        records_created = 0
        for _, row in df.iterrows():
            try:
                # Map required fields
                soh_col = [k for k, v in column_mapping.items() if v == 'state_of_health'][0]
                timestamp_col = [k for k, v in column_mapping.items() if v == 'measurement_timestamp'][0] if 'measurement_timestamp' in column_mapping.values() else None
                
                data_dict = {
                    'vehicle_id': vehicle_id,
                    'state_of_health': float(row[soh_col]),
                    'measurement_timestamp': pd.to_datetime(row[timestamp_col]) if timestamp_col else datetime.now(),
                    'data_source': 'File Upload'
                }
                
                # Map optional fields
                optional_fields = ['state_of_charge', 'voltage', 'current', 'temperature', 'cycle_count', 'capacity_fade', 'internal_resistance']
                for field in optional_fields:
                    for col in df.columns:
                        if col.lower() == field.lower() or col.lower().replace('_', '') == field.replace('_', ''):
                            if pd.notna(row[col]):
                                data_dict[field] = float(row[col])
                            break
                
                battery_data = BatteryData(**data_dict)
                db.add(battery_data)
                records_created += 1
                
            except Exception as e:
                continue  # Skip invalid rows
        
        db.commit()
        return {"message": f"Successfully uploaded {records_created} records"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )

@router.delete("/{data_id}")
async def delete_battery_data(
    data_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get battery data and verify ownership through vehicle
    battery_data = db.query(BatteryData).join(Vehicle).filter(
        BatteryData.id == data_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not battery_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battery data not found"
        )
    
    db.delete(battery_data)
    db.commit()
    return {"message": "Battery data deleted successfully"}