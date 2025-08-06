# backend/app/api/deps.py
"""
Dependencias para los endpoints de la API.
Incluye funciones para obtener el usuario autenticado y verificar permisos.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

# Esquema OAuth2 para obtener el token del header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que valida el token JWT y obtiene el usuario actual.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependencia que verifica que el usuario actual sea un administrador.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes privilegios"
        )
    
    return current_user