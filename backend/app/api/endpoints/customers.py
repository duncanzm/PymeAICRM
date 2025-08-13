# backend/app/api/endpoints/customers.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.db.base import get_db
from app.models.user import User
from app.models.customer import Customer
from app.api.deps import get_current_user

# Definir modelos Pydantic
from pydantic import BaseModel, EmailStr

class CustomerBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    segment: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    segment: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None
    status: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    organization_id: int
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    segment: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    last_interaction: Optional[datetime] = None
    status: str
    lifetime_value: float
    
    # Campos de segmentación
    first_purchase_date: Optional[date] = None
    last_purchase_date: Optional[date] = None
    purchase_count: Optional[int] = None
    total_spent: Optional[float] = None
    average_purchase_value: Optional[float] = None
    purchase_frequency_days: Optional[float] = None
    days_since_last_purchase: Optional[int] = None
    segment_updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Cambiado de orm_mode=True

# Crear router
router = APIRouter()

@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo cliente en la organización del usuario autenticado.
    """
    # Crear objeto Cliente
    customer = Customer(
        **customer_data.dict(),
        organization_id=current_user.organization_id,
        status="active"
    )
    
    # Guardar en la base de datos
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer

@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    segment: Optional[str] = None
):
    """
    Lista los clientes de la organización del usuario autenticado.
    Soporta paginación, búsqueda y filtrado por estado y segmento.
    """
    # Construir query base
    query = db.query(Customer).filter(Customer.organization_id == current_user.organization_id)
    
    # Aplicar filtros si se proporcionan
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.first_name.ilike(search_term)) | 
            (Customer.last_name.ilike(search_term)) |
            (Customer.email.ilike(search_term))
        )
    
    if status:
        query = query.filter(Customer.status == status)
    
    if segment:
        query = query.filter(Customer.segment == segment)
    
    # Aplicar paginación
    customers = query.offset(skip).limit(limit).all()
    
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un cliente específico por su ID.
    """
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un cliente existente.
    """
    # Buscar el cliente
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar solo los campos proporcionados
    update_data = customer_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
    
    # Guardar cambios
    db.commit()
    db.refresh(customer)
    
    return customer

@router.delete("/{customer_id}", response_model=CustomerResponse)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca un cliente como inactivo (eliminación lógica).
    """
    # Buscar el cliente
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Marcar como inactivo
    customer.status = "inactive"
    
    # Guardar cambios
    db.commit()
    db.refresh(customer)
    
    return customer

class PurchaseRecord(BaseModel):
    purchase_date: date
    amount: float
    items_count: Optional[int] = 1
    notes: Optional[str] = None

@router.post("/{customer_id}/purchase", response_model=CustomerResponse)
def record_customer_purchase(
    customer_id: int,
    purchase_data: PurchaseRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra una compra para un cliente y actualiza sus métricas para segmentación.
    """
    # Buscar el cliente
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == current_user.organization_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar datos de compra
    if not customer.first_purchase_date:
        customer.first_purchase_date = purchase_data.purchase_date
    
    # Si ya tenía compras, calcular la frecuencia
    if customer.purchase_count > 0 and customer.last_purchase_date:
        days_between = (purchase_data.purchase_date - customer.last_purchase_date).days
        
        # Actualizar la frecuencia promedio
        if customer.purchase_frequency_days:
            # Promedio ponderado, dando más peso a las compras recientes
            customer.purchase_frequency_days = (customer.purchase_frequency_days * 0.7) + (days_between * 0.3)
        else:
            customer.purchase_frequency_days = days_between
    
    # Actualizar estadísticas de compra
    customer.last_purchase_date = purchase_data.purchase_date
    customer.purchase_count += 1
    customer.total_spent += purchase_data.amount
    customer.average_purchase_value = customer.total_spent / customer.purchase_count
    
    # Guardar cambios
    db.commit()
    db.refresh(customer)
    
    return customer