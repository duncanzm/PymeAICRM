// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import './index.css';

// Crear cliente de React Query para gestión de datos del servidor
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Configuraciones por defecto para todas las consultas
      refetchOnWindowFocus: false, // No recargar datos cuando la ventana recupera el foco
      retry: 1, // Intentar de nuevo una vez si falla
      staleTime: 5 * 60 * 1000, // Considerar datos "frescos" durante 5 minutos
    },
  },
});

// Renderizar la aplicación en el elemento root del HTML
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    {/* BrowserRouter: Proveedor para enrutamiento basado en navegador */}
    <BrowserRouter>
      {/* QueryClientProvider: Proveedor para React Query */}
      <QueryClientProvider client={queryClient}>
        {/* AuthProvider: Proveedor del contexto de autenticación */}
        <AuthProvider>
          {/* Componente principal de la aplicación */}
          <App />
        </AuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
);