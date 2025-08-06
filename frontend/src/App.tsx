// frontend/src/App.tsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Importar componentes de páginas
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Navbar from './components/Navbar';

// Componente para rutas protegidas (requieren autenticación)
const ProtectedRoute: React.FC<{element: React.ReactNode}> = ({ element }) => {
  const { authState } = useAuth();
  
  // Si está cargando, mostrar indicador de carga
  if (authState.isLoading) {
    return <div className="flex justify-center items-center h-screen">Cargando...</div>;
  }
  
  // Si no está autenticado, redirigir a login
  if (!authState.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // Si está autenticado, mostrar el componente
  return <>{element}</>;
};

// Componente principal de la aplicación
const App: React.FC = () => {
  const { authState } = useAuth();
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Barra de navegación siempre visible */}
      <Navbar />
      
      {/* Contenido principal */}
      <main>
        <Routes>
          {/* Ruta de inicio - redirige según estado de autenticación */}
          <Route 
            path="/" 
            element={
              authState.isAuthenticated 
                ? <Navigate to="/dashboard" replace /> 
                : <Navigate to="/login" replace />
            } 
          />
          
          {/* Rutas públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Rutas protegidas */}
          <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
          
          {/* Ruta para errores 404 */}
          <Route path="*" element={
            <div className="flex flex-col items-center justify-center min-h-screen">
              <h1 className="text-4xl font-bold text-indigo-600">404</h1>
              <p className="mt-2 text-lg">Página no encontrada</p>
            </div>
          } />
        </Routes>
      </main>
    </div>
  );
};

export default App;