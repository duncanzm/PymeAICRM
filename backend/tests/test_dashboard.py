# backend/tests/test_dashboard.py
"""
Script para probar el módulo de dashboard.
Ejecutar con: python -m tests.test_dashboard
"""
import requests
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_dashboard@pymeai.com"
TEST_PASSWORD = "dashboard123!"

def main():
    print("=== Prueba del Módulo de Dashboard ===")
    
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
    
    # Paso 3: Obtener visión general del dashboard
    print("\n2. Obteniendo visión general del dashboard...")
    overview_response = requests.get(
        f"{BASE_URL}/dashboard/overview",
        headers=headers
    )
    
    if overview_response.status_code != 200:
        print(f"Error al obtener visión general: {overview_response.text}")
        return
    
    overview = overview_response.json()
    print(f"Visión general obtenida correctamente:")
    print(f"  Total de clientes activos: {overview['customers_count']}")
    print(f"  Oportunidades activas: {overview['active_opportunities_count']}")
    print(f"  Oportunidades ganadas (último mes): {overview['won_opportunities_count']}")
    print(f"  Valor total en pipeline: {overview['total_pipeline_value']}")
    print(f"  Tamaño promedio de acuerdo: {overview['average_deal_size']}")
    print(f"  Interacciones recientes: {overview['recent_interactions_count']}")
    
    # Paso 4: Obtener datos de rendimiento de ventas
    print("\n3. Obteniendo datos de rendimiento de ventas...")
    sales_response = requests.get(
        f"{BASE_URL}/dashboard/sales-performance",
        headers=headers
    )
    
    if sales_response.status_code != 200:
        print(f"Error al obtener rendimiento de ventas: {sales_response.text}")
        return
    
    sales_data = sales_response.json()
    print(f"Datos de rendimiento obtenidos correctamente:")
    print(f"  Comparación con período anterior:")
    print(f"    Período actual: {sales_data['comparison']['current_period_value']}")
    print(f"    Período anterior: {sales_data['comparison']['previous_period_value']}")
    print(f"    Cambio porcentual: {sales_data['comparison']['change_percentage']}%")
    
    # Mostrar datos de tendencias si hay
    if sales_data['won_opportunities']:
        print(f"  Datos de tendencias:")
        for period in sales_data['won_opportunities'][:3]:  # Mostrar solo los primeros 3 períodos
            print(f"    {period['period']}: {period['count']} oportunidades, valor {period['value']}")
    else:
        print("  No hay datos de tendencias disponibles.")
    
    # Paso 5: Obtener rendimiento del pipeline
    print("\n4. Obteniendo rendimiento del pipeline...")
    pipeline_response = requests.get(
        f"{BASE_URL}/dashboard/pipeline-performance",
        headers=headers
    )
    
    if pipeline_response.status_code != 200:
        print(f"Error al obtener rendimiento del pipeline: {pipeline_response.text}")
        return
    
    pipeline_data = pipeline_response.json()
    print(f"Datos de pipeline obtenidos correctamente:")
    print(f"  Pipeline: {pipeline_data['pipeline_name']}")
    print(f"  Tasa de conversión general: {pipeline_data['overall_conversion_rate']}%")
    
    if pipeline_data['stage_metrics']:
        print(f"  Métricas por etapa:")
        for stage in pipeline_data['stage_metrics']:
            print(f"    {stage['stage_name']}:")
            print(f"      Oportunidades: {stage['opportunity_count']}")
            print(f"      Valor: {stage['stage_value']}")
            print(f"      Tiempo promedio: {stage['avg_time_in_days']} días")
            print(f"      Tasa de conversión: {stage['conversion_rate']}%")
    else:
        print("  No hay etapas configuradas.")
    
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
            "last_name": "Dashboard",
            "organization_name": "Test Organization for Dashboard"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if register_response.status_code == 200:
            print("Usuario registrado correctamente.")
            
            # Crear algunos datos de prueba (clientes, pipeline, oportunidades)
            token = register_response.json()["access_token"]
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Crear clientes
            for i in range(5):
                customer_data = {
                    "first_name": f"Cliente Test {i+1}",
                    "last_name": "Dashboard",
                    "email": f"cliente_dashboard_{i+1}@example.com",
                    "segment": ["VIP", "Regular", "Ocasional"][i % 3]
                }
                
                requests.post(f"{BASE_URL}/customers/", headers=headers, json=customer_data)
            
            # Crear pipeline
            pipeline_data = {
                "name": "Pipeline Test Dashboard",
                "description": "Pipeline para prueba de dashboard",
                "color": "#4f46e5",
                "is_default": True,
                "stages": [
                    {
                        "name": "Contacto Inicial",
                        "color": "#3b82f6",
                        "order": 0,
                        "probability": 10.0
                    },
                    {
                        "name": "Calificación",
                        "color": "#8b5cf6",
                        "order": 1,
                        "probability": 25.0
                    },
                    {
                        "name": "Propuesta",
                        "color": "#ec4899",
                        "order": 2,
                        "probability": 50.0
                    },
                    {
                        "name": "Negociación",
                        "color": "#f59e0b",
                        "order": 3,
                        "probability": 75.0
                    },
                    {
                        "name": "Ganada",
                        "color": "#10b981",
                        "order": 4,
                        "probability": 100.0,
                        "is_won": True
                    }
                ]
            }
            
            pipeline_response = requests.post(
                f"{BASE_URL}/pipelines/",
                headers=headers,
                json=pipeline_data
            )
            
            if pipeline_response.status_code == 200:
                pipeline = pipeline_response.json()
                stages = pipeline["stages"]
                
                # Crear oportunidades
                for i in range(10):
                    stage_index = min(i % 5, len(stages) - 1)
                    stage_id = stages[stage_index]["id"]
                    status = "won" if stage_index == 4 else "open"
                    
                    opportunity_data = {
                        "title": f"Oportunidad Dashboard {i+1}",
                        "description": "Oportunidad para prueba de dashboard",
                        "value": (i + 1) * 1000.0,
                        "pipeline_id": pipeline["id"],
                        "stage_id": stage_id,
                        "status": status
                    }
                    
                    requests.post(f"{BASE_URL}/opportunities/", headers=headers, json=opportunity_data)
                
                # Crear interacciones
                customers_response = requests.get(f"{BASE_URL}/customers/", headers=headers)
                if customers_response.status_code == 200:
                    customers = customers_response.json()
                    
                    for i, customer in enumerate(customers):
                        interaction_data = {
                            "customer_id": customer["id"],
                            "type": ["call", "email", "meeting"][i % 3],
                            "date_time": datetime.now().isoformat(),
                            "notes": f"Interacción de prueba para dashboard {i+1}",
                            "outcome": ["positive", "neutral", "negative"][i % 3]
                        }
                        
                        requests.post(f"{BASE_URL}/interactions/", headers=headers, json=interaction_data)
            
            print("Datos de prueba creados correctamente.")
        else:
            print(f"Error al registrar usuario: {register_response.text}")
            print("Continuando con el usuario existente (posiblemente con otra contraseña).")
    else:
        print("Usuario de prueba existe. Continuando...")

if __name__ == "__main__":
    main()