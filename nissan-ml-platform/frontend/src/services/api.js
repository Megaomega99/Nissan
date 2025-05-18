// frontend/src/services/api.js
import axios from 'axios';

// URL base para API
const API_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Cliente axios con configuración predeterminada
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Redirigir a login si hay error de autenticación
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Servicios de autenticación
export const authService = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post(`${API_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    
    return response.data;
  },
  
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('token');
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

// Servicios para archivos
export const fileService = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
  
  getFiles: async () => {
    const response = await apiClient.get('/files/list');
    return response.data;
  },
  
  getFileById: async (fileId) => {
    const response = await apiClient.get(`/files/${fileId}`);
    return response.data;
  },
  
  getFilePreview: async (fileId, maxRows = 10) => {
    const response = await apiClient.get(`/files/${fileId}/preview?max_rows=${maxRows}`);
    return response.data;
  },
  
  deleteFile: async (fileId) => {
    await apiClient.delete(`/files/${fileId}`);
    return true;
  },
};

// Servicios para preprocesamiento
export const preprocessingService = {
  cleanData: async (fileId, options) => {
    const response = await apiClient.post(`/preprocessing/${fileId}/clean`, options);
    return response.data;
  },
  
  analyzeFile: async (fileId) => {
    const response = await apiClient.get(`/preprocessing/${fileId}/analysis`);
    return response.data;
  },
};

// Servicios para modelos ML
export const mlModelService = {
  trainModel: async (modelConfig) => {
    const response = await apiClient.post('/models/train', modelConfig);
    return response.data;
  },
  
  getModels: async (fileId = null) => {
    let url = '/models/list';
    if (fileId) {
      url += `?file_id=${fileId}`;
    }
    
    const response = await apiClient.get(url);
    return response.data;
  },
  
  getModelById: async (modelId) => {
    const response = await apiClient.get(`/models/${modelId}`);
    return response.data;
  },
  
  predict: async (modelId, predictionData) => {
    const response = await apiClient.post(`/models/${modelId}/predict`, predictionData);
    return response.data;
  },
  
  deleteModel: async (modelId) => {
    await apiClient.delete(`/models/${modelId}`);
    return true;
  },
};

export default apiClient;