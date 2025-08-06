# backend/app/api/api.py
"""
Configuración central de todos los routers de la API.
"""

from fastapi import APIRouter

# Importar los diferentes routers de endpoints
from app.api.endpoints import auth, users, customers, password_reset, sessions, invitations

# Crear el router principal
api_router = APIRouter()

# Incluir los diferentes routers con sus prefijos y etiquetas
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(password_reset.router, prefix="/password-reset", tags=["password-reset"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])