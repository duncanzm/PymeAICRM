# backend/app/models/stage_history.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class StageHistory(Base):
    """
    Modelo para el historial de cambios de etapa de una oportunidad.
    Registra cuándo una oportunidad se mueve de una etapa a otra.
    """
    __tablename__ = "stage_history"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    from_stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=True)  # Puede ser null si es la primera etapa
    to_stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Usuario que realizó el cambio
    
    # Información del cambio
    changed_at = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)  # Notas sobre el cambio
    time_in_stage = Column(Integer, nullable=True)  # Tiempo (en segundos) que estuvo en la etapa anterior
    
    # Relaciones
    opportunity = relationship("Opportunity", back_populates="stage_history")
    from_stage = relationship("PipelineStage", foreign_keys=[from_stage_id])
    to_stage = relationship("PipelineStage", foreign_keys=[to_stage_id])
    user = relationship("User")