// frontend/src/components/Navbar.tsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  // Estado para controlar el menú móvil
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  // Estado para controlar el menú desplegable de perfil
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  
  // Obtener funciones y estado del contexto de autenticación
  const { authState, logout } = useAuth();
  
  // Hook para navegación programática
  const navigate = useNavigate();
  
  // Función para manejar el cierre de sesión
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <nav className="bg-indigo-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo y enlaces principales */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/" className="text-white font-bold text-xl">
                PymeAI
              </Link>
            </div>
            
            {/* Enlaces de navegación en desktop */}
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {/* Mostrar estos enlaces solo si el usuario está autenticado */}
                {authState.isAuthenticated && (
                  <>
                    <Link 
                      to="/dashboard" 
                      className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Dashboard
                    </Link>
                    <Link 
                      to="/customers" 
                      className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Clientes
                    </Link>
                    <Link 
                      to="/opportunities" 
                      className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Oportunidades
                    </Link>
                  </>
                )}
                
                {/* Enlaces visibles para todos */}
                <Link 
                  to="/about" 
                  className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Acerca de
                </Link>
              </div>
            </div>
          </div>
          
          {/* Sección derecha: botones de acción/perfil */}
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              {/* Si el usuario NO está autenticado, mostrar botones de login/registro */}
              {!authState.isAuthenticated ? (
                <div className="flex space-x-4">
                  <Link 
                    to="/login" 
                    className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Iniciar Sesión
                  </Link>
                  <Link 
                    to="/register" 
                    className="bg-white text-indigo-600 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Registrarse
                  </Link>
                </div>
              ) : (
                // Si el usuario ESTÁ autenticado, mostrar menú de perfil
                <div className="relative ml-3">
                  <div>
                    <button
                      onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                      className="max-w-xs bg-indigo-600 rounded-full flex items-center text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-indigo-600 focus:ring-white"
                    >
                      <span className="sr-only">Abrir menú de usuario</span>
                      {/* Avatar/iniciales del usuario */}
                      <div className="h-8 w-8 rounded-full bg-indigo-800 flex items-center justify-center text-white">
                        {authState.user?.first_name?.[0] || authState.user?.email[0]}
                      </div>
                    </button>
                  </div>
                  
                  {/* Menú desplegable de perfil */}
                  {isProfileMenuOpen && (
                    <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
                      {/* Nombre del usuario */}
                      <div className="block px-4 py-2 text-sm text-gray-700 border-b">
                        <p className="font-medium">{authState.user?.first_name} {authState.user?.last_name}</p>
                        <p className="text-xs text-gray-500">{authState.user?.email}</p>
                      </div>
                      
                      {/* Enlaces del menú */}
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Mi Perfil
                      </Link>
                      <Link
                        to="/settings"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Configuración
                      </Link>
                      
                      {/* Opción de cerrar sesión */}
                      <button
                        onClick={handleLogout}
                        className="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Cerrar Sesión
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
          
          {/* Botón de menú móvil */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="bg-indigo-600 inline-flex items-center justify-center p-2 rounded-md text-white hover:text-white hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-indigo-600 focus:ring-white"
            >
              <span className="sr-only">Abrir menú principal</span>
              {/* Icono de menú (hamburguesa o X) */}
              {isMenuOpen ? (
                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
      
      {/* Menú móvil desplegable */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {/* Enlaces para usuarios autenticados */}
            {authState.isAuthenticated && (
              <>
                <Link
                  to="/dashboard"
                  className="text-white hover:bg-indigo-500 block px-3 py-2 rounded-md text-base font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  to="/customers"
                  className="text-white hover:bg-indigo-500 block px-3 py-2 rounded-md text-base font-medium"
                >
                  Clientes
                </Link>
                <Link
                  to="/opportunities"
                  className="text-white hover:bg-indigo-500 block px-3 py-2 rounded-md text-base font-medium"
                >
                  Oportunidades
                </Link>
              </>
            )}
            
            {/* Enlaces para todos */}
            <Link
              to="/about"
              className="text-white hover:bg-indigo-500 block px-3 py-2 rounded-md text-base font-medium"
            >
              Acerca de
            </Link>
            
            {/* Opciones de autenticación para móvil */}
            {!authState.isAuthenticated ? (
              <div className="pt-4 pb-3 border-t border-indigo-700">
                <Link
                  to="/login"
                  className="text-white hover:bg-indigo-500 block px-3 py-2 rounded-md text-base font-medium"
                >
                  Iniciar Sesión
                </Link>
                <Link
                  to="/register"
                  className="bg-white text-indigo-600 hover:bg-gray-100 block px-3 py-2 mt-1 rounded-md text-base font-medium"
                >
                  Registrarse
                </Link>
              </div>
            ) : (
              <div className="pt-4 pb-3 border-t border-indigo-700">
                <div className="flex items-center px-5">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-indigo-800 flex items-center justify-center text-white">
                      {authState.user?.first_name?.[0] || authState.user?.email[0]}
                    </div>
                  </div>
                  <div className="ml-3">
                    <div className="text-base font-medium leading-none text-white">
                      {authState.user?.first_name} {authState.user?.last_name}
                    </div>
                    <div className="text-sm font-medium leading-none text-indigo-300">
                      {authState.user?.email}
                    </div>
                  </div>
                </div>
                <div className="mt-3 px-2 space-y-1">
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-indigo-500"
                  >
                    Mi Perfil
                  </Link>
                  <Link
                    to="/settings"
                    className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-indigo-500"
                  >
                    Configuración
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-indigo-500"
                  >
                    Cerrar Sesión
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;