"""
Endpoints relacionados con la autenticación:
- Login
- Registro
- Recuperación de contraseña
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
import sqlalchemy
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr

from app.db.base import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.models.organization import Organization
from app.models.active_session import ActiveSession
from app.models.password_reset import PasswordReset
from app.services.email_service import EmailService
from app.core.config import settings

# Crear router
router = APIRouter()

# Definir modelos Pydantic para validar datos
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organization_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    
    class Config:
        from_attributes = True  # Actualizado de orm_mode=True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Modelos para recuperación de contraseña
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetToken(BaseModel):
    token: str
    new_password: str

class TokenValidateRequest(BaseModel):
    token: str

class MessageResponse(BaseModel):
    detail: str

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Endpoint de login OAuth2 compatible.
    Recibe username (email) y password, y devuelve un token JWT.
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verificar credenciales
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token = create_access_token(subject=user.id)
    
    # Registrar la sesión (con manejo de errores para tokens duplicados)
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Datos del cliente
            client_info = "python-requests/2.32.4"  # Para pruebas, podría obtenerse del User-Agent
            ip_address = "127.0.0.1"  # Para pruebas, podría obtenerse del request
            
            # Crear sesión activa
            active_session = ActiveSession(
                user_id=user.id,
                token=access_token,
                device_info=client_info,
                ip_address=ip_address,
                last_activity=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                is_active=True
            )
            
            db.add(active_session)
            db.commit()
            break  # Si tiene éxito, salir del bucle
            
        except sqlalchemy.exc.IntegrityError as e:
            # Si hay un error de duplicación de token
            db.rollback()
            
            if "duplicate key" in str(e) and attempt < max_attempts - 1:
                # Si es un error de clave duplicada y no es el último intento,
                # generar un nuevo token y reintentar
                access_token = create_access_token(subject=user.id)
            else:
                # Si es otro tipo de error o el último intento, continuar con el token
                # (el usuario podrá autenticarse, pero no se registrará la sesión)
                print(f"Warning: Could not register session after {attempt+1} attempts: {str(e)}")
                break
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=TokenResponse)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """
    Endpoint para registrar un nuevo usuario y organización.
    """
    # Verificar si el email ya está registrado
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear nueva organización
    organization = Organization(
        name=user_data.organization_name,
        is_active=True
    )
    db.add(organization)
    db.flush()  # Obtener el ID generado
    
    # Crear nuevo usuario
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        organization_id=organization.id,
        role="admin",  # El primer usuario es admin por defecto
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generar token de acceso
    access_token = create_access_token(subject=user.id)
    
    # Crear respuesta
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
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
    
    # Crear nuevo token utilizando el modelo PasswordReset existente
    reset_token = PasswordReset.generate_token(user.id)
    
    # Guardar token en la base de datos
    db.add(reset_token)
    db.commit()
    
    # Enviar correo en segundo plano usando el servicio existente
    await EmailService.send_password_reset_email(
        background_tasks=background_tasks,
        email=user.email,
        token=reset_token.token,
        username=user.first_name
    )
    
    # Para desarrollo, incluir el token en la respuesta
    return {
        "detail": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.",
        "debug_token": reset_token.token,  # Solo para pruebas en desarrollo
        "reset_link": f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
    }

@router.post("/validate-reset-token", response_model=MessageResponse)
def validate_reset_token(
    request: TokenValidateRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Valida si un token de restablecimiento es válido
    """
    # Buscar token en la base de datos
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
    
    return {"detail": "Token válido"}

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    request: PasswordResetToken,
    db: Session = Depends(get_db)
) -> Any:
    """
    Restablece la contraseña de un usuario usando un token válido
    """
    # Buscar token en la base de datos
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
    
    # Validar requisitos de la nueva contraseña
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Actualizar contraseña
    user.password_hash = get_password_hash(request.new_password)
    
    # Marcar el token como usado
    token_record.used = True
    
    # Guardar cambios
    db.commit()
    
    return {"detail": "Contraseña restablecida correctamente"}