from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import os
import logging
from contextlib import asynccontextmanager

# Local imports
from .database import get_db, engine
from .models import Base, User, FileRecord, ModelRecord
from .schemas import UserCreate, UserLogin, UserResponse, TokenResponse, FileResponse
from .security import authenticate_user, create_access_token, get_current_user, get_password_hash
from .ml_utils import validate_model_params, clean_filename
from .celery_tasks import preprocess_data_task, train_model_task
from .config import settings
from celery.result import AsyncResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create upload directory
UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create models directory
MODELS_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Application shutting down")

# FastAPI app
app = FastAPI(
    title="Nissan EV Battery Predictor API",
    description="API for predicting EV battery state using machine learning models",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication routes
@app.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint to obtain JWT token for authentication."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with secure password hashing."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password_hash=hashed_password)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "username": new_user.username, "created_at": new_user.created_at}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )

# File management routes
@app.post("/files/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV file for processing."""
    # Validate file extension
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Create safe filename
        safe_filename = clean_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{current_user.id}_{timestamp}_{safe_filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            file_size = len(content)
        
        # Create file record
        new_file = FileRecord(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_size=file_size,
            content_type=file.content_type or "text/csv",
            status="uploaded"
        )
        
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        return {
            "id": new_file.id,
            "filename": new_file.original_filename,
            "upload_date": new_file.upload_date,
            "status": new_file.status,
            "file_size": new_file.file_size
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@app.get("/files", response_model=List[FileResponse])
async def list_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all files uploaded by the current user."""
    try:
        files = db.query(FileRecord).filter(FileRecord.user_id == current_user.id).all()
        return [
            {
                "id": file.id,
                "filename": file.original_filename,
                "upload_date": file.upload_date,
                "status": file.status,
                "file_size": file.file_size
            } 
            for file in files
        ]
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving files: {str(e)}"
        )

@app.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Delete a file uploaded by the current user."""
    file_record = db.query(FileRecord).filter(
        FileRecord.id == file_id,
        FileRecord.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    try:
        # Delete file from filesystem
        file_path = os.path.join(UPLOAD_DIR, file_record.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Delete any preprocessed versions
        preprocessed_path = file_path.replace(".csv", "_preprocessed.csv")
        if os.path.exists(preprocessed_path):
            os.remove(preprocessed_path)
            
        # Delete file record
        db.delete(file_record)
        db.commit()
        
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )

# Data processing routes
@app.post("/files/{file_id}/preprocess")
async def preprocess_file(
    file_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Preprocess a file asynchronously using Celery."""
    file_record = db.query(FileRecord).filter(
        FileRecord.id == file_id,
        FileRecord.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, file_record.filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File does not exist on server"
        )

    try:
        # Delegate preprocessing to Celery task
        task = preprocess_data_task.delay(file_path)
        
        # Update file status in database
        file_record.status = "preprocessing"
        db.commit()
        
        return {"message": "File preprocessing started", "task_id": task.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting preprocessing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@app.post("/files/{file_id}/train")
async def train_model_endpoint(
    file_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a model asynchronously using Celery."""
    # Get request body
    body = await request.json()
    model_type = body.get("model_type")
    params = body.get("params", {})
    polynomial_degree = body.get("polynomial_degree", 1)
    
    # Validate model type
    valid_models = ["LinearRegression", "SVR", "ElasticNet", "SGD"]
    if model_type not in valid_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model type. Choose from: {', '.join(valid_models)}"
        )
    
    # Validate parameters
    try:
        params = validate_model_params(model_type, params)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Get file record
    file_record = db.query(FileRecord).filter(
        FileRecord.id == file_id,
        FileRecord.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Check for preprocessed file
    preprocessed_path = os.path.join(
        UPLOAD_DIR, 
        file_record.filename.replace(".csv", "_preprocessed.csv")
    )
    
    if not os.path.exists(preprocessed_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Preprocessed file not found. Please preprocess the file first."
        )

    try:
        # Delegate model training to Celery task
        task = train_model_task.delay(
            preprocessed_path, 
            model_type, 
            params, 
            polynomial_degree,
            current_user.id,
            file_id
        )
        
        # Update file status in database
        file_record.status = "training"
        db.commit()
        
        return {"message": "Model training started", "task_id": task.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting model training: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error training model: {str(e)}"
        )

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Get the status of a Celery task."""
    try:
        task = AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Pending...'
            }
        elif task.state == 'FAILURE':
            response = {
                'state': task.state,
                'status': str(task.info),
                'error': str(task.result) if task.result else None
            }
        else:
            response = {
                'state': task.state,
                'result': task.result
            }
        
        return response
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving task status: {str(e)}"
        )

# Model routes
@app.get("/models")
async def list_models(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all models created by the current user."""
    try:
        models = db.query(ModelRecord).filter(ModelRecord.user_id == current_user.id).all()
        return [{
            "id": model.id,
            "file_id": model.file_id,
            "model_type": model.model_type,
            "created_at": model.created_at,
            "parameters": model.parameters,
            "metrics": model.metrics
        } for model in models]
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving models: {str(e)}"
        )

@app.get("/models/{model_id}")
async def get_model(
    model_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get details of a specific model."""
    model = db.query(ModelRecord).filter(
        ModelRecord.id == model_id,
        ModelRecord.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    
    return {
        "id": model.id,
        "file_id": model.file_id,
        "model_type": model.model_type,
        "created_at": model.created_at,
        "parameters": model.parameters,
        "metrics": model.metrics,
        "visualization_data": model.visualization_data
    }