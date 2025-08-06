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
TEST_EMAIL = "test_customer_module@pymeai.com"
TEST_PASSWORD = "TestPassword123!"

def main():
    print("=== Prueba del Módulo de Clientes ===")
    
    # Intentar iniciar sesión con el usuario de prueba
    print("\n1. Intentando iniciar sesión con usuario de prueba...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"No se pudo iniciar sesión: {login_response.text}")
        print("Intentando registrar el usuario de prueba...")
        
        # Registrar el usuario de prueba
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "first_name": "Test",
            "last_name": "Customer Module",
            "organization_name": "Test Organization for Customer Module"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if register_response.status_code != 200:
            print(f"Error al registrar usuario: {register_response.text}")
            print("¿El usuario ya existe con otra contraseña? Considera eliminar el usuario o usar otro email.")
            return
        
        print("Usuario de prueba registrado correctamente.")
        
        # Iniciar sesión con el usuario recién creado
        login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"Error inesperado al iniciar sesión después del registro: {login_response.text}")
            return
    
    token = login_response.json()["access_token"]
    print(f"Sesión iniciada correctamente. Token: {token[:20]}...")
    
    # Paso 2: Crear un cliente
    print("\n2. Creando un cliente...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Usar un timestamp para hacer únicos los datos del cliente en cada ejecución
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    customer_data = {
        "first_name": f"Cliente {timestamp}",
        "last_name": "Prueba",
        "email": f"cliente_{timestamp}@example.com",
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
        "first_name": f"ClienteActualizado {timestamp}",
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
    
    # Paso 7: Limpiar datos de prueba
    # Aquí se limpiarían los datos creados durante la prueba
    # (Esto requeriría endpoints adicionales)
    # Por ahora, solo eliminamos los clientes, que ya hicimos en el paso 6
    
    print("\n=== Prueba completada con éxito ===")

if __name__ == "__main__":
    main()