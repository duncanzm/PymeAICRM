// frontend/src/context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AuthService, { User, LoginCredentials, RegisterData } from '../services/auth.service';

// Estado de autenticación - Define la estructura del estado que manejará el contexto
interface AuthState {
  user: User | null;          // Datos del usuario o null si no está autenticado
  token: string | null;       // Token JWT o null si no está autenticado
  isAuthenticated: boolean;   // Flag que indica si hay un usuario autenticado
  isLoading: boolean;         // Flag para mostrar estado de carga
  error: string | null;       // Mensaje de error si algo falla
}

// Propiedades del contexto - Define qué funcionalidades expone el contexto
interface AuthContextProps {
  authState: AuthState;                             // Estado actual
  login: (credentials: LoginCredentials) => Promise<void>;  // Función para iniciar sesión
  register: (data: RegisterData) => Promise<void>;          // Función para registrarse
  logout: () => void;                                       // Función para cerrar sesión
}

// Estado inicial - Valores por defecto cuando no hay usuario autenticado
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,  // Comienza en true porque verificamos localStorage al iniciar
  error: null,
};

// Crear contexto - Este es el contexto que se proveerá a los componentes
const AuthContext = createContext<AuthContextProps>({
  authState: initialState,
  login: async () => {},      // Funciones vacías por defecto
  register: async () => {},
  logout: () => {},
});

// Hook personalizado - Facilita el uso del contexto en componentes
export const useAuth = () => useContext(AuthContext);

// Proveedor del contexto - Componente que envuelve la aplicación y proporciona el contexto
export const AuthProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  // Estado local que se compartirá a través del contexto
  const [authState, setAuthState] = useState<AuthState>(initialState);
  
  // Efecto para inicializar el estado de autenticación al cargar la aplicación
  useEffect(() => {
    const initAuth = async () => {
      // Verificar si hay un token almacenado
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          // Intentar obtener el usuario actual usando el token
          const user = await AuthService.getCurrentUser();
          
          // Si todo va bien, establecer el estado de autenticación
          setAuthState({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          // Si hay un error (token inválido, etc.), limpiar todo
          console.error('Error al inicializar autenticación:', error);
          AuthService.logout();
          setAuthState({
            ...initialState,
            isLoading: false,
          });
        }
      } else {
        // Si no hay token, simplemente marcar como "no cargando"
        setAuthState({
          ...initialState,
          isLoading: false,
        });
      }
    };
    
    // Ejecutar la función de inicialización
    initAuth();
  }, []); // Array vacío = ejecutar solo una vez al montar el componente
  
  // Función para iniciar sesión
  const login = async (credentials: LoginCredentials) => {
    // Actualizar estado a "cargando"
    setAuthState((prevState) => ({
      ...prevState,
      isLoading: true,
      error: null,
    }));
    
    try {
      // Llamar al servicio de autenticación
      const response = await AuthService.login(credentials);
      
      // Obtener datos del usuario
      const user = await AuthService.getCurrentUser();
      
      // Actualizar estado con usuario autenticado
      setAuthState({
        user,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      // Manejar errores de autenticación
      setAuthState((prevState) => ({
        ...prevState,
        isLoading: false,
        error: error.response?.data?.detail || 'Error al iniciar sesión',
      }));
      
      // Re-lanzar el error para que los componentes puedan manejarlo
      throw error;
    }
  };
  
  // Función para registrar un nuevo usuario
  const register = async (data: RegisterData) => {
    // Actualizar estado a "cargando"
    setAuthState((prevState) => ({
      ...prevState,
      isLoading: true,
      error: null,
    }));
    
    try {
      // Llamar al servicio de registro
      const response = await AuthService.register(data);
      
      // Actualizar estado con el nuevo usuario
      setAuthState({
        user: response,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      // Manejar errores de registro
      setAuthState((prevState) => ({
        ...prevState,
        isLoading: false,
        error: error.response?.data?.detail || 'Error al registrarse',
      }));
      
      // Re-lanzar el error
      throw error;
    }
  };
  
  // Función para cerrar sesión
  const logout = () => {
    // Llamar al servicio para limpiar localStorage
    AuthService.logout();
    
    // Restablecer el estado a los valores iniciales
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  };
  
  // Valor del contexto que se proporcionará
  const contextValue: AuthContextProps = {
    authState,
    login,
    register,
    logout,
  };
  
  // Renderizar el Provider con el valor del contexto
  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;