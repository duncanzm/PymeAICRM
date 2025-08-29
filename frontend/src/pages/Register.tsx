// src/pages/Register.tsx
import { useState, useEffect } from 'react';
import { 
  Container, Box, Paper, Typography, TextField, 
  Button, Alert, Stack, Link
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import authService from '../services/authService';

const Register = () => {
  // Estados para el formulario
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    organization_name: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  
  // Verificar si el usuario ya está autenticado (con useEffect para evitar redirección antes del render)
  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [navigate]);
  
  // Manejar cambios en los campos
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Manejar envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Validación básica
    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Extraer datos para registro (excluyendo confirmPassword)
      const { confirmPassword, ...registerData } = formData;
      
      // Usar el servicio de autenticación para registrarse
      await authService.register(registerData);
      
      // La navegación ocurrirá automáticamente después del registro exitoso
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Error al registrarse:', err);
      // Manejar diferentes tipos de errores
      if (err.response) {
        setError(err.response.data?.detail || 'Error al registrarse');
      } else {
        setError(err.message || 'Error al conectar con el servidor');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography component="h1" variant="h4" color="primary" fontWeight="bold">
            PymeAI
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={1}>
            Optimización de ventas para PYMEs
          </Typography>
        </Box>
        
        <Typography component="h2" variant="h5" align="center" gutterBottom>
          Crear una cuenta
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
          <Stack spacing={2}>
            {/* Nombre y apellidos en una fila */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Box sx={{ flex: 1 }}>
                <TextField
                  required
                  fullWidth
                  label="Nombre"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </Box>
              <Box sx={{ flex: 1 }}>
                <TextField
                  fullWidth
                  label="Apellidos"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </Box>
            </Box>
            
            {/* Campos que ocupan ancho completo */}
            <TextField
              required
              fullWidth
              label="Nombre de la empresa"
              name="organization_name"
              value={formData.organization_name}
              onChange={handleChange}
            />
            
            <TextField
              required
              fullWidth
              label="Correo electrónico"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
            />
            
            <TextField
              required
              fullWidth
              label="Contraseña"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
            />
            
            <TextField
              required
              fullWidth
              label="Confirmar contraseña"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </Stack>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2, py: 1.5 }}
          >
            {isLoading ? 'Creando cuenta...' : 'Registrarse'}
          </Button>
          
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2">
              ¿Ya tienes una cuenta?{' '}
              <Link component={RouterLink} to="/login" variant="body2">
                Iniciar sesión
              </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;