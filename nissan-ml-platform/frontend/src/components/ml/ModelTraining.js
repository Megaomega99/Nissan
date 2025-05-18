// frontend/src/components/ml/ModelTraining.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  FormControl,
  FormGroup,
  FormControlLabel,
  Checkbox,
  TextField,
  MenuItem,
  InputLabel,
  Select,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress
} from '@mui/material';
import { 
  ExpandMore, 
  ScienceOutlined, 
  CheckCircle,
  ShowChart,
  ModelTraining as ModelIcon
} from '@mui/icons-material';
import { fileService, mlModelService } from '../../services/api';

// Tipos de modelos disponibles
const MODEL_TYPES = [
  { value: 'linear_regression', label: 'Regresión Lineal' },
  { value: 'svr', label: 'Support Vector Regression (SVR)' },
  { value: 'elasticnet', label: 'ElasticNet' },
  { value: 'sgd', label: 'Stochastic Gradient Descent (SGD)' }
];

// Parámetros por defecto por tipo de modelo
const DEFAULT_PARAMS = {
  linear_regression: {
    fit_intercept: true,
    polynomial_degree: 1
  },
  svr: {
    kernel: 'rbf',
    C: 1.0,
    epsilon: 0.1
  },
  elasticnet: {
    alpha: 1.0,
    l1_ratio: 0.5,
    max_iter: 1000
  },
  sgd: {
    loss: 'squared_error',
    penalty: 'l2',
    alpha: 0.0001,
    max_iter: 1000
  }
};

// Opciones para parámetros específicos
const KERNEL_OPTIONS = [
  { value: 'linear', label: 'Linear' },
  { value: 'poly', label: 'Polynomial' },
  { value: 'rbf', label: 'RBF' },
  { value: 'sigmoid', label: 'Sigmoid' }
];

const LOSS_OPTIONS = [
  { value: 'squared_error', label: 'Squared Error' },
  { value: 'huber', label: 'Huber' },
  { value: 'epsilon_insensitive', label: 'Epsilon Insensitive' },
  { value: 'squared_epsilon_insensitive', label: 'Squared Epsilon Insensitive' }
];

const PENALTY_OPTIONS = [
  { value: 'l2', label: 'L2 (Ridge)' },
  { value: 'l1', label: 'L1 (Lasso)' },
  { value: 'elasticnet', label: 'ElasticNet' },
  { value: 'none', label: 'None' }
];

const ModelTraining = ({ fileId, onModelTrained }) => {
  // Estado para datos del archivo
  const [fileData, setFileData] = useState(null);
  const [preview, setPreview] = useState(null);
  
  // Estado para configuración del modelo
  const [modelConfig, setModelConfig] = useState({
    name: '',
    model_type: 'linear_regression',
    index_column: '',
    target_column: '',
    parameters: DEFAULT_PARAMS.linear_regression,
    file_id: fileId
  });
  
  // Estado para manejo de proceso
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(null);
  const [trainingResult, setTrainingResult] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [pollingInterval, setPollingInterval] = useState(null);
  
  // Cargar datos del archivo
  useEffect(() => {
    const loadFileData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Cargar información del archivo
        const fileInfo = await fileService.getFileById(fileId);
        setFileData(fileInfo);
        
        // Cargar vista previa de datos
        const previewData = await fileService.getFilePreview(fileId);
        setPreview(previewData);
        
        // Inicializar nombre del modelo
        setModelConfig(prev => ({
          ...prev,
          name: `Modelo para ${fileInfo.original_filename}`
        }));
        
      } catch (err) {
        setError(err.response?.data?.detail || 'Error al cargar datos del archivo');
      } finally {
        setLoading(false);
      }
    };
    
    if (fileId) {
      loadFileData();
    }
    
    // Limpiar intervalo de polling al desmontar
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [fileId]);
  
  // Manejar cambios en configuración del modelo
  const handleConfigChange = (event) => {
    const { name, value } = event.target;
    
    if (name === 'model_type') {
      // Actualizar parámetros por defecto cuando cambia el tipo de modelo
      setModelConfig({
        ...modelConfig,
        model_type: value,
        parameters: DEFAULT_PARAMS[value]
      });
    } else {
      setModelConfig({
        ...modelConfig,
        [name]: value
      });
    }
  };
  
  // Manejar cambios en parámetros del modelo
  const handleParamChange = (event) => {
    const { name, value, type, checked } = event.target;
    
    // Convertir a número si es numérico
    let paramValue = value;
    if (type === 'number') {
      paramValue = parseFloat(value);
    } else if (type === 'checkbox') {
      paramValue = checked;
    }
    
    setModelConfig({
      ...modelConfig,
      parameters: {
        ...modelConfig.parameters,
        [name]: paramValue
      }
    });
  };
  
  // Entrenar modelo
  const handleTrainModel = async () => {
    try {
      setTraining(true);
      setError(null);
      
      // Validar configuración
      if (!modelConfig.index_column || !modelConfig.target_column) {
        setError('Debes seleccionar columnas de índice y objetivo');
        setTraining(false);
        return;
      }
      
      // Iniciar entrenamiento
      const result = await mlModelService.trainModel(modelConfig);
      setTrainingResult(result);
      
      // Avanzar al siguiente paso
      setActiveStep(1);
      
      // Iniciar polling para actualizar estado del modelo
      const interval = setInterval(async () => {
        try {
          const modelInfo = await mlModelService.getModelById(result.model_id);
          
          if (modelInfo.training_status === 'completed' || modelInfo.training_status === 'failed') {
            // Detener polling cuando el entrenamiento termina
            clearInterval(interval);
            setPollingInterval(null);
            
            // Actualizar resultado con información completa
            setTrainingResult(modelInfo);
            
            // Notificar finalización si es necesario
            if (onModelTrained && modelInfo.training_status === 'completed') {
              onModelTrained(modelInfo);
            }
            
            // Mostrar error si falló
            if (modelInfo.training_status === 'failed') {
              setError('El entrenamiento del modelo falló. Por favor, intenta con diferentes parámetros.');
            }
          }
        } catch (err) {
          console.error('Error al obtener estado del modelo:', err);
        }
      }, 3000); // Consultar cada 3 segundos
      
      setPollingInterval(interval);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al entrenar modelo');
      setTraining(false);
    }
  };
  
  // Reiniciar proceso
  const handleReset = () => {
    setTrainingResult(null);
    setActiveStep(0);
    setError(null);
    setTraining(false);
  };
  
  // Renderizar parámetros específicos según el tipo de modelo
  const renderModelParameters = () => {
    const { model_type, parameters } = modelConfig;
    
    switch (model_type) {
      case 'linear_regression':
        return (
          <>
            <TextField
              label="Grado del Polinomio"
              name="polynomial_degree"
              type="number"
              value={parameters.polynomial_degree}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 1, max: 10, step: 1 }}
              helperText="Grado del polinomio para regresión (1 para lineal, >1 para polinómica)"
            />
            
            <FormControlLabel
              control={
                <Checkbox
                  checked={parameters.fit_intercept}
                  onChange={handleParamChange}
                  name="fit_intercept"
                />
              }
              label="Incluir término independiente (intercepto)"
            />
          </>
        );
        
      case 'svr':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel id="kernel-label">Kernel</InputLabel>
              <Select
                labelId="kernel-label"
                name="kernel"
                value={parameters.kernel}
                onChange={handleParamChange}
                label="Kernel"
              >
                {KERNEL_OPTIONS.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label="C (Regularización)"
              name="C"
              type="number"
              value={parameters.C}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 0.001, step: 0.1 }}
              helperText="Parámetro de regularización. Menor valor = mayor regularización."
            />
            
            <TextField
              label="Epsilon"
              name="epsilon"
              type="number"
              value={parameters.epsilon}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 0.001, step: 0.01 }}
              helperText="Margen de tolerancia en la función de pérdida."
            />
          </>
        );
        
      case 'elasticnet':
        return (
          <>
            <TextField
              label="Alpha"
              name="alpha"
              type="number"
              value={parameters.alpha}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 0.0001, step: 0.01 }}
              helperText="Término de regularización. Mayor valor = más regularización."
            />
            
            <TextField
              label="L1 Ratio"
              name="l1_ratio"
              type="number"
              value={parameters.l1_ratio}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              helperText="Ratio de mezcla entre L1 (Lasso) y L2 (Ridge). 0 = Ridge, 1 = Lasso."
            />
            
            <TextField
              label="Máximo de Iteraciones"
              name="max_iter"
              type="number"
              value={parameters.max_iter}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 100, step: 100 }}
            />
          </>
        );
        
      case 'sgd':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel id="loss-label">Función de Pérdida</InputLabel>
              <Select
                labelId="loss-label"
                name="loss"
                value={parameters.loss}
                onChange={handleParamChange}
                label="Función de Pérdida"
              >
                {LOSS_OPTIONS.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="penalty-label">Penalización</InputLabel>
              <Select
                labelId="penalty-label"
                name="penalty"
                value={parameters.penalty}
                onChange={handleParamChange}
                label="Penalización"
              >
                {PENALTY_OPTIONS.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label="Alpha"
              name="alpha"
              type="number"
              value={parameters.alpha}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 0.00001, step: 0.0001 }}
              helperText="Término de regularización. Mayor valor = más regularización."
            />
            
            <TextField
              label="Máximo de Iteraciones"
              name="max_iter"
              type="number"
              value={parameters.max_iter}
              onChange={handleParamChange}
              fullWidth
              margin="normal"
              inputProps={{ min: 100, step: 100 }}
            />
          </>
        );
        
      default:
        return null;
    }
  };
  
  // Pasos del proceso
  const steps = ['Configurar modelo', 'Entrenamiento y resultados'];
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!fileData || !preview) {
    return (
      <Alert severity="error">
        No se pudo cargar la información del archivo.
      </Alert>
    );
  }
  
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Entrenamiento de Modelo ML
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ my: 3 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {activeStep === 0 ? (
        <>
          <Grid container spacing={3}>
            {/* Información del archivo */}
            <Grid item xs={12}>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <ShowChart sx={{ mr: 1 }} />
                    <Typography variant="subtitle1">Información del Archivo</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        Nombre: <strong>{fileData.original_filename}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        Filas: <strong>{preview.rows_count}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        Columnas: <strong>{preview.columns?.length || 0}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        Estado: <Chip size="small" label={fileData.is_processed ? 'Procesado' : 'Sin procesar'} 
                                     color={fileData.is_processed ? 'success' : 'default'} />
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
            
            {/* Configuración básica del modelo */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Configuración Básica
                  </Typography>
                  
                  <TextField
                    label="Nombre del Modelo"
                    name="name"
                    value={modelConfig.name}
                    onChange={handleConfigChange}
                    fullWidth
                    margin="normal"
                  />
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="model-type-label">Tipo de Modelo</InputLabel>
                    <Select
                      labelId="model-type-label"
                      name="model_type"
                      value={modelConfig.model_type}
                      onChange={handleConfigChange}
                      label="Tipo de Modelo"
                    >
                      {MODEL_TYPES.map(model => (
                        <MenuItem key={model.value} value={model.value}>
                          {model.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="index-column-label">Columna de Índice (X)</InputLabel>
                    <Select
                      labelId="index-column-label"
                      name="index_column"
                      value={modelConfig.index_column}
                      onChange={handleConfigChange}
                      label="Columna de Índice (X)"
                    >
                      {preview.columns?.map(column => (
                        <MenuItem key={column} value={column}>
                          {column}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="target-column-label">Columna Objetivo (Y)</InputLabel>
                    <Select
                      labelId="target-column-label"
                      name="target_column"
                      value={modelConfig.target_column}
                      onChange={handleConfigChange}
                      label="Columna Objetivo (Y)"
                    >
                      {preview.columns?.map(column => (
                        <MenuItem key={column} value={column}>
                          {column}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Parámetros del modelo */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Parámetros del Modelo
                  </Typography>
                  
                  {renderModelParameters()}
                </CardContent>
              </Card>
            </Grid>
            
            {/* Vista previa de datos */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <ShowChart sx={{ mr: 1 }} />
                    <Typography variant="subtitle1">Vista Previa de Datos</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ overflow: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          {preview.columns?.map((column) => (
                            <th key={column} style={{ 
                              border: '1px solid #ddd', 
                              padding: '8px',
                              backgroundColor: '#f2f2f2',
                              backgroundColor: 
                                column === modelConfig.index_column ? 'rgba(33, 150, 243, 0.2)' : 
                                column === modelConfig.target_column ? 'rgba(76, 175, 80, 0.2)' : 
                                '#f2f2f2'
                            }}>
                              {column}
                              {column === modelConfig.index_column && ' (X)'}
                              {column === modelConfig.target_column && ' (Y)'}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {preview.preview_data?.map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            {preview.columns?.map((column) => (
                              <td key={column} style={{ 
                                border: '1px solid #ddd', 
                                padding: '8px',
                                textAlign: !isNaN(row[column]) ? 'right' : 'left',
                                backgroundColor: 
                                  column === modelConfig.index_column ? 'rgba(33, 150, 243, 0.05)' : 
                                  column === modelConfig.target_column ? 'rgba(76, 175, 80, 0.05)' : 
                                  'transparent'
                              }}>
                                {row[column] === null || row[column] === undefined ? 
                                  <span style={{ color: '#999' }}>NULL</span> : 
                                  String(row[column])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="contained"
              startIcon={training ? <CircularProgress size={20} /> : <ModelIcon />}
              onClick={handleTrainModel}
              disabled={training || !modelConfig.index_column || !modelConfig.target_column}
            >
              {training ? 'Entrenando...' : 'Entrenar Modelo'}
            </Button>
          </Box>
        </>
      ) : (
        // Resultados del entrenamiento
        <>
          {trainingResult?.training_status === 'pending' || trainingResult?.training_status === 'training' ? (
            <Card sx={{ mb: 3, p: 3 }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Entrenando Modelo...
                </Typography>
                
                <CircularProgress sx={{ my: 2 }} />
                
                <Typography variant="body2" color="textSecondary">
                  Este proceso puede tomar varios minutos dependiendo del tamaño de los datos
                  y la complejidad del modelo.
                </Typography>
                
                <LinearProgress sx={{ width: '100%', mt: 3 }} />
              </Box>
            </Card>
          ) : trainingResult?.training_status === 'completed' ? (
            <>
              <Box sx={{ mb: 3 }}>
                <Alert severity="success" icon={<CheckCircle />}>
                  ¡Entrenamiento completado exitosamente!
                </Alert>
              </Box>
              
              <Card variant="outlined" sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Métricas del Modelo
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        MAE: <strong>{trainingResult?.mae?.toFixed(4) || 'N/A'}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        MSE: <strong>{trainingResult?.mse?.toFixed(4) || 'N/A'}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        RMSE: <strong>{trainingResult?.rmse?.toFixed(4) || 'N/A'}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        R²: <strong>{trainingResult?.r2?.toFixed(4) || 'N/A'}</strong>
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={handleReset}
                  sx={{ mr: 1 }}
                >
                  Entrenar Otro Modelo
                </Button>
                
                <Button
                  variant="contained"
                  component="a"
                  href={`/models/${trainingResult.id}`}
                >
                  Ver Resultados y Predicciones
                </Button>
              </Box>
            </>
          ) : (
            <Alert severity="error">
              El entrenamiento del modelo falló. Por favor, intenta con diferentes parámetros.
            </Alert>
          )}
        </>
      )}
    </Paper>
  );
};

export default ModelTraining;