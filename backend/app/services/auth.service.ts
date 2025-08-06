// frontend/src/services/auth.service.ts
import api from './api';

// Definición de tipos para TypeScript
// Estas interfaces definen la estructura de los datos que manejamos

// Datos necesarios para iniciar sesión
export interface LoginCredentials {
  username: string;  // Email del usuario
  password: string;  // Contraseña
}

// Datos necesarios para registrar un nuevo usuario
export interface RegisterData {
  email: string;     // Email (obligatorio)
  password: string;  // Contraseña (obligatorio)
  first_name?: string;       // Nombre (opcional)
  last_name?: string;        // Apellido (opcional)
  organization_name?: string; // Nombre de nueva organización (opcional)
  organization_id?: number;   // ID de organización existente (opcional)
}

// Estructura de un usuario en el sistema
export interface User {
  id: number;         // ID único
  email: string;      // Email
  first_name: string | null;  // Nombre (puede ser null)
  last_name: string | null;   // Apellido (puede ser null)
  role: string;       // Rol (admin, user, etc.)
  organization_id: number;    // ID de su organización
  is_active: boolean; // Si está activo o no
  created_at: string; // Fecha de creación (formato ISO)
}

// Respuesta del servidor al iniciar sesión
export interface LoginResponse {
  access_token: string;  // Token JWT
  token_type: string;    // Tipo de token (siempre "bearer")
}

// Respuesta del servidor al registrarse (usuario + token)
export interface RegisterResponse extends User {
  access_token: string;
  token_type: string;
}

// Servicio para operaciones de autenticación
// Este objeto contiene métodos para todas las operaciones relacionadas con autenticación
const AuthService = {
  // Iniciar sesión
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // Para login se usa form-data (requisito de OAuth2)
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    // Hacer petición POST al endpoint de login
    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: {
        // Especificar el tipo de contenido apropiado para form-data
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // Guardar el token en localStorage para mantener la sesión
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },
  
  // Registrar nuevo usuario/organización
  async register(data: RegisterData): Promise<RegisterResponse> {
    // Hacer petición POST al endpoint de registro
    const response = await api.post<RegisterResponse>('/auth/register', data);
    
    // Guardar token y datos del usuario en localStorage
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    
    return response.data;
  },
  
  // Obtener usuario actual
  async getCurrentUser(): Promise<User> {
    // En una implementación real, habría un endpoint para esto
    // Por ahora, simplemente recuperamos los datos del localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      return JSON.parse(userData);
    }
    throw new Error('No hay usuario autenticado');
  },
  
  // Cerrar sesión
  logout(): void {
    // Eliminar datos de autenticación del localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  // Verificar si hay un usuario autenticado
  isAuthenticated(): boolean {
    // Simplemente verificamos si existe un token
    return !!localStorage.getItem('token');
  },
};

export default AuthService;