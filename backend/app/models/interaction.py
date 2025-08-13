# backend/app/models/interaction.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Interaction(Base):
    """
    Modelo para las interacciones con clientes.
    Registra cada punto de contacto con un cliente (llamadas, correos, reuniones, etc.).
    """
    __tablename__ = "interactions"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información básica
    type = Column(String, nullable=False)  # Tipo: call, email, meeting, etc.
    date_time = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    duration_minutes = Column(Integer, nullable=True)  # Duración en minutos
    
    # Detalles
    notes = Column(Text, nullable=True)  # Notas sobre la interacción
    outcome = Column(String, nullable=True)  # Resultado: positive, neutral, negative
    
    # Seguimiento
    requires_followup = Column(Boolean, default=False)
    followup_date = Column(DateTime, nullable=True)
    followup_type = Column(String, nullable=True)
    followup_notes = Column(Text, nullable=True)
    followup_completed = Column(Boolean, default=False)
    followup_completed_date = Column(DateTime, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    customer = relationship("Customer", back_populates="interactions")
    user = relationship("User", back_populates="interactions")