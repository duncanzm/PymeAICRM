# backend/app/api/endpoints/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel

from app.db.base import get_db
from app.models.user import User
from app.models.active_session import ActiveSession
from app.api.deps import get_current_user

router = APIRouter()

# Modelos Pydantic
class SessionResponse(BaseModel):
    id: int
    device_info: str = None
    ip_address: str = None
    last_activity: datetime
    created_at: datetime
    is_current: bool = False
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[SessionResponse])
async def get_active_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las sesiones activas del usuario.
    """
    # Obtener el token actual
    auth_header = request.headers.get("Authorization")
    current_token = auth_header.split("Bearer ")[1] if auth_header and "Bearer " in auth_header else None
    
    # Obtener todas las sesiones activas
    sessions = db.query(ActiveSession).filter(
        ActiveSession.user_id == current_user.id,
        ActiveSession.is_active == True,
        ActiveSession.expires_at > datetime.now(timezone.utc)
    ).all()
    
    # Marcar la sesión actual
    session_responses = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "last_activity": session.last_activity,
            "created_at": session.created_at,
            "is_current": (session.token == current_token)
        }
        session_responses.append(session_dict)
    
    return session_responses

# IMPORTANTE: Las rutas específicas deben definirse antes que las rutas con parámetros
# para evitar que las rutas con parámetros capturen las rutas específicas

@router.delete("/all", summary="Revoca todas las sesiones")
async def revoke_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoca todas las sesiones, incluida la actual.
    """
    # Actualizar todas las sesiones
    db.query(ActiveSession).filter(
        ActiveSession.user_id == current_user.id,
        ActiveSession.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    return {"message": "Todas las sesiones han sido cerradas, deberá iniciar sesión nuevamente"}

@router.delete("/all/except-current", summary="Revoca todas las sesiones excepto la actual")
async def revoke_all_except_current(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoca todas las sesiones excepto la actual.
    """
    # Obtener el token actual
    auth_header = request.headers.get("Authorization")
    current_token = auth_header.split("Bearer ")[1] if auth_header and "Bearer " in auth_header else None
    
    if not current_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo identificar la sesión actual"
        )
    
    # Actualizar todas las sesiones excepto la actual
    db.query(ActiveSession).filter(
        ActiveSession.user_id == current_user.id,
        ActiveSession.token != current_token,
        ActiveSession.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    return {"message": "Todas las demás sesiones han sido cerradas"}

# Esta ruta debe definirse DESPUÉS de las rutas específicas "/all" y "/all/except-current"
@router.delete("/{session_id}", summary="Revoca una sesión específica")
async def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoca una sesión específica.
    """
    # Buscar la sesión
    session = db.query(ActiveSession).filter(
        ActiveSession.id == session_id,
        ActiveSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    # Desactivar la sesión
    session.is_active = False
    db.commit()
    
    return {"message": "Sesión cerrada correctamente"}