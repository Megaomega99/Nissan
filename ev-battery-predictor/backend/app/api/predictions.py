from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from ..core.database import get_db
from ..models.user import User
from ..models.ml_model import MLModel
from ..models.prediction import Prediction
from ..models.battery_data import BatteryData
from ..ml.models import ModelTrainer, predict_battery_failure
from .auth import get_current_user

router = APIRouter()

class PredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: int
    input_data: Dict[str, Any]
    prediction_type: str = "current"  # current, future, failure_analysis

class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    model_id: int
    predicted_soh: float
    confidence_interval: List[float] | None
    estimated_failure_date: datetime | None
    failure_probability: float | None
    prediction_timestamp: datetime
    prediction_type: str

class FailureAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: int
    failure_threshold: float = 80.0
    time_horizon_days: int = 1095  # 3 years default

class FailureAnalysisResponse(BaseModel):
    current_soh: float
    failure_threshold: float
    estimated_failure_date: datetime | None
    days_to_failure: int | None
    failure_probability: float
    degradation_rate_per_year: float | None

class TimeSeriesPredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: int
    prediction_days: int = 365
    interval_days: int = 30

class TimeSeriesPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    current_soh: float
    predicted_trend: str  # "declining", "stable", "improving"

@router.post("/predict", response_model=PredictionResponse)
async def make_prediction(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get and validate model
    ml_model = db.query(MLModel).filter(
        MLModel.id == request.model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    if not ml_model.is_trained:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is not trained yet"
        )
    
    try:
        # Load the trained model
        trainer = ModelTrainer()
        model_data = trainer.load_model(ml_model.model_file_path, ml_model.model_type)
        
        if ml_model.model_type == "rnn":
            model = model_data
        else:
            model = model_data['model']
            scaler = model_data.get('scaler')
        
        # Prepare input data
        feature_columns = ml_model.feature_columns or ['state_of_charge', 'voltage', 'current', 'temperature', 'cycle_count']
        
        # Create input DataFrame
        input_df = pd.DataFrame([request.input_data])
        
        # Ensure all required features are present
        for col in feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0  # Default value for missing features
        
        X = input_df[feature_columns].fillna(0)
        
        # Make prediction
        if ml_model.model_type in ["svm", "sgd", "neural_network"] and scaler:
            X_scaled = scaler.transform(X)
            prediction = model.predict(X_scaled)[0]
        else:
            prediction = model.predict(X)[0]
        
        # Calculate confidence interval (simplified)
        confidence_interval = [max(0, prediction - 5), min(100, prediction + 5)]
        
        # Estimate failure if requested
        estimated_failure_date = None
        failure_probability = None
        
        if request.prediction_type == "failure_analysis":
            days_to_failure, failure_prob = predict_battery_failure(model, prediction)
            if days_to_failure is not None:
                estimated_failure_date = datetime.now() + timedelta(days=days_to_failure)
            failure_probability = failure_prob
        
        # Save prediction to database
        db_prediction = Prediction(
            model_id=request.model_id,
            input_data=request.input_data,
            predicted_soh=float(prediction),
            confidence_interval=confidence_interval,
            estimated_failure_date=estimated_failure_date,
            failure_probability=failure_probability,
            prediction_type=request.prediction_type
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        return db_prediction
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@router.post("/failure-analysis", response_model=FailureAnalysisResponse)
async def analyze_failure_risk(
    request: FailureAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get and validate model
    ml_model = db.query(MLModel).filter(
        MLModel.id == request.model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    if not ml_model.is_trained:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is not trained yet"
        )
    
    try:
        # Get latest battery data
        latest_data = db.query(BatteryData).filter(
            BatteryData.vehicle_id == ml_model.vehicle_id
        ).order_by(BatteryData.measurement_timestamp.desc()).first()
        
        if not latest_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No battery data available for analysis"
            )
        
        current_soh = latest_data.state_of_health
        
        # Load model and predict failure
        trainer = ModelTrainer()
        model_data = trainer.load_model(ml_model.model_file_path, ml_model.model_type)
        
        if ml_model.model_type == "rnn":
            model = model_data
        else:
            model = model_data['model']
        
        days_to_failure, failure_probability = predict_battery_failure(
            model, current_soh, request.failure_threshold
        )
        
        # Calculate degradation rate
        degradation_rate = None
        battery_history = db.query(BatteryData).filter(
            BatteryData.vehicle_id == ml_model.vehicle_id
        ).order_by(BatteryData.measurement_timestamp.asc()).limit(100).all()
        
        if len(battery_history) > 5:
            # Calculate trend over time
            timestamps = [data.measurement_timestamp for data in battery_history]
            soh_values = [data.state_of_health for data in battery_history]
            
            # Simple linear regression for trend
            days_elapsed = [(ts - timestamps[0]).days for ts in timestamps]
            if max(days_elapsed) > 30:  # At least a month of data
                soh_change = soh_values[-1] - soh_values[0]
                time_span_years = max(days_elapsed) / 365.25
                degradation_rate = -soh_change / time_span_years if time_span_years > 0 else None
        
        estimated_failure_date = None
        if days_to_failure is not None:
            estimated_failure_date = datetime.now() + timedelta(days=days_to_failure)
        
        return FailureAnalysisResponse(
            current_soh=current_soh,
            failure_threshold=request.failure_threshold,
            estimated_failure_date=estimated_failure_date,
            days_to_failure=days_to_failure,
            failure_probability=failure_probability,
            degradation_rate_per_year=degradation_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failure analysis failed: {str(e)}"
        )

@router.post("/time-series", response_model=TimeSeriesPredictionResponse)
async def predict_time_series(
    request: TimeSeriesPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get and validate model
    ml_model = db.query(MLModel).filter(
        MLModel.id == request.model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    if not ml_model.is_trained:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is not trained yet"
        )
    
    try:
        # Get latest battery data for baseline
        latest_data = db.query(BatteryData).filter(
            BatteryData.vehicle_id == ml_model.vehicle_id
        ).order_by(BatteryData.measurement_timestamp.desc()).first()
        
        if not latest_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No battery data available"
            )
        
        current_soh = latest_data.state_of_health
        
        # Generate future predictions
        predictions = []
        current_date = datetime.now()
        
        for days_ahead in range(0, request.prediction_days + 1, request.interval_days):
            prediction_date = current_date + timedelta(days=days_ahead)
            
            # Simple degradation model for demonstration
            # In practice, you'd use the actual trained model with proper feature engineering
            degradation_factor = 1 - (days_ahead / 3650) * 0.2  # 20% degradation over 10 years
            predicted_soh = current_soh * degradation_factor
            
            predictions.append({
                "date": prediction_date.isoformat(),
                "days_from_now": days_ahead,
                "predicted_soh": max(0, predicted_soh),
                "confidence_low": max(0, predicted_soh - 3),
                "confidence_high": min(100, predicted_soh + 3)
            })
        
        # Determine trend
        if len(predictions) > 1:
            start_soh = predictions[0]["predicted_soh"]
            end_soh = predictions[-1]["predicted_soh"]
            soh_change = end_soh - start_soh
            
            if soh_change < -2:
                trend = "declining"
            elif soh_change > 2:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return TimeSeriesPredictionResponse(
            predictions=predictions,
            current_soh=current_soh,
            predicted_trend=trend
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Time series prediction failed: {str(e)}"
        )

@router.get("/history/{model_id}", response_model=List[PredictionResponse])
async def get_prediction_history(
    model_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify model ownership
    ml_model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    predictions = db.query(Prediction).filter(
        Prediction.model_id == model_id
    ).order_by(Prediction.prediction_timestamp.desc()).limit(limit).all()
    
    return predictions