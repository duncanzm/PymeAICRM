// src/services/authService.ts
import axios from 'axios';

// URL base de la API - Debe ser configurable según el entorno
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Configuración de axios para incluir cookies en las solicitudes
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Importante para manejar cookies de sesión
});

// Interface para la respuesta de login
interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
  };
}

// Interface para los datos de login
interface LoginData {
  username: string; // El backend espera 'username', aunque es un email
  password: string;
}

// Interface para datos de registro
interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name?: string;
  organization_name: string;
}

// Servicio de autenticación
const authService = {
  // Función para iniciar sesión
  async login(data: LoginData): Promise<LoginResponse> {
    try {
        // Intentar login
        const formData = new FormData();
        formData.append('username', data.username);
        formData.append('password', data.password);
        
        const response = await api.post<LoginResponse>('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        });
        
        // Si llegamos aquí, el login fue exitoso
        if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        return response.data;
    } catch (error) {
        // Importante: simplemente re-lanzar el error sin hacer nada más
        throw error;
    }
    },
  
  // Función para registrar un nuevo usuario
  async register(userData: RegisterData): Promise<LoginResponse> {
    // Realizar la petición POST al endpoint de registro
    const response = await api.post<LoginResponse>('/auth/register', userData);
    
    // Guardar el token en localStorage
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },
  
  // Función para cerrar sesión
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // Redirigir a la página de login
    window.location.href = '/login';
  },
  
  // Función para obtener el token actual
  getToken(): string | null {
    return localStorage.getItem('token');
  },
  
  // Función para obtener el usuario actual
  getCurrentUser(): any {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },
  
  // Función para verificar si el usuario está autenticado
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
};

// Interceptor para añadir el token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Si el error es 401 (No autorizado), cerrar sesión
    if (error.response && error.response.status === 401) {
      authService.logout();
    }
    return Promise.reject(error);
  }
);

export default authService;