# backend/app/api/endpoints/interactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from app.db.base import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.interaction import Interaction
from app.api.deps import get_current_user

router = APIRouter()

# Modelos Pydantic
class InteractionBase(BaseModel):
    type: str
    date_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    requires_followup: Optional[bool] = False
    followup_date: Optional[datetime] = None
    followup_type: Optional[str] = None
    followup_notes: Optional[str] = None

class InteractionCreate(InteractionBase):
    customer_id: int

class InteractionUpdate(BaseModel):
    type: Optional[str] = None  # Ahora es opcional
    date_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    requires_followup: Optional[bool] = None
    followup_date: Optional[datetime] = None
    followup_type: Optional[str] = None
    followup_notes: Optional[str] = None
    followup_completed: Optional[bool] = None
    followup_completed_date: Optional[datetime] = None

class InteractionResponse(InteractionBase):
    id: int
    customer_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    followup_completed: bool
    followup_completed_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Cambiado de orm_mode=True a from_attributes=True

# Endpoints
@router.post("/", response_model=InteractionResponse)
def create_interaction(
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva interacción con un cliente.
    """
    # Verificar que el cliente existe y pertenece a la organización del usuario
    customer = db.query(Customer).filter(
        Customer.id == interaction_data.customer_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Establecer fecha actual si no se proporciona
    if interaction_data.date_time is None:
        interaction_data.date_time = datetime.now(timezone.utc)
    
    # Crear la interacción
    interaction_dict = interaction_data.dict()
    interaction = Interaction(
        **interaction_dict,
        user_id=current_user.id
    )
    
    # Actualizar la fecha de última interacción del cliente
    customer.last_interaction = interaction.date_time
    
    # Guardar en la base de datos
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    return interaction

@router.get("/", response_model=List[InteractionResponse])
def list_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    requires_followup: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """
    Lista las interacciones con filtros opcionales.
    """
    # Construir la consulta base
    query = db.query(Interaction).join(
        Customer, Interaction.customer_id == Customer.id
    ).filter(
        Customer.organization_id == current_user.organization_id
    )
    
    # Aplicar filtros adicionales si se proporcionan
    if customer_id:
        query = query.filter(Interaction.customer_id == customer_id)
    
    if type:
        query = query.filter(Interaction.type == type)
    
    if requires_followup is not None:
        query = query.filter(Interaction.requires_followup == requires_followup)
    
    if from_date:
        query = query.filter(Interaction.date_time >= from_date)
    
    if to_date:
        query = query.filter(Interaction.date_time <= to_date)
    
    # Aplicar paginación y ordenar por fecha
    query = query.order_by(Interaction.date_time.desc()).offset(skip).limit(limit)
    
    return query.all()

@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una interacción específica por su ID.
    """
    # Buscar la interacción asegurándose que pertenece a la organización del usuario
    interaction = db.query(Interaction).join(
        Customer, Interaction.customer_id == Customer.id
    ).filter(
        Interaction.id == interaction_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    
    return interaction

@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    interaction_data: InteractionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una interacción existente.
    """
    # Buscar la interacción
    interaction = db.query(Interaction).join(
        Customer, Interaction.customer_id == Customer.id
    ).filter(
        Interaction.id == interaction_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    
    # Si se marca como completada y no hay fecha de completado, establecerla
    if interaction_data.followup_completed and not interaction_data.followup_completed_date:
        interaction_data.followup_completed_date = datetime.now(timezone.utc)
    
    # Actualizar solo los campos proporcionados
    update_data = interaction_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(interaction, key, value)
    
    # Guardar cambios
    db.commit()
    db.refresh(interaction)
    
    return interaction

@router.delete("/{interaction_id}", response_model=InteractionResponse)
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una interacción.
    """
    # Buscar la interacción
    interaction = db.query(Interaction).join(
        Customer, Interaction.customer_id == Customer.id
    ).filter(
        Interaction.id == interaction_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    
    # Eliminar la interacción
    db.delete(interaction)
    db.commit()
    
    return interaction

@router.get("/customer/{customer_id}", response_model=List[InteractionResponse])
def list_customer_interactions(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todas las interacciones de un cliente específico.
    """
    # Verificar que el cliente existe y pertenece a la organización del usuario
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Obtener las interacciones del cliente
    interactions = db.query(Interaction).filter(
        Interaction.customer_id == customer_id
    ).order_by(
        Interaction.date_time.desc()
    ).offset(skip).limit(limit).all()
    
    return interactions

@router.get("/followup/pending", response_model=List[InteractionResponse])
def list_pending_followups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = 7,
    skip: int = 0,
    limit: int = 100
):
    """
    Lista las interacciones que requieren seguimiento en los próximos días.
    """
    # Calcular la fecha límite (hoy + número de días)
    today = datetime.now(timezone.utc)
    limit_date = today + timedelta(days=days)
    
    # Buscar interacciones que requieren seguimiento
    followups = db.query(Interaction).join(
        Customer, Interaction.customer_id == Customer.id
    ).filter(
        Customer.organization_id == current_user.organization_id,
        Interaction.requires_followup == True,
        Interaction.followup_completed == False,
        Interaction.followup_date <= limit_date,
        Interaction.followup_date >= today
    ).order_by(
        Interaction.followup_date
    ).offset(skip).limit(limit).all()
    
    return followups

@router.put("/{interaction_id}/complete-followup", response_model=InteractionResponse)
def complete_followup(
    interaction_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca el seguimiento de una interacción como completado.
    """
    # Buscar la interacción
    interaction = db.query(Interaction).join(
        Customer, Interaction.customer_id == Customer.id
    ).filter(
        Interaction.id == interaction_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    
    # Verificar que la interacción requiere seguimiento
    if not interaction.requires_followup:
        raise HTTPException(status_code=400, detail="Esta interacción no requiere seguimiento")
    
    # Marcar el seguimiento como completado
    interaction.followup_completed = True
    interaction.followup_completed_date = datetime.now(timezone.utc)
    
    # Añadir notas si se proporcionan
    if notes:
        if interaction.followup_notes:
            interaction.followup_notes += f"\n\nCompletado: {notes}"
        else:
            interaction.followup_notes = f"Completado: {notes}"
    
    # Guardar cambios
    db.commit()
    db.refresh(interaction)
    
    return interaction