# EV Battery Predictor Backend

FastAPI-based backend service for electric vehicle battery health prediction.

## Features

- User authentication with JWT tokens
- Vehicle and battery data management
- Multiple ML models support (Linear, Polynomial, SVM, SGD, Neural Networks, RNN)
- Real-time predictions and failure analysis
- File upload for batch data import
- RESTful API with automatic documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt
- **ML Libraries**: scikit-learn, TensorFlow/Keras
- **Task Queue**: Redis + Celery (for async training)
- **Migration**: Alembic

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export DATABASE_URL="postgresql://evuser:evpass123@localhost:5432/evbattery"
export SECRET_KEY="your-secret-key"
export REDIS_URL="redis://localhost:6379"
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

### Docker Development

```bash
docker-compose up --build
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Supported ML Models

### 1. Linear Regression
```json
{
  "model_type": "linear",
  "parameters": {}
}
```

### 2. Polynomial Regression
```json
{
  "model_type": "polynomial",
  "parameters": {
    "degree": 2
  }
}
```

### 3. Support Vector Machine
```json
{
  "model_type": "svm",
  "parameters": {
    "kernel": "rbf",
    "C": 1.0,
    "gamma": "scale"
  }
}
```

### 4. Stochastic Gradient Descent
```json
{
  "model_type": "sgd",
  "parameters": {
    "learning_rate": "adaptive",
    "eta0": 0.01,
    "max_iter": 1000
  }
}
```

### 5. Neural Network (MLP)
```json
{
  "model_type": "neural_network",
  "parameters": {
    "hidden_layer_sizes": [100, 50],
    "activation": "relu",
    "solver": "adam",
    "max_iter": 500
  }
}
```

### 6. Recurrent Neural Network (LSTM)
```json
{
  "model_type": "rnn",
  "parameters": {
    "sequence_length": 10,
    "lstm_units": 50,
    "dense_units": 25,
    "dropout_rate": 0.2,
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 32
  }
}
```

## Data Format

Battery data should include:
- `state_of_health` (required): 0-100%
- `state_of_charge`: 0-100%
- `voltage`: Volts
- `current`: Amperes
- `temperature`: Celsius
- `cycle_count`: Number of charge cycles
- `capacity_fade`: Percentage capacity loss
- `internal_resistance`: Ohms
- `measurement_timestamp`: ISO timestamp

## File Upload

Supports CSV and Excel files with flexible column mapping:
- SOH columns: `soh`, `state_of_health`, `health`
- Timestamp columns: `timestamp`, `time`, `date`, `measurement_timestamp`

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `REDIS_URL`: Redis connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `MAX_FILE_SIZE`: Max upload size in bytes (default: 10MB)

## Testing

```bash
pytest
```

## Production Deployment

Use `docker-compose.prod.yml` with proper environment variables:

```bash
export POSTGRES_PASSWORD=secure_password
export SECRET_KEY=secure_secret_key
export BACKEND_URL=https://your-domain.com

docker-compose -f docker-compose.prod.yml up -d
```