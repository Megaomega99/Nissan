import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import { handleApiError, handleApiSuccess } from '../utils/errorHandling';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user profile
      authAPI.getProfile()
        .then((response) => {
          setUser(response.data);
          setIsAuthenticated(true);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    try {
      // Convert to FormData for OAuth2PasswordRequestForm
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      const response = await authAPI.login(formData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      
      // Get user profile
      const profileResponse = await authAPI.getProfile();
      setUser(profileResponse.data);
      setIsAuthenticated(true);
      
      return handleApiSuccess();
    } catch (error) {
      return handleApiError(error, 'Login failed');
    }
  };

  const register = async (userData) => {
    try {
      await authAPI.register(userData);
      return handleApiSuccess();
    } catch (error) {
      return handleApiError(error, 'Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateUser = (userData) => {
    setUser({ ...user, ...userData });
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};