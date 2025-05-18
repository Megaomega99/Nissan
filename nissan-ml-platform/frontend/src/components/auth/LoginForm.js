// frontend/src/components/auth/LoginForm.js
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
import { LockOutlined } from '@mui/icons-material';

// Esquema de validación
const loginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Email inválido')
    .required('Email es requerido'),
  password: Yup.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .required('Contraseña es requerida'),
});

const LoginForm = () => {
  const { login, error: authError } = useAuth();
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  const handleLogin = async (values, { setSubmitting }) => {
    try {
      setError(null);
      await login(values.email, values.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <Container component="main" maxWidth="xs">
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
          <LockOutlined sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
          <Typography component="h1" variant="h5">
            Iniciar Sesión
          </Typography>
        </Box>
        
        {(error || authError) && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error || authError}
          </Alert>
        )}
        
        <Formik
          initialValues={{ email: '', password: '' }}
          validationSchema={loginSchema}
          onSubmit={handleLogin}
        >
          {({ errors, touched, isSubmitting }) => (
            <Form>
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
              
              <Field
                as={TextField}
                variant="outlined"
                margin="normal"
                fullWidth
                name="password"
                label="Contraseña"
                type="password"
                id="password"
                autoComplete="current-password"
                error={touched.password && Boolean(errors.password)}
                helperText={touched.password && errors.password}
              />
              
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
                  'Iniciar Sesión'
                )}
              </Button>
              
              <Grid container justifyContent="flex-end">
                <Grid item>
                  <Link component={RouterLink} to="/register" variant="body2">
                    ¿No tienes una cuenta? Regístrate
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

export default LoginForm;