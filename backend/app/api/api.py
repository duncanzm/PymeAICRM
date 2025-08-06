# backend/app/api/api.py
"""
Configuración central de todos los routers de la API.
"""

from fastapi import APIRouter

# Importar los diferentes routers de endpoints
from app.api.endpoints import auth, users, customers

# Crear el router principal
api_router = APIRouter()

# Incluir los diferentes routers con sus prefijos y etiquetas
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])