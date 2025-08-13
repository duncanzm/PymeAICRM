# backend/app/api/endpoints/opportunities.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.models.pipeline import Pipeline
from app.models.pipeline_stage import PipelineStage
from app.models.opportunity import Opportunity
from app.models.stage_history import StageHistory
from app.api.deps import get_current_user

# Definir modelos Pydantic
from pydantic import BaseModel, Field

class OpportunityBase(BaseModel):
    title: str
    description: Optional[str] = None
    value: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    source: Optional[str] = None
    custom_fields: Optional[dict] = None
    expected_close_date: Optional[datetime] = None

class OpportunityCreate(OpportunityBase):
    pipeline_id: int
    stage_id: int
    customer_id: Optional[int] = None
    user_id: Optional[int] = None  # Si no se proporciona, se asigna al usuario actual

class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    source: Optional[str] = None
    custom_fields: Optional[dict] = None
    expected_close_date: Optional[datetime] = None
    status: Optional[str] = None
    customer_id: Optional[int] = None
    user_id: Optional[int] = None

class StageChangeRequest(BaseModel):
    notes: Optional[str] = None

class OpportunityResponse(OpportunityBase):
    id: int
    organization_id: int
    pipeline_id: int
    stage_id: int
    customer_id: Optional[int] = None
    user_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    last_stage_change: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class StageHistoryResponse(BaseModel):
    id: int
    opportunity_id: int
    from_stage_id: Optional[int] = None
    to_stage_id: int
    user_id: Optional[int] = None
    changed_at: datetime
    notes: Optional[str] = None
    time_in_stage: Optional[int] = None
    
    class Config:
        orm_mode = True

# Crear router
router = APIRouter()

@router.post("/", response_model=OpportunityResponse)
def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva oportunidad de venta.
    """
    # Verificar que el pipeline existe y pertenece a la organización
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == opportunity_data.pipeline_id,
        Pipeline.organization_id == current_user.organization_id,
        Pipeline.is_active == True
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado o inactivo")
    
    # Verificar que la etapa existe y pertenece al pipeline
    stage = db.query(PipelineStage).filter(
        PipelineStage.id == opportunity_data.stage_id,
        PipelineStage.pipeline_id == opportunity_data.pipeline_id
    ).first()
    
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa no encontrada o no pertenece al pipeline")
    
    # Si no se proporciona un usuario, asignar al usuario actual
    user_id = opportunity_data.user_id or current_user.id
    
    # Crear la oportunidad
    opportunity = Opportunity(
        organization_id=current_user.organization_id,
        pipeline_id=opportunity_data.pipeline_id,
        stage_id=opportunity_data.stage_id,
        customer_id=opportunity_data.customer_id,
        user_id=user_id,
        title=opportunity_data.title,
        description=opportunity_data.description,
        value=opportunity_data.value,
        currency=opportunity_data.currency,
        source=opportunity_data.source,
        custom_fields=opportunity_data.custom_fields,
        expected_close_date=opportunity_data.expected_close_date,
        last_stage_change=datetime.now()
    )
    
    db.add(opportunity)
    db.flush()
    
    # Registrar el historial de etapas (primera etapa)
    stage_history = StageHistory(
        opportunity_id=opportunity.id,
        to_stage_id=opportunity_data.stage_id,
        user_id=current_user.id,
        changed_at=datetime.now()
    )
    
    db.add(stage_history)
    db.commit()
    db.refresh(opportunity)
    
    return opportunity

@router.get("/", response_model=List[OpportunityResponse])
def list_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    pipeline_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Lista las oportunidades de venta de la organización.
    """
    # Consulta base
    query = db.query(Opportunity).filter(
        Opportunity.organization_id == current_user.organization_id
    )
    
    # Aplicar filtros
    if pipeline_id:
        query = query.filter(Opportunity.pipeline_id == pipeline_id)
    
    if stage_id:
        query = query.filter(Opportunity.stage_id == stage_id)
    
    if customer_id:
        query = query.filter(Opportunity.customer_id == customer_id)
    
    if user_id:
        query = query.filter(Opportunity.user_id == user_id)
    
    if status:
        query = query.filter(Opportunity.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(Opportunity.title.ilike(search_term))
    
    # Aplicar paginación
    opportunities = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit).all()
    
    return opportunities

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una oportunidad específica por su ID.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.organization_id == current_user.organization_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    return opportunity

@router.put("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una oportunidad existente.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.organization_id == current_user.organization_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    # Actualizar campos
    update_data = opportunity_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(opportunity, key, value)
    
    db.commit()
    db.refresh(opportunity)
    
    return opportunity

@router.delete("/{opportunity_id}", response_model=dict)
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una oportunidad.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.organization_id == current_user.organization_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    # Eliminar la oportunidad y su historial asociado
    db.delete(opportunity)
    db.commit()
    
    return {"success": True, "message": "Oportunidad eliminada correctamente"}

@router.put("/{opportunity_id}/stage/{stage_id}", response_model=OpportunityResponse)
def change_stage(
    opportunity_id: int,
    stage_id: int,
    stage_change: StageChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cambia la etapa de una oportunidad.
    """
    # Buscar la oportunidad
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.organization_id == current_user.organization_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    # Verificar que la etapa existe y pertenece al pipeline de la oportunidad
    stage = db.query(PipelineStage).filter(
        PipelineStage.id == stage_id,
        PipelineStage.pipeline_id == opportunity.pipeline_id
    ).first()
    
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa no encontrada o no pertenece al pipeline")
    
    # Si la etapa es la misma, no hacer nada
    if opportunity.stage_id == stage_id:
        return opportunity
    
    # Obtener la etapa anterior
    from_stage_id = opportunity.stage_id
    
    # Calcular el tiempo en la etapa anterior
    now = datetime.now()
    time_in_stage = None
    if opportunity.last_stage_change:
        time_in_stage = int((now - opportunity.last_stage_change).total_seconds())
    
    # Actualizar la etapa
    opportunity.stage_id = stage_id
    opportunity.last_stage_change = now
    
    # Actualizar el estado si corresponde
    if stage.is_won:
        opportunity.status = "won"
    elif stage.is_lost:
        opportunity.status = "lost"
    else:
        opportunity.status = "open"
    
    # Registrar el cambio en el historial
    stage_history = StageHistory(
        opportunity_id=opportunity.id,
        from_stage_id=from_stage_id,
        to_stage_id=stage_id,
        user_id=current_user.id,
        changed_at=now,
        notes=stage_change.notes,
        time_in_stage=time_in_stage
    )
    
    db.add(stage_history)
    db.commit()
    db.refresh(opportunity)
    
    return opportunity

@router.get("/{opportunity_id}/history", response_model=List[StageHistoryResponse])
def get_opportunity_history(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de cambios de etapa de una oportunidad.
    """
    # Verificar que la oportunidad existe y pertenece a la organización
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.organization_id == current_user.organization_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    # Obtener el historial
    history = db.query(StageHistory).filter(
        StageHistory.opportunity_id == opportunity_id
    ).order_by(StageHistory.changed_at.desc()).all()
    
    return history