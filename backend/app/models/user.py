# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func  # Para funciones SQL como NOW()
from sqlalchemy.orm import relationship  # Para relaciones entre modelos
from app.db.base import Base  # Importamos la clase Base para heredar

class User(Base):
    """
    Modelo para los usuarios que acceden a la plataforma.
    Cada usuario pertenece a una organización y puede tener diferentes roles.
    """
    __tablename__ = "users"  # Nombre de la tabla en la base de datos
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)  # Clave primaria autoincremental
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)  # Clave foránea a organización
    email = Column(String, unique=True, index=True, nullable=False)  # Email único, indexado para búsquedas rápidas
    password_hash = Column(String, nullable=False)  # Hash de la contraseña (nunca guardar contraseñas en texto plano)
    first_name = Column(String, nullable=True)  # Nombre (opcional)
    last_name = Column(String, nullable=True)  # Apellido (opcional)
    role = Column(String, default="user")  # Rol: admin, user, etc. (por defecto: user)
    is_active = Column(Boolean, default=True)  # Indica si la cuenta está activa
    created_at = Column(DateTime, server_default=func.now())  # Fecha de creación (automática)
    
    # Relaciones con otros modelos
    # Un usuario pertenece a una organización (muchos a uno)
    organization = relationship("Organization", back_populates="users")