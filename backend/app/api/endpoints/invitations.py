# backend/app/api/endpoints/invitations.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import json
from pydantic import BaseModel, EmailStr

from app.db.base import get_db
from app.models.user import User
from app.models.invitation import Invitation
from app.models.organization import Organization
from app.core.security import get_password_hash, create_access_token
from app.api.deps import get_current_user, get_current_admin
from app.services.email_service import EmailService

router = APIRouter()

# Modelos Pydantic
class InvitationCreate(BaseModel):
    email: EmailStr
    role: str
    custom_permissions: Optional[dict] = None

class InvitationResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime
    expires_at: datetime
    is_accepted: bool
    
    class Config:
        orm_mode = True

class InvitationAccept(BaseModel):
    token: str
    first_name: str
    last_name: str
    password: str

@router.post("/", response_model=InvitationResponse)
async def create_invitation(
    invitation_data: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Solo admin puede invitar
):
    """
    Crea una invitación para un nuevo miembro del equipo.
    """
    # Verificar si ya existe una invitación para este email
    existing_invitation = db.query(Invitation).filter(
        Invitation.organization_id == current_user.organization_id,
        Invitation.email == invitation_data.email,
        Invitation.is_accepted == False,
        Invitation.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una invitación activa para este email"
        )
    
    # Verificar si ya existe un usuario con este email en la organización
    existing_user = db.query(User).filter(
        User.email == invitation_data.email,
        User.organization_id == current_user.organization_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email en tu organización"
        )
    
    # Convertir permisos personalizados a JSON string si existen
    custom_permissions_str = None
    if invitation_data.custom_permissions:
        custom_permissions_str = json.dumps(invitation_data.custom_permissions)
    
    # Crear la invitación
    invitation = Invitation.create_invitation(
        organization_id=current_user.organization_id,
        invited_by_user_id=current_user.id,
        email=invitation_data.email,
        role=invitation_data.role,
        custom_permissions=custom_permissions_str
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # Obtener información para el correo
    organization = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    
    # Enviar correo electrónico de invitación
    await EmailService.send_invitation_email(
        background_tasks=background_tasks,
        email=invitation_data.email,
        token=invitation.token,
        inviter_name=f"{current_user.first_name} {current_user.last_name}",
        organization_name=organization.name,
        role=invitation_data.role
    )
    
    return invitation

@router.get("/", response_model=List[InvitationResponse])
async def list_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Solo admin puede ver invitaciones
):
    """
    Lista todas las invitaciones activas de la organización.
    """
    invitations = db.query(Invitation).filter(
        Invitation.organization_id == current_user.organization_id,
        Invitation.is_accepted == False,
        Invitation.expires_at > datetime.now(timezone.utc)
    ).all()
    
    return invitations

@router.delete("/{invitation_id}", response_model=InvitationResponse)
async def cancel_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Solo admin puede cancelar invitaciones
):
    """
    Cancela una invitación existente.
    """
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.organization_id == current_user.organization_id,
        Invitation.is_accepted == False
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )
    
    # Establecer fecha de expiración como ahora para invalidarla
    invitation.expires_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(invitation)
    
    return invitation

@router.post("/accept", response_model=dict)
async def accept_invitation(
    invitation_data: InvitationAccept,
    db: Session = Depends(get_db)
):
    """
    Acepta una invitación y crea un nuevo usuario.
    """
    # Buscar la invitación por token
    invitation = db.query(Invitation).filter(
        Invitation.token == invitation_data.token,
        Invitation.is_accepted == False,
        Invitation.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitación inválida o expirada"
        )
    
    # Verificar si ya existe un usuario con este email
    existing_user = db.query(User).filter(User.email == invitation.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Crear el usuario
    user = User(
        email=invitation.email,
        password_hash=get_password_hash(invitation_data.password),
        first_name=invitation_data.first_name,
        last_name=invitation_data.last_name,
        role=invitation.role,
        organization_id=invitation.organization_id
    )
    
    # Marcar la invitación como aceptada
    invitation.is_accepted = True
    
    # Guardar cambios
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generar token de acceso
    access_token = create_access_token(subject=user.id)
    
    return {
        "message": "Invitación aceptada correctamente",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
    }

@router.get("/verify/{token}")
async def verify_invitation(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verifica si una invitación es válida.
    """
    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.is_accepted == False,
        Invitation.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitación inválida o expirada"
        )
    
    # Obtener organización
    organization = db.query(Organization).filter(
        Organization.id == invitation.organization_id
    ).first()
    
    return {
        "valid": True,
        "email": invitation.email,
        "role": invitation.role,
        "organization_name": organization.name,
        "expires_at": invitation.expires_at
    }