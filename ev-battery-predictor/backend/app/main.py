from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from .core.config import settings
from .api import auth, users, vehicles, battery_data, ml_models, predictions

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="EV Battery Health Prediction API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(vehicles.router, prefix=f"{settings.API_V1_STR}/vehicles", tags=["vehicles"])
app.include_router(battery_data.router, prefix=f"{settings.API_V1_STR}/battery-data", tags=["battery-data"])
app.include_router(ml_models.router, prefix=f"{settings.API_V1_STR}/ml-models", tags=["ml-models"])
app.include_router(predictions.router, prefix=f"{settings.API_V1_STR}/predictions", tags=["predictions"])

@app.get("/")
async def root():
    return {"message": "EV Battery Health Predictor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}