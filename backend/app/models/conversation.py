# backend/app/models/conversation.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Conversation(Base):
    """
    Modelo para las conversaciones con el chatbot Kula.
    """
    __tablename__ = "conversations"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Información básica
    title = Column(String, nullable=True)  # Título generado automáticamente basado en el contenido
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")
    organization = relationship("Organization", back_populates="conversations")