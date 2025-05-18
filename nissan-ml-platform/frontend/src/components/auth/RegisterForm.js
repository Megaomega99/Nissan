// frontend/src/components/auth/RegisterForm.js
import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Link,
  Grid,
  Alert,
  CircularProgress
} from '@mui/material';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { PersonAddOutlined } from '@mui/icons-material';

// Esquema de validación
const registerSchema = Yup.object().shape({
  username: Yup.string()
    .min(3, 'El nombre de usuario debe tener al menos 3 caracteres')
    .max(50, 'El nombre de usuario debe tener máximo 50 caracteres')
    .required('Nombre de usuario es requerido'),
  email: Yup.string()
    .email('Email inválido')
    .required('Email es requerido'),
  full_name: Yup.string()
    .min(2, 'El nombre completo debe tener al menos 2 caracteres'),
  password: Yup.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .matches(
      /(?=.*[A-Z])/,
      'La contraseña debe tener al menos una letra mayúscula'
    )
    .matches(
      /(?=.*\d)/,
      'La contraseña debe tener al menos un número'
    )
    .required('Contraseña es requerida'),
  passwordConfirm: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Las contraseñas deben coincidir')
    .required('Confirmación de contraseña es requerida'),
});

const RegisterForm = () => {
  const { register, login } = useAuth();
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  const handleRegister = async (values, { setSubmitting }) => {
    try {
      setError(null);
      
      // Eliminar confirmación de contraseña para enviar al servidor
      const { passwordConfirm, ...userData } = values;
      
      // Registrar nuevo usuario
      await register(userData);
      
      // Iniciar sesión automáticamente
      await login(values.email, values.password);
      
      // Redirigir al dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrar usuario');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <Container component="main" maxWidth="sm">
      <Paper 
        elevation={3}
        sx={{
          p: 4,
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mb: 3
          }}
        >
          <PersonAddOutlined sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
          <Typography component="h1" variant="h5">
            Crear Cuenta
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Formik
          initialValues={{ 
            username: '', 
            email: '', 
            full_name: '', 
            password: '', 
            passwordConfirm: '' 
          }}
          validationSchema={registerSchema}
          onSubmit={handleRegister}
        >
          {({ errors, touched, isSubmitting }) => (
            <Form>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Field
                    as={TextField}
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="username"
                    label="Nombre de usuario"
                    name="username"
                    autoComplete="username"
                    error={touched.username && Boolean(errors.username)}
                    helperText={touched.username && errors.username}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Field
                    as={TextField}
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="email"
                    label="Email"
                    name="email"
                    autoComplete="email"
                    error={touched.email && Boolean(errors.email)}
                    helperText={touched.email && errors.email}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Field
                    as={TextField}
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="full_name"
                    label="Nombre completo (opcional)"
                    name="full_name"
                    autoComplete="name"
                    error={touched.full_name && Boolean(errors.full_name)}
                    helperText={touched.full_name && errors.full_name}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Field
                    as={TextField}
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    name="password"
                    label="Contraseña"
                    type="password"
                    id="password"
                    autoComplete="new-password"
                    error={touched.password && Boolean(errors.password)}
                    helperText={touched.password && errors.password}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Field
                    as={TextField}
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    name="passwordConfirm"
                    label="Confirmar contraseña"
                    type="password"
                    id="passwordConfirm"
                    error={touched.passwordConfirm && Boolean(errors.passwordConfirm)}
                    helperText={touched.passwordConfirm && errors.passwordConfirm}
                  />
                </Grid>
              </Grid>
              
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <CircularProgress size={24} />
                ) : (
                  'Registrarse'
                )}
              </Button>
              
              <Grid container justifyContent="flex-end">
                <Grid item>
                  <Link component={RouterLink} to="/login" variant="body2">
                    ¿Ya tienes una cuenta? Inicia sesión
                  </Link>
                </Grid>
              </Grid>
            </Form>
          )}
        </Formik>
      </Paper>
    </Container>
  );
};

export default RegisterForm;