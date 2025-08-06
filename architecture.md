# Arquitectura PymeAI

## Visión General

PymeAI es una plataforma SaaS basada en inteligencia artificial diseñada específicamente para pequeñas y medianas empresas (PYMEs) en Costa Rica. La plataforma ayudará a estos negocios a optimizar sus ventas a través del análisis de datos, gestión inteligente de clientes (CRM), y automatización de marketing, todo presentado en una interfaz simple y localizada para el mercado costarricense.

## Flujo Principal del Sistema

### 1. Onboarding y Configuración
- El dueño de la PYME se registra en la plataforma
- Configura información básica de su negocio
- Personaliza campos para sus clientes según su industria
- Define las etapas de su pipeline de ventas

### 2. Gestión de Clientes (CRM)
- Registro manual de clientes o importación desde Excel/CSV
- Organización de clientes con campos personalizados
- Registro de interacciones con cada cliente
- Visualización del historial completo de cada cliente
- Segmentación automática (frecuentes/ocasionales/inactivos)

### 3. Gestión de Oportunidades (Pipelines)
- Creación de oportunidades asociadas a clientes
- Movimiento de oportunidades a través de las etapas del pipeline
- Seguimiento visual en formato Kanban
- Registro de actividades y notas en cada etapa
- Cálculo de probabilidades de cierre

### 4. Análisis de Datos
- Visualización de métricas clave en el dashboard
- Análisis de la efectividad del pipeline
- Identificación de segmentos de clientes
- Reportes de actividad y conversión
- Detección de clientes inactivos o en riesgo

### 5. Asistencia con IA (Kula)
- Consultas en lenguaje natural sobre los datos
- Asistencia para uso de la plataforma
- Sugerencias para mejorar la gestión de clientes
- Alertas sobre tendencias o cambios importantes

## Arquitectura General

PymeAI se implementará como una aplicación SaaS multi-tenancy siguiendo una arquitectura de capas:

1. **Capa de Datos**
   - Base de datos relacional para clientes, oportunidades, pipelines
   - Esquemas separados por cliente (multi-tenancy)
   - Modelo flexible para campos personalizados

2. **Capa de Aplicación**
   - API RESTful para comunicación frontend-backend
   - Servicios para funcionalidades específicas
   - Integración con OpenAI para el chatbot Kula

3. **Capa de Presentación**
   - Aplicación web responsive en React
   - Dashboard interactivo personalizable
   - Interfaz Kanban para pipelines
   - Interfaz conversacional para Kula

## Esquema de Base de Datos

### Enfoque Multi-tenancy
Implementaremos una estrategia de "schema-based multi-tenancy" donde cada cliente (PYME) tendrá su propio schema en PostgreSQL para asegurar la separación de datos.

### Tablas Principales

1. **Organizations**
   - organization_id (PK)
   - name
   - industry_type
   - subscription_plan
   - created_at
   - active_until
   - settings (JSONB)

2. **Users**
   - user_id (PK)
   - organization_id (FK)
   - email
   - password_hash
   - first_name
   - last_name
   - role
   - last_login
   - is_active

3. **Customers**
   - customer_id (PK)
   - organization_id (FK)
   - first_name
   - last_name
   - email
   - phone
   - address
   - created_at
   - updated_at
   - segment
   - last_interaction
   - custom_fields (JSONB)
   - status (active/inactive)
   - lifetime_value (calculado)

4. **CustomFields**
   - field_id (PK)
   - organization_id (FK)
   - entity_type (customer, opportunity)
   - field_name
   - field_type (text, number, date, dropdown)
   - is_required
   - options (para dropdown)
   - display_order

5. **Interactions**
   - interaction_id (PK)
   - customer_id (FK)
   - user_id (FK)
   - type (call, email, meeting, etc.)
   - date_time
   - notes
   - followup_date
   - outcome

6. **Pipelines**
   - pipeline_id (PK)
   - organization_id (FK)
   - name
   - description
   - is_active

7. **Stages**
   - stage_id (PK)
   - pipeline_id (FK)
   - name
   - order
   - color
   - probability
   - expected_duration_days

8. **Opportunities**
   - opportunity_id (PK)
   - pipeline_id (FK)
   - customer_id (FK)
   - user_id (FK - owner)
   - title
   - value
   - stage_id (FK)
   - status
   - created_at
   - last_stage_change
   - expected_close_date
   - custom_fields (JSONB)
   - description
   - source

9. **StageHistory**
   - history_id (PK)
   - opportunity_id (FK)
   - stage_id (FK)
   - user_id (FK)
   - changed_at
   - notes
   - time_in_stage

10. **AnalyticsData** (opcional - para datos precalculados)
    - data_id (PK)
    - organization_id (FK)
    - data_type (customer_segments, pipeline_performance)
    - period_start
    - period_end
    - data (JSONB)
    - created_at

## Diseño de la API

Siguiendo el estándar RESTful, la API se estructurará en los siguientes endpoints principales:

### Autenticación
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh-token
- POST /api/auth/forgot-password
- POST /api/auth/reset-password
- GET /api/auth/sessions
- DELETE /api/auth/sessions/:id

### Usuarios
- GET /api/users
- POST /api/users/invite
- GET /api/users/:id
- PUT /api/users/:id
- DELETE /api/users/:id
- PUT /api/users/:id/role

### Clientes
- GET /api/customers
- POST /api/customers
- GET /api/customers/:id
- PUT /api/customers/:id
- DELETE /api/customers/:id
- GET /api/customers/segments
- GET /api/customers/segments/:segment
- GET /api/customers/:id/interactions
- POST /api/customers/:id/interactions

### Campos personalizados
- GET /api/custom-fields
- POST /api/custom-fields
- PUT /api/custom-fields/:id
- DELETE /api/custom-fields/:id

### Pipelines
- GET /api/pipelines
- POST /api/pipelines
- GET /api/pipelines/:id
- PUT /api/pipelines/:id
- DELETE /api/pipelines/:id
- GET /api/pipelines/:id/stages
- POST /api/pipelines/:id/stages
- PUT /api/pipelines/:id/stages/:stage_id
- DELETE /api/pipelines/:id/stages/:stage_id

### Oportunidades
- GET /api/opportunities
- POST /api/opportunities
- GET /api/opportunities/:id
- PUT /api/opportunities/:id
- DELETE /api/opportunities/:id
- PUT /api/opportunities/:id/stage
- GET /api/opportunities/:id/history

### Análisis
- GET /api/analytics/dashboard
- GET /api/analytics/customers/segments
- GET /api/analytics/pipeline/performance
- GET /api/analytics/opportunities/conversion

### Chatbot Kula
- POST /api/kula/query
- GET /api/kula/conversations
- GET /api/kula/help/:topic

## Personalización por Tipo de Negocio

La personalización es una característica clave de PymeAI que permite adaptar la plataforma a diferentes tipos de negocios:

### Elementos Personalizables

1. **Campos de Clientes**
   - Campos específicos por industria
   - Tipos de datos variados (texto, número, fecha, selección)
   - Agrupación en secciones lógicas

2. **Pipelines y Etapas**
   - Etapas personalizadas según el proceso de ventas
   - Probabilidades y tiempos esperados por etapa
   - Actividades sugeridas por etapa

3. **Tipos de Interacciones**
   - Personalizables según el tipo de negocio
   - Campos específicos por tipo de interacción
   - Plantillas para notas y seguimientos

4. **Dashboard y KPIs**
   - Métricas relevantes por industria
   - Widgets configurables
   - Alertas personalizables

### Implementación Técnica

1. **Plantillas Predefinidas**
   - Configuraciones iniciales por industria
   - Carga automática al seleccionar tipo de negocio
   - Posibilidad de personalización posterior

2. **Sistema de Campos Dinámicos**
   - Uso de JSONB para almacenar campos personalizados
   - Validación por tipo de dato
   - Interfaz administrativa para gestión de campos

3. **Dashboard Configurable**
   - Componentes arrastrar y soltar
   - Guardado de configuraciones favoritas
   - Adaptación automática a los datos disponibles

## Elecciones Tecnológicas

### Backend
1. **Python + FastAPI**
   - FastAPI para API RESTful y documentación automática
   - Pydantic para validación de datos
   - SQLAlchemy como ORM
   - Alembic para migraciones
   - Asyncpg para conexiones asíncronas a PostgreSQL

2. **Seguridad**
   - JWT para autenticación
   - Passlib para hashing de contraseñas
   - CORS configurado para la aplicación web
   - Validación de entrada con Pydantic

### Frontend
1. **React.js + TypeScript**
   - React Router para navegación
   - Redux Toolkit para gestión de estado
   - React Query para manejo de datos del servidor
   - Formik + Yup para formularios y validación

2. **Componentes UI**
   - Tailwind CSS para estilos
   - React Beautiful DnD para la interfaz Kanban
   - Recharts para visualizaciones
   - React-Table para tablas de datos

### Base de Datos
1. **PostgreSQL**
   - Esquemas separados por cliente (multi-tenancy)
   - JSONB para campos dinámicos
   - Índices optimizados para consultas frecuentes
   - Triggers para actualizaciones automáticas

### Integración IA
1. **OpenAI**
   - API GPT-4 para el chatbot Kula
   - Fine-tuning con datos específicos de PYMEs
   - Prompt engineering para respuestas contextualizadas

2. **Análisis de Datos**
   - Scikit-learn para segmentación de clientes
   - Pandas para manipulación de datos
   - Cálculos de KPIs personalizados

### Infraestructura
1. **Contenedorización**
   - Docker para desarrollo y producción
   - Docker Compose para entorno de desarrollo

2. **CI/CD**
   - GitHub Actions para integración continua
   - Pruebas automatizadas antes de despliegue

## Secuencia de Desarrollo (MVP)

1. **Configuración Básica** (Sprint 1-2)
   - Registro e inicio de sesión
   - Gestión de usuarios y permisos
   - Configuración de la organización

2. **CRM Base** (Sprint 3-4)
   - Gestión de clientes
   - Campos personalizables
   - Registro de interacciones

3. **Pipeline de Oportunidades** (Sprint 5-6)
   - Creación de pipelines y etapas
   - Interfaz Kanban
   - Seguimiento de oportunidades

4. **Análisis y Chatbot** (Sprint 7-8)
   - Segmentación de clientes
   - Dashboard básico
   - Integración inicial de Kula

## Consideraciones para Fases Posteriores

1. **Integración con Sistemas Externos**
   - Conexión con sistemas de punto de venta
   - Importación automática de datos
   - APIs para integración con otras herramientas

2. **Módulo de Marketing**
   - Campañas automatizadas
   - Seguimiento de efectividad
   - Plantillas personalizables

3. **Análisis Avanzado**
   - Predicciones de ventas
   - Identificación de patrones complejos
   - Recomendaciones personalizadas
