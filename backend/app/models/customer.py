# backend/app/models/customer.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Date
from datetime import datetime, date, timedelta
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Customer(Base):
    """
    Modelo para los clientes de cada PYME.
    Almacena información de contacto y seguimiento de clientes.
    """
    __tablename__ = "customers"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Información básica
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    segment = Column(String, default="new")  # Posibles valores: new, active, at_risk, inactive, vip, frequent, high_value
    last_interaction = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active, inactive
    
    # Campos avanzados
    notes = Column(Text, nullable=True)  # Notas generales sobre el cliente
    custom_fields = Column(JSON, nullable=True)  # Campos personalizados según industria
    lifetime_value = Column(Float, default=0.0)  # Valor total de compras del cliente
    
    # Datos para segmentación
    first_purchase_date = Column(Date, nullable=True)
    last_purchase_date = Column(Date, nullable=True)
    purchase_count = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    average_purchase_value = Column(Float, default=0.0)
    purchase_frequency_days = Column(Float, nullable=True)  # Promedio de días entre compras
    days_since_last_purchase = Column(Integer, nullable=True)
    segment_updated_at = Column(DateTime, nullable=True)
    
    # Relaciones
    organization = relationship("Organization", back_populates="customers")
    interactions = relationship("Interaction", back_populates="customer", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="customer")