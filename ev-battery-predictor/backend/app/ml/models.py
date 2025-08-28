import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, SGDRegressor, Perceptron
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, RobustScaler, MinMaxScaler
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_regression
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
import os
import warnings
from typing import Dict, Any, Tuple, Optional, List
import logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')
tf.get_logger().setLevel('ERROR')

class DataPreprocessor:
    """Comprehensive data preprocessing for ML model training"""
    
    def __init__(self):
        self.scaler = None
        self.imputer = None
        self.feature_selector = None
        self.processed_features = None
        
    def validate_and_clean_data(self, df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Validate and clean input data"""
        df_clean = df.copy()
        
        # 1. Remove completely empty rows
        df_clean = df_clean.dropna(how='all')
        
        # 2. Ensure target column exists and has valid values
        if target_column not in df_clean.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        
        # 3. Remove rows where target is null
        df_clean = df_clean.dropna(subset=[target_column])
        
        # 4. Validate target column has numeric values
        if not pd.api.types.is_numeric_dtype(df_clean[target_column]):
            try:
                df_clean[target_column] = pd.to_numeric(df_clean[target_column], errors='coerce')
                df_clean = df_clean.dropna(subset=[target_column])
            except:
                raise ValueError(f"Target column '{target_column}' contains non-numeric values that cannot be converted")
        
        # 5. Ensure we have enough data
        if len(df_clean) < 5:
            raise ValueError(f"Insufficient data after cleaning. Need at least 5 samples, got {len(df_clean)}")
        
        # 6. Validate target values are reasonable for SOH (0-100%)
        if target_column == 'state_of_health':
            # Remove unrealistic SOH values
            df_clean = df_clean[
                (df_clean[target_column] >= 0) & 
                (df_clean[target_column] <= 100)
            ]
            
            if len(df_clean) < 5:
                raise ValueError("Insufficient valid SOH data (should be between 0-100%)")
        
        return df_clean
    
    def extract_features(self, df: pd.DataFrame, target_column: str, feature_columns: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
        """Extract and validate feature columns"""
        
        # Define columns to exclude from features
        exclude_cols = {
            target_column, 
            'measurement_timestamp', 
            'created_at', 
            'updated_at', 
            'data_source',
            'id',
            'vehicle_id',
            'user_id'
        }
        
        if feature_columns is None:
            # Auto-detect numeric feature columns
            feature_columns = []
            for col in df.columns:
                if col not in exclude_cols:
                    # Check if column contains numeric data
                    if pd.api.types.is_numeric_dtype(df[col]):
                        feature_columns.append(col)
                    else:
                        # Try to convert to numeric
                        try:
                            numeric_series = pd.to_numeric(df[col], errors='coerce')
                            if not numeric_series.isna().all():  # At least some values can be converted
                                feature_columns.append(col)
                        except:
                            continue
        
        # Validate feature columns exist
        valid_features = []
        for col in feature_columns:
            if col in df.columns:
                valid_features.append(col)
            else:
                print(f"Warning: Feature column '{col}' not found in data")
        
        if not valid_features:
            raise ValueError("No valid feature columns found")
        
        # Extract feature data and convert to numeric
        X = pd.DataFrame()
        for col in valid_features:
            if pd.api.types.is_numeric_dtype(df[col]):
                X[col] = df[col]
            else:
                # Convert to numeric, coercing errors to NaN
                X[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove features that are all NaN
        X = X.dropna(axis=1, how='all')
        final_features = list(X.columns)
        
        if not final_features:
            raise ValueError("No valid numeric features found after preprocessing")
        
        return X, final_features
    
    def handle_missing_values(self, X: pd.DataFrame, strategy: str = 'adaptive') -> pd.DataFrame:
        """Handle missing values intelligently"""
        
        if X.isna().sum().sum() == 0:
            return X  # No missing values
        
        X_filled = X.copy()
        
        if strategy == 'adaptive':
            # Use different strategies based on missing percentage
            for col in X.columns:
                missing_pct = X[col].isna().sum() / len(X)
                
                if missing_pct == 0:
                    continue
                elif missing_pct > 0.5:
                    # Drop columns with >50% missing
                    X_filled = X_filled.drop(columns=[col])
                elif missing_pct > 0.2:
                    # Use median for high missing percentage
                    X_filled[col] = X_filled[col].fillna(X_filled[col].median())
                else:
                    # Use KNN imputer for low missing percentage
                    if len(X) > 10:  # Only use KNN if we have enough samples
                        try:
                            imputer = KNNImputer(n_neighbors=min(5, len(X)-1))
                            X_filled[[col]] = imputer.fit_transform(X_filled[[col]])
                        except:
                            # Fallback to median
                            X_filled[col] = X_filled[col].fillna(X_filled[col].median())
                    else:
                        X_filled[col] = X_filled[col].fillna(X_filled[col].median())
        else:
            # Simple imputation strategies
            if strategy == 'mean':
                X_filled = X_filled.fillna(X_filled.mean())
            elif strategy == 'median':
                X_filled = X_filled.fillna(X_filled.median())
            elif strategy == 'zero':
                X_filled = X_filled.fillna(0)
        
        # Final check - fill any remaining NaNs with 0
        X_filled = X_filled.fillna(0)
        
        return X_filled
    
    def remove_outliers(self, X: pd.DataFrame, y: pd.Series, method: str = 'iqr') -> Tuple[pd.DataFrame, pd.Series]:
        """Remove outliers from the dataset"""
        
        if method == 'iqr':
            # Use IQR method for each feature
            mask = pd.Series([True] * len(X), index=X.index)
            
            for col in X.columns:
                Q1 = X[col].quantile(0.25)
                Q3 = X[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                col_mask = (X[col] >= lower_bound) & (X[col] <= upper_bound)
                mask = mask & col_mask
            
            return X[mask], y[mask]
        
        elif method == 'zscore':
            # Use Z-score method
            from scipy import stats
            z_scores = np.abs(stats.zscore(X))
            mask = (z_scores < 3).all(axis=1)
            return X[mask], y[mask]
        
        return X, y
    
    def create_additional_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create additional engineered features"""
        X_enhanced = X.copy()
        
        # Feature engineering for battery data
        if 'voltage' in X.columns and 'current' in X.columns:
            # Power calculation
            X_enhanced['power'] = X['voltage'] * X['current']
            
        if 'temperature' in X.columns:
            # Temperature-based features
            X_enhanced['temp_squared'] = X['temperature'] ** 2
            
        if 'cycle_count' in X.columns:
            # Cycle-based features
            X_enhanced['log_cycles'] = np.log1p(X['cycle_count'])
            
        if 'capacity_fade' in X.columns and 'cycle_count' in X.columns:
            # Degradation rate
            X_enhanced['fade_per_cycle'] = X['capacity_fade'] / (X['cycle_count'] + 1)
        
        # Remove any infinite or very large values
        X_enhanced = X_enhanced.replace([np.inf, -np.inf], np.nan)
        X_enhanced = X_enhanced.fillna(0)
        
        return X_enhanced
    
    def scale_features(self, X: pd.DataFrame, scaler_type: str = 'standard') -> pd.DataFrame:
        """Scale features appropriately"""
        
        if scaler_type == 'standard':
            self.scaler = StandardScaler()
        elif scaler_type == 'robust':
            self.scaler = RobustScaler()
        elif scaler_type == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            return X  # No scaling
        
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        return X_scaled
    
    def preprocess_for_training(self, df: pd.DataFrame, target_column: str, 
                              feature_columns: List[str] = None,
                              scale_features: bool = True,
                              remove_outliers: bool = True,
                              add_features: bool = True) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Complete preprocessing pipeline"""
        
        try:
            # 1. Validate and clean data
            df_clean = self.validate_and_clean_data(df, target_column)
            print(f"✓ Data validation complete. Shape: {df_clean.shape}")
            
            # 2. Extract features
            X, feature_names = self.extract_features(df_clean, target_column, feature_columns)
            y = df_clean[target_column]
            print(f"✓ Feature extraction complete. Features: {len(feature_names)}")
            
            # 3. Handle missing values
            X = self.handle_missing_values(X)
            print(f"✓ Missing values handled")
            
            # 4. Remove outliers if requested
            if remove_outliers and len(X) > 20:  # Only if we have enough data
                X, y = self.remove_outliers(X, y)
                print(f"✓ Outliers removed. Remaining samples: {len(X)}")
            
            # 5. Create additional features if requested
            if add_features:
                X = self.create_additional_features(X)
                print(f"✓ Feature engineering complete. Final features: {X.shape[1]}")
            
            # 6. Final validation
            if len(X) < 5:
                raise ValueError(f"Insufficient data after preprocessing: {len(X)} samples")
            
            if X.shape[1] == 0:
                raise ValueError("No features remaining after preprocessing")
            
            # 7. Scale features if requested
            if scale_features:
                X = self.scale_features(X, 'robust')  # Use robust scaler for battery data
                print(f"✓ Feature scaling complete")
            
            # Store processed feature names
            self.processed_features = list(X.columns)
            
            print(f"✅ Preprocessing complete: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y, self.processed_features
            
        except Exception as e:
            print(f"❌ Preprocessing failed: {str(e)}")
            raise e

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
        
        elif model_type == "random_forest":
            default_params = {
                "n_estimators": 100,
                "random_state": 42,
                "max_depth": None,
                "min_samples_split": 2
            }
            default_params.update(parameters)
            return RandomForestRegressor(**default_params)
        
        elif model_type == "perceptron":
            default_params = {
                "max_iter": 1000,
                "random_state": 42,
                "eta0": 1.0
            }
            default_params.update(parameters)
            return PerceptronWrapper(**default_params)
        
        elif model_type == "rnn":
            return RNNWrapper(**parameters)
        
        elif model_type == "gru":
            return GRUWrapper(**parameters)
        
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
        self.sequence_length = max(3, min(sequence_length, 20))  # Clamp sequence length
        self.lstm_units = lstm_units
        self.dense_units = dense_units
        self.dropout_rate = max(0.0, min(dropout_rate, 0.5))  # Clamp dropout
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
    def _create_sequences(self, data, target):
        """Create sequences for RNN training"""
        if len(data) <= self.sequence_length:
            raise ValueError(f"Data length ({len(data)}) must be greater than sequence_length ({self.sequence_length})")
        
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(target[i + self.sequence_length])
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
        
    def _build_model(self, input_shape):
        """Build the RNN model"""
        try:
            model = keras.Sequential([
                layers.LSTM(
                    self.lstm_units, 
                    return_sequences=True, 
                    input_shape=input_shape,
                    recurrent_dropout=0.1
                ),
                layers.Dropout(self.dropout_rate),
                layers.LSTM(
                    max(1, self.lstm_units // 2), 
                    return_sequences=False,
                    recurrent_dropout=0.1
                ),
                layers.Dropout(self.dropout_rate),
                layers.Dense(self.dense_units, activation='relu'),
                layers.Dense(1, activation='linear')
            ])
            
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='mse',
                metrics=['mae']
            )
            return model
        except Exception as e:
            print(f"Error building RNN model: {e}")
            raise e
        
    def fit(self, X, y):
        try:
            # Convert to numpy arrays if needed
            if isinstance(X, pd.DataFrame):
                X = X.values
            if isinstance(y, pd.Series):
                y = y.values
            
            # Ensure data is numeric
            X = np.array(X, dtype=np.float32)
            y = np.array(y, dtype=np.float32)
            
            # Validate input shapes
            if X.ndim != 2:
                raise ValueError(f"X must be 2D, got shape {X.shape}")
            if len(X) != len(y):
                raise ValueError(f"X and y must have same length: {len(X)} vs {len(y)}")
            
            # Check for sufficient data
            min_samples = self.sequence_length + 5  # Need extra for validation
            if len(X) < min_samples:
                raise ValueError(f"Need at least {min_samples} samples for sequence length {self.sequence_length}, got {len(X)}")
            
            # Handle NaN values
            if np.any(np.isnan(X)) or np.any(np.isnan(y)):
                print("Warning: Found NaN values, filling with zeros")
                X = np.nan_to_num(X, nan=0.0)
                y = np.nan_to_num(y, nan=0.0)
            
            # Scale the data
            X_scaled = self.scaler_X.fit_transform(X)
            y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # Create sequences
            X_seq, y_seq = self._create_sequences(X_scaled, y_scaled)
            
            if len(X_seq) < 3:
                raise ValueError(f"Too few sequences created: {len(X_seq)}. Need at least 3.")
            
            print(f"Created {len(X_seq)} sequences from {len(X)} samples")
            
            # Build and train model
            self.model = self._build_model((self.sequence_length, X.shape[1]))
            
            # Adjust training parameters based on data size
            validation_split = min(0.2, max(0.1, (len(X_seq) - 1) / len(X_seq)))
            batch_size = min(self.batch_size, max(1, len(X_seq) // 4))
            
            history = self.model.fit(
                X_seq, y_seq,
                epochs=self.epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=0,
                callbacks=[
                    keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                    keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
                ]
            )
            
            print(f"✓ RNN training completed. Final loss: {history.history['loss'][-1]:.4f}")
            return self
            
        except Exception as e:
            print(f"❌ RNN training failed: {str(e)}")
            raise e
        
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

class PerceptronWrapper:
    """Wrapper for Perceptron with regression capabilities"""
    
    def __init__(self, max_iter=1000, random_state=42, eta0=1.0):
        self.max_iter = max_iter
        self.random_state = random_state
        self.eta0 = eta0
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
    def fit(self, X, y):
        # Scale data
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Create and train perceptron
        self.model = Perceptron(
            max_iter=self.max_iter,
            random_state=self.random_state,
            eta0=self.eta0
        )
        self.model.fit(X_scaled, y_scaled)
        return self
        
    def predict(self, X):
        if self.model is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X_scaled = self.scaler_X.transform(X)
        y_pred_scaled = self.model.predict(X_scaled)
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        return y_pred
        
    def score(self, X, y):
        predictions = self.predict(X)
        return r2_score(y, predictions)

class GRUWrapper:
    """Wrapper for GRU models using TensorFlow"""
    
    def __init__(self, sequence_length=10, gru_units=50, dense_units=25, 
                 dropout_rate=0.2, learning_rate=0.001, epochs=100, batch_size=32):
        self.sequence_length = max(3, min(sequence_length, 20))  # Clamp sequence length
        self.gru_units = gru_units
        self.dense_units = dense_units
        self.dropout_rate = max(0.0, min(dropout_rate, 0.5))  # Clamp dropout
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
    def _create_sequences(self, data, target):
        """Create sequences for GRU training"""
        if len(data) <= self.sequence_length:
            raise ValueError(f"Data length ({len(data)}) must be greater than sequence_length ({self.sequence_length})")
        
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(target[i + self.sequence_length])
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
        
    def _build_model(self, input_shape):
        """Build the GRU model"""
        try:
            model = keras.Sequential([
                layers.GRU(
                    self.gru_units, 
                    return_sequences=True, 
                    input_shape=input_shape,
                    recurrent_dropout=0.1
                ),
                layers.Dropout(self.dropout_rate),
                layers.GRU(
                    max(1, self.gru_units // 2), 
                    return_sequences=False,
                    recurrent_dropout=0.1
                ),
                layers.Dropout(self.dropout_rate),
                layers.Dense(self.dense_units, activation='relu'),
                layers.Dense(1, activation='linear')
            ])
            
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='mse',
                metrics=['mae']
            )
            return model
        except Exception as e:
            print(f"Error building GRU model: {e}")
            raise e
        
    def fit(self, X, y):
        try:
            # Convert to numpy arrays if needed
            if isinstance(X, pd.DataFrame):
                X = X.values
            if isinstance(y, pd.Series):
                y = y.values
            
            # Ensure data is numeric
            X = np.array(X, dtype=np.float32)
            y = np.array(y, dtype=np.float32)
            
            # Validate input shapes
            if X.ndim != 2:
                raise ValueError(f"X must be 2D, got shape {X.shape}")
            if len(X) != len(y):
                raise ValueError(f"X and y must have same length: {len(X)} vs {len(y)}")
            
            # Check for sufficient data
            min_samples = self.sequence_length + 5  # Need extra for validation
            if len(X) < min_samples:
                raise ValueError(f"Need at least {min_samples} samples for sequence length {self.sequence_length}, got {len(X)}")
            
            # Handle NaN values
            if np.any(np.isnan(X)) or np.any(np.isnan(y)):
                print("Warning: Found NaN values, filling with zeros")
                X = np.nan_to_num(X, nan=0.0)
                y = np.nan_to_num(y, nan=0.0)
            
            # Scale the data
            X_scaled = self.scaler_X.fit_transform(X)
            y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # Create sequences
            X_seq, y_seq = self._create_sequences(X_scaled, y_scaled)
            
            if len(X_seq) < 3:
                raise ValueError(f"Too few sequences created: {len(X_seq)}. Need at least 3.")
            
            print(f"Created {len(X_seq)} sequences from {len(X)} samples")
            
            # Build and train model
            self.model = self._build_model((self.sequence_length, X.shape[1]))
            
            # Adjust training parameters based on data size
            validation_split = min(0.2, max(0.1, (len(X_seq) - 1) / len(X_seq)))
            batch_size = min(self.batch_size, max(1, len(X_seq) // 4))
            
            history = self.model.fit(
                X_seq, y_seq,
                epochs=self.epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=0,
                callbacks=[
                    keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                    keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
                ]
            )
            
            print(f"✓ GRU training completed. Final loss: {history.history['loss'][-1]:.4f}")
            return self
            
        except Exception as e:
            print(f"❌ GRU training failed: {str(e)}")
            raise e
        
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
        self.preprocessor = DataPreprocessor()
        
    def prepare_data(self, df: pd.DataFrame, target_column: str, feature_columns: list = None):
        """Prepare data for training using comprehensive preprocessing"""
        try:
            print(f"🔄 Starting data preparation for {len(df)} samples...")
            
            # Use the comprehensive preprocessor
            X, y, processed_features = self.preprocessor.preprocess_for_training(
                df=df,
                target_column=target_column,
                feature_columns=feature_columns,
                scale_features=False,  # We'll handle scaling per model type
                remove_outliers=True,
                add_features=True
            )
            
            print(f"✅ Data preparation complete: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y, processed_features
            
        except Exception as e:
            print(f"❌ Data preparation failed: {str(e)}")
            # Fallback to simple preprocessing
            print("⚠️ Falling back to simple preprocessing...")
            return self._simple_prepare_data(df, target_column, feature_columns)
    
    def _simple_prepare_data(self, df: pd.DataFrame, target_column: str, feature_columns: list = None):
        """Simple fallback data preparation"""
        try:
            if feature_columns is None:
                # Exclude timestamp and non-numeric columns
                exclude_cols = [target_column, 'measurement_timestamp', 'created_at', 'updated_at', 'data_source', 'id']
                feature_columns = [col for col in df.columns 
                                 if col not in exclude_cols and 
                                 df[col].dtype in ['int64', 'float64', 'int32', 'float32']]
            
            # Remove rows with missing target values
            df_clean = df.dropna(subset=[target_column])
            
            if len(df_clean) < 5:
                raise ValueError("Insufficient data after cleaning")
            
            # Ensure we only use numeric columns for features
            numeric_features = []
            for col in feature_columns:
                if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                    numeric_features.append(col)
            
            if not numeric_features:
                raise ValueError("No valid numeric features found")
            
            X = df_clean[numeric_features].fillna(0)  # Fill missing features with 0
            y = df_clean[target_column]
            
            print(f"✓ Simple preprocessing complete: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y, numeric_features
            
        except Exception as e:
            print(f"❌ Simple preprocessing also failed: {str(e)}")
            raise e
        
    def train_model(self, model, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Train a model and return performance metrics with comprehensive error handling"""
        try:
            print(f"🔄 Starting model training with {type(model).__name__}...")
            
            # Validate input data
            if len(X) != len(y):
                raise ValueError(f"Feature and target length mismatch: {len(X)} vs {len(y)}")
            
            if len(X) < 5:
                raise ValueError(f"Insufficient training data: {len(X)} samples")
            
            # Adjust test size for small datasets
            min_test_size = max(1, int(len(X) * 0.1))
            max_test_size = len(X) - 3  # Leave at least 3 for training
            actual_test_size = max(min_test_size, min(max_test_size, int(len(X) * test_size)))
            
            print(f"✓ Using {len(X) - actual_test_size} samples for training, {actual_test_size} for testing")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=actual_test_size, random_state=42, shuffle=True
            )
            
            # Handle scaling and training based on model type
            models_needing_scaling = (SVR, SGDRegressor, MLPRegressor, PerceptronWrapper)
            models_with_internal_scaling = (RNNWrapper, GRUWrapper)
            
            if isinstance(model, models_needing_scaling):
                print("✓ Applying feature scaling...")
                X_train_processed = self.scaler.fit_transform(X_train)
                X_test_processed = self.scaler.transform(X_test)
            elif isinstance(model, models_with_internal_scaling):
                # These models handle their own scaling
                X_train_processed = X_train
                X_test_processed = X_test
            else:
                # Tree-based models (Random Forest) don't need scaling
                X_train_processed = X_train
                X_test_processed = X_test
            
            # Train the model with error handling
            print("✓ Training model...")
            try:
                model.fit(X_train_processed, y_train)
                print("✓ Model training completed successfully")
            except Exception as train_error:
                print(f"❌ Training failed: {train_error}")
                raise train_error
            
            # Make predictions with error handling
            print("✓ Making predictions...")
            try:
                train_pred = model.predict(X_train_processed)
                test_pred = model.predict(X_test_processed)
            except Exception as pred_error:
                print(f"❌ Prediction failed: {pred_error}")
                raise pred_error
            
            # Validate and clean predictions
            if len(train_pred) != len(y_train):
                raise ValueError(f"Training prediction length mismatch: {len(train_pred)} vs {len(y_train)}")
            if len(test_pred) != len(y_test):
                raise ValueError(f"Test prediction length mismatch: {len(test_pred)} vs {len(y_test)}")
            
            # Handle NaN predictions
            if np.any(np.isnan(train_pred)):
                print("⚠️ NaN values in training predictions, replacing with target mean")
                train_pred = np.nan_to_num(train_pred, nan=np.mean(y_train))
            
            if np.any(np.isnan(test_pred)):
                print("⚠️ NaN values in test predictions, replacing with target mean") 
                test_pred = np.nan_to_num(test_pred, nan=np.mean(y_test))
            
            # Calculate metrics
            print("✓ Calculating performance metrics...")
            train_score = r2_score(y_train, train_pred)
            test_score = r2_score(y_test, test_pred)
            train_mse = mean_squared_error(y_train, train_pred)
            test_mse = mean_squared_error(y_test, test_pred)
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            
            # Validate metrics
            if np.isnan(train_score) or np.isnan(test_score):
                print("⚠️ NaN scores detected, clipping to valid range")
                train_score = max(0.0, train_score) if not np.isnan(train_score) else 0.0
                test_score = max(0.0, test_score) if not np.isnan(test_score) else 0.0
            
            print(f"✅ Training completed successfully!")
            print(f"   - Training R²: {train_score:.4f}")
            print(f"   - Test R²: {test_score:.4f}")
            print(f"   - Training MSE: {train_mse:.4f}")
            print(f"   - Test MSE: {test_mse:.4f}")
            
            return {
                "train_score": float(train_score),
                "test_score": float(test_score),
                "train_mse": float(train_mse),
                "test_mse": float(test_mse),
                "train_mae": float(train_mae),
                "test_mae": float(test_mae),
                "X_test": X_test,
                "y_test": y_test,
                "test_predictions": test_pred,
                "scaler": self.scaler if isinstance(model, models_needing_scaling) else None,
                "feature_names": list(X.columns) if hasattr(X, 'columns') else None
            }
            
        except Exception as e:
            print(f"❌ Model training failed: {str(e)}")
            print(f"   Model type: {type(model).__name__}")
            print(f"   Data shape: X={X.shape}, y={y.shape}")
            raise e
        
    def save_model(self, model, file_path: str, scaler=None):
        """Save a trained model to disk"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if isinstance(model, (RNNWrapper, GRUWrapper)):
            # Save TensorFlow model
            model.model.save(file_path + "_tf_model")
            # Save scalers and metadata
            metadata = {
                'scaler_X': model.scaler_X,
                'scaler_y': model.scaler_y,
                'sequence_length': model.sequence_length,
                'dense_units': model.dense_units,
                'dropout_rate': model.dropout_rate
            }
            if isinstance(model, RNNWrapper):
                metadata['lstm_units'] = model.lstm_units
            else:  # GRUWrapper
                metadata['gru_units'] = model.gru_units
            joblib.dump(metadata, file_path + "_metadata.pkl")
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
        elif model_type == "gru":
            # Load TensorFlow model
            tf_model = keras.models.load_model(file_path + "_tf_model")
            metadata = joblib.load(file_path + "_metadata.pkl")
            
            # Recreate GRU wrapper
            gru_model = GRUWrapper(
                sequence_length=metadata['sequence_length'],
                gru_units=metadata['gru_units'],
                dense_units=metadata['dense_units'],
                dropout_rate=metadata['dropout_rate']
            )
            gru_model.model = tf_model
            gru_model.scaler_X = metadata['scaler_X']
            gru_model.scaler_y = metadata['scaler_y']
            
            return gru_model
        else:
            # Load sklearn model
            model_data = joblib.load(file_path)
            return model_data

def predict_soh_forecast(model, last_data_points: pd.DataFrame, 
                        prediction_steps: int = 365, time_step_days: int = 1) -> Dict[str, Any]:
    """
    Predict SOH forecast until 20% threshold with key threshold crossings
    
    Args:
        model: Trained model
        last_data_points: Recent battery data for prediction context
        prediction_steps: Number of prediction steps to make
        time_step_days: Days between each prediction step
        
    Returns:
        Dictionary containing forecast data and threshold crossings
    """
    try:
        # Extract features for prediction (excluding target column)
        feature_cols = [col for col in last_data_points.columns 
                       if col not in ['state_of_health', 'measurement_timestamp']]
        
        if len(feature_cols) == 0:
            raise ValueError("No feature columns found for prediction")
        
        # Get the most recent data point as baseline
        last_point = last_data_points.iloc[-1]
        current_soh = last_point['state_of_health']
        
        # Create prediction features with realistic degradation trends
        predictions = []
        timestamps = []
        current_features = last_point[feature_cols].values.reshape(1, -1)
        
        base_timestamp = pd.to_datetime(last_point['measurement_timestamp'])
        
        for step in range(prediction_steps):
            # Make prediction
            if hasattr(model, 'predict'):
                try:
                    pred_soh = model.predict(current_features)[0]
                except Exception as e:
                    # Fallback to exponential decay model
                    days_elapsed = step * time_step_days
                    pred_soh = current_soh * np.exp(-days_elapsed / 2000.0)  # Gradual decay
            else:
                # Fallback to exponential decay model
                days_elapsed = step * time_step_days
                pred_soh = current_soh * np.exp(-days_elapsed / 2000.0)
            
            # Ensure SOH doesn't go below 0 or above 100
            pred_soh = max(0, min(100, pred_soh))
            
            predictions.append(pred_soh)
            timestamp = base_timestamp + pd.Timedelta(days=step * time_step_days)
            timestamps.append(timestamp)
            
            # Stop if we've reached 20% threshold
            if pred_soh <= 20.0:
                break
            
            # Update features for next prediction (simulate gradual changes)
            if len(current_features[0]) > 0:
                # Apply small random variations to simulate real-world changes
                noise = np.random.normal(0, 0.01, current_features.shape)
                current_features = current_features + noise
        
        # Find threshold crossings
        threshold_crossings = {}
        thresholds = [70.0, 50.0, 20.0]
        
        for threshold in thresholds:
            crossing_point = None
            for i, (pred, ts) in enumerate(zip(predictions, timestamps)):
                if pred <= threshold:
                    crossing_point = {
                        'step': i,
                        'timestamp': ts,
                        'soh': pred,
                        'days_from_start': i * time_step_days
                    }
                    break
            threshold_crossings[f'{threshold}%'] = crossing_point
        
        return {
            'timestamps': [ts.isoformat() for ts in timestamps],
            'predictions': predictions,
            'current_soh': current_soh,
            'threshold_crossings': threshold_crossings,
            'prediction_steps': len(predictions),
            'time_step_days': time_step_days,
            'total_forecast_days': len(predictions) * time_step_days
        }
        
    except Exception as e:
        print(f"Error in SOH forecasting: {e}")
        return {
            'error': str(e),
            'timestamps': [],
            'predictions': [],
            'current_soh': None,
            'threshold_crossings': {},
            'prediction_steps': 0
        }

def calculate_model_metrics(model, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics for a trained model
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test targets
        
    Returns:
        Dictionary containing various evaluation metrics
    """
    try:
        # Use the data as-is without adding engineered features for metrics calculation
        X_processed = X_test.copy()
        
        # Basic data cleaning
        X_processed = X_processed.fillna(0)
        X_processed = X_processed.replace([np.inf, -np.inf], 0)
        
        # Make predictions
        predictions = model.predict(X_processed)
        
        # Handle potential issues with predictions
        if len(predictions) != len(y_test):
            # Handle sequence models that might return fewer predictions
            min_len = min(len(predictions), len(y_test))
            predictions = predictions[-min_len:] if len(predictions) > min_len else predictions
            y_test_adjusted = y_test.iloc[-min_len:] if len(y_test) > min_len else y_test
        else:
            y_test_adjusted = y_test
        
        # Basic regression metrics
        mse = mean_squared_error(y_test_adjusted, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_adjusted, predictions)
        r2 = r2_score(y_test_adjusted, predictions)
        
        # Additional metrics with error handling
        try:
            mape = np.mean(np.abs((y_test_adjusted - predictions) / y_test_adjusted)) * 100
            # Ensure MAPE is finite
            if not np.isfinite(mape):
                mape = None
        except:
            mape = None
        
        # Calculate residuals
        residuals = y_test_adjusted - predictions
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        
        # Ensure all values are finite and can be serialized
        def safe_float(value):
            if value is None or not np.isfinite(value):
                return None
            return float(value)
        
        return {
            'mse': safe_float(mse),
            'rmse': safe_float(rmse),
            'mae': safe_float(mae),
            'r2_score': safe_float(r2),
            'mape': safe_float(mape),
            'mean_residual': safe_float(mean_residual),
            'std_residual': safe_float(std_residual),
            'min_prediction': safe_float(np.min(predictions)),
            'max_prediction': safe_float(np.max(predictions)),
            'mean_prediction': safe_float(np.mean(predictions))
        }
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        # Return default values instead of error
        return {
            'mse': None,
            'rmse': None,
            'mae': None,
            'r2_score': None,
            'mape': None,
            'mean_residual': None,
            'std_residual': None,
            'min_prediction': None,
            'max_prediction': None,
            'mean_prediction': None
        }