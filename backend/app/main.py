# backend/app/main.py
"""
Punto de entrada principal para la aplicación FastAPI.
Define la aplicación FastAPI y configura los routers.
"""

import logging

# Configurar logging primero, antes de cualquier otra cosa
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers
from app.api.api import api_router

# Crear aplicación FastAPI
app = FastAPI(
    title="PymeAI API",
    description="API para la plataforma PymeAI - CRM inteligente para PYMEs",
    version="0.1.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API
app.include_router(api_router, prefix="/api")

# Endpoint raíz para verificar que la API está funcionando
@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de PymeAI",
        "docs": "/docs",  # Enlace a la documentación Swagger
        "status": "online"
    }

# Si este archivo se ejecuta directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)