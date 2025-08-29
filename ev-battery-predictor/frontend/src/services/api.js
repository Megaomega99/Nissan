import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // If sending FormData, let axios set the Content-Type automatically
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
};

// User APIs
export const userAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (data) => api.put('/users/profile', data),
};

// Vehicle APIs
export const vehicleAPI = {
  getVehicles: () => api.get('/vehicles'),
  getVehicle: (id) => api.get(`/vehicles/${id}`),
  createVehicle: (data) => api.post('/vehicles', data),
  updateVehicle: (id, data) => api.put(`/vehicles/${id}`, data),
  deleteVehicle: (id) => api.delete(`/vehicles/${id}`),
};

// Battery Data APIs
export const batteryDataAPI = {
  getBatteryData: (vehicleId, params = {}) => 
    api.get(`/battery-data/vehicle/${vehicleId}`, { params }),
  createBatteryData: (data) => api.post('/battery-data', data),
  uploadBatteryData: (vehicleId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/battery-data/upload/${vehicleId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  deleteBatteryData: (id) => api.delete(`/battery-data/${id}`),
};

// ML Model APIs
export const modelAPI = {
  getModels: (vehicleId) => api.get('/ml-models', { params: { vehicle_id: vehicleId } }),
  getModel: (id) => api.get(`/ml-models/${id}`),
  createModel: (data) => api.post('/ml-models', data),
  updateModel: (id, data) => api.put(`/ml-models/${id}`, data),
  deleteModel: (id) => api.delete(`/ml-models/${id}`),
  trainModel: (id, data) => api.post(`/ml-models/${id}/train`, data),
};

// Prediction APIs
export const predictionAPI = {
  makePrediction: (data) => api.post('/predictions/predict', data),
  getFailureAnalysis: (data) => api.post('/predictions/failure-analysis', data),
  getTimeSeriesPrediction: (data) => api.post('/predictions/time-series', data),
  getSOHForecast: (data) => api.post('/predictions/soh-forecast', data),
  getModelMetrics: (modelId) => api.get(`/predictions/metrics/${modelId}`),
  getPredictionHistory: (modelId, limit = 50) => 
    api.get(`/predictions/history/${modelId}`, { params: { limit } }),
};

export default api;