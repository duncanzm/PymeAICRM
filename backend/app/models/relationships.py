# backend/app/models/relationships.py
"""
Este archivo configura las relaciones entre modelos para evitar
dependencias circulares.
"""

from sqlalchemy.orm import relationship

def configure_relationships():
    """
    Configura las relaciones entre modelos después de que todas las
    clases han sido definidas.
    """
    from app.models.organization import Organization