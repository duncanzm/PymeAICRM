// frontend/src/services/api.ts
import axios from 'axios';

// Obtener la URL base de la API desde variables de entorno
// Si no existe, usar la URL de desarrollo por defecto
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Crear instancia de axios con configuración base
// Esto nos permite tener una configuración centralizada para todas las peticiones
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',  // Todas las peticiones serán en formato JSON por defecto
  },
});

// Interceptor para incluir el token en cada petición
// Este código se ejecuta automáticamente antes de cada petición HTTP
api.interceptors.request.use(
  (config) => {
    // Obtener el token de autenticación almacenado
    const token = localStorage.getItem('token');
    
    // Si existe un token, añadirlo al header de autorización
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Si hay un error al preparar la petición, rechazar la promesa
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
// Este código se ejecuta automáticamente después de cada respuesta
api.interceptors.response.use(
  (response) => response,  // Si la respuesta es exitosa, simplemente pasarla
  (error) => {
    // Si recibimos un error 401 (No autorizado)
    if (error.response?.status === 401) {
      // Significa que el token es inválido o expiró
      // Eliminar credenciales almacenadas
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirigir al usuario a la página de login
      window.location.href = '/login';
    }
    // Propagar el error para que los componentes puedan manejarlo
    return Promise.reject(error);
  }
);

export default api;