# backend/app/models/opportunity.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Opportunity(Base):
    """
    Modelo para las oportunidades de venta.
    Representa una posible venta que avanza a través de las etapas de un pipeline.
    """
    __tablename__ = "opportunities"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)  # Puede ser null si no está asociado a un cliente
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Usuario asignado/propietario
    
    # Información básica
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    value = Column(Float, default=0.0)  # Valor estimado de la oportunidad
    currency = Column(String, default="USD")  # Moneda del valor
    
    # Información adicional
    source = Column(String, nullable=True)  # Origen de la oportunidad (referencia, web, etc.)
    custom_fields = Column(JSON, nullable=True)  # Campos personalizados
    
    # Estado y fechas
    status = Column(String, default="open")  # open, won, lost
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_stage_change = Column(DateTime, nullable=True)  # Última vez que cambió de etapa
    expected_close_date = Column(DateTime, nullable=True)  # Fecha estimada de cierre
    
    # Relaciones
    organization = relationship("Organization", back_populates="opportunities")
    pipeline = relationship("Pipeline", back_populates="opportunities")
    stage = relationship("PipelineStage", back_populates="opportunities")
    customer = relationship("Customer", back_populates="opportunities")
    user = relationship("User", back_populates="opportunities")
    stage_history = relationship("StageHistory", back_populates="opportunity", cascade="all, delete-orphan")