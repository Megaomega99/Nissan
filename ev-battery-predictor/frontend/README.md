# EV Battery Predictor Frontend

React-based frontend application for electric vehicle battery health monitoring and prediction.

## Features

- User authentication and registration
- Vehicle management
- Battery data visualization
- ML model configuration and training
- Real-time predictions and failure analysis
- Interactive dashboards and charts
- Responsive design with Ant Design

## Tech Stack

- **Framework**: React 18
- **UI Library**: Ant Design
- **Charts**: Recharts
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: CSS + Styled Components

## Setup

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Set environment variables (optional):
```bash
export REACT_APP_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm start
```

### Docker Development

```bash
docker-compose up --build
```

## Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Layout.js       # Main app layout
│   ├── ProtectedRoute.js # Route protection
│   └── BatteryHealthChart.js # Chart component
├── pages/              # Page components
│   ├── Login.js        # Login page
│   ├── Register.js     # Registration page
│   ├── Dashboard.js    # Main dashboard
│   ├── Vehicles.js     # Vehicle management
│   ├── Models.js       # ML model management
│   └── Predictions.js  # Predictions and analysis
├── contexts/           # React contexts
│   └── AuthContext.js  # Authentication context
├── services/           # API services
│   └── api.js          # API client configuration
└── utils/              # Utility functions
```

## Key Features

### Authentication
- JWT-based authentication
- Persistent login state
- Protected routes

### Dashboard
- Overview statistics
- Recent battery health trends
- Quick health status indicators

### Vehicle Management
- Add/edit/delete vehicles
- Vehicle-specific data views
- Battery specifications

### Data Upload
- CSV/Excel file upload
- Flexible column mapping
- Batch data import

### ML Models
- Support for 6 model types
- Configurable parameters
- Training progress tracking
- Model performance metrics

### Predictions
- Real-time health predictions
- Failure time estimation
- Time series forecasting
- Confidence intervals

## API Integration

The frontend communicates with the FastAPI backend through RESTful APIs:

- Authentication: `/api/v1/auth/*`
- Users: `/api/v1/users/*`
- Vehicles: `/api/v1/vehicles/*`
- Battery Data: `/api/v1/battery-data/*`
- ML Models: `/api/v1/ml-models/*`
- Predictions: `/api/v1/predictions/*`

## Environment Variables

- `REACT_APP_API_URL`: Backend API base URL (default: http://localhost:8000)

## Building for Production

```bash
npm run build
```

The build folder contains optimized production files ready for deployment.

## Deployment

### Docker Production

```bash
docker build -f Dockerfile.prod -t ev-predictor-frontend .
docker run -p 3000:80 ev-predictor-frontend
```

### Static Hosting

The built files can be deployed to any static hosting service (Netlify, Vercel, AWS S3, etc.).

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Maintain consistent code formatting
4. Add proper error handling
5. Include loading states for async operations