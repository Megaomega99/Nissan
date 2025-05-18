# backend/app/services/preprocessing.py
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
import logging
from fastapi import HTTPException

from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class PreprocessingService:
    """
    Servicio para operaciones de preprocesamiento de datos CSV.
    
    Proporciona funcionalidades para limpiar, transformar y preparar datos
    para el entrenamiento de modelos ML.
    """
    
    @staticmethod
    def read_csv_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Lee un archivo CSV y lo convierte en DataFrame de pandas.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            pd.DataFrame: DataFrame con los datos del CSV
            
        Raises:
            HTTPException: Si el archivo no existe o no es válido
        """
        try:
            # Intentar diferentes configuraciones de lectura para mayor robustez
            try:
                df = pd.read_csv(file_path)
            except Exception:
                # Intentar con diferentes delimitadores y encodings
                for encoding in ['utf-8', 'latin1', 'iso-8859-1']:
                    for delimiter in [',', ';', '\t', '|']:
                        try:
                            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
                            # Si tiene más de una columna, asumimos que es correcto
                            if len(df.columns) > 1:
                                return df
                        except Exception:
                            continue
                
                # Si llegamos aquí, ninguna combinación funcionó
                raise ValueError("No se pudo determinar el formato del CSV")
                
            return df
        except Exception as e:
            logger.error(f"Error al leer el archivo CSV {file_path}: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error al procesar el archivo CSV: {str(e)}"
            )

    @staticmethod
    def get_file_metadata(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extrae metadatos del DataFrame.
        
        Args:
            df: DataFrame de pandas con los datos del CSV
            
        Returns:
            Dict: Diccionario con metadatos (columnas, filas, tipos, etc.)
        """
        # Obtener estadísticas básicas para columnas numéricas
        numeric_stats = df.describe().to_dict() if not df.empty else {}
        
        # Detectar tipos de datos
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Contar valores nulos por columna
        null_counts = {col: int(count) for col, count in df.isnull().sum().items()}
        
        # Generar una vista previa de los datos (primeras 5 filas)
        preview = df.head(5).to_dict(orient='records')
        
        return {
            "columns": df.columns.tolist(),
            "rows_count": len(df),
            "dtypes": dtypes,
            "null_counts": null_counts,
            "numeric_stats": numeric_stats,
            "preview_data": preview
        }

    @staticmethod
    def clean_data(
        df: pd.DataFrame,
        remove_nulls: bool = True,
        fill_nulls: bool = False,
        fill_method: str = 'mean',
        drop_duplicates: bool = True,
        remove_outliers: bool = False,
        columns_to_process: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Realiza limpieza y preprocesamiento en el DataFrame.
        
        Args:
            df: DataFrame a procesar
            remove_nulls: Si se deben eliminar filas con valores nulos
            fill_nulls: Si se deben rellenar valores nulos
            fill_method: Método para rellenar nulos ('mean', 'median', 'mode', 'constant')
            drop_duplicates: Si se deben eliminar filas duplicadas
            remove_outliers: Si se deben eliminar outliers (IQR method)
            columns_to_process: Columnas específicas a procesar (None = todas)
            
        Returns:
            Tuple[pd.DataFrame, Dict]: DataFrame procesado y diccionario con estadísticas
        """
        original_shape = df.shape
        stats = {"original_rows": original_shape[0], "original_cols": original_shape[1]}
        
        # Hacer una copia para no modificar el original
        processed_df = df.copy()
        
        # Seleccionar columnas a procesar
        cols_to_process = columns_to_process or df.columns.tolist()
        
        # Convertir columnas a tipo numérico donde sea posible
        for col in cols_to_process:
            try:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
            except:
                pass  # Si no se puede convertir, dejar como está
        
        # Tratar valores infinitos
        processed_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # Procesar valores nulos
        if fill_nulls:
            for col in cols_to_process:
                if col in processed_df.select_dtypes(include=np.number).columns:
                    # Para columnas numéricas
                    if fill_method == 'mean':
                        processed_df[col].fillna(processed_df[col].mean(), inplace=True)
                    elif fill_method == 'median':
                        processed_df[col].fillna(processed_df[col].median(), inplace=True)
                    elif fill_method == 'mode':
                        processed_df[col].fillna(processed_df[col].mode()[0], inplace=True)
                    elif fill_method == 'zero':
                        processed_df[col].fillna(0, inplace=True)
                else:
                    # Para columnas categóricas
                    if processed_df[col].dtype == 'object':
                        processed_df[col].fillna(processed_df[col].mode()[0] if not processed_df[col].mode().empty else "", inplace=True)
        
        elif remove_nulls:
            processed_df.dropna(subset=cols_to_process, inplace=True)
        
        # Eliminar duplicados
        if drop_duplicates:
            processed_df.drop_duplicates(inplace=True)
        
        # Eliminar outliers usando el método IQR
        if remove_outliers:
            for col in processed_df.select_dtypes(include=np.number).columns:
                if col in cols_to_process:
                    Q1 = processed_df[col].quantile(0.25)
                    Q3 = processed_df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # Filtrar outliers
                    processed_df = processed_df[(processed_df[col] >= lower_bound) & 
                                             (processed_df[col] <= upper_bound)]
        
        # Calcular estadísticas de procesamiento
        stats["processed_rows"] = processed_df.shape[0]
        stats["processed_cols"] = processed_df.shape[1]
        stats["removed_rows"] = original_shape[0] - processed_df.shape[0]
        stats["null_counts_after"] = {col: int(count) for col, count in processed_df.isnull().sum().items()}
        
        return processed_df, stats

    @staticmethod
    def save_processed_data(
        df: pd.DataFrame, 
        original_file_path: Union[str, Path], 
        suffix: str = "_processed"
    ) -> str:
        """
        Guarda el DataFrame procesado como un nuevo archivo CSV.
        
        Args:
            df: DataFrame procesado
            original_file_path: Ruta del archivo original
            suffix: Sufijo para el nuevo archivo
            
        Returns:
            str: Ruta del nuevo archivo guardado
        """
        file_path = Path(original_file_path)
        directory = file_path.parent
        stem = file_path.stem
        processed_path = directory / f"{stem}{suffix}.csv"
        
        # Guardar el DataFrame procesado
        df.to_csv(processed_path, index=False)
        
        return str(processed_path)