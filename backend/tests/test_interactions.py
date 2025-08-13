# backend/tests/test_interactions.py
"""
Script simple para probar la gestión de interacciones con clientes.
Ejecutar con: python -m tests.test_interactions
"""
import requests
import json
import time
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_interactions@pymeai.com"
TEST_PASSWORD = "TestInteractions123!"

def main():
    print("=== Prueba de Gestión de Interacciones ===")
    
    # Asegurarnos de que existe un usuario para pruebas
    ensure_user_exists()
    
    # Paso 1: Iniciar sesión
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
    
    # Paso 2: Crear un cliente para las pruebas
    print("\n2. Creando un cliente para pruebas...")
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    customer_data = {
        "first_name": f"Cliente {timestamp}",
        "last_name": "Prueba Interacciones",
        "email": f"cliente_{timestamp}@example.com",
        "phone": "123-456-7890",
        "address": "Calle Principal 123",
        "segment": "VIP",
        "notes": "Cliente de prueba para interacciones"
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
    print(f"Nombre: {customer['first_name']} {customer['last_name']}")
    
    # Paso 3: Crear una interacción con el cliente
    print("\n3. Creando una interacción...")
    
    interaction_data = {
        "customer_id": customer_id,
        "type": "call",
        "date_time": datetime.now().isoformat(),
        "duration_minutes": 15,
        "notes": "Primera llamada con el cliente para presentar el producto.",
        "outcome": "positive",
        "requires_followup": True,
        "followup_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "followup_type": "meeting",
        "followup_notes": "Programar una demostración del producto."
    }
    
    create_response = requests.post(
        f"{BASE_URL}/interactions/",
        headers=headers,
        json=interaction_data
    )
    
    if create_response.status_code != 200:
        print(f"Error al crear interacción: {create_response.text}")
        return
    
    interaction = create_response.json()
    interaction_id = interaction["id"]
    print(f"Interacción creada correctamente. ID: {interaction_id}")
    print(f"Tipo: {interaction['type']}")
    print(f"Resultado: {interaction['outcome']}")
    print(f"Seguimiento requerido: {'Sí' if interaction['requires_followup'] else 'No'}")
    
    # Paso 4: Listar todas las interacciones
    print("\n4. Listando todas las interacciones...")
    
    list_response = requests.get(
        f"{BASE_URL}/interactions/",
        headers=headers
    )
    
    if list_response.status_code != 200:
        print(f"Error al listar interacciones: {list_response.text}")
        return
    
    interactions = list_response.json()
    print(f"Se encontraron {len(interactions)} interacciones.")
    
    # Paso 5: Listar interacciones de un cliente específico
    print(f"\n5. Listando interacciones del cliente ID {customer_id}...")
    
    customer_interactions_response = requests.get(
        f"{BASE_URL}/interactions/customer/{customer_id}",
        headers=headers
    )
    
    if customer_interactions_response.status_code != 200:
        print(f"Error al listar interacciones del cliente: {customer_interactions_response.text}")
        return
    
    customer_interactions = customer_interactions_response.json()
    print(f"Se encontraron {len(customer_interactions)} interacciones para el cliente.")
    
    # Paso 6: Actualizar una interacción
    print(f"\n6. Actualizando interacción con ID {interaction_id}...")

    update_data = {
        "type": "call",  # Añadir el tipo aquí
        "notes": "Primera llamada con el cliente para presentar el producto. El cliente mostró mucho interés.",
        "outcome": "very_positive"
    }
    
    update_response = requests.put(
        f"{BASE_URL}/interactions/{interaction_id}",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code != 200:
        print(f"Error al actualizar interacción: {update_response.text}")
        return
    
    updated_interaction = update_response.json()
    print(f"Interacción actualizada correctamente.")
    print(f"Nuevas notas: {updated_interaction['notes']}")
    print(f"Nuevo resultado: {updated_interaction['outcome']}")
    
    # Paso 7: Listar seguimientos pendientes
    print("\n7. Listando seguimientos pendientes...")
    
    followups_response = requests.get(
        f"{BASE_URL}/interactions/followup/pending",
        headers=headers
    )
    
    if followups_response.status_code != 200:
        print(f"Error al listar seguimientos pendientes: {followups_response.text}")
        return
    
    followups = followups_response.json()
    print(f"Se encontraron {len(followups)} seguimientos pendientes.")
    
    # Paso 8: Marcar seguimiento como completado
    print(f"\n8. Marcando seguimiento como completado para interacción ID {interaction_id}...")
    
    complete_response = requests.put(
        f"{BASE_URL}/interactions/{interaction_id}/complete-followup",
        headers=headers,
        params={"notes": "Se realizó la demostración del producto con éxito."}
    )
    
    if complete_response.status_code != 200:
        print(f"Error al completar seguimiento: {complete_response.text}")
        return
    
    completed_interaction = complete_response.json()
    print(f"Seguimiento marcado como completado.")
    print(f"Completado: {'Sí' if completed_interaction['followup_completed'] else 'No'}")
    print(f"Fecha de completado: {completed_interaction['followup_completed_date']}")
    
    # Paso 9: Eliminar una interacción
    print(f"\n9. Eliminando interacción con ID {interaction_id}...")
    
    delete_response = requests.delete(
        f"{BASE_URL}/interactions/{interaction_id}",
        headers=headers
    )
    
    if delete_response.status_code != 200:
        print(f"Error al eliminar interacción: {delete_response.text}")
        return
    
    deleted_interaction = delete_response.json()
    print(f"Interacción eliminada correctamente.")
    
    # Paso 10: Eliminar cliente de prueba
    print(f"\n10. Eliminando cliente de prueba con ID {customer_id}...")
    
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
            "last_name": "Interactions",
            "organization_name": "Test Organization for Interactions"
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