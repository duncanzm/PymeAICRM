# backend/app/api/endpoints/pipelines.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.models.pipeline import Pipeline
from app.models.pipeline_stage import PipelineStage
from app.api.deps import get_current_user

# Definir modelos Pydantic
from pydantic import BaseModel, Field

class PipelineStageBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"
    order: int
    probability: Optional[float] = 0.0
    expected_duration_days: Optional[int] = 7
    is_won: Optional[bool] = False
    is_lost: Optional[bool] = False

class PipelineStageCreate(PipelineStageBase):
    pass

class PipelineStageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None
    probability: Optional[float] = None
    expected_duration_days: Optional[int] = None
    is_won: Optional[bool] = None
    is_lost: Optional[bool] = None

class PipelineStageResponse(PipelineStageBase):
    id: int
    pipeline_id: int
    
    class Config:
        orm_mode = True

class PipelineBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"
    is_default: Optional[bool] = False

class PipelineCreate(PipelineBase):
    stages: List[PipelineStageCreate]

class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class PipelineResponse(PipelineBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    stages: List[PipelineStageResponse]
    
    class Config:
        orm_mode = True

# Crear router
router = APIRouter()

@router.post("/", response_model=PipelineResponse)
def create_pipeline(
    pipeline_data: PipelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo pipeline para la organización del usuario.
    """
    # Si es el pipeline por defecto, quitar el flag de los demás
    if pipeline_data.is_default:
        existing_default = db.query(Pipeline).filter(
            Pipeline.organization_id == current_user.organization_id,
            Pipeline.is_default == True
        ).first()
        
        if existing_default:
            existing_default.is_default = False
            db.commit()
    
    # Crear el pipeline
    pipeline = Pipeline(
        organization_id=current_user.organization_id,
        name=pipeline_data.name,
        description=pipeline_data.description,
        color=pipeline_data.color,
        is_default=pipeline_data.is_default
    )
    
    db.add(pipeline)
    db.flush()  # Para obtener el ID antes de crear las etapas
    
    # Crear las etapas
    stages = []
    for stage_data in pipeline_data.stages:
        stage = PipelineStage(
            pipeline_id=pipeline.id,
            name=stage_data.name,
            description=stage_data.description,
            color=stage_data.color,
            order=stage_data.order,
            probability=stage_data.probability,
            expected_duration_days=stage_data.expected_duration_days,
            is_won=stage_data.is_won,
            is_lost=stage_data.is_lost
        )
        db.add(stage)
        stages.append(stage)
    
    db.commit()
    db.refresh(pipeline)
    
    return pipeline

@router.get("/", response_model=List[PipelineResponse])
def list_pipelines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_inactive: bool = False
):
    """
    Lista los pipelines de la organización del usuario.
    """
    query = db.query(Pipeline).filter(Pipeline.organization_id == current_user.organization_id)
    
    if not include_inactive:
        query = query.filter(Pipeline.is_active == True)
    
    pipelines = query.all()
    return pipelines

@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un pipeline específico por su ID.
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    return pipeline

@router.put("/{pipeline_id}", response_model=PipelineResponse)
def update_pipeline(
    pipeline_id: int,
    pipeline_data: PipelineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un pipeline existente.
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # Si se está estableciendo como default, quitar el flag de los demás
    if pipeline_data.is_default and not pipeline.is_default:
        existing_default = db.query(Pipeline).filter(
            Pipeline.organization_id == current_user.organization_id,
            Pipeline.is_default == True,
            Pipeline.id != pipeline_id
        ).first()
        
        if existing_default:
            existing_default.is_default = False
    
    # Actualizar campos
    update_data = pipeline_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pipeline, key, value)
    
    db.commit()
    db.refresh(pipeline)
    
    return pipeline

@router.delete("/{pipeline_id}", response_model=PipelineResponse)
def delete_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un pipeline (marca como inactivo).
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # No permitir eliminar el pipeline por defecto
    if pipeline.is_default:
        raise HTTPException(status_code=400, detail="No se puede eliminar el pipeline por defecto")
    
    # Marcar como inactivo en lugar de eliminar
    pipeline.is_active = False
    
    db.commit()
    db.refresh(pipeline)
    
    return pipeline

@router.post("/{pipeline_id}/set-default", response_model=PipelineResponse)
def set_default_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Establece un pipeline como el predeterminado para la organización.
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # Quitar el flag de pipeline por defecto de los demás
    existing_default = db.query(Pipeline).filter(
        Pipeline.organization_id == current_user.organization_id,
        Pipeline.is_default == True
    ).all()
    
    for p in existing_default:
        p.is_default = False
    
    # Establecer este pipeline como predeterminado
    pipeline.is_default = True
    
    db.commit()
    db.refresh(pipeline)
    
    return pipeline

# Endpoints para gestión de etapas
@router.post("/{pipeline_id}/stages", response_model=PipelineStageResponse)
def create_stage(
    pipeline_id: int,
    stage_data: PipelineStageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Añade una etapa a un pipeline existente.
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # Crear la etapa
    stage = PipelineStage(
        pipeline_id=pipeline_id,
        name=stage_data.name,
        description=stage_data.description,
        color=stage_data.color,
        order=stage_data.order,
        probability=stage_data.probability,
        expected_duration_days=stage_data.expected_duration_days,
        is_won=stage_data.is_won,
        is_lost=stage_data.is_lost
    )
    
    db.add(stage)
    db.commit()
    db.refresh(stage)
    
    return stage

@router.put("/{pipeline_id}/stages/{stage_id}", response_model=PipelineStageResponse)
def update_stage(
    pipeline_id: int,
    stage_id: int,
    stage_data: PipelineStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una etapa de un pipeline.
    """
    # Verificar que el pipeline existe y pertenece a la organización
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # Buscar la etapa
    stage = db.query(PipelineStage).filter(
        PipelineStage.id == stage_id,
        PipelineStage.pipeline_id == pipeline_id
    ).first()
    
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa no encontrada")
    
    # Actualizar campos
    update_data = stage_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(stage, key, value)
    
    db.commit()
    db.refresh(stage)
    
    return stage

@router.delete("/{pipeline_id}/stages/{stage_id}", response_model=dict)
def delete_stage(
    pipeline_id: int,
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una etapa de un pipeline.
    """
    # Verificar que el pipeline existe y pertenece a la organización
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # Buscar la etapa
    stage = db.query(PipelineStage).filter(
        PipelineStage.id == stage_id,
        PipelineStage.pipeline_id == pipeline_id
    ).first()
    
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa no encontrada")
    
    # Verificar si hay oportunidades en esta etapa
    opportunities_count = db.query(Opportunity).filter(
        Opportunity.stage_id == stage_id
    ).count()
    
    if opportunities_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la etapa porque tiene {opportunities_count} oportunidades asociadas"
        )
    
    # Eliminar la etapa
    db.delete(stage)
    db.commit()
    
    return {"success": True, "message": "Etapa eliminada correctamente"}

@router.put("/{pipeline_id}/reorder-stages", response_model=List[PipelineStageResponse])
def reorder_stages(
    pipeline_id: int,
    stage_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # El resto del código sigue igual
    """
    Reordena las etapas de un pipeline según el orden proporcionado.
    """
    # Verificar que el pipeline existe y pertenece a la organización
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.organization_id == current_user.organization_id
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline no encontrado")
    
    # Verificar que todas las etapas existen y pertenecen al pipeline
    stages = db.query(PipelineStage).filter(
        PipelineStage.pipeline_id == pipeline_id,
        PipelineStage.id.in_(stage_ids)
    ).all()
    
    if len(stages) != len(stage_ids):
        raise HTTPException(status_code=400, detail="Una o más etapas no existen o no pertenecen a este pipeline")
    
    # Crear un mapa de ID a etapa para acceso rápido
    stage_map = {stage.id: stage for stage in stages}
    
    # Actualizar el orden de las etapas
    for i, stage_id in enumerate(stage_ids):
        stage_map[stage_id].order = i
    
    db.commit()
    
    # Obtener las etapas actualizadas en el nuevo orden
    updated_stages = db.query(PipelineStage).filter(
        PipelineStage.pipeline_id == pipeline_id
    ).order_by(PipelineStage.order).all()
    
    return updated_stages