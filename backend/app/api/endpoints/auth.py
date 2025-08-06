# backend/app/api/endpoints/auth.py
"""
Endpoints relacionados con la autenticación:
- Login
- Registro
- Recuperación de contraseña
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Dict
from pydantic import BaseModel, EmailStr

from app.db.base import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.models.organization import Organization
from app.models.active_session import ActiveSession

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
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
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
    
    # Obtener información del dispositivo y dirección IP
    device_info = request.headers.get("User-Agent") if request else None
    ip_address = request.client.host if request and request.client else None
    
    # Registrar la sesión activa
    session = ActiveSession.create_session(
        user_id=user.id,
        token=access_token,
        device_info=device_info,
        ip_address=ip_address
    )
    db.add(session)
    db.commit()
    
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
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Crear organización
    organization = Organization(
        name=user_data.organization_name,
        subscription_plan="free"
    )
    db.add(organization)
    db.flush()
    
    # Crear usuario administrador
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="admin",
        organization_id=organization.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Crear token de acceso
    access_token = create_access_token(subject=user.id)
    
    # Crear respuesta
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }