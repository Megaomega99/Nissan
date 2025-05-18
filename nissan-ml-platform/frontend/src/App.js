// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Contexto de autenticación
import { AuthProvider } from './context/AuthContext';

// Protección de rutas
import ProtectedRoute from './routes/ProtectedRoute';
import PublicRoute from './routes/PublicRoute';

// Componente de layout
import Layout from './components/layout/Layout';

// Páginas públicas
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Páginas privadas
import Dashboard from './pages/Dashboard';
import FilesListPage from './pages/FilesListPage';
import FileUploadPage from './pages/FileUploadPage';
import FileDetailsPage from './pages/FileDetailsPage';
import FileProcessingPage from './pages/FileProcessingPage';
import ModelsListPage from './pages/ModelsListPage';
import ModelTrainingPage from './pages/ModelTrainingPage';
import ModelDetailsPage from './pages/ModelDetailsPage';
import AnalysisPage from './pages/AnalysisPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import NotFoundPage from './pages/NotFoundPage';

// Tema personalizado
const theme = createTheme({
  palette: {
    primary: {
      main: '#c3002f', // Rojo Nissan
      light: '#ff5458',
      dark: '#8b0009',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#0c2340', // Azul oscuro Nissan
      light: '#354b6c',
      dark: '#000018',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: 'none',
        },
      },
    },
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0 2px 4px rgba(0, 0, 0, 0.05)',
    // ... resto de sombras
  ],
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Rutas públicas */}
            <Route path="/login" element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            } />
            <Route path="/register" element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            } />
            
            {/* Rutas protegidas */}
            <Route path="/" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/files" element={
              <ProtectedRoute>
                <Layout>
                  <FilesListPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/upload" element={
              <ProtectedRoute>
                <Layout>
                  <FileUploadPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/files/:fileId" element={
              <ProtectedRoute>
                <Layout>
                  <FileDetailsPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/files/:fileId/process" element={
              <ProtectedRoute>
                <Layout>
                  <FileProcessingPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/files/:fileId/train" element={
              <ProtectedRoute>
                <Layout>
                  <ModelTrainingPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/files/:fileId/analyze" element={
              <ProtectedRoute>
                <Layout>
                  <AnalysisPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/models" element={
              <ProtectedRoute>
                <Layout>
                  <ModelsListPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/models/train" element={
              <ProtectedRoute>
                <Layout>
                  <ModelTrainingPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/models/:modelId" element={
              <ProtectedRoute>
                <Layout>
                  <ModelDetailsPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/analysis" element={
              <ProtectedRoute>
                <Layout>
                  <AnalysisPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <ProfilePage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/settings" element={
              <ProtectedRoute>
                <Layout>
                  <SettingsPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Ruta por defecto - Redirigir a dashboard */}
            <Route index element={<Navigate to="/dashboard" replace />} />
            
            {/* 404 - Página no encontrada */}
            <Route path="*" element={
              <Layout>
                <NotFoundPage />
              </Layout>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;