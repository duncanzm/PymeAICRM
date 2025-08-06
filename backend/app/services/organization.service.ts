// frontend/src/services/organization.service.ts
import api from './api';

// Definición de tipos para TypeScript

// Estructura de una organización (PYME)
export interface Organization {
  id: number;                 // ID único
  name: string;               // Nombre de la organización
  industry_type: string | null;  // Tipo de industria (puede ser null)
  subscription_plan: string;     // Plan de suscripción (free, basic, pro, etc.)
  created_at: string;            // Fecha de creación (formato ISO)
  settings: Record<string, any> | null;  // Configuraciones como objeto JSON (puede ser null)
}

// Datos necesarios para crear una organización
export interface CreateOrganizationData {
  name: string;              // Nombre (obligatorio)
  industry_type?: string;    // Tipo de industria (opcional)
  subscription_plan?: string; // Plan de suscripción (opcional)
}

// Datos para actualizar una organización (todos opcionales)
export interface UpdateOrganizationData {
  name?: string;
  industry_type?: string;
  subscription_plan?: string;
  settings?: Record<string, any>;
}

// Servicio para operaciones con organizaciones
// Este objeto contiene métodos para todas las operaciones relacionadas con organizaciones
const OrganizationService = {
  // Obtener todas las organizaciones (solo para usuarios admin)
  async getAll(): Promise<Organization[]> {
    const response = await api.get<Organization[]>('/organizations');
    return response.data;
  },
  
  // Obtener la organización del usuario actual
  async getMyOrganization(): Promise<Organization> {
    const response = await api.get<Organization>('/organizations/my-organization');
    return response.data;
  },
  
  // Crear una nueva organización
  async create(data: CreateOrganizationData): Promise<Organization> {
    const response = await api.post<Organization>('/organizations', data);
    return response.data;
  },
  
  // Actualizar la organización del usuario actual
  async updateMyOrganization(data: UpdateOrganizationData): Promise<Organization> {
    const response = await api.put<Organization>('/organizations/my-organization', data);
    return response.data;
  }
};

export default OrganizationService;