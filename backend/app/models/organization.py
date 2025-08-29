# backend/app/models/organization.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func  # Para funciones SQL como NOW()
from sqlalchemy.orm import relationship  # Para relaciones entre modelos
from app.db.base import Base  # Importamos la clase Base para heredar

class Organization(Base):
    """
    Modelo para las organizaciones (PYMEs) que utilizan la plataforma.
    Cada organización tendrá sus propios usuarios, clientes, etc.
    """
    __tablename__ = "organizations"  # Nombre de la tabla en la base de datos
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)  # Clave primaria autoincremental
    name = Column(String, nullable=False)  # Nombre de la organización (obligatorio)
    industry_type = Column(String, nullable=True)  # Tipo de industria (opcional)
    subscription_plan = Column(String, default="free")  # Plan de suscripción (por defecto: free)
    created_at = Column(DateTime, server_default=func.now())  # Fecha de creación (automática)
    active_until = Column(DateTime, nullable=True)  # Fecha de fin de suscripción (opcional)
    settings = Column(JSON, nullable=True)  # Configuraciones personalizadas en formato JSON
    
    # Relaciones con otros modelos (uno a muchos)
    # Una organización tiene muchos usuarios
    users = relationship("User", back_populates="organization")
    customers = relationship("Customer", back_populates="organization")
    pipelines = relationship("Pipeline", back_populates="organization")
    opportunities = relationship("Opportunity", back_populates="organization")
    conversations = relationship("Conversation", back_populates="organization")