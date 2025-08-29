// src/App.tsx
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box } from '@mui/material';
import Login from './pages/Login';
import Register from './pages/Register';
import authService from './services/authService';
import { getLoginError } from './utils/errorStorage';

// Componente para rutas protegidas
const ProtectedRoute = ({ children }: { children: React.ReactElement }) => {
  const location = useLocation();
  const isAuthenticated = authService.isAuthenticated();
  
  if (!isAuthenticated) {
    // Redirigir a login si no está autenticado
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
};

// Componente para rutas públicas (como login)
// Que solo debe ser accesible si NO está autenticado
const PublicRoute = ({ children }: { children: React.ReactElement }) => {
  const isAuthenticated = authService.isAuthenticated();
  const hasError = !!getLoginError(); // Verificar si hay un error guardado
  
  // Si está autenticado y no hay error, redirigir a dashboard
  if (isAuthenticated && !hasError) {
    return <Navigate to="/dashboard" replace />;
  }
  
  // Si no está autenticado o hay un error, mostrar el componente
  return children;
};

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <BrowserRouter>
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" />} />
          
          {/* Rutas protegidas - requieren autenticación */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <div>Dashboard (Implementar componente)</div>
              </ProtectedRoute>
            } 
          />
          
          {/* Ruta para 404 */}
          <Route path="*" element={<div>Página no encontrada</div>} />
        </Routes>
      </BrowserRouter>
    </Box>
  );
}

export default App;