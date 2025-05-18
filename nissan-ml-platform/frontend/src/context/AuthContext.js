// frontend/src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';
import jwtDecode from 'jwt-decode';

// Crear contexto de autenticación
const AuthContext = createContext(null);

// Proveedor de contexto
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Verificar si hay token
        const token = localStorage.getItem('token');
        
        if (token) {
          // Verificar si el token ha expirado
          try {
            const decodedToken = jwtDecode(token);
            const currentTime = Date.now() / 1000;
            
            if (decodedToken.exp < currentTime) {
              // Token expirado
              localStorage.removeItem('token');
              setCurrentUser(null);
            } else {
              // Token válido, obtener usuario actual
              const userData = await authService.getCurrentUser();
              setCurrentUser(userData);
            }
          } catch (e) {
            // Error al decodificar token
            localStorage.removeItem('token');
            setCurrentUser(null);
          }
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  // Función para iniciar sesión
  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      
      // Llamar al servicio de login
      await authService.login(email, password);
      
      // Obtener datos del usuario
      const userData = await authService.getCurrentUser();
      setCurrentUser(userData);
      
      return userData;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  // Función para registro
  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      // Llamar al servicio de registro
      const newUser = await authService.register(userData);
      
      return newUser;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  // Función para cerrar sesión
  const logout = () => {
    authService.logout();
    setCurrentUser(null);
  };
  
  // Valores proporcionados por el contexto
  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!currentUser
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizado para usar el contexto de autenticación
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export default AuthContext;