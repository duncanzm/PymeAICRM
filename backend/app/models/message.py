# backend/app/models/message.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Message(Base):
    """
    Modelo para los mensajes en una conversación con Kula.
    """
    __tablename__ = "messages"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Contenido
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    
    # Metadatos
    created_at = Column(DateTime, server_default=func.now())
    tokens = Column(Integer, nullable=True)  # Número de tokens utilizados
    meta_info = Column(JSON, nullable=True)  # Metadatos adicionales (entidades, acciones, etc.)
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")