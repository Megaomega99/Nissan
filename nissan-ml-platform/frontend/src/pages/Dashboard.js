// frontend/src/pages/Dashboard.js
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Typography,
  Paper,
  Box,
  Card,
  CardContent,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Psychology,
  Visibility,
  ArrowForward,
  BarChart,
  MenuBook
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fileService, mlModelService } from '../services/api';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [recentFiles, setRecentFiles] = useState([]);
  const [recentModels, setRecentModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Cargar archivos recientes
        const files = await fileService.getFiles();
        setRecentFiles(files.slice(0, 5)); // Mostrar solo los 5 más recientes
        
        // Cargar modelos recientes
        const models = await mlModelService.getModels();
        setRecentModels(models.slice(0, 5)); // Mostrar solo los 5 más recientes
      } catch (err) {
        setError('Error al cargar datos del dashboard');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Formatear fecha
  const formatDate = (dateString) => {
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Bienvenido, {currentUser?.full_name || currentUser?.username}
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {/* Acciones rápidas */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Acciones Rápidas
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <List>
              <ListItem
                button
                component={RouterLink}
                to="/upload"
                sx={{
                  mb: 1,
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <ListItemIcon>
                  <CloudUpload color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Subir Archivo CSV" 
                  secondary="Sube un nuevo conjunto de datos para analizar"
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" color="primary">
                    <ArrowForward />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              
              <ListItem
                button
                component={RouterLink}
                to="/files"
                sx={{
                  mb: 1,
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <ListItemIcon>
                  <InsertDriveFile color="info" />
                </ListItemIcon>
                <ListItemText 
                  primary="Mis Archivos" 
                  secondary="Gestiona tus datos subidos"
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" color="info">
                    <ArrowForward />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              
              <ListItem
                button
                component={RouterLink}
                to="/models"
                sx={{
                  mb: 1,
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <ListItemIcon>
                  <Psychology color="secondary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Modelos ML" 
                  secondary="Ver y gestionar tus modelos"
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" color="secondary">
                    <ArrowForward />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              
              <ListItem
                button
                component={RouterLink}
                to="/analysis"
                sx={{
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <ListItemIcon>
                  <BarChart color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Analizar Datos" 
                  secondary="Explorar y visualizar conjuntos de datos"
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" color="success">
                    <ArrowForward />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </Paper>
        </Grid>
        
        {/* Archivos recientes */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6">
                Archivos Recientes
              </Typography>
              
              <Button
                component={RouterLink}
                to="/files"
                size="small"
                endIcon={<ArrowForward />}
              >
                Ver todos
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : recentFiles.length === 0 ? (
              <Box sx={{ textAlign: 'center', p: 4 }}>
                <InsertDriveFile sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                <Typography variant="body1" color="textSecondary" gutterBottom>
                  No hay archivos subidos todavía
                </Typography>
                <Button
                  variant="contained"
                  component={RouterLink}
                  to="/upload"
                  startIcon={<CloudUpload />}
                  sx={{ mt: 2 }}
                >
                  Subir Archivo
                </Button>
              </Box>
            ) : (
              <List>
                {recentFiles.map((file) => (
                  <ListItem
                    key={file.id}
                    button
                    component={RouterLink}
                    to={`/files/${file.id}`}
                    sx={{
                      mb: 1,
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider'
                    }}
                  >
                    <ListItemIcon>
                      <InsertDriveFile color="info" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={file.original_filename} 
                      secondary={`Subido el ${formatDate(file.created_at)}`}
                      primaryTypographyProps={{ noWrap: true }}
                    />
                    <ListItemSecondaryAction>
                      <Chip 
                        size="small" 
                        label={file.is_processed ? 'Procesado' : 'Sin procesar'} 
                        color={file.is_processed ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Modelos recientes */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6">
                Modelos ML Recientes
              </Typography>
              
              <Button
                component={RouterLink}
                to="/models"
                size="small"
                endIcon={<ArrowForward />}
              >
                Ver todos
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : recentModels.length === 0 ? (
              <Box sx={{ textAlign: 'center', p: 4 }}>
                <Psychology sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                <Typography variant="body1" color="textSecondary" gutterBottom>
                  No hay modelos entrenados todavía
                </Typography>
                <Button
                  variant="contained"
                  component={RouterLink}
                  to="/models/train"
                  startIcon={<Psychology />}
                  sx={{ mt: 2 }}
                >
                  Entrenar Modelo
                </Button>
              </Box>
            ) : (
              <List>
                {recentModels.map((model) => (
                  <ListItem
                    key={model.id}
                    button
                    component={RouterLink}
                    to={`/models/${model.id}`}
                    sx={{
                      mb: 1,
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider'
                    }}
                    disabled={!model.is_trained}
                  >
                    <ListItemIcon>
                      <Psychology color="secondary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={model.name} 
                      secondary={`${model.model_type} - R²: ${model.metrics?.r2?.toFixed(3) || 'N/A'}`}
                      primaryTypographyProps={{ noWrap: true }}
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        edge="end" 
                        color="info"
                        component={RouterLink}
                        to={`/models/${model.id}`}
                        disabled={!model.is_trained}
                      >
                        <Visibility />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Recursos y Documentación */}
        <Grid item xs={12}>
          <Paper elevation={0} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Documentación y Recursos
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Guía de Inicio
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      Aprende a utilizar la plataforma ML de Nissan con nuestra guía paso a paso.
                    </Typography>
                    <Button
                      variant="text"
                      endIcon={<ArrowForward />}
                      component="a"
                      href="#"
                    >
                      Ver guía
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Modelos ML
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      Información detallada sobre los modelos ML disponibles y sus parámetros.
                    </Typography>
                    <Button
                      variant="text"
                      endIcon={<ArrowForward />}
                      component="a"
                      href="#"
                    >
                      Ver documentación
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Preparación de Datos
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      Consejos para preparar tus datos CSV para obtener mejores resultados.
                    </Typography>
                    <Button
                      variant="text"
                      endIcon={<ArrowForward />}
                      component="a"
                      href="#"
                    >
                      Ver consejos
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      API Reference
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      Documentación completa de la API para integrar con otros sistemas.
                    </Typography>
                    <Button
                      variant="text"
                      endIcon={<ArrowForward />}
                      component="a"
                      href="#"
                    >
                      Ver API docs
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;