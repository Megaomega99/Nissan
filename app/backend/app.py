from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import pandas as pd
import os
from fastapi.responses import JSONResponse
from sklearn.linear_model import LinearRegression, ElasticNet, SGDRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Configuración de la base de datos
DATABASE_URL = "postgresql://user:password@localhost/nissan_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de la base de datos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Modelos Pydantic
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Dependencia para la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas de autenticación
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    new_user = User(username=user.username, password_hash=user.password)  # Aquí se debe usar hashing
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado exitosamente"}

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password_hash != user.password:  # Aquí se debe usar verificación de hash
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    return {"message": "Inicio de sesión exitoso"}

# Rutas para gestión de archivos
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    new_file = FileRecord(filename=file.filename)
    db.add(new_file)
    db.commit()
    return {"message": "Archivo subido exitosamente", "filename": file.filename}

@app.get("/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileRecord).all()
    return files

@app.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    file_path = os.path.join(UPLOAD_DIR, file_record.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(file_record)
    db.commit()
    return {"message": "Archivo eliminado exitosamente"}

# Ruta para preprocesar datos
@app.post("/preprocess/{file_id}")
def preprocess_file(file_id: int, db: Session = Depends(get_db)):
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file_path = os.path.join(UPLOAD_DIR, file_record.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="El archivo no existe en el servidor")

    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path)

        # Eliminar valores nulos, vacíos o infinitos
        df = df.dropna()
        df = df.replace([float("inf"), float("-inf")], pd.NA).dropna()

        # Guardar el archivo preprocesado
        preprocessed_path = file_path.replace(".csv", "_preprocessed.csv")
        df.to_csv(preprocessed_path, index=False)

        return JSONResponse(content={"message": "Archivo preprocesado exitosamente", "preprocessed_file": preprocessed_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

# Ruta para entrenar modelos de Machine Learning
@app.post("/train/{file_id}")
def train_model(file_id: int, model_type: str, params: dict, db: Session = Depends(get_db)):
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file_path = os.path.join(UPLOAD_DIR, file_record.filename.replace(".csv", "_preprocessed.csv"))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="El archivo preprocesado no existe")

    try:
        # Leer el archivo CSV preprocesado
        df = pd.read_csv(file_path)

        # Asignar índices como características y valores como etiquetas
        X = np.arange(len(df)).reshape(-1, 1)
        y = df.iloc[:, 0].values

        # Dividir los datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Seleccionar el modelo
        if model_type == "LinearRegression":
            model = LinearRegression(**params)
        elif model_type == "SVR":
            model = SVR(**params)
        elif model_type == "ElasticNet":
            model = ElasticNet(**params)
        elif model_type == "SGD":
            model = SGDRegressor(**params)
        else:
            raise HTTPException(status_code=400, detail="Modelo no soportado")

        # Entrenar el modelo
        model.fit(X_train, y_train)

        # Realizar predicciones
        y_pred = model.predict(X_test)

        # Calcular métricas
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        return {
            "message": "Modelo entrenado exitosamente",
            "mse": mse,
            "r2": r2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al entrenar el modelo: {str(e)}")
