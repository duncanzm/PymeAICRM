// frontend/src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import OrganizationService, { Organization } from '../services/organization.service';

const Dashboard: React.FC = () => {
  // Obtener estado de autenticación y usuario
  const { authState } = useAuth();
  
  // Estado para almacenar los datos de la organización
  const [organization, setOrganization] = useState<Organization | null>(null);
  
  // Estado para manejar carga y errores
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Efecto para cargar los datos de la organización al montar el componente
  useEffect(() => {
    const fetchOrganizationData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Llamar al servicio para obtener la organización del usuario actual
        const data = await OrganizationService.getMyOrganization();
        setOrganization(data);
      } catch (err: any) {
        console.error('Error al cargar datos de la organización:', err);
        setError(err.response?.data?.detail || 'Error al cargar los datos de la organización');
      } finally {
        setIsLoading(false);
      }
    };
    
    // Ejecutar la función si el usuario está autenticado
    if (authState.user) {
      fetchOrganizationData();
    }
  }, [authState.user]);
  
  // Renderizar estado de carga
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="spinner-border text-indigo-600" role="status">
            <span className="sr-only">Cargando...</span>
          </div>
          <p className="mt-2">Cargando datos...</p>
        </div>
      </div>
    );
  }
  
  // Renderizar mensaje de error
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative m-4" role="alert">
        <strong className="font-bold">Error:</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Encabezado de bienvenida */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Bienvenido, {authState.user?.first_name || 'Usuario'}
        </h1>
        <p className="text-gray-600 mt-1">
          Este es tu panel de control para gestionar {organization?.name || 'tu organización'}
        </p>
      </div>
      
      {/* Información de la organización */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Información de la Organización</h2>
        
        {organization ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Nombre</p>
              <p className="font-medium">{organization.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Tipo de Industria</p>
              <p className="font-medium">{organization.industry_type || 'No definido'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Plan de Suscripción</p>
              <p className="font-medium capitalize">{organization.subscription_plan}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Fecha de Creación</p>
              <p className="font-medium">
                {new Date(organization.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        ) : (
          <p>No se encontró información de la organización.</p>
        )}
      </div>
      
      {/* Módulos disponibles (tarjetas) */}
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Módulos Disponibles</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Tarjeta de Clientes */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-5">
            <div className="flex items-center">
              <div className="rounded-full bg-indigo-100 p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold">Gestión de Clientes</h3>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Registra, organiza y segmenta a tus clientes. Mantén un historial completo de interacciones.
            </p>
            <button className="mt-4 w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition-colors">
              Ir a Clientes
            </button>
          </div>
        </div>
        
        {/* Tarjeta de Oportunidades */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-5">
            <div className="flex items-center">
              <div className="rounded-full bg-green-100 p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold">Pipeline de Ventas</h3>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Gestiona tus oportunidades de venta a través de un pipeline personalizable en formato Kanban.
            </p>
            <button className="mt-4 w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition-colors">
              Ir a Oportunidades
            </button>
          </div>
        </div>
        
        {/* Tarjeta de Análisis */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-5">
            <div className="flex items-center">
              <div className="rounded-full bg-blue-100 p-3 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold">Análisis y Reportes</h3>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Visualiza métricas clave de tu negocio, identifica tendencias y toma decisiones informadas.
            </p>
            <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors">
              Ver Análisis
            </button>
          </div>
        </div>
      </div>
      
      {/* Sección de actividad reciente (ejemplo) */}
      <div className="bg-white shadow rounded-lg p-6 mt-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Actividad Reciente</h2>
        
        {/* Lista de actividades (datos de ejemplo) */}
        <div className="space-y-4">
          <div className="flex items-start">
            <div className="rounded-full bg-blue-100 p-2 mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Se agregó un nuevo cliente: María González</p>
              <p className="text-xs text-gray-500">Hace 2 horas</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="rounded-full bg-green-100 p-2 mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Oportunidad "Proyecto XYZ" avanzó a etapa de Negociación</p>
              <p className="text-xs text-gray-500">Ayer</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="rounded-full bg-yellow-100 p-2 mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Recordatorio: Seguimiento pendiente con cliente Carlos Pérez</p>
              <p className="text-xs text-gray-500">Hace 3 días</p>
            </div>
          </div>
        </div>
        
        {/* Botón para ver toda la actividad */}
        <button className="mt-4 text-indigo-600 hover:text-indigo-800 text-sm font-medium">
          Ver toda la actividad →
        </button>
      </div>
      
      {/* Sección Kula (chatbot IA) */}
      <div className="bg-white shadow rounded-lg p-6 mt-6">
        <div className="flex items-center mb-4">
          <div className="rounded-full bg-purple-100 p-2 mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-800">Kula - Tu Asistente IA</h2>
        </div>
        
        <p className="text-gray-600 mb-4">
          Kula puede ayudarte a analizar tus datos, responder preguntas sobre la plataforma y ofrecerte recomendaciones personalizadas.
        </p>
        
        {/* Ejemplos de preguntas para Kula */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Prueba preguntar a Kula:</p>
          <div className="space-y-2">
            <p className="text-sm text-purple-600 hover:text-purple-800 cursor-pointer">
              "¿Cuáles son mis clientes más activos este mes?"
            </p>
            <p className="text-sm text-purple-600 hover:text-purple-800 cursor-pointer">
              "Muéstrame un resumen de mis oportunidades de venta"
            </p>
            <p className="text-sm text-purple-600 hover:text-purple-800 cursor-pointer">
              "¿Cómo puedo crear un pipeline personalizado?"
            </p>
          </div>
        </div>
        
        {/* Botón para abrir Kula */}
        <button className="w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700 transition-colors">
          Hablar con Kula
        </button>
      </div>
    </div>
  );
};

export default Dashboard;