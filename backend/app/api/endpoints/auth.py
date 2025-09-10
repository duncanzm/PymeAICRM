# backend/app/api/endpoints/auth.py (actualizar o añadir a este archivo)

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Any, Optional
from pydantic import BaseModel, EmailStr
import secrets
import hashlib
from jose import jwt

from app.core.config import settings
from app.db.base import get_db
from app.core import security
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.email import send_reset_password_email

router = APIRouter()

# Modelos de Pydantic para la solicitud y respuesta
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class TokenValidateRequest(BaseModel):
    token: str

class MessageResponse(BaseModel):
    detail: str

# Endpoint para solicitar restablecimiento de contraseña
@router.post("/forgot-password", response_model=MessageResponse)
def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Solicita un token para restablecer la contraseña
    """
    # Verificar si el usuario existe
    user = db.query(User).filter(User.email == request.email).first()
    
    # Aunque el usuario no exista, devolver mensaje éxito para evitar enumeración de usuarios
    if not user:
        return {"detail": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."}
    
    # Generar token único de restablecimiento
    reset_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
    
    # Guardar token en la base de datos (o en un modelo PasswordReset si lo tienes)
    user.reset_token = token_hash
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)  # Expira en 24 horas
    db.commit()
    
    # Enviar correo en segundo plano
    # Nota: Necesitarás crear esta función en app/utils/email.py
    frontend_url = settings.FRONTEND_URL  # Define esto en tu configuración
    reset_url = f"{frontend_url}/reset-password/{reset_token}"
    background_tasks.add_task(
        send_reset_password_email,
        email_to=user.email,
        username=user.first_name,
        reset_url=reset_url
    )
    
    return {"detail": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."}

# Endpoint para validar un token de restablecimiento
@router.post("/validate-reset-token", response_model=MessageResponse)
def validate_reset_token(
    request: TokenValidateRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Valida si un token de restablecimiento es válido
    """
    # Calcular hash del token recibido
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    
    # Buscar usuario con ese token
    user = db.query(User).filter(
        User.reset_token == token_hash,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    return {"detail": "Token válido"}

# Endpoint para restablecer la contraseña
@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    request: PasswordReset,
    db: Session = Depends(get_db)
) -> Any:
    """
    Restablece la contraseña de un usuario usando un token válido
    """
    # Calcular hash del token recibido
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    
    # Buscar usuario con ese token
    user = db.query(User).filter(
        User.reset_token == token_hash,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    # Validar requisitos de la nueva contraseña
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Actualizar contraseña
    user.hashed_password = get_password_hash(request.new_password)
    
    # Invalidar el token de restablecimiento
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()
    
    return {"detail": "Contraseña restablecida correctamente"}