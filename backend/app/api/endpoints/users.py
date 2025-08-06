# backend/app/api/endpoints/users.py
"""
Endpoints relacionados con los usuarios:
- Obtener perfil de usuario
- Actualizar perfil
- Listar usuarios (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_admin

# Definir modelos Pydantic
from pydantic import BaseModel, EmailStr

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    organization_id: int
    
    class Config:
        orm_mode = True

# Crear router
router = APIRouter()

@router.get("/me", response_model=UserProfile)
def get_my_profile(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtiene el perfil del usuario autenticado.
    """
    return current_user

@router.get("/", response_model=List[UserProfile])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> List[User]:
    """
    Lista todos los usuarios de la organización del usuario autenticado.
    Solo accesible para administradores.
    """
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return users