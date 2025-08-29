import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Vehicles from './pages/Vehicles';
import VehicleDetail from './pages/VehicleDetail';
import DataUpload from './pages/DataUpload';
import Models from './pages/Models';
import ModelDetail from './pages/ModelDetail';
import Predictions from './pages/Predictions';
import ProtectedRoute from './components/ProtectedRoute';

const theme = {
  token: {
    colorPrimary: '#1890ff',
  },
};

function App() {
  return (
    <ConfigProvider theme={theme}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/vehicles" element={<Vehicles />} />
                      <Route path="/vehicles/:id" element={<VehicleDetail />} />
                      <Route path="/data-upload" element={<DataUpload />} />
                      <Route path="/models" element={<Models />} />
                      <Route path="/models/:id" element={<ModelDetail />} />
                      <Route path="/predictions" element={<Predictions />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;