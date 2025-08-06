# backend/tests/test_customer_module.py
"""
Script simple para probar el módulo de clientes.
Ejecutar con: python -m tests.test_customer_module
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
EMAIL = "testuser@pymeai.com"
PASSWORD = "password123"

def main():
    print("=== Prueba del Módulo de Clientes ===")
    
    # Paso 1: Iniciar sesión
    print("\n1. Iniciando sesión...")
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"Error al iniciar sesión: {login_response.text}")
        # Intentar registrar un usuario
        register_user()
        return
    
    token = login_response.json()["access_token"]
    print(f"Sesión iniciada correctamente. Token: {token[:20]}...")
    
    # Paso 2: Crear un cliente
    print("\n2. Creando un cliente...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    customer_data = {
        "first_name": f"Cliente {datetime.now().strftime('%H:%M:%S')}",
        "last_name": "Prueba",
        "email": f"cliente_{datetime.now().strftime('%H%M%S')}@example.com",
        "phone": "123-456-7890",
        "address": "Calle Principal 123",
        "segment": "VIP",
        "notes": "Cliente de prueba"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/customers/",
        headers=headers,
        json=customer_data
    )
    
    if create_response.status_code != 200:
        print(f"Error al crear cliente: {create_response.text}")
        return
    
    customer = create_response.json()
    customer_id = customer["id"]
    print(f"Cliente creado correctamente. ID: {customer_id}")
    print(f"Nombre: {customer['first_name']} {customer['last_name']}")
    print(f"Email: {customer['email']}")
    
    # Paso 3: Listar clientes
    print("\n3. Listando clientes...")
    list_response = requests.get(
        f"{BASE_URL}/customers/",
        headers=headers
    )
    
    if list_response.status_code != 200:
        print(f"Error al listar clientes: {list_response.text}")
        return
    
    customers = list_response.json()
    print(f"Se encontraron {len(customers)} clientes.")
    
    # Paso 4: Obtener un cliente específico
    print(f"\n4. Obteniendo cliente con ID {customer_id}...")
    get_response = requests.get(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers
    )
    
    if get_response.status_code != 200:
        print(f"Error al obtener cliente: {get_response.text}")
        return
    
    customer_detail = get_response.json()
    print(f"Cliente obtenido: {customer_detail['first_name']} {customer_detail['last_name']}")
    
    # Paso 5: Actualizar un cliente
    print(f"\n5. Actualizando cliente con ID {customer_id}...")
    update_data = {
        "first_name": f"ClienteActualizado {datetime.now().strftime('%H:%M:%S')}",
        "segment": "Regular"
    }
    
    update_response = requests.put(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code != 200:
        print(f"Error al actualizar cliente: {update_response.text}")
        return
    
    updated_customer = update_response.json()
    print(f"Cliente actualizado: {updated_customer['first_name']} {updated_customer['last_name']}")
    print(f"Nuevo segmento: {updated_customer['segment']}")
    
    # Paso 6: Eliminar un cliente
    print(f"\n6. Eliminando cliente con ID {customer_id}...")
    delete_response = requests.delete(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers
    )
    
    if delete_response.status_code != 200:
        print(f"Error al eliminar cliente: {delete_response.text}")
        return
    
    deleted_customer = delete_response.json()
    print(f"Cliente eliminado (inactivado): {deleted_customer['first_name']} {deleted_customer['last_name']}")
    print(f"Estado: {deleted_customer['status']}")
    
    print("\n=== Prueba completada con éxito ===")

def register_user():
    """Registrar un usuario si no existe"""
    print("Intentando registrar un usuario...")
    
    register_data = {
        "email": EMAIL,
        "password": PASSWORD,
        "first_name": "Test",
        "last_name": "User",
        "organization_name": "Test Organization"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if register_response.status_code != 200:
        print(f"Error al registrar usuario: {register_response.text}")
        return
    
    print("Usuario registrado correctamente.")
    main()  # Reintentar la prueba

if __name__ == "__main__":
    main()