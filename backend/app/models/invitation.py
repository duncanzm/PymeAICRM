# backend/app/models/invitation.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
import secrets
from app.db.base import Base

class Invitation(Base):
    """
    Modelo para invitaciones a nuevos miembros del equipo.
    """
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    invited_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False, default="user")  # admin, user, analyst, readonly
    custom_permissions = Column(String, nullable=True)  # JSON string con permisos personalizados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_accepted = Column(Boolean, default=False)
    
    @classmethod
    def create_invitation(cls, organization_id, invited_by_user_id, email, role="user", custom_permissions=None, expires_in_days=7):
        """
        Crea una nueva invitación.
        
        Args:
            organization_id: ID de la organización
            invited_by_user_id: ID del usuario que invita
            email: Email del invitado
            role: Rol asignado (default: user)
            custom_permissions: Permisos personalizados (opcional)
            expires_in_days: Días hasta la expiración de la invitación
            
        Returns:
            Instancia de Invitation
        """
        # Generar token único
        token = secrets.token_urlsafe(32)
        
        # Calcular fecha de expiración
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        return cls(
            organization_id=organization_id,
            invited_by_user_id=invited_by_user_id,
            email=email,
            token=token,
            role=role,
            custom_permissions=custom_permissions,
            expires_at=expires_at
        )