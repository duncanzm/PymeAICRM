# backend/app/core/ai/kula_service.py
"""
Servicio principal para Kula, el asistente de IA de PymeAI.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from .openai_service import OpenAIService

class KulaService:
    """
    Servicio para manejar las interacciones con Kula.
    """
    def __init__(self, db: Session):
        """
        Inicializa el servicio con una conexión a la base de datos.
        """
        self.db = db
        self.openai_service = OpenAIService()
    
    async def process_query(
        self, 
        user: User, 
        query: str, 
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario y devuelve la respuesta de Kula.
        
        Args:
            user: El usuario que realiza la consulta
            query: La consulta del usuario
            conversation_id: ID de la conversación si es una continuación (opcional)
            
        Returns:
            Un diccionario con la respuesta y metadatos
        """
        # Obtener o crear conversación
        conversation = None
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            ).first()
        
        if not conversation:
            # Crear nueva conversación
            conversation = Conversation(
                user_id=user.id,
                organization_id=user.organization_id,
                title=self._generate_title(query)
            )
            self.db.add(conversation)
            self.db.flush()  # Para obtener el ID asignado
        
        # Obtener historial de mensajes para contexto
        messages_history = []
        if conversation_id:
            db_messages = self.db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at).all()
            
            messages_history = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]
        
        # Guardar mensaje del usuario
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=query
        )
        self.db.add(user_message)
        
        # Añadir contexto específico para PymeAI
        system_message = self._get_system_message(user)
        
        # Obtener respuesta de OpenAI
        response_text = await self.openai_service.generate_response(
            prompt=query,
            system_message=system_message,
            conversation_history=messages_history
        )
        
        # Guardar respuesta de Kula
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text
        )
        self.db.add(assistant_message)
        
        # Actualizar título de la conversación si es nueva
        if not conversation.title or conversation.title == "Nueva conversación":
            conversation.title = self._generate_title(query)
        
        # Actualizar fecha de última modificación
        conversation.updated_at = datetime.now()
        
        # Guardar cambios
        self.db.commit()
        
        # Devolver respuesta con metadatos
        return {
            "conversation_id": conversation.id,
            "message": response_text,
            "created_at": assistant_message.created_at.isoformat()
        }
    
    def get_conversations(self, user_id: int, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene las conversaciones del usuario.
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de conversaciones a devolver
            skip: Número de conversaciones a omitir (para paginación)
            
        Returns:
            Lista de conversaciones
        """
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_archived == False
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
        
        return [
            {
                "id": conv.id,
                "title": conv.title or "Nueva conversación",
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    
    def get_conversation_messages(self, conversation_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene los mensajes de una conversación.
        
        Args:
            conversation_id: ID de la conversación
            user_id: ID del usuario (para verificar acceso)
            
        Returns:
            Lista de mensajes
        """
        # Verificar que la conversación pertenece al usuario
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return []
        
        # Obtener mensajes
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    def archive_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Archiva una conversación.
        
        Args:
            conversation_id: ID de la conversación a archivar
            user_id: ID del usuario (para verificar acceso)
            
        Returns:
            True si se archivó correctamente, False en caso contrario
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return False
        
        conversation.is_archived = True
        self.db.commit()
        
        return True
    
    def _generate_title(self, query: str) -> str:
        """
        Genera un título para la conversación basado en la consulta.
        """
        # Simplemente usar los primeros 50 caracteres como título
        if len(query) > 50:
            return query[:47] + "..."
        return query
    
    def _get_system_message(self, user: User) -> str:
        """
        Crea un mensaje de sistema personalizado con contexto específico.
        """
        return (
            f"Eres Kula, el asistente de IA para PymeAI, una plataforma para pequeñas y medianas empresas en Costa Rica. "
            f"Estás hablando con {user.first_name} {user.last_name}, quien trabaja para {user.organization.name}. "
            f"Tu objetivo es ayudar a los usuarios a entender sus datos comerciales, responder preguntas sobre el sistema "
            f"y proporcionar recomendaciones para mejorar su negocio. "
            f"Cuando respondas preguntas sobre el sistema, debes mencionar que PymeAI incluye: "
            f"gestión de clientes (CRM), pipelines de ventas, análisis de datos y asistencia con IA. "
            f"Sé conciso, amigable y útil. Cuando no estés seguro de algo, admítelo claramente."
        )