# backend/app/models/pipeline_stage.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class PipelineStage(Base):
    """
    Modelo para las etapas de un pipeline de ventas.
    Cada pipeline tiene múltiples etapas por las que pasan las oportunidades.
    """
    __tablename__ = "pipeline_stages"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    
    # Información básica
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, default="#3b82f6")  # Color para visualización (hex)
    order = Column(Integer, nullable=False)  # Orden de la etapa en el pipeline
    
    # Configuración
    probability = Column(Float, default=0.0)  # Probabilidad de cierre en esta etapa (0-100%)
    expected_duration_days = Column(Integer, default=7)  # Duración esperada en días
    is_won = Column(Boolean, default=False)  # Indica si las oportunidades en esta etapa están ganadas
    is_lost = Column(Boolean, default=False)  # Indica si las oportunidades en esta etapa están perdidas
    
    # Relaciones
    pipeline = relationship("Pipeline", back_populates="stages")
    opportunities = relationship("Opportunity", back_populates="stage")