# backend/app/services/ml_service.py
from typing import Dict, List, Optional, Tuple, Any, Union, cast
import pandas as pd
import numpy as np
import pickle
import os
import json
from pathlib import Path
import logging
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, ElasticNet, SGDRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class MLService:
    """
    Servicio para operaciones de machine learning.
    
    Proporciona funcionalidades para entrenar modelos, realizar predicciones
    y evaluar el rendimiento de modelos.
    """
    
    # Tipos de modelos soportados
    SUPPORTED_MODELS = {
        "linear_regression": "Regresión Lineal",
        "svr": "Support Vector Regression",
        "elasticnet": "ElasticNet",
        "sgd": "Stochastic Gradient Descent"
    }
    
    @classmethod
    def get_model_class(cls, model_type: str) -> Any:
        """
        Obtiene la clase de modelo según el tipo.
        
        Args:
            model_type: Tipo de modelo a usar
        
        Returns:
            Any: Clase del modelo correspondiente
            
        Raises:
            ValueError: Si el tipo de modelo no es soportado
        """
        if model_type == "linear_regression":
            return LinearRegression
        elif model_type == "svr":
            return SVR
        elif model_type == "elasticnet":
            return ElasticNet
        elif model_type == "sgd":
            return SGDRegressor
        else:
            raise ValueError(f"Tipo de modelo no soportado: {model_type}")

    @classmethod
    def create_model_instance(cls, model_type: str, params: Dict[str, Any]) -> Any:
        """
        Crea una instancia del modelo especificado con los parámetros proporcionados.
        
        Args:
            model_type: Tipo de modelo a crear
            params: Parámetros para la inicialización del modelo
            
        Returns:
            Any: Instancia del modelo
        """
        ModelClass = cls.get_model_class(model_type)
        
        # Filtrar parámetros válidos para el modelo
        valid_params = {}
        for param, value in params.items():
            try:
                model = ModelClass()
                if hasattr(model, param):
                    valid_params[param] = value
            except Exception as e:
                logger.warning(f"Parámetro inválido {param} para {model_type}: {str(e)}")
        
        try:
            return ModelClass(**valid_params)
        except Exception as e:
            logger.error(f"Error al crear modelo {model_type}: {str(e)}")
            raise ValueError(f"Error al crear modelo: {str(e)}")

    @staticmethod
    def prepare_data(
        df: pd.DataFrame,
        index_column: str,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
        """
        Prepara los datos para entrenamiento y prueba.
        
        Args:
            df: DataFrame con los datos
            index_column: Columna a usar como índice/feature
            target_column: Columna objetivo a predecir
            test_size: Proporción de datos para prueba
            random_state: Semilla aleatoria para reproducibilidad
            
        Returns:
            Tuple: X_train, y_train, X_test, y_test
            
        Raises:
            ValueError: Si las columnas no existen o los datos no son numéricos
        """
        # Verificar que las columnas existan
        if index_column not in df.columns:
            raise ValueError(f"La columna de índice '{index_column}' no existe en el DataFrame")
        
        if target_column not in df.columns:
            raise ValueError(f"La columna objetivo '{target_column}' no existe en el DataFrame")
        
        # Convertir a numérico si es posible
        try:
            X = pd.to_numeric(df[index_column], errors='coerce').values.reshape(-1, 1)
            y = pd.to_numeric(df[target_column], errors='coerce')
        except Exception as e:
            raise ValueError(f"Error al convertir columnas a valores numéricos: {str(e)}")
        
        # Eliminar nulos después de la conversión
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X = X[mask]
        y = y[mask]
        
        if len(X) == 0 or len(y) == 0:
            raise ValueError("No hay datos válidos después de convertir a numérico y eliminar nulos")
        
        # Dividir en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        return X_train, y_train, X_test, y_test

    @classmethod
    def train_model(
        cls, 
        df: pd.DataFrame,
        model_type: str,
        index_column: str,
        target_column: str,
        params: Dict[str, Any],
        save_path: Optional[Union[str, Path]] = None
    ) -> Tuple[Any, Dict[str, float], np.ndarray, np.ndarray]:
        """
        Entrena un modelo con los datos proporcionados.
        
        Args:
            df: DataFrame con los datos
            model_type: Tipo de modelo a entrenar
            index_column: Columna a usar como índice/feature
            target_column: Columna objetivo a predecir
            params: Parámetros para el modelo
            save_path: Ruta donde guardar el modelo entrenado
            
        Returns:
            Tuple: Modelo entrenado, métricas, predicciones, proyecciones
            
        Raises:
            ValueError: Si hay problemas con los datos o el entrenamiento
        """
        # Preparar datos
        X_train, y_train, X_test, y_test = cls.prepare_data(df, index_column, target_column)
        
        # Crear y configurar modelo
        model = None
        
        try:
            # Para regresión lineal con polinomios
            if model_type == "linear_regression" and "polynomial_degree" in params:
                degree = int(params.pop("polynomial_degree", 1))
                # Crear pipeline con características polinómicas
                model = Pipeline([
                    ('poly', PolynomialFeatures(degree=degree)),
                    ('linear', LinearRegression(**params))
                ])
            else:
                model = cls.create_model_instance(model_type, params)
            
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            metrics = {
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "mse": float(mean_squared_error(y_test, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                "r2": float(r2_score(y_test, y_pred))
            }
            
            # Generar proyecciones futuras (al doble del índice máximo)
            max_index = float(df[index_column].max())
            future_indices = np.linspace(max_index, max_index * 2, 50).reshape(-1, 1)
            
            # Predicciones para proyección futura
            if model_type == "linear_regression" and "polynomial_degree" in params:
                future_predictions = model.predict(future_indices)
            else:
                future_predictions = model.predict(future_indices)
            
            # Guardar modelo si se proporciona una ruta
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    pickle.dump(model, f)
            
            return model, metrics, y_pred, np.column_stack((future_indices, future_predictions))
        
        except Exception as e:
            logger.error(f"Error en entrenamiento del modelo {model_type}: {str(e)}")
            raise ValueError(f"Error al entrenar modelo: {str(e)}")

    @staticmethod
    def load_model(model_path: Union[str, Path]) -> Any:
        """
        Carga un modelo guardado.
        
        Args:
            model_path: Ruta al archivo del modelo
            
        Returns:
            Any: Modelo cargado
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si hay error al cargar el modelo
        """
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo del modelo no existe: {model_path}")
        except Exception as e:
            raise ValueError(f"Error al cargar el modelo: {str(e)}")

    @classmethod
    def predict(
        cls,
        model: Any,
        input_data: Union[List[float], np.ndarray, pd.DataFrame],
        input_is_dataframe: bool = False,
        index_column: Optional[str] = None
    ) -> np.ndarray:
        """
        Realiza predicciones con el modelo proporcionado.
        
        Args:
            model: Modelo entrenado
            input_data: Datos para predicción
            input_is_dataframe: Si input_data es un DataFrame
            index_column: Columna a usar como índice si input_is_dataframe es True
            
        Returns:
            np.ndarray: Predicciones
            
        Raises:
            ValueError: Si hay error en la predicción
        """
        try:
            # Preparar datos de entrada
            if input_is_dataframe and index_column:
                # Si es un DataFrame, extraer la columna de índice
                X = pd.to_numeric(input_data[index_column], errors='coerce').values.reshape(-1, 1)
            elif isinstance(input_data, (list, np.ndarray)):
                # Si es lista o array, asegurar formato correcto
                X = np.asarray(input_data).reshape(-1, 1)
            else:
                raise ValueError("Formato de datos de entrada no soportado")
            
            # Realizar predicción
            predictions = model.predict(X)
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error en predicción: {str(e)}")
            raise ValueError(f"Error al realizar predicciones: {str(e)}")

    @classmethod
    def generate_model_path(cls, model_type: str, file_id: int, user_id: int) -> str:
        """
        Genera una ruta única para guardar el modelo.
        
        Args:
            model_type: Tipo de modelo
            file_id: ID del archivo
            user_id: ID del usuario
            
        Returns:
            str: Ruta para guardar el modelo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        
        # Crear directorio base
        base_dir = os.path.join(settings.UPLOAD_DIRECTORY, "models", str(user_id))
        os.makedirs(base_dir, exist_ok=True)
        
        # Generar nombre de archivo
        filename = f"{model_type}_{file_id}_{timestamp}_{unique_id}.pkl"
        
        return os.path.join(base_dir, filename)