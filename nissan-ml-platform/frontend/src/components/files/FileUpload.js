// frontend/src/components/files/FileUpload.js
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Typography,
  Alert,
  LinearProgress
} from '@mui/material';
import { UploadFile, CloudUpload } from '@mui/icons-material';
import { fileService } from '../../services/api';

const FileUpload = ({ onFileUploaded }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const onDrop = useCallback(async (acceptedFiles) => {
    // Validar archivo CSV
    const file = acceptedFiles[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
      setError('Solo se permiten archivos CSV');
      return;
    }
    
    try {
      setError(null);
      setSuccess(false);
      setUploading(true);
      
      // Crear intervalo para simular progreso (ya que no podemos obtener progreso real)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);
      
      // Subir archivo
      const uploadedFile = await fileService.uploadFile(file);
      
      // Limpiar intervalo y completar progreso
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Mostrar mensaje de éxito
      setSuccess(true);
      
      // Notificar al componente padre
      if (onFileUploaded) {
        onFileUploaded(uploadedFile);
      }
      
      // Resetear estado después de un tiempo
      setTimeout(() => {
        setUploadProgress(0);
        setSuccess(false);
      }, 3000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al subir archivo');
    } finally {
      setUploading(false);
    }
  }, [onFileUploaded]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    disabled: uploading
  });
  
  return (
    <Paper 
      elevation={3}
      sx={{ p: 3, mb: 3 }}
    >
      <Typography variant="h6" gutterBottom>
        Subir Archivo CSV
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Archivo subido exitosamente
        </Alert>
      )}
      
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          borderRadius: 2,
          py: 3,
          px: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: uploading ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        
        <CloudUpload 
          sx={{ 
            fontSize: 48, 
            color: isDragActive ? 'primary.main' : 'text.secondary',
            mb: 2
          }} 
        />
        
        {uploading ? (
          <CircularProgress size={24} />
        ) : (
          <Typography align="center" color="textSecondary">
            {isDragActive
              ? "Suelta el archivo aquí"
              : "Arrastra un archivo CSV aquí, o haz clic para seleccionar"}
          </Typography>
        )}
        
        <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
          Solo archivos CSV
        </Typography>
      </Box>
      
      {uploadProgress > 0 && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={uploadProgress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2" color="textSecondary" align="right" sx={{ mt: 0.5 }}>
            {uploadProgress}%
          </Typography>
        </Box>
      )}
      
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          startIcon={<UploadFile />}
          onClick={() => document.querySelector('input').click()}
          disabled={uploading}
        >
          Seleccionar Archivo
        </Button>
      </Box>
    </Paper>
  );
};

export default FileUpload;