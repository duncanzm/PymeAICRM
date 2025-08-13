# backend/app/models/pipeline.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Pipeline(Base):
    """
    Modelo para los pipelines de ventas.
    Cada organización puede tener múltiples pipelines para diferentes procesos de venta.
    """
    __tablename__ = "pipelines"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Información básica
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, default="#3b82f6")  # Color para visualización (hex)
    
    # Metadatos
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Indica si es el pipeline por defecto
    
    # Relaciones
    organization = relationship("Organization", back_populates="pipelines")
    stages = relationship("PipelineStage", back_populates="pipeline", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="pipeline")