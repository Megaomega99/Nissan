// frontend/src/routes/PublicRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CircularProgress, Box } from '@mui/material';

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  // Si aún está cargando, mostrar spinner
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Si ya está autenticado, redirigir a dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  // Si no está autenticado, mostrar el componente hijo
  return children;
};

export default PublicRoute;