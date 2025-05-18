# backend/app/api/preprocessing.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.file import File
from app.services.preprocessing import PreprocessingService
from app.services.file_service import FileService

router = APIRouter()


@router.post("/{file_id}/clean", response_model=Dict[str, Any])
async def clean_data(
    file_id: int,
    preprocessing_options: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Realiza preprocesamiento en un archivo CSV.
    
    Permite opciones como remover valores nulos, eliminar duplicados,
    eliminar outliers y más.
    
    Args:
        file_id: ID del archivo a procesar
        preprocessing_options: Opciones de preprocesamiento
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Dict[str, Any]: Estadísticas y metadatos del procesamiento
    """
    # Obtener archivo de la base de datos
    file = FileService.get_file_by_id(file_id, current_user.id, db)
    
    # Configurar opciones de preprocesamiento
    options = {
        "remove_nulls": preprocessing_options.get("remove_nulls", True),
        "fill_nulls": preprocessing_options.get("fill_nulls", False),
        "fill_method": preprocessing_options.get("fill_method", "mean"),
        "drop_duplicates": preprocessing_options.get("drop_duplicates", True),
        "remove_outliers": preprocessing_options.get("remove_outliers", False),
        "columns_to_process": preprocessing_options.get("columns_to_process", None)
    }
    
    try:
        # Leer archivo
        df = PreprocessingService.read_csv_file(file.file_path)
        
        # Limpiar datos
        processed_df, stats = PreprocessingService.clean_data(
            df=df,
            remove_nulls=options["remove_nulls"],
            fill_nulls=options["fill_nulls"],
            fill_method=options["fill_method"],
            drop_duplicates=options["drop_duplicates"],
            remove_outliers=options["remove_outliers"],
            columns_to_process=options["columns_to_process"]
        )
        
        # Guardar datos procesados
        processed_file_path = PreprocessingService.save_processed_data(
            processed_df, 
            file.file_path,
            suffix="_processed"
        )
        
        # Actualizar archivo en la base de datos
        file.file_path = processed_file_path
        file.rows_count = processed_df.shape[0]
        file.is_processed = True
        file.processing_status = "completed"
        
        db.commit()
        db.refresh(file)
        
        # Añadir información al resultado
        stats["file_id"] = file.id
        stats["processed_file_path"] = processed_file_path
        
        # Incluir vista previa de datos procesados
        preview_df = processed_df.head(5)
        stats["preview"] = preview_df.to_dict(orient='records')
        
        return stats
    
    except Exception as e:
        # Actualizar estado de procesamiento en caso de error
        file.processing_status = "failed"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar archivo: {str(e)}"
        )


@router.get("/{file_id}/analysis", response_model=Dict[str, Any])
async def analyze_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Realiza un análisis exploratorio de los datos.
    
    Proporciona estadísticas, distribuciones, correlaciones y más.
    
    Args:
        file_id: ID del archivo a analizar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Dict[str, Any]: Resultados del análisis
    """
    # Obtener archivo de la base de datos
    file = FileService.get_file_by_id(file_id, current_user.id, db)
    
    try:
        # Leer archivo
        df = PreprocessingService.read_csv_file(file.file_path)
        
        # Obtener metadatos detallados
        metadata = PreprocessingService.get_file_metadata(df)
        
        # Calcular estadísticas adicionales para columnas numéricas
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        # Estadísticas básicas para cada columna numérica
        column_stats = {}
        for col in numeric_columns:
            column_stats[col] = {
                "min": float(df[col].min()) if not df[col].empty else None,
                "max": float(df[col].max()) if not df[col].empty else None,
                "mean": float(df[col].mean()) if not df[col].empty else None,
                "median": float(df[col].median()) if not df[col].empty else None,
                "std": float(df[col].std()) if not df[col].empty else None,
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique())
            }
        
        # Calcular matriz de correlación para columnas numéricas
        correlation_matrix = None
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr().to_dict()
        
        # Construir respuesta
        analysis_result = {
            "metadata": metadata,
            "column_stats": column_stats,
            "correlation_matrix": correlation_matrix,
            "file_id": file.id
        }
        
        return analysis_result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar archivo: {str(e)}"
        )