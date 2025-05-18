// frontend/src/components/ml/ModelsList.js
import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Tooltip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  Delete,
  Visibility,
  Add,
  Science,
  ShowChart
} from '@mui/icons-material';
import { mlModelService } from '../../services/api';

// Mapeo de tipos de modelos a nombres legibles
const MODEL_TYPE_LABELS = {
  'linear_regression': 'Regresión Lineal',
  'svr': 'Support Vector Regression (SVR)',
  'elasticnet': 'ElasticNet',
  'sgd': 'Stochastic Gradient Descent'
};

// Mapeo de estados de entrenamiento a chips
const STATUS_CHIPS = {
  'pending': { label: 'Pendiente', color: 'default' },
  'training': { label: 'Entrenando', color: 'warning' },
  'completed': { label: 'Completado', color: 'success' },
  'failed': { label: 'Fallido', color: 'error' }
};

// Función para formatear fecha
const formatDate = (dateString) => {
  const options = { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const ModelsList = ({ fileId, onModelSelected }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [modelToDelete, setModelToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  
  // Cargar lista de modelos
  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const modelsData = await mlModelService.getModels(fileId);
      setModels(modelsData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar modelos');
    } finally {
      setLoading(false);
    }
  };
  
  // Cargar modelos al montar el componente
  useEffect(() => {
    loadModels();
    
    // Configurar intervalo para actualizar modelos en entrenamiento
    const interval = setInterval(() => {
      const hasTrainingModels = models.some(
        model => model.training_status === 'pending' || model.training_status === 'training'
      );
      
      if (hasTrainingModels) {
        loadModels();
      }
    }, 5000); // Actualizar cada 5 segundos
    
    return () => clearInterval(interval);
  }, [fileId]);
  
  // Abrir diálogo de confirmación para eliminar
  const handleDeleteClick = (model) => {
    setModelToDelete(model);
    setDeleteDialogOpen(true);
  };
  
  // Cerrar diálogo de confirmación
  const handleCloseDialog = () => {
    setDeleteDialogOpen(false);
    setModelToDelete(null);
  };
  
  // Eliminar modelo
  const handleDeleteConfirm = async () => {
    if (!modelToDelete) return;
    
    try {
      setDeleting(true);
      await mlModelService.deleteModel(modelToDelete.id);
      
      // Actualizar lista de modelos
      setModels(models.filter(model => model.id !== modelToDelete.id));
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al eliminar modelo');
    } finally {
      setDeleting(false);
      handleCloseDialog();
    }
  };
  
  // Seleccionar modelo para trabajar
  const handleSelectModel = (model) => {
    if (onModelSelected) {
      onModelSelected(model);
    }
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Modelos ML
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<Add />}
          component={RouterLink}
          to={fileId ? `/files/${fileId}/train` : '/models/train'}
        >
          Entrenar Nuevo
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {models.length === 0 ? (
        <Card variant="outlined">
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Science sx={{ fontSize: 60, color: 'text.secondary', mb: 2, opacity: 0.3 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No hay modelos entrenados
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ maxWidth: 400, mx: 'auto', mb: 3 }}>
              Entrena un nuevo modelo de machine learning para predecir valores a partir de tus datos.
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              component={RouterLink}
              to={fileId ? `/files/${fileId}/train` : '/models/train'}
            >
              Entrenar Primer Modelo
            </Button>
          </CardContent>
        </Card>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Métricas</TableCell>
                <TableCell>Fecha</TableCell>
                <TableCell align="center">Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {models.map((model) => (
                <TableRow key={model.id}>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {model.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={MODEL_TYPE_LABELS[model.model_type] || model.model_type}
                      color="primary"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={STATUS_CHIPS[model.training_status]?.label || model.training_status}
                      color={STATUS_CHIPS[model.training_status]?.color || 'default'}
                      icon={model.training_status === 'training' ? <CircularProgress size={16} /> : undefined}
                    />
                  </TableCell>
                  <TableCell>
                    {model.is_trained && model.metrics ? (
                      <Box>
                        <Typography variant="caption" display="block">
                          R²: <strong>{model.metrics.r2?.toFixed(3) || 'N/A'}</strong>
                        </Typography>
                        <Typography variant="caption" display="block">
                          RMSE: <strong>{model.metrics.rmse?.toFixed(3) || 'N/A'}</strong>
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="caption" color="textSecondary">
                        No disponible
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{formatDate(model.created_at)}</TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                      <Tooltip title="Ver detalles">
                        <IconButton 
                          color="info"
                          component={RouterLink}
                          to={`/models/${model.id}`}
                          disabled={!model.is_trained}
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Ver predicciones">
                        <IconButton 
                          color="primary"
                          onClick={() => handleSelectModel(model)}
                          disabled={!model.is_trained}
                        >
                          <ShowChart fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Eliminar">
                        <IconButton 
                          color="error"
                          onClick={() => handleDeleteClick(model)}
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {/* Diálogo de confirmación para eliminar */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDialog}
      >
        <DialogTitle>Confirmar eliminación</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Estás seguro de que deseas eliminar el modelo 
            <strong>{modelToDelete?.name}</strong>?
            Esta acción no se puede deshacer.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={deleting}>
            Cancelar
          </Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            disabled={deleting}
            startIcon={deleting ? <CircularProgress size={20} /> : <Delete />}
          >
            {deleting ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ModelsList;