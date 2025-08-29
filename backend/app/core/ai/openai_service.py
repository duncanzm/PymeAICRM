# backend/app/core/ai/openai_service.py
"""
Servicio para interactuar con la API de OpenAI.
"""
from typing import List, Dict, Any, Optional
from .openai_config import OpenAIConfig

class OpenAIService:
    """
    Servicio para interactuar con la API de OpenAI.
    """
    def __init__(self):
        """
        Inicializa el servicio con la configuración de OpenAI.
        """
        config = OpenAIConfig.get_config()
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.temperature = config["temperature"]
        self.max_tokens = config["max_tokens"]
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Genera una respuesta simulada (para pruebas sin API KEY).
        
        Args:
            prompt: El mensaje del usuario
            system_message: Instrucciones para el modelo (opcional)
            conversation_history: Historial de conversación anterior (opcional)
            
        Returns:
            La respuesta simulada
        """
        # Si tenemos API KEY y queremos usar OpenAI, descomentar este código
        # y comentar el resto de la función
        # try:
        #     openai.api_key = self.api_key
        #     messages = []
        #     if system_message:
        #         messages.append({"role": "system", "content": system_message})
        #     if conversation_history:
        #         messages.extend(conversation_history)
        #     messages.append({"role": "user", "content": prompt})
        #     
        #     response = await openai.ChatCompletion.acreate(
        #         model=self.model,
        #         messages=messages,
        #         temperature=self.temperature,
        #         max_tokens=self.max_tokens
        #     )
        #     return response.choices[0].message["content"]
        # except Exception as e:
        #     print(f"Error al llamar a la API de OpenAI: {e}")
        #     return f"Lo siento, tuve un problema al procesar tu solicitud. Error: {str(e)}"
        
        # Simulamos diferentes respuestas según la consulta del usuario
        prompt_lower = prompt.lower()
        
        if "hola" in prompt_lower or "saludos" in prompt_lower:
            return "¡Hola! Soy Kula, tu asistente de PymeAI. ¿En qué puedo ayudarte hoy?"
            
        elif "qué es pymeai" in prompt_lower or "explicarme pymeai" in prompt_lower:
            return (
                "PymeAI es una plataforma SaaS basada en inteligencia artificial diseñada específicamente para "
                "pequeñas y medianas empresas (PYMEs) en Costa Rica. La plataforma ayuda a estos negocios a "
                "optimizar sus ventas a través del análisis de datos, gestión inteligente de clientes (CRM), "
                "y automatización de marketing, todo presentado en una interfaz simple y localizada para el "
                "mercado costarricense."
            )
            
        elif "módulos" in prompt_lower or "funcionalidades" in prompt_lower:
            return (
                "PymeAI incluye varios módulos clave:\n\n"
                "1. CRM Inteligente: Para gestionar clientes, segmentarlos automáticamente y realizar seguimiento de interacciones.\n"
                "2. Pipeline de Ventas: Gestión visual de oportunidades comerciales con etapas personalizables.\n"
                "3. Análisis de Datos: Visualización de tendencias, productos más vendidos y comportamiento de clientes.\n"
                "4. Dashboard: Panel central con métricas clave del negocio en tiempo real.\n"
                "5. Kula (IA): Asistente inteligente que responde consultas y proporciona recomendaciones."
            )
            
        elif "clientes" in prompt_lower or "crm" in prompt_lower:
            return (
                "La función de gestión de clientes (CRM) en PymeAI te permite:\n\n"
                "- Registrar clientes con campos personalizados según tu tipo de negocio\n"
                "- Segmentar automáticamente a tus clientes (frecuentes, ocasionales, inactivos)\n"
                "- Realizar seguimiento de todas las interacciones con cada cliente\n"
                "- Visualizar el historial completo de cada cliente\n"
                "- Recibir alertas sobre clientes inactivos o en riesgo\n\n"
                "Esto te ayuda a mantener relaciones sólidas con tus clientes y a identificar oportunidades de venta."
            )
            
        elif "pipeline" in prompt_lower or "oportunidades" in prompt_lower:
            return (
                "El módulo de Pipeline de Ventas de PymeAI te permite:\n\n"
                "- Crear pipelines personalizados según tu proceso de ventas\n"
                "- Visualizar y gestionar oportunidades en formato Kanban (arrastrar y soltar)\n"
                "- Definir etapas con probabilidades de cierre y tiempos estimados\n"
                "- Seguir el progreso de cada oportunidad\n"
                "- Analizar métricas de rendimiento del pipeline\n\n"
                "Esta función te ayuda a optimizar tu proceso de ventas y a cerrar más negocios."
            )
            
        elif "dashboard" in prompt_lower or "panel" in prompt_lower:
            return (
                "El Dashboard de PymeAI es un panel central que muestra métricas clave de tu negocio, incluyendo:\n\n"
                "- Número de clientes activos y su segmentación\n"
                "- Oportunidades abiertas y su valor total\n"
                "- Rendimiento de ventas comparado con períodos anteriores\n"
                "- Métricas de pipeline (conversión, tiempo promedio por etapa)\n"
                "- Tendencias de ventas\n\n"
                "Estas métricas te proporcionan una visión clara del estado actual de tu negocio para tomar decisiones informadas."
            )
            
        elif "ayuda" in prompt_lower or "asistencia" in prompt_lower:
            return (
                "Para obtener ayuda en PymeAI, puedes:\n\n"
                "1. Usar el chatbot Kula (¡como lo estás haciendo ahora!) para consultas generales\n"
                "2. Revisar los tooltips y guías dentro de cada sección\n"
                "3. Acceder a la documentación completa desde el menú de Ayuda\n"
                "4. Ver los videos tutoriales disponibles en cada módulo\n\n"
                "¿Hay algo específico sobre lo que necesites ayuda?"
            )
            
        else:
            return (
                "Gracias por tu consulta. Como parte del sistema PymeAI, estoy aquí para ayudarte con la gestión de "
                "clientes, análisis de ventas, seguimiento de oportunidades y más funcionalidades de la plataforma. "
                "¿Hay algo específico sobre PymeAI que te gustaría conocer? Puedes preguntarme sobre CRM, pipeline de ventas, "
                "dashboard, o cualquier otra característica del sistema."
            )