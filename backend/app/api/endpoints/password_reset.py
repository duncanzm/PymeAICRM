# backend/app/api/endpoints/password_reset.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db.base import get_db
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.core.security import get_password_hash
from app.services.email_service import EmailService

router = APIRouter()

# Modelos Pydantic para validación
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class PasswordResetResponse(BaseModel):
    message: str

@router.post("/request-reset", response_model=None)  # Cambiamos el tipo de respuesta para incluir campos adicionales
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Solicita un token para restablecer la contraseña.
    Envía un correo electrónico al usuario con un enlace.
    """
    # Buscar el usuario por email
    user = db.query(User).filter(User.email == request.email).first()
    
    # No revelar si el email existe o no por razones de seguridad
    if not user:
        return {"message": "Si el correo existe en nuestra base de datos, recibirás un enlace para restablecer tu contraseña."}
    
    # Crear nuevo token
    reset_token = PasswordReset.generate_token(user.id)
    
    # Guardar token en la base de datos
    db.add(reset_token)
    db.commit()
    
    # Enviar correo electrónico (esto podría no estar funcionando)
    await EmailService.send_password_reset_email(
        background_tasks=background_tasks,
        email=user.email,
        token=reset_token.token,
        username=user.first_name or "Usuario"
    )
    
    # Para propósitos de prueba, devolver el token directamente
    # En producción, esto NUNCA debería hacerse
    return {
        "message": "Si el correo existe en nuestra base de datos, recibirás un enlace para restablecer tu contraseña.",
        "debug_token": reset_token.token,  # Solo para pruebas en desarrollo
        "reset_link": f"http://localhost:3000/reset-password?token={reset_token.token}"
    }

@router.post("/verify-reset", response_model=PasswordResetResponse)
async def verify_password_reset(
    request: PasswordResetVerify,
    db: Session = Depends(get_db)
):
    """
    Verifica el token y establece una nueva contraseña.
    """
    # Validar que las contraseñas coincidan
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden"
        )
    
    # Verificar que la contraseña tenga al menos 8 caracteres
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Buscar el token
    token_record = db.query(PasswordReset).filter(
        PasswordReset.token == request.token,
        PasswordReset.used == False,
        PasswordReset.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    # Obtener el usuario
    user = db.query(User).filter(User.id == token_record.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar la contraseña
    user.password_hash = get_password_hash(request.new_password)
    
    # Marcar el token como usado
    token_record.used = True
    
    # Guardar cambios
    db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}