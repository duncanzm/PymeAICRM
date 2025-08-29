# backend/app/api/endpoints/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta

from app.db.base import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.interaction import Interaction
from app.api.deps import get_current_user

# Intentar importar los otros modelos, manejando excepciones si no existen
try:
    from app.models.pipeline import Pipeline
    from app.models.pipeline_stage import PipelineStage
    from app.models.opportunity import Opportunity
    from app.models.stage_history import StageHistory
except ImportError:
    Pipeline = None
    PipelineStage = None
    Opportunity = None
    StageHistory = None

# Crear router
router = APIRouter()

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "month"  # 'week', 'month', 'quarter', 'year'
):
    """
    Obtiene una visión general de los principales KPIs para el dashboard.
    """
    # Definir rango de fechas según el período seleccionado
    now = datetime.now()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)  # Default: mes
    
    # Clientes
    customers_count = db.query(Customer).filter(
        Customer.organization_id == current_user.organization_id,
        Customer.status == "active"
    ).count()
    
    # Valores predeterminados
    active_opportunities_count = 0
    won_opportunities_count = 0
    total_pipeline_value = 0.0
    recent_interactions_count = 0
    customers_by_segment = {}
    opportunities_by_stage = {}
    
    # Oportunidades activas
    if Opportunity is not None:
        try:
            active_opportunities_count = db.query(Opportunity).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.status == "open"
            ).count()
            
            # Oportunidades ganadas en el período
            won_opportunities_count = db.query(Opportunity).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.status == "won",
                Opportunity.updated_at >= start_date
            ).count()
            
            # Valor total en pipeline
            total_pipeline_value = db.query(func.sum(Opportunity.value)).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.status == "open"
            ).scalar() or 0
        except Exception as e:
            print(f"Error al consultar Opportunity: {e}")
    
    # Interacciones recientes
    try:
        # Obtener los IDs de clientes que pertenecen a nuestra organización
        customer_ids = db.query(Customer.id).filter(
            Customer.organization_id == current_user.organization_id
        ).all()
        customer_ids = [id[0] for id in customer_ids]
        
        if customer_ids:
            # Usar esos IDs para filtrar interacciones
            recent_interactions_count = db.query(Interaction).filter(
                Interaction.customer_id.in_(customer_ids),
                Interaction.date_time >= start_date
            ).count()
    except Exception as e:
        print(f"Error al consultar Interaction: {e}")
    
    # Distribución de clientes por segmento
    try:
        customers_by_segment_query = db.query(
            Customer.segment, 
            func.count(Customer.id)
        ).filter(
            Customer.organization_id == current_user.organization_id,
            Customer.status == "active"
        ).group_by(Customer.segment).all()
        
        for segment, count in customers_by_segment_query:
            if segment:  # Evitar segmentos nulos
                customers_by_segment[segment] = count
    except Exception as e:
        print(f"Error al consultar segmentos de clientes: {e}")
    
    # Distribución de oportunidades por etapa
    if Pipeline is not None and PipelineStage is not None and Opportunity is not None:
        try:
            stages_query = db.query(
                PipelineStage.id, 
                PipelineStage.name
            ).join(
                Pipeline, Pipeline.id == PipelineStage.pipeline_id
            ).filter(
                Pipeline.organization_id == current_user.organization_id
            ).all()
            
            stages_map = {stage_id: stage_name for stage_id, stage_name in stages_query}
            
            opportunities_by_stage_query = db.query(
                Opportunity.stage_id, 
                func.count(Opportunity.id)
            ).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.status == "open"
            ).group_by(Opportunity.stage_id).all()
            
            for stage_id, count in opportunities_by_stage_query:
                stage_name = stages_map.get(stage_id, "Unknown")
                opportunities_by_stage[stage_name] = count
        except Exception as e:
            print(f"Error al consultar etapas de oportunidades: {e}")
    
    # Calcular tamaño promedio de acuerdo
    average_deal_size = 0
    if active_opportunities_count > 0:
        average_deal_size = float(total_pipeline_value) / active_opportunities_count
    
    return {
        "customers_count": customers_count,
        "active_opportunities_count": active_opportunities_count,
        "won_opportunities_count": won_opportunities_count,
        "total_pipeline_value": float(total_pipeline_value),
        "average_deal_size": float(average_deal_size),
        "recent_interactions_count": recent_interactions_count,
        "customers_by_segment": customers_by_segment,
        "opportunities_by_stage": opportunities_by_stage
    }

@router.get("/sales-performance")
def get_sales_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "month"  # 'week', 'month', 'quarter', 'year'
):
    """
    Obtiene datos de rendimiento de ventas para visualizaciones de tendencias.
    """
    # Si no tenemos el modelo Opportunity, devolvemos datos vacíos
    if Opportunity is None:
        return {
            "won_opportunities": [],
            "new_opportunities": [],
            "comparison": {
                "previous_period_value": 0.0,
                "current_period_value": 0.0,
                "change_percentage": 0.0
            }
        }
    
    # Definir rango de fechas según el período seleccionado
    now = datetime.now()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)  # Default: mes
    
    try:
        # Oportunidades ganadas por período
        won_opportunities = db.query(
            func.date(Opportunity.updated_at).label('period'),
            func.count(Opportunity.id).label('count'),
            func.sum(Opportunity.value).label('value')
        ).filter(
            Opportunity.organization_id == current_user.organization_id,
            Opportunity.status == "won",
            Opportunity.updated_at >= start_date
        ).group_by('period').all()
        
        won_data = []
        for period, count, value in won_opportunities:
            won_data.append({
                "period": str(period),
                "count": count,
                "value": float(value) if value else 0
            })
        
        # Oportunidades nuevas por período
        new_opportunities = db.query(
            func.date(Opportunity.created_at).label('period'),
            func.count(Opportunity.id).label('count')
        ).filter(
            Opportunity.organization_id == current_user.organization_id,
            Opportunity.created_at >= start_date
        ).group_by('period').all()
        
        new_data = []
        for period, count in new_opportunities:
            new_data.append({
                "period": str(period),
                "count": count
            })
        
        # Comparar con período anterior
        previous_start = start_date - (now - start_date)  # Mismo intervalo, período anterior
        
        previous_won_value = db.query(func.sum(Opportunity.value)).filter(
            Opportunity.organization_id == current_user.organization_id,
            Opportunity.status == "won",
            Opportunity.updated_at >= previous_start,
            Opportunity.updated_at < start_date
        ).scalar() or 0
        
        current_won_value = db.query(func.sum(Opportunity.value)).filter(
            Opportunity.organization_id == current_user.organization_id,
            Opportunity.status == "won",
            Opportunity.updated_at >= start_date
        ).scalar() or 0
        
        value_change_pct = 0
        if float(previous_won_value) > 0:
            value_change_pct = ((float(current_won_value) - float(previous_won_value)) / float(previous_won_value) * 100)
        
        return {
            "won_opportunities": won_data,
            "new_opportunities": new_data,
            "comparison": {
                "previous_period_value": float(previous_won_value),
                "current_period_value": float(current_won_value),
                "change_percentage": round(value_change_pct, 2)
            }
        }
    except Exception as e:
        print(f"Error en sales-performance: {e}")
        return {
            "won_opportunities": [],
            "new_opportunities": [],
            "comparison": {
                "previous_period_value": 0.0,
                "current_period_value": 0.0,
                "change_percentage": 0.0
            }
        }

@router.get("/pipeline-performance")
def get_pipeline_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pipeline_id: int = None
):
    """
    Obtiene métricas de rendimiento del pipeline para identificar cuellos de botella.
    """
    # Si no tenemos los modelos necesarios, devolvemos datos vacíos
    if Pipeline is None or PipelineStage is None or Opportunity is None:
        return {
            "pipeline_id": None,
            "pipeline_name": "Todos",
            "stage_metrics": [],
            "overall_conversion_rate": 0.0
        }
    
    try:
        # Verificar que el pipeline pertenece a la organización si se especifica
        if pipeline_id:
            pipeline = db.query(Pipeline).filter(
                Pipeline.id == pipeline_id,
                Pipeline.organization_id == current_user.organization_id
            ).first()
            
            if not pipeline:
                raise HTTPException(status_code=404, detail="Pipeline no encontrado")
            
            pipeline_name = pipeline.name
            pipeline_filter = Pipeline.id == pipeline_id
        else:
            pipeline_name = "Todos"
            pipeline_filter = Pipeline.organization_id == current_user.organization_id
        
        # Obtener etapas del pipeline
        stages = db.query(
            PipelineStage
        ).join(
            Pipeline, Pipeline.id == PipelineStage.pipeline_id
        ).filter(
            Pipeline.organization_id == current_user.organization_id,
            pipeline_filter
        ).order_by(PipelineStage.order).all()
        
        # Calcular métricas para cada etapa
        stage_metrics = []
        
        for stage in stages:
            # Contar oportunidades actuales en la etapa
            current_count = db.query(Opportunity).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.stage_id == stage.id,
                Opportunity.status == "open"
            ).count()
            
            # Valor total en la etapa
            stage_value = db.query(func.sum(Opportunity.value)).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.stage_id == stage.id,
                Opportunity.status == "open"
            ).scalar() or 0
            
            # Tiempo promedio en la etapa (desde historial)
            avg_time = 0
            conversion_rate = 0
            
            if StageHistory is not None:
                try:
                    avg_time = db.query(func.avg(StageHistory.time_in_stage)).filter(
                        StageHistory.from_stage_id == stage.id
                    ).scalar() or 0
                    
                    # Tasa de conversión a la siguiente etapa
                    next_stage = db.query(PipelineStage).filter(
                        PipelineStage.pipeline_id == stage.pipeline_id,
                        PipelineStage.order > stage.order
                    ).order_by(PipelineStage.order).first()
                    
                    if next_stage:
                        # Contar movimientos a la siguiente etapa
                        moves_to_next = db.query(StageHistory).filter(
                            StageHistory.from_stage_id == stage.id,
                            StageHistory.to_stage_id == next_stage.id
                        ).count()
                        
                        # Contar todos los movimientos desde esta etapa
                        total_moves = db.query(StageHistory).filter(
                            StageHistory.from_stage_id == stage.id
                        ).count()
                        
                        if total_moves > 0:
                            conversion_rate = (moves_to_next / total_moves * 100)
                except Exception as e:
                    print(f"Error al consultar StageHistory: {e}")
            
            avg_time_in_stage = round(float(avg_time) / 86400, 1) if avg_time > 0 else 0  # Convertir segundos a días
            
            stage_metrics.append({
                "stage_id": stage.id,
                "stage_name": stage.name,
                "opportunity_count": current_count,
                "stage_value": float(stage_value),
                "avg_time_in_days": avg_time_in_stage,
                "conversion_rate": round(conversion_rate, 2),
                "probability": stage.probability
            })
        
        # Calcular tasa de conversión general del pipeline
        overall_conversion = 0
        
        # Buscar etapa inicial y final
        initial_stage = next((s for s in stages if s.order == 0), None)
        final_stage = next((s for s in stages if getattr(s, 'is_won', False)), None)
        
        if initial_stage and final_stage:
            # Contar oportunidades que han llegado a la etapa final
            won_count = db.query(Opportunity).filter(
                Opportunity.organization_id == current_user.organization_id,
                Opportunity.status == "won"
            ).count()
            
            # Contar todas las oportunidades que han pasado por la etapa inicial
            total_opps = db.query(Opportunity).filter(
                Opportunity.organization_id == current_user.organization_id
            ).count()
            
            if total_opps > 0:
                overall_conversion = (won_count / total_opps * 100)
        
        return {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "stage_metrics": stage_metrics,
            "overall_conversion_rate": round(overall_conversion, 2)
        }
    except Exception as e:
        print(f"Error en pipeline-performance: {e}")
        return {
            "pipeline_id": None,
            "pipeline_name": "Todos",
            "stage_metrics": [],
            "overall_conversion_rate": 0.0
        }