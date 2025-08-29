# backend/app/models/__init__.py
"""
Este archivo importa todos los modelos para facilitar su acceso desde otros módulos.
También es importante para que Alembic pueda detectar automáticamente todos los modelos
durante las migraciones.
"""

from app.models.organization import Organization
from app.models.user import User
from app.models.customer import Customer
from app.models.interaction import Interaction
from app.models.active_session import ActiveSession
from app.models.invitation import Invitation
from app.models.password_reset import PasswordReset
from app.models.pipeline import Pipeline
from app.models.pipeline_stage import PipelineStage
from app.models.opportunity import Opportunity
from app.models.stage_history import StageHistory
from app.models.conversation import Conversation
from app.models.message import Message