# backend/app/api/endpoints/kula.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.db.base import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.core.ai.kula_service import KulaService
from app.core.ai.openai_config import OpenAIConfig

# Definir modelos Pydantic
class KulaQuery(BaseModel):
    query: str
    conversation_id: Optional[int] = None

class KulaResponse(BaseModel):
    conversation_id: int
    message: str
    created_at: str

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str

# Crear router
router = APIRouter()

# Verificar configuración de OpenAI
if not OpenAIConfig.validate():
    print("WARNING: OPENAI_API_KEY no está configurada. La funcionalidad de Kula estará limitada.")

@router.post("/query", response_model=KulaResponse)
async def query_kula(
    query_data: KulaQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Envía una consulta a Kula y obtiene una respuesta.
    """
    # Verificar configuración de OpenAI
    if not OpenAIConfig.validate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de Kula no está disponible actualmente. Contacte al administrador."
        )
    
    # Procesar consulta
    kula_service = KulaService(db)
    response = await kula_service.process_query(
        user=current_user,
        query=query_data.query,
        conversation_id=query_data.conversation_id
    )
    
    return response

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Obtiene las conversaciones del usuario actual.
    """
    kula_service = KulaService(db)
    conversations = kula_service.get_conversations(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return conversations

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los mensajes de una conversación específica.
    """
    kula_service = KulaService(db)
    messages = kula_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada o sin acceso"
        )
    
    return messages

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Archiva una conversación.
    """
    kula_service = KulaService(db)
    success = kula_service.archive_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada o sin acceso"
        )

@router.get("/help/{topic}", response_model=KulaResponse)
async def get_help(
    topic: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene ayuda sobre un tema específico.
    """
    # Verificar configuración de OpenAI
    if not OpenAIConfig.validate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de Kula no está disponible actualmente. Contacte al administrador."
        )
    
    # Crear una consulta formateada para obtener ayuda
    help_query = f"Por favor, explícame cómo funciona la función de {topic} en PymeAI"
    
    # Procesar consulta
    kula_service = KulaService(db)
    response = await kula_service.process_query(
        user=current_user,
        query=help_query
    )
    
    return response