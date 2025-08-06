# backend/app/models/password_reset.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
import secrets
from app.db.base import Base

class PasswordReset(Base):
    """
    Modelo para almacenar tokens de restablecimiento de contraseña.
    """
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)  # Para marcar si ya fue utilizado
    
    @classmethod
    def generate_token(cls, user_id, expires_in_hours=24):
        """
        Genera un nuevo token de restablecimiento para un usuario.
        
        Args:
            user_id: ID del usuario
            expires_in_hours: Horas hasta la expiración del token
            
        Returns:
            Instancia de PasswordReset con el token generado
        """
        # Generar token aleatorio y seguro
        token = secrets.token_urlsafe(32)
        
        # Calcular fecha de expiración usando método compatible con timezone
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        
        # Crear instancia
        return cls(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )