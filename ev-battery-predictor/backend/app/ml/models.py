import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
import os
from typing import Dict, Any, Tuple, Optional

class MLModelFactory:
    """Factory class for creating and managing ML models"""
    
    @staticmethod
    def create_model(model_type: str, parameters: Dict[str, Any] = None):
        """Create a model instance based on type and parameters"""
        if parameters is None:
            parameters = {}
            
        if model_type == "linear":
            return LinearRegression(**parameters)
        
        elif model_type == "polynomial":
            degree = parameters.get("degree", 2)
            return PolynomialWrapper(degree=degree)
        
        elif model_type == "svm":
            default_params = {"kernel": "rbf", "C": 1.0, "gamma": "scale"}
            default_params.update(parameters)
            return SVR(**default_params)
        
        elif model_type == "sgd":
            default_params = {"learning_rate": "adaptive", "eta0": 0.01, "max_iter": 1000}
            default_params.update(parameters)
            return SGDRegressor(**default_params)
        
        elif model_type == "neural_network":
            default_params = {
                "hidden_layer_sizes": (100, 50),
                "activation": "relu",
                "solver": "adam",
                "max_iter": 500
            }
            default_params.update(parameters)
            return MLPRegressor(**default_params)
        
        elif model_type == "rnn":
            return RNNWrapper(**parameters)
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

class PolynomialWrapper:
    """Wrapper for polynomial regression"""
    
    def __init__(self, degree=2):
        self.degree = degree
        self.poly_features = PolynomialFeatures(degree=degree)
        self.linear_model = LinearRegression()
        self.scaler = StandardScaler()
        
    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        X_poly = self.poly_features.fit_transform(X_scaled)
        self.linear_model.fit(X_poly, y)
        return self
        
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        X_poly = self.poly_features.transform(X_scaled)
        return self.linear_model.predict(X_poly)
        
    def score(self, X, y):
        predictions = self.predict(X)
        return r2_score(y, predictions)

class RNNWrapper:
    """Wrapper for RNN/LSTM models using TensorFlow"""
    
    def __init__(self, sequence_length=10, lstm_units=50, dense_units=25, 
                 dropout_rate=0.2, learning_rate=0.001, epochs=100, batch_size=32):
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dense_units = dense_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
    def _create_sequences(self, data, target):
        """Create sequences for RNN training"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(target[i + self.sequence_length])
        return np.array(X), np.array(y)
        
    def _build_model(self, input_shape):
        """Build the RNN model"""
        model = keras.Sequential([
            layers.LSTM(self.lstm_units, return_sequences=True, input_shape=input_shape),
            layers.Dropout(self.dropout_rate),
            layers.LSTM(self.lstm_units // 2, return_sequences=False),
            layers.Dropout(self.dropout_rate),
            layers.Dense(self.dense_units, activation='relu'),
            layers.Dense(1)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        return model
        
    def fit(self, X, y):
        # Scale the data
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Create sequences
        X_seq, y_seq = self._create_sequences(X_scaled, y_scaled)
        
        if len(X_seq) < self.sequence_length:
            raise ValueError(f"Not enough data points. Need at least {self.sequence_length + 1} samples.")
        
        # Build and train model
        self.model = self._build_model((self.sequence_length, X.shape[1]))
        
        history = self.model.fit(
            X_seq, y_seq,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=0.2,
            verbose=0
        )
        
        return self
        
    def predict(self, X):
        if self.model is None:
            raise ValueError("Model must be fitted before making predictions")
            
        X_scaled = self.scaler_X.transform(X)
        
        # For prediction, we need to create sequences
        if len(X_scaled) < self.sequence_length:
            # If we don't have enough data, pad with the last available values
            padding_needed = self.sequence_length - len(X_scaled)
            padding = np.tile(X_scaled[-1], (padding_needed, 1))
            X_scaled = np.vstack([padding, X_scaled])
        
        X_seq, _ = self._create_sequences(X_scaled, np.zeros(len(X_scaled)))
        
        predictions_scaled = self.model.predict(X_seq[-1:], verbose=0)
        predictions = self.scaler_y.inverse_transform(predictions_scaled.reshape(-1, 1)).flatten()
        
        return predictions
        
    def score(self, X, y):
        predictions = self.predict(X)
        if len(predictions) != len(y):
            # Adjust for sequence prediction
            y_adjusted = y[-len(predictions):]
        else:
            y_adjusted = y
        return r2_score(y_adjusted, predictions)

class ModelTrainer:
    """Class for training and evaluating models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def prepare_data(self, df: pd.DataFrame, target_column: str, feature_columns: list = None):
        """Prepare data for training"""
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        # Remove rows with missing target values
        df_clean = df.dropna(subset=[target_column])
        
        X = df_clean[feature_columns].fillna(0)  # Fill missing features with 0
        y = df_clean[target_column]
        
        return X, y, feature_columns
        
    def train_model(self, model, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Train a model and return performance metrics"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features for certain models
        if isinstance(model, (SVR, SGDRegressor, MLPRegressor, RNNWrapper)):
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            train_pred = model.predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
        else:
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_score = r2_score(y_train, train_pred)
        test_score = r2_score(y_test, test_pred)
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        
        return {
            "train_score": train_score,
            "test_score": test_score,
            "train_mse": train_mse,
            "test_mse": test_mse,
            "X_test": X_test,
            "y_test": y_test,
            "test_predictions": test_pred
        }
        
    def save_model(self, model, file_path: str, scaler=None):
        """Save a trained model to disk"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if isinstance(model, RNNWrapper):
            # Save TensorFlow model
            model.model.save(file_path + "_tf_model")
            # Save scalers and metadata
            joblib.dump({
                'scaler_X': model.scaler_X,
                'scaler_y': model.scaler_y,
                'sequence_length': model.sequence_length,
                'lstm_units': model.lstm_units,
                'dense_units': model.dense_units,
                'dropout_rate': model.dropout_rate
            }, file_path + "_metadata.pkl")
        else:
            # Save sklearn model
            model_data = {'model': model}
            if scaler is not None:
                model_data['scaler'] = scaler
            joblib.dump(model_data, file_path)
            
    def load_model(self, file_path: str, model_type: str):
        """Load a trained model from disk"""
        if model_type == "rnn":
            # Load TensorFlow model
            tf_model = keras.models.load_model(file_path + "_tf_model")
            metadata = joblib.load(file_path + "_metadata.pkl")
            
            # Recreate RNN wrapper
            rnn_model = RNNWrapper(
                sequence_length=metadata['sequence_length'],
                lstm_units=metadata['lstm_units'],
                dense_units=metadata['dense_units'],
                dropout_rate=metadata['dropout_rate']
            )
            rnn_model.model = tf_model
            rnn_model.scaler_X = metadata['scaler_X']
            rnn_model.scaler_y = metadata['scaler_y']
            
            return rnn_model
        else:
            # Load sklearn model
            model_data = joblib.load(file_path)
            return model_data

def predict_battery_failure(model, current_soh: float, threshold: float = 80.0, 
                          time_step_days: int = 30) -> Tuple[Optional[int], float]:
    """
    Predict when battery will reach failure threshold
    
    Args:
        model: Trained model
        current_soh: Current state of health
        threshold: SOH threshold for failure (default 80%)
        time_step_days: Days between predictions
        
    Returns:
        Tuple of (days_to_failure, failure_probability)
    """
    if current_soh <= threshold:
        return 0, 1.0
    
    # Simple degradation prediction
    # This is a simplified approach - in practice, you'd use more sophisticated methods
    try:
        # Create a sequence of future time points
        future_days = np.arange(0, 3650, time_step_days)  # Up to 10 years
        
        # For simple models, create dummy features
        if hasattr(model, 'predict'):
            # Create synthetic data points for prediction
            # This is simplified - you'd normally use actual feature trends
            predictions = []
            for days in future_days:
                # Simple exponential decay assumption
                estimated_soh = current_soh * np.exp(-days / 3650 * 0.2)  # 20% degradation over 10 years
                predictions.append(estimated_soh)
            
            # Find when SOH drops below threshold
            for i, pred_soh in enumerate(predictions):
                if pred_soh <= threshold:
                    days_to_failure = future_days[i]
                    failure_prob = min(1.0, (current_soh - threshold) / (current_soh - pred_soh))
                    return days_to_failure, failure_prob
                    
    except Exception as e:
        print(f"Error in failure prediction: {e}")
    
    return None, 0.0