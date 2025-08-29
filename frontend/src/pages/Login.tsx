// src/pages/Login.tsx
import { useState, useEffect } from 'react';
import { 
  Container, Box, Paper, Typography, TextField, 
  Button, FormControlLabel, Checkbox, Link, Alert
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import authService from '../services/authService';
import { storeLoginError, getLoginError, clearLoginError } from '../utils/errorStorage';

const Login = () => {
  // Estados para formulario
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(getLoginError());
  
  const navigate = useNavigate();

  // Verifica si hay un error guardado cuando el componente se monta
  useEffect(() => {
    const savedError = getLoginError();
    if (savedError) {
      setError(savedError);
    }
  }, []);

  // Limpia el error cuando el usuario cambia los campos
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    
    // Limpiar el error cuando el usuario comienza a editar
    if (error) {
      clearLoginError();
      setError(null);
    }
    
    // Actualizar el campo correspondiente
    if (name === 'email') {
      setEmail(value);
    } else if (name === 'password') {
      setPassword(value);
    } else if (name === 'remember') {
      setRemember(checked);
    }
  };

  // Función para manejar el envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Intenta hacer login
      await authService.login({
        username: email,
        password
      });
      
      // Si llegamos aquí, el login fue exitoso
      clearLoginError(); // Limpia cualquier error anterior
      navigate('/dashboard');
    } catch (err: any) {
      console.log('Error durante login:', err);
      
      // Determina el mensaje de error
      let errorMessage = 'Error desconocido al intentar iniciar sesión';
      
      if (err.response) {
        // El servidor respondió con un error
        if (err.response.status === 401) {
          errorMessage = 'Credenciales incorrectas. Por favor, intenta de nuevo.';
        } else {
          errorMessage = `Error: ${err.response.data?.detail || 'No se pudo conectar con el servidor'}`;
        }
      } else if (err.request) {
        // No se recibió respuesta
        errorMessage = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.';
      }
      
      console.log('Guardando error:', errorMessage);
      
      // Guarda el error en sessionStorage y en el estado
      storeLoginError(errorMessage);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Verificar autenticación (dentro de useEffect para evitar redirecciones durante el render)
  useEffect(() => {
    // Importante: verificar autenticación con un pequeño retraso
    // para asegurar que el error se muestre primero
    const timer = setTimeout(() => {
      if (authService.isAuthenticated()) {
        navigate('/dashboard');
      }
    }, 100);
    
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <Container maxWidth="xs" sx={{ py: 8 }}>
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
          Iniciar Sesión
        </Typography>
        
        {/* Mostrar el error si existe */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 3 }}
            onClose={() => {
              clearLoginError();
              setError(null);
            }}
          >
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Correo electrónico"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={handleInputChange}
            error={!!error}
          />
          
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Contraseña"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={handleInputChange}
            error={!!error}
          />
          
          <Box sx={{ 
            mt: 2, 
            mb: 2,
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
          }}>
            <FormControlLabel
              control={
                <Checkbox 
                  name="remember"
                  color="primary" 
                  checked={remember}
                  onChange={handleInputChange}
                />
              }
              label="Recordarme"
            />
            
            <Link component={RouterLink} to="/forgot-password" variant="body2">
              ¿Olvidaste tu contraseña?
            </Link>
          </Box>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2, py: 1.5 }}
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </Button>
          
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2">
              ¿Nuevo en PymeAI?{' '}
              <Link component={RouterLink} to="/register" variant="body2">
                Crear una cuenta
              </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;