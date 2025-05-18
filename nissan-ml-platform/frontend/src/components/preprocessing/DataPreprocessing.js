// frontend/src/components/preprocessing/DataPreprocessing.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  FormControl,
  FormControlLabel,
  FormGroup,
  Checkbox,
  TextField,
  MenuItem,
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
  AccordionDetails
} from '@mui/material';
import { 
  ExpandMore, 
  CleaningServices, 
  BarChart, 
  CheckCircle,
  Storage 
} from '@mui/icons-material';
import { fileService, preprocessingService } from '../../services/api';

// Opciones para rellenar valores nulos
const FILL_OPTIONS = [
  { value: 'mean', label: 'Media' },
  { value: 'median', label: 'Mediana' },
  { value: 'mode', label: 'Moda' },
  { value: 'zero', label: 'Cero' }
];

const DataPreprocessing = ({ fileId, onProcessingComplete }) => {
  // Estado para datos del archivo
  const [fileData, setFileData] = useState(null);
  const [preview, setPreview] = useState(null);
  
  // Estado para opciones de preprocesamiento
  const [options, setOptions] = useState({
    remove_nulls: true,
    fill_nulls: false,
    fill_method: 'mean',
    drop_duplicates: true,
    remove_outliers: false,
    columns_to_process: []
  });
  
  // Estado para selección de columnas
  const [selectedColumns, setSelectedColumns] = useState([]);
  
  // Estado para manejo de proceso
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [processingResult, setProcessingResult] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  
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
        
        // Inicializar columnas seleccionadas (todas por defecto)
        if (previewData && previewData.columns) {
          setSelectedColumns(previewData.columns);
          setOptions(prev => ({
            ...prev,
            columns_to_process: previewData.columns
          }));
        }
        
      } catch (err) {
        setError(err.response?.data?.detail || 'Error al cargar datos del archivo');
      } finally {
        setLoading(false);
      }
    };
    
    if (fileId) {
      loadFileData();
    }
  }, [fileId]);
  
  // Manejar cambios en opciones
  const handleOptionChange = (event) => {
    const { name, checked, value } = event.target;
    
    // Para checkboxes
    if (typeof checked !== 'undefined') {
      setOptions({ ...options, [name]: checked });
    }
    // Para selects u otros inputs
    else {
      setOptions({ ...options, [name]: value });
    }
  };
  
  // Manejar selección de columnas
  const handleColumnToggle = (columnName) => {
    const currentIndex = selectedColumns.indexOf(columnName);
    const newSelectedColumns = [...selectedColumns];
    
    if (currentIndex === -1) {
      newSelectedColumns.push(columnName);
    } else {
      newSelectedColumns.splice(currentIndex, 1);
    }
    
    setSelectedColumns(newSelectedColumns);
    setOptions({ ...options, columns_to_process: newSelectedColumns });
  };
  
  // Seleccionar todas o ninguna columna
  const handleSelectAllColumns = (select) => {
    if (select) {
      const allColumns = preview?.columns || [];
      setSelectedColumns(allColumns);
      setOptions({ ...options, columns_to_process: allColumns });
    } else {
      setSelectedColumns([]);
      setOptions({ ...options, columns_to_process: [] });
    }
  };
  
  // Procesar datos
  const handleProcessData = async () => {
    try {
      setProcessing(true);
      setError(null);
      
      // Enviar opciones de preprocesamiento
      const result = await preprocessingService.cleanData(fileId, options);
      
      // Actualizar estado con resultado
      setProcessingResult(result);
      
      // Avanzar al siguiente paso
      setActiveStep(1);
      
      // Notificar finalización si es necesario
      if (onProcessingComplete) {
        onProcessingComplete(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar datos');
    } finally {
      setProcessing(false);
    }
  };
  
  // Reiniciar proceso
  const handleReset = () => {
    setProcessingResult(null);
    setActiveStep(0);
  };
  
  // Pasos del proceso
  const steps = ['Configurar opciones', 'Resultados del procesamiento'];
  
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
        Preprocesamiento de Datos
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
                    <Storage sx={{ mr: 1 }} />
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
            
            {/* Opciones de limpieza */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Opciones de Limpieza
                  </Typography>
                  
                  <FormGroup>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={options.remove_nulls}
                          onChange={handleOptionChange}
                          name="remove_nulls"
                          color="primary"
                        />
                      }
                      label="Eliminar filas con valores nulos"
                    />
                    
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={options.fill_nulls}
                          onChange={handleOptionChange}
                          name="fill_nulls"
                          color="primary"
                        />
                      }
                      label="Rellenar valores nulos"
                    />
                    
                    {options.fill_nulls && (
                      <FormControl variant="outlined" size="small" sx={{ ml: 3, mb: 2, mt: 1 }}>
                        <TextField
                          select
                          label="Método de relleno"
                          name="fill_method"
                          value={options.fill_method}
                          onChange={handleOptionChange}
                          size="small"
                        >
                          {FILL_OPTIONS.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </TextField>
                      </FormControl>
                    )}
                    
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={options.drop_duplicates}
                          onChange={handleOptionChange}
                          name="drop_duplicates"
                          color="primary"
                        />
                      }
                      label="Eliminar filas duplicadas"
                    />
                    
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={options.remove_outliers}
                          onChange={handleOptionChange}
                          name="remove_outliers"
                          color="primary"
                        />
                      }
                      label="Eliminar valores atípicos (outliers)"
                    />
                  </FormGroup>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Selección de columnas */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1">
                      Columnas a Procesar
                    </Typography>
                    
                    <Box>
                      <Button 
                        size="small"
                        onClick={() => handleSelectAllColumns(true)}
                        sx={{ mr: 1 }}
                      >
                        Todas
                      </Button>
                      <Button 
                        size="small"
                        onClick={() => handleSelectAllColumns(false)}
                      >
                        Ninguna
                      </Button>
                    </Box>
                  </Box>
                  
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                    <List dense>
                      {preview.columns?.map((column) => (
                        <ListItem key={column} dense>
                          <FormControlLabel
                            control={
                              <Checkbox
                                edge="start"
                                checked={selectedColumns.indexOf(column) !== -1}
                                onChange={() => handleColumnToggle(column)}
                                tabIndex={-1}
                                disableRipple
                              />
                            }
                            label={
                              <ListItemText 
                                primary={column} 
                              />
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Vista previa de datos */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BarChart sx={{ mr: 1 }} />
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
                              backgroundColor: '#f2f2f2' 
                            }}>
                              {column}
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
                                textAlign: !isNaN(row[column]) ? 'right' : 'left'
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
              startIcon={processing ? <CircularProgress size={20} /> : <CleaningServices />}
              onClick={handleProcessData}
              disabled={processing || selectedColumns.length === 0}
            >
              {processing ? 'Procesando...' : 'Procesar Datos'}
            </Button>
          </Box>
        </>
      ) : (
        // Resultados del procesamiento
        <>
          <Box sx={{ mb: 3 }}>
            <Alert severity="success" icon={<CheckCircle />}>
              ¡Procesamiento completado exitosamente!
            </Alert>
          </Box>
          
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Estadísticas del Procesamiento
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    Filas originales: <strong>{processingResult?.original_rows || 0}</strong>
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    Filas procesadas: <strong>{processingResult?.processed_rows || 0}</strong>
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    Filas eliminadas: <strong>{processingResult?.removed_rows || 0}</strong>
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    Columnas: <strong>{processingResult?.processed_cols || 0}</strong>
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
          
          {/* Vista previa de datos procesados */}
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Vista Previa de Datos Procesados
              </Typography>
              
              <Box sx={{ overflow: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      {processingResult?.preview && processingResult.preview.length > 0 &&
                        Object.keys(processingResult.preview[0]).map((column) => (
                          <th key={column} style={{ 
                            border: '1px solid #ddd', 
                            padding: '8px',
                            backgroundColor: '#f2f2f2' 
                          }}>
                            {column}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody>
                    {processingResult?.preview?.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {Object.entries(row).map(([column, value]) => (
                          <td key={column} style={{ 
                            border: '1px solid #ddd', 
                            padding: '8px',
                            textAlign: !isNaN(value) ? 'right' : 'left'
                          }}>
                            {value === null || value === undefined ? 
                              <span style={{ color: '#999' }}>NULL</span> : 
                              String(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            </CardContent>
          </Card>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="outlined"
              onClick={handleReset}
              sx={{ mr: 1 }}
            >
              Volver a Opciones
            </Button>
            
            <Button
              variant="contained"
              component="a"
              href={`/files/${fileId}/models`}
            >
              Continuar a Modelos ML
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default DataPreprocessing;