import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, ElasticNet, SGDRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import re
from typing import Dict, Tuple, List, Any, Optional
from datetime import datetime
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

def clean_filename(filename: str) -> str:
    """Clean a filename to prevent path traversal and injection."""
    # Replace unsafe characters
    safe_name = re.sub(r'[^\w\-\.]', '_', filename)
    # Ensure it's a CSV file
    if not safe_name.lower().endswith('.csv'):
        safe_name += '.csv'
    return safe_name

def validate_model_params(model_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize model parameters."""
    valid_params = {}
    
    if model_type == "LinearRegression":
        # Only allow specific params for LinearRegression
        valid_keys = ["fit_intercept", "normalize", "copy_X", "n_jobs"]
        for key in valid_keys:
            if key in params:
                valid_params[key] = params[key]
    
    elif model_type == "SVR":
        # Only allow specific params for SVR
        valid_keys = ["kernel", "degree", "C", "epsilon", "gamma"]
        for key in valid_keys:
            if key in params:
                valid_params[key] = params[key]
        
        # Validate kernel
        if "kernel" in valid_params:
            if valid_params["kernel"] not in ["linear", "poly", "rbf", "sigmoid"]:
                raise ValueError(f"Invalid kernel: {valid_params['kernel']}")
    
    elif model_type == "ElasticNet":
        # Only allow specific params for ElasticNet
        valid_keys = ["alpha", "l1_ratio", "fit_intercept", "max_iter"]
        for key in valid_keys:
            if key in params:
                valid_params[key] = params[key]
    
    elif model_type == "SGD":
        # Only allow specific params for SGDRegressor
        valid_keys = ["loss", "penalty", "alpha", "l1_ratio", "max_iter"]
        for key in valid_keys:
            if key in params:
                valid_params[key] = params[key]
        
        # Validate loss function
        if "loss" in valid_params:
            valid_losses = ["squared_loss", "huber", "epsilon_insensitive", "squared_epsilon_insensitive"]
            if valid_params["loss"] not in valid_losses:
                raise ValueError(f"Invalid loss function: {valid_params['loss']}")
    
    return valid_params

def preprocess_data(file_path: str) -> str:
    """
    Preprocess data by removing nulls, empty values, and infinities.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Path to preprocessed file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Get initial data shape
        initial_shape = df.shape
        
        # Handle missing values
        df = df.dropna()
        
        # Handle infinite values
        df = df.replace([float("inf"), float("-inf")], pd.NA).dropna()
        
        # Get final data shape
        final_shape = df.shape
        
        # Log preprocessing results
        logger.info(f"Preprocessing: Initial shape {initial_shape}, Final shape {final_shape}")
        
        # Save preprocessed file
        preprocessed_path = file_path.replace(".csv", "_preprocessed.csv")
        df.to_csv(preprocessed_path, index=False)
        
        return preprocessed_path
    
    except Exception as e:
        logger.error(f"Error preprocessing data: {e}")
        raise

def train_model(
    file_path: str, 
    model_type: str, 
    params: Dict[str, Any], 
    polynomial_degree: int = 1,
    user_id: Optional[int] = None,
    file_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Train ML model with polynomial features support and projection capability.
    
    Args:
        file_path: Path to preprocessed CSV file
        model_type: Type of ML model to train
        params: Model parameters
        polynomial_degree: Degree of polynomial features (for regression)
        user_id: ID of user training the model
        file_id: ID of file used for training
        
    Returns:
        Dictionary with model metrics and visualization data
    """
    try:
        # Load and prepare data
        df = pd.read_csv(file_path)
        
        # Ensure data is numeric
        try:
            df = df.apply(pd.to_numeric, errors='coerce')
            df = df.dropna()
        except Exception as e:
            logger.error(f"Error converting data to numeric: {e}")
            raise ValueError("Data contains non-numeric values that couldn't be converted")
        
        # Prepare features and target
        X = np.arange(len(df)).reshape(-1, 1)
        y = df.iloc[:, 0].values
        
        # Split data for training and testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create model pipeline with polynomial features if needed
        model_instance = None
        
        if model_type == "LinearRegression":
            if polynomial_degree > 1:
                model_instance = Pipeline([
                    ('poly', PolynomialFeatures(degree=polynomial_degree)),
                    ('model', LinearRegression(**params))
                ])
            else:
                model_instance = LinearRegression(**params)
        
        elif model_type == "SVR":
            model_instance = SVR(**params)
        
        elif model_type == "ElasticNet":
            model_instance = ElasticNet(**params)
        
        elif model_type == "SGD":
            model_instance = SGDRegressor(**params)
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Train model
        model_instance.fit(X_train, y_train)
        
        # Generate predictions for test data
        y_pred = model_instance.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Generate future projections (double the max index)
        max_index = np.max(X)
        future_indices = np.arange(max_index + 1, 2 * max_index + 1).reshape(-1, 1)
        future_predictions = model_instance.predict(future_indices)
        
        # Save model
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        model_filename = f"{model_type}_{timestamp}.joblib"
        
        if user_id and file_id:
            model_filename = f"{user_id}_{file_id}_{model_filename}"
        
        models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, model_filename)
        
        joblib.dump(model_instance, model_path)
        
        # Prepare visualization data
        test_indices = X_test.flatten().tolist()
        test_predictions = y_pred.tolist()
        future_indices_list = future_indices.flatten().tolist()
        
        # Prepare result dictionary
        result = {
            "mse": float(mse),
            "r2": float(r2),
            "model_path": model_path,
            "metrics": {
                "mse": float(mse),
                "r2": float(r2),
                "rmse": float(np.sqrt(mse))
            },
            "visualization_data": {
                "original_data": df.iloc[:, 0].values.tolist(),
                "test_indices": test_indices,
                "test_predictions": test_predictions,
                "future_indices": future_indices_list,
                "future_predictions": future_predictions.tolist()
            }
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise