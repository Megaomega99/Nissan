// frontend/src/components/ml/ModelResults.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import { 
  ShowChart, 
  DownloadOutlined,
  Science,
  BarChart
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import { mlModelService, fileService } from '../../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ModelResults = ({ modelId }) => {
  // Estado para datos del modelo
  const [model, setModel] = useState(null);
  const [fileData, setFileData] = useState(null);
  const [predictions, setPredictions] = useState(null);
  
  // Estado para entrada de predicción
  const [predictionInput, setPredictionInput] = useState('');
  const [customPrediction, setCustomPrediction] = useState(null);
  
  // Estado para manejo de proceso
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState(null);
  
  // Cargar datos del modelo
  useEffect(() => {
    const loadModelData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Cargar información del modelo
        const modelInfo = await mlModelService.getModelById(modelId);
        setModel(modelInfo);
        
        // Cargar información del archivo asociado
        const fileInfo = await fileService.getFileById(modelInfo.file_id);
        setFileData(fileInfo);
        
        // Cargar predicciones
        const predictionData = await mlModelService.predict(modelId, {});
        setPredictions(predictionData);
        
      } catch (err) {
        setError(err.response?.data?.detail || 'Error al cargar datos del modelo');
      } finally {
        setLoading(false);
      }
    };
    
    if (modelId) {
      loadModelData();
    }
  }, [modelId]);
  
  // Realizar predicción personalizada
  const handlePredict = async () => {
    try {
      setPredicting(true);
      setError(null);
      
      // Validar entrada
      if (!predictionInput || isNaN(parseFloat(predictionInput))) {
        setError('Ingresa un valor numérico válido');
        setPredicting(false);
        return;
      }
      
      // Realizar predicción
      const result = await mlModelService.predict(modelId, {
        indices: [parseFloat(predictionInput)]
      });
      
      setCustomPrediction({
        index: parseFloat(predictionInput),
        prediction: result.predictions[0]
      });
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al realizar predicción');
    } finally {
      setPredicting(false);
    }
  };
  
  // Preparar datos para gráfica
  const prepareChartData = () => {
    if (!predictions) return null;
    
    // Datos originales
    const originalData = {
      labels: predictions.original.indices,
      datasets: [
        {
          label: 'Valores Reales',
          data: predictions.original.actual_values,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          pointRadius: 3,
          pointHoverRadius: 5,
          borderWidth: 2,
        },
        {
          label: 'Predicciones',
          data: predictions.original.predictions,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          pointRadius: 3,
          pointHoverRadius: 5,
          borderWidth: 2,
        }
      ]
    };
    
    // Datos de proyección
    const projectionData = {
      labels: [...predictions.original.indices, ...predictions.projection.indices],
      datasets: [
        {
          label: 'Valores Reales',
          data: [...predictions.original.actual_values, ...Array(predictions.projection.indices.length).fill(null)],
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          pointRadius: 3,
          pointHoverRadius: 5,
          borderWidth: 2,
        },
        {
          label: 'Predicciones & Proyecciones',
          data: [...predictions.original.predictions, ...predictions.projection.predictions],
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          pointRadius: 3,
          pointHoverRadius: 5,
          borderWidth: 2,
        }
      ]
    };
    
    return { original: originalData, projection: projectionData };
  };
  
  // Opciones para gráficas
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Predicciones del Modelo',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: model?.index_column || 'Índice',
        }
      },
      y: {
        title: {
          display: true,
          text: model?.target_column || 'Valor',
        }
      }
    }
  };
  
  // Formatear parámetros del modelo
  const formatModelParams = () => {
    if (!model?.parameters) return 'No disponible';
    
    return Object.entries(model.parameters).map(([key, value]) => (
      <div key={key}>
        <strong>{key}:</strong> {value.toString()}
      </div>
    ));
  };
  
  // Mapeo de tipos de modelos
  const modelTypeLabels = {
    'linear_regression': 'Regresión Lineal',
    'svr': 'Support Vector Regression (SVR)',
    'elasticnet': 'ElasticNet',
    'sgd': 'Stochastic Gradient Descent'
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!model) {
    return (
      <Alert severity="error">
        No se pudo cargar la información del modelo.
      </Alert>
    );
  }
  
  const chartData = prepareChartData();
  
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          {model.name}
        </Typography>
        
        <Chip
          label={modelTypeLabels[model.model_type] || model.model_type}
          color="primary"
          icon={<Science />}
        />
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Información del modelo */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Información del Modelo
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Archivo: <strong>{fileData?.original_filename || 'No disponible'}</strong>
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Columna índice: <strong>{model.index_column}</strong>
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Columna objetivo: <strong>{model.target_column}</strong>
                </Typography>
              </Box>
              
              <Typography variant="subtitle2" gutterBottom>
                Parámetros
              </Typography>
              
              <Box sx={{ pl: 2, borderLeft: '2px solid #eee', mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  {formatModelParams()}
                </Typography>
              </Box>
              
              <Typography variant="subtitle2" gutterBottom>
                Métricas
              </Typography>
              
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    MAE: <strong>{model.metrics?.mae?.toFixed(4) || 'N/A'}</strong>
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    MSE: <strong>{model.metrics?.mse?.toFixed(4) || 'N/A'}</strong>
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    RMSE: <strong>{model.metrics?.rmse?.toFixed(4) || 'N/A'}</strong>
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    R²: <strong>{model.metrics?.r2?.toFixed(4) || 'N/A'}</strong>
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
          
          {/* Predicción personalizada */}
          <Card variant="outlined" sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Realizar Predicción
              </Typography>
              
              <TextField
                label={`Valor para ${model.index_column}`}
                type="number"
                fullWidth
                margin="normal"
                value={predictionInput}
                onChange={(e) => setPredictionInput(e.target.value)}
                helperText="Ingresa un valor para predecir"
              />
              
              <Button
                variant="contained"
                onClick={handlePredict}
                disabled={predicting}
                startIcon={predicting ? <CircularProgress size={20} /> : <ShowChart />}
                sx={{ mt: 2 }}
                fullWidth
              >
                {predicting ? 'Prediciendo...' : 'Predecir'}
              </Button>
              
              {customPrediction && (
                <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Resultado de la Predicción
                  </Typography>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      Entrada ({model.index_column}):
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {customPrediction.index}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="textSecondary">
                      Predicción ({model.target_column}):
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {customPrediction.prediction.toFixed(4)}
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Gráficos */}
        <Grid item xs={12} md={8}>
          <Card variant="outlined">
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Visualización de Resultados
                </Typography>
                
                <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
                  <InputLabel id="chart-type-label">Mostrar</InputLabel>
                  <Select
                    labelId="chart-type-label"
                    id="chart-type"
                    label="Mostrar"
                    defaultValue="original"
                  >
                    <MenuItem value="original">Solo datos de prueba</MenuItem>
                    <MenuItem value="projection">Incluir proyección</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <Box sx={{ height: 400, position: 'relative' }}>
                {chartData ? (
                  <Line 
                    data={chartData.projection} 
                    options={chartOptions} 
                  />
                ) : (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                    <CircularProgress />
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
          
          {/* Tabla de resultados */}
          <Card variant="outlined" sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Resultados detallados
              </Typography>
              
              <TableContainer sx={{ maxHeight: 300 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Índice ({model.index_column})</TableCell>
                      <TableCell>Valor Real ({model.target_column})</TableCell>
                      <TableCell>Predicción</TableCell>
                      <TableCell>Error</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {predictions?.original.indices.map((index, i) => {
                      const actual = predictions.original.actual_values[i];
                      const prediction = predictions.original.predictions[i];
                      const error = Math.abs(actual - prediction);
                      
                      return (
                        <TableRow key={i}>
                          <TableCell>{index.toFixed(2)}</TableCell>
                          <TableCell>{actual.toFixed(4)}</TableCell>
                          <TableCell>{prediction.toFixed(4)}</TableCell>
                          <TableCell>{error.toFixed(4)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ModelResults;