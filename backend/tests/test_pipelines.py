# backend/tests/test_pipelines.py
"""
Script para probar el módulo de pipelines y oportunidades.
Ejecutar con: python -m tests.test_pipelines
"""
import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_pipelines@pymeai.com"
TEST_PASSWORD = "pipeline123!"

def main():
    print("=== Prueba del Módulo de Pipelines y Oportunidades ===")
    
    # Paso 1: Asegurarnos de que existe un usuario de prueba
    ensure_user_exists()
    
    # Paso 2: Iniciar sesión
    print("\n1. Iniciando sesión...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"Error al iniciar sesión: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"Sesión iniciada correctamente. Token: {token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Paso 3: Crear un cliente para las pruebas
    print("\n2. Creando un cliente de prueba...")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    customer_data = {
        "first_name": f"Cliente {timestamp}",
        "last_name": "Prueba Pipeline",
        "email": f"cliente_pipeline_{timestamp}@example.com",
        "phone": "123-456-7890",
        "address": "Calle Prueba 123"
    }
    
    customer_response = requests.post(
        f"{BASE_URL}/customers/",
        headers=headers,
        json=customer_data
    )
    
    if customer_response.status_code != 200:
        print(f"Error al crear cliente: {customer_response.text}")
        return
    
    customer = customer_response.json()
    customer_id = customer["id"]
    print(f"Cliente creado correctamente. ID: {customer_id}")
    
    # Paso 4: Crear un pipeline
    print("\n3. Creando un pipeline de ventas...")
    pipeline_data = {
        "name": f"Pipeline de Ventas {timestamp}",
        "description": "Pipeline para prueba de ventas",
        "color": "#4f46e5",
        "is_default": True,
        "stages": [
            {
                "name": "Contacto Inicial",
                "description": "Primer contacto con el cliente",
                "color": "#3b82f6",
                "order": 0,
                "probability": 10.0,
                "expected_duration_days": 3,
                "is_won": False,
                "is_lost": False
            },
            {
                "name": "Calificación",
                "description": "Evaluación de necesidades y presupuesto",
                "color": "#8b5cf6",
                "order": 1,
                "probability": 25.0,
                "expected_duration_days": 5,
                "is_won": False,
                "is_lost": False
            },
            {
                "name": "Propuesta",
                "description": "Envío de propuesta formal",
                "color": "#ec4899",
                "order": 2,
                "probability": 50.0,
                "expected_duration_days": 7,
                "is_won": False,
                "is_lost": False
            },
            {
                "name": "Negociación",
                "description": "Negociación de términos",
                "color": "#f59e0b",
                "order": 3,
                "probability": 75.0,
                "expected_duration_days": 10,
                "is_won": False,
                "is_lost": False
            },
            {
                "name": "Ganada",
                "description": "Oportunidad cerrada y ganada",
                "color": "#10b981",
                "order": 4,
                "probability": 100.0,
                "expected_duration_days": 0,
                "is_won": True,
                "is_lost": False
            },
            {
                "name": "Perdida",
                "description": "Oportunidad cerrada y perdida",
                "color": "#ef4444",
                "order": 5,
                "probability": 0.0,
                "expected_duration_days": 0,
                "is_won": False,
                "is_lost": True
            }
        ]
    }
    
    pipeline_response = requests.post(
        f"{BASE_URL}/pipelines/",
        headers=headers,
        json=pipeline_data
    )
    
    if pipeline_response.status_code != 200:
        print(f"Error al crear pipeline: {pipeline_response.text}")
        return
    
    pipeline = pipeline_response.json()
    pipeline_id = pipeline["id"]
    print(f"Pipeline creado correctamente. ID: {pipeline_id}")
    print(f"Nombre: {pipeline['name']}")
    print(f"Etapas: {len(pipeline['stages'])}")
    
    # Obtener la primera etapa (Contacto Inicial)
    initial_stage_id = pipeline["stages"][0]["id"]
    
    # Paso 5: Listar pipelines
    print("\n4. Listando pipelines...")
    list_response = requests.get(
        f"{BASE_URL}/pipelines/",
        headers=headers
    )
    
    if list_response.status_code != 200:
        print(f"Error al listar pipelines: {list_response.text}")
        return
    
    pipelines = list_response.json()
    print(f"Se encontraron {len(pipelines)} pipelines.")
    
    # Paso 6: Crear una oportunidad
    print("\n5. Creando una oportunidad de venta...")
    opportunity_data = {
        "title": f"Venta de Producto {timestamp}",
        "description": "Oportunidad de venta para prueba",
        "value": 5000.0,
        "currency": "USD",
        "source": "Prueba",
        "pipeline_id": pipeline_id,
        "stage_id": initial_stage_id,
        "customer_id": customer_id,
        "expected_close_date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    opportunity_response = requests.post(
        f"{BASE_URL}/opportunities/",
        headers=headers,
        json=opportunity_data
    )
    
    if opportunity_response.status_code != 200:
        print(f"Error al crear oportunidad: {opportunity_response.text}")
        return
    
    opportunity = opportunity_response.json()
    opportunity_id = opportunity["id"]
    print(f"Oportunidad creada correctamente. ID: {opportunity_id}")
    print(f"Título: {opportunity['title']}")
    print(f"Valor: {opportunity['value']} {opportunity['currency']}")
    print(f"Etapa inicial: {opportunity['stage_id']} (Contacto Inicial)")
    
    # Paso 7: Listar oportunidades
    print("\n6. Listando oportunidades...")
    list_opps_response = requests.get(
        f"{BASE_URL}/opportunities/",
        headers=headers
    )
    
    if list_opps_response.status_code != 200:
        print(f"Error al listar oportunidades: {list_opps_response.text}")
        return
    
    opportunities = list_opps_response.json()
    print(f"Se encontraron {len(opportunities)} oportunidades.")
    
    # Paso 8: Mover la oportunidad a la siguiente etapa
    print("\n7. Moviendo la oportunidad a la etapa de Calificación...")
    qualification_stage_id = pipeline["stages"][1]["id"]
    
    stage_change_data = {
        "notes": "Cliente calificado positivamente. Presupuesto confirmado."
    }
    
    stage_change_response = requests.put(
        f"{BASE_URL}/opportunities/{opportunity_id}/stage/{qualification_stage_id}",
        headers=headers,
        json=stage_change_data
    )
    
    if stage_change_response.status_code != 200:
        print(f"Error al cambiar etapa: {stage_change_response.text}")
        return
    
    updated_opportunity = stage_change_response.json()
    print(f"Oportunidad movida correctamente a la etapa: {qualification_stage_id} (Calificación)")
    print(f"Estado actual: {updated_opportunity['status']}")
    
    # Paso 9: Verificar el historial de la oportunidad
    print("\n8. Verificando el historial de la oportunidad...")
    history_response = requests.get(
        f"{BASE_URL}/opportunities/{opportunity_id}/history",
        headers=headers
    )
    
    if history_response.status_code != 200:
        print(f"Error al obtener historial: {history_response.text}")
        return
    
    history = history_response.json()
    print(f"Se encontraron {len(history)} registros en el historial.")
    for i, record in enumerate(history):
        print(f"  Registro {i+1}:")
        print(f"    De etapa: {record['from_stage_id'] or 'Inicial'}")
        print(f"    A etapa: {record['to_stage_id']}")
        print(f"    Fecha: {record['changed_at']}")
        print(f"    Notas: {record['notes'] or 'Sin notas'}")
    
    # Paso 10: Mover la oportunidad a Ganada
    print("\n9. Moviendo la oportunidad a la etapa Ganada...")
    won_stage_id = pipeline["stages"][4]["id"]
    
    stage_change_data = {
        "notes": "Cliente aceptó la propuesta. Contrato firmado."
    }
    
    stage_change_response = requests.put(
        f"{BASE_URL}/opportunities/{opportunity_id}/stage/{won_stage_id}",
        headers=headers,
        json=stage_change_data
    )
    
    if stage_change_response.status_code != 200:
        print(f"Error al cambiar etapa: {stage_change_response.text}")
        return
    
    updated_opportunity = stage_change_response.json()
    print(f"Oportunidad movida correctamente a la etapa: {won_stage_id} (Ganada)")
    print(f"Estado actual: {updated_opportunity['status']}")
    
    # Paso 11: Actualizar datos de la oportunidad
    print("\n10. Actualizando datos de la oportunidad...")
    update_data = {
        "value": 5500.0,
        "description": "Oportunidad actualizada con monto final negociado"
    }
    
    update_response = requests.put(
        f"{BASE_URL}/opportunities/{opportunity_id}",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code != 200:
        print(f"Error al actualizar oportunidad: {update_response.text}")
        return
    
    updated_opportunity = update_response.json()
    print(f"Oportunidad actualizada correctamente.")
    print(f"Nuevo valor: {updated_opportunity['value']} {updated_opportunity['currency']}")
    print(f"Nueva descripción: {updated_opportunity['description']}")
    
    # Paso 12: Añadir una etapa al pipeline
    print("\n11. Añadiendo una nueva etapa al pipeline...")
    new_stage_data = {
        "name": "Implementación",
        "description": "Fase de implementación del producto",
        "color": "#0ea5e9",
        "order": 6,
        "probability": 100.0,
        "expected_duration_days": 14,
        "is_won": False,
        "is_lost": False
    }
    
    new_stage_response = requests.post(
        f"{BASE_URL}/pipelines/{pipeline_id}/stages",
        headers=headers,
        json=new_stage_data
    )
    
    if new_stage_response.status_code != 200:
        print(f"Error al añadir etapa: {new_stage_response.text}")
        return
    
    new_stage = new_stage_response.json()
    print(f"Etapa añadida correctamente. ID: {new_stage['id']}")
    print(f"Nombre: {new_stage['name']}")
    
    # Paso 13: Reordenar las etapas del pipeline
    print("\n12. Reordenando las etapas del pipeline...")
    
    # Obtener el pipeline actualizado con la nueva etapa
    pipeline_response = requests.get(
        f"{BASE_URL}/pipelines/{pipeline_id}",
        headers=headers
    )
    
    if pipeline_response.status_code != 200:
        print(f"Error al obtener pipeline: {pipeline_response.text}")
        return
    
    updated_pipeline = pipeline_response.json()
    
    # Obtener los IDs de las etapas
    stage_ids = [stage["id"] for stage in updated_pipeline["stages"]]
    
    # Mover la etapa "Implementación" antes de "Ganada"
    implementation_id = new_stage["id"]
    won_position = next(i for i, stage in enumerate(updated_pipeline["stages"]) if stage["name"] == "Ganada")
    
    # Quitar la etapa de Implementación de su posición actual
    stage_ids.remove(implementation_id)
    # Insertarla antes de Ganada
    stage_ids.insert(won_position, implementation_id)
    
    reorder_response = requests.put(
        f"{BASE_URL}/pipelines/{pipeline_id}/reorder-stages",  # Nueva ruta
        headers=headers,
        json=stage_ids
    )
    
    if reorder_response.status_code != 200:
        print(f"Error al reordenar etapas: {reorder_response.text}")
        return
    
    reordered_stages = reorder_response.json()
    print(f"Etapas reordenadas correctamente. Nuevo orden:")
    for i, stage in enumerate(reordered_stages):
        print(f"  {i+1}. {stage['name']}")
    
    # Paso 14: Eliminar la oportunidad de prueba
    print("\n13. Eliminando la oportunidad de prueba...")
    delete_response = requests.delete(
        f"{BASE_URL}/opportunities/{opportunity_id}",
        headers=headers
    )
    
    if delete_response.status_code != 200:
        print(f"Error al eliminar oportunidad: {delete_response.text}")
        return
    
    print(f"Oportunidad eliminada correctamente.")
    
    # Paso 15: Desactivar el pipeline de prueba
    print("\n14. Desactivando el pipeline de prueba...")
    update_pipeline_data = {
        "is_active": False
    }
    
    update_pipeline_response = requests.put(
        f"{BASE_URL}/pipelines/{pipeline_id}",
        headers=headers,
        json=update_pipeline_data
    )
    
    if update_pipeline_response.status_code != 200:
        print(f"Error al desactivar pipeline: {update_pipeline_response.text}")
        return
    
    print(f"Pipeline desactivado correctamente.")
    
    # Paso 16: Eliminar el cliente de prueba
    print("\n15. Eliminando el cliente de prueba...")
    delete_customer_response = requests.delete(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers
    )
    
    if delete_customer_response.status_code != 200:
        print(f"Error al eliminar cliente: {delete_customer_response.text}")
        return
    
    print(f"Cliente eliminado (inactivado) correctamente.")
    
    print("\n=== Prueba completada con éxito ===")

def ensure_user_exists():
    """
    Asegurarse de que existe un usuario para pruebas.
    Primero intenta iniciar sesión, si falla, registra un usuario nuevo.
    """
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print("El usuario de prueba no existe o la contraseña ha cambiado.")
        print("Intentando registrar un usuario nuevo...")
        
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "first_name": "Test",
            "last_name": "Pipelines",
            "organization_name": "Test Organization for Pipelines"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if register_response.status_code == 200:
            print("Usuario registrado correctamente.")
        else:
            print(f"Error al registrar usuario: {register_response.text}")
            print("Continuando con el usuario existente (posiblemente con otra contraseña).")
    else:
        print("Usuario de prueba existe. Continuando...")

if __name__ == "__main__":
    main()