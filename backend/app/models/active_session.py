# backend/app/models/active_session.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
import secrets
from app.db.base import Base

class ActiveSession(Base):
    """
    Modelo para rastrear sesiones activas de usuarios.
    """
    __tablename__ = "active_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    device_info = Column(String, nullable=True)  # Información sobre el dispositivo
    ip_address = Column(String, nullable=True)  # Dirección IP
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    @classmethod
    def create_session(cls, user_id, token, device_info=None, ip_address=None, expires_in_days=30):
        """
        Crea una nueva sesión activa.
        
        Args:
            user_id: ID del usuario
            token: Token JWT generado
            device_info: Información del dispositivo (opcional)
            ip_address: Dirección IP (opcional)
            expires_in_days: Días hasta la expiración del token
            
        Returns:
            Instancia de ActiveSession
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        return cls(
            user_id=user_id,
            token=token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at
        )