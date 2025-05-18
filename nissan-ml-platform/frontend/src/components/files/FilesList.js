// frontend/src/components/files/FilesList.js
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
  Alert
} from '@mui/material';
import {
  Delete,
  Visibility,
  Edit,
  BarChart,
  Add
} from '@mui/icons-material';
import { fileService } from '../../services/api';

// Función para formatear tamaño de archivo
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

const FilesList = ({ onFileSelected, onRefreshNeeded }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  
  // Cargar lista de archivos
  const loadFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filesData = await fileService.getFiles();
      setFiles(filesData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar archivos');
    } finally {
      setLoading(false);
    }
  };
  
  // Cargar archivos al montar el componente
  useEffect(() => {
    loadFiles();
  }, []);
  
  // Abrir diálogo de confirmación para eliminar
  const handleDeleteClick = (file) => {
    setFileToDelete(file);
    setDeleteDialogOpen(true);
  };
  
  // Cerrar diálogo de confirmación
  const handleCloseDialog = () => {
    setDeleteDialogOpen(false);
    setFileToDelete(null);
  };
  
  // Eliminar archivo
  const handleDeleteConfirm = async () => {
    if (!fileToDelete) return;
    
    try {
      setDeleting(true);
      await fileService.deleteFile(fileToDelete.id);
      
      // Actualizar lista de archivos
      setFiles(files.filter(file => file.id !== fileToDelete.id));
      
      // Notificar cambios si es necesario
      if (onRefreshNeeded) {
        onRefreshNeeded();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al eliminar archivo');
    } finally {
      setDeleting(false);
      handleCloseDialog();
    }
  };
  
  // Seleccionar archivo para trabajar
  const handleSelectFile = (file) => {
    if (onFileSelected) {
      onFileSelected(file);
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
          Mis Archivos CSV
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<Add />}
          component={RouterLink}
          to="/upload"
        >
          Subir Nuevo
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {files.length === 0 ? (
        <Typography align="center" color="textSecondary" sx={{ py: 4 }}>
          No hay archivos subidos. Sube un archivo CSV para comenzar.
        </Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Tamaño</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Fecha</TableCell>
                <TableCell align="center">Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {files.map((file) => (
                <TableRow key={file.id}>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {file.original_filename}
                    </Typography>
                  </TableCell>
                  <TableCell>{formatFileSize(file.file_size)}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={file.is_processed ? 'Procesado' : 'Sin procesar'}
                      color={file.is_processed ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{formatDate(file.created_at)}</TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                      <Tooltip title="Ver detalles">
                        <IconButton 
                          color="info"
                          component={RouterLink}
                          to={`/files/${file.id}`}
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Procesar datos">
                        <IconButton 
                          color="primary"
                          onClick={() => handleSelectFile(file)}
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Analizar datos">
                        <IconButton 
                          color="secondary"
                          component={RouterLink}
                          to={`/files/${file.id}/analyze`}
                        >
                          <BarChart fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Eliminar">
                        <IconButton 
                          color="error"
                          onClick={() => handleDeleteClick(file)}
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
            ¿Estás seguro de que deseas eliminar el archivo 
            <strong>{fileToDelete?.original_filename}</strong>?
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

export default FilesList;