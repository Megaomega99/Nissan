# EV Battery Health Predictor

A comprehensive application for electric vehicle battery health monitoring and prediction using machine learning.

## 🚗 Features

### User Management
- **Authentication**: Secure JWT-based login/registration
- **Profile Management**: User profiles with vehicle associations

### Vehicle & Data Management
- **Vehicle Registry**: Add and manage multiple EVs
- **Data Upload**: CSV/Excel file import with flexible column mapping
- **Real-time Monitoring**: Track battery health metrics over time

### Machine Learning Models
- **Linear Regression**: Simple trend analysis
- **Polynomial Regression**: Non-linear pattern detection
- **Support Vector Machine (SVM)**: Complex boundary learning
- **Stochastic Gradient Descent (SGD)**: Efficient large-scale learning
- **Neural Networks (MLP)**: Deep pattern recognition
- **Recurrent Neural Networks (RNN/LSTM)**: Time series prediction

### Predictions & Analytics
- **Health Predictions**: Current and future battery state
- **Failure Analysis**: Estimate time to battery degradation
- **Time Series Forecasting**: Long-term trend prediction
- **Confidence Intervals**: Prediction uncertainty quantification

### Visualization & Reporting
- **Interactive Dashboards**: Real-time health metrics
- **Chart Visualizations**: Battery trends and predictions
- **Model Performance**: Training metrics and accuracy scores
- **Export Capabilities**: Prediction data export

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt hashing
- **ML Libraries**: scikit-learn, TensorFlow/Keras, NumPy, Pandas
- **Task Queue**: Redis + Celery (async training)
- **Migrations**: Alembic

### Frontend
- **Framework**: React 18 with functional components
- **UI Library**: Ant Design for components
- **Charts**: Recharts for data visualization
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **State Management**: React Context + Hooks

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Web Server**: Nginx (production)
- **SSL**: Let's Encrypt support

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ev-battery-predictor
```

2. **Copy environment configuration**:
```bash
cp .env.example .env
```

3. **Start all services**:
```bash
docker-compose up --build
```

4. **Access the application**:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### First Steps

1. **Register** a new account through the frontend
2. **Add a vehicle** in the Vehicles section
3. **Upload battery data** (see data format below)
4. **Create ML models** with different algorithms
5. **Train models** and view performance metrics
6. **Generate predictions** and analyze results

## 📊 Data Format

The application expects battery data with the following fields:

### Required Fields
- `state_of_health`: Battery health percentage (0-100%)
- `measurement_timestamp`: ISO timestamp of measurement

### Optional Fields
- `state_of_charge`: Charge level (0-100%)
- `voltage`: Battery voltage (Volts)
- `current`: Current flow (Amperes)
- `temperature`: Battery temperature (Celsius)
- `cycle_count`: Number of charge/discharge cycles
- `capacity_fade`: Capacity loss percentage
- `internal_resistance`: Internal resistance (Ohms)

### File Upload Support
- **CSV files**: Comma-separated values
- **Excel files**: .xlsx format
- **Flexible mapping**: Automatic column detection
- **Batch import**: Multiple data points at once

### Example CSV Format
```csv
timestamp,soh,voltage,current,temperature
2023-01-01 10:00:00,95.2,400.5,12.3,25.1
2023-01-01 11:00:00,95.1,398.2,11.8,26.2
2023-01-01 12:00:00,95.0,401.1,12.0,25.8
```

## 🧠 ML Model Configuration

Each model type supports configurable parameters:

### Linear Regression
```json
{
  "model_type": "linear",
  "parameters": {}
}
```

### Polynomial Regression
```json
{
  "model_type": "polynomial", 
  "parameters": {
    "degree": 2
  }
}
```

### Support Vector Machine
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

### Neural Network (RNN/LSTM)
```json
{
  "model_type": "rnn",
  "parameters": {
    "sequence_length": 10,
    "lstm_units": 50,
    "epochs": 100,
    "batch_size": 32
  }
}
```

## 📁 Project Structure

```
ev-battery-predictor/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   │   ├── auth.py        # Authentication routes
│   │   │   ├── vehicles.py    # Vehicle management
│   │   │   ├── battery_data.py # Data upload/management
│   │   │   ├── ml_models.py   # Model CRUD operations
│   │   │   └── predictions.py # Prediction services
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Application settings
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT & password handling
│   │   ├── models/            # SQLAlchemy database models
│   │   │   ├── user.py        # User model
│   │   │   ├── vehicle.py     # Vehicle model
│   │   │   ├── battery_data.py # Battery data model
│   │   │   ├── ml_model.py    # ML model metadata
│   │   │   └── prediction.py  # Prediction results
│   │   ├── ml/                # Machine learning components
│   │   │   └── models.py      # ML model implementations
│   │   └── main.py            # FastAPI application entry
│   ├── alembic/               # Database migrations
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Development container
│   ├── Dockerfile.prod        # Production container
│   └── README.md              # Backend documentation
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   │   ├── Layout.js      # Application layout
│   │   │   ├── ProtectedRoute.js # Route protection
│   │   │   └── BatteryHealthChart.js # Chart component
│   │   ├── pages/             # Page components
│   │   │   ├── Login.js       # Login page
│   │   │   ├── Dashboard.js   # Main dashboard
│   │   │   ├── Vehicles.js    # Vehicle management
│   │   │   ├── Models.js      # ML model management
│   │   │   └── Predictions.js # Prediction interface
│   │   ├── contexts/          # React context providers
│   │   │   └── AuthContext.js # Authentication state
│   │   ├── services/          # API service layer
│   │   │   └── api.js         # HTTP client configuration
│   │   └── App.js             # Root application component
│   ├── package.json           # Node.js dependencies
│   ├── Dockerfile             # Development container
│   ├── Dockerfile.prod        # Production container
│   └── README.md              # Frontend documentation
├── docker-compose.yml         # Development orchestration
├── docker-compose.prod.yml    # Production orchestration
├── DEPLOYMENT.md              # Deployment guide
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🚀 Deployment

### Development
```bash
docker-compose up --build
```

### Production
```bash
# Set environment variables
export POSTGRES_PASSWORD=secure_password
export SECRET_KEY=secure_secret_key
export BACKEND_URL=https://your-domain.com

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including cloud platforms.

## 📖 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Vehicle Management
- `GET /api/v1/vehicles` - List user vehicles
- `POST /api/v1/vehicles` - Create new vehicle
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `PUT /api/v1/vehicles/{id}` - Update vehicle
- `DELETE /api/v1/vehicles/{id}` - Delete vehicle

### Battery Data
- `GET /api/v1/battery-data/vehicle/{id}` - Get vehicle data
- `POST /api/v1/battery-data` - Add single data point
- `POST /api/v1/battery-data/upload/{id}` - Upload file

### ML Models
- `GET /api/v1/ml-models` - List models
- `POST /api/v1/ml-models` - Create model
- `POST /api/v1/ml-models/{id}/train` - Train model
- `DELETE /api/v1/ml-models/{id}` - Delete model

### Predictions
- `POST /api/v1/predictions/predict` - Make prediction
- `POST /api/v1/predictions/failure-analysis` - Analyze failure risk
- `POST /api/v1/predictions/time-series` - Time series forecast

Interactive API documentation available at `/docs` when running.

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the README files in `/backend` and `/frontend`
- **API Docs**: Visit `/docs` endpoint for interactive API documentation
- **Issues**: Report bugs and feature requests via GitHub issues
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guidance

## 🔮 Future Enhancements

- **Advanced Analytics**: More sophisticated failure prediction algorithms
- **Real-time Streaming**: WebSocket support for live data updates
- **Mobile App**: React Native mobile application
- **Cloud Integration**: Native cloud provider integrations
- **Advanced Visualizations**: 3D plots and interactive dashboards
- **Alert System**: Email/SMS notifications for critical battery states
- **Multi-tenancy**: Support for fleet management
- **API Rate Limiting**: Enhanced security and usage controls