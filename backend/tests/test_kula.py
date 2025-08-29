# backend/tests/test_kula.py
"""
Script para probar el módulo de Kula (chatbot IA).
Ejecutar con: python -m tests.test_kula
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_kula@pymeai.com"
TEST_PASSWORD = "kula123!"

def main():
    print("=== Prueba del Módulo de Kula (Chatbot IA) ===")
    
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
    
    # Paso 3: Enviar una consulta a Kula
    print("\n2. Enviando consulta a Kula...")
    query_data = {
        "query": "Hola Kula, ¿puedes explicarme qué es PymeAI?"
    }
    
    query_response = requests.post(
        f"{BASE_URL}/kula/query",
        headers=headers,
        json=query_data
    )
    
    if query_response.status_code != 200:
        print(f"Error al enviar consulta: {query_response.text}")
        return
    
    query_result = query_response.json()
    conversation_id = query_result["conversation_id"]
    print(f"Consulta enviada correctamente. Conversación ID: {conversation_id}")
    print(f"Respuesta de Kula:")
    print(f"  {query_result['message']}")
    
    # Paso 4: Enviar una segunda consulta en la misma conversación
    print("\n3. Enviando segunda consulta a la misma conversación...")
    follow_up_data = {
        "query": "¿Qué módulos incluye PymeAI?",
        "conversation_id": conversation_id
    }
    
    follow_up_response = requests.post(
        f"{BASE_URL}/kula/query",
        headers=headers,
        json=follow_up_data
    )
    
    if follow_up_response.status_code != 200:
        print(f"Error al enviar segunda consulta: {follow_up_response.text}")
        return
    
    follow_up_result = follow_up_response.json()
    print(f"Segunda consulta enviada correctamente.")
    print(f"Respuesta de Kula:")
    print(f"  {follow_up_result['message']}")
    
    # Paso 5: Listar conversaciones
    print("\n4. Listando conversaciones...")
    conversations_response = requests.get(
        f"{BASE_URL}/kula/conversations",
        headers=headers
    )
    
    if conversations_response.status_code != 200:
        print(f"Error al listar conversaciones: {conversations_response.text}")
        return
    
    conversations = conversations_response.json()
    print(f"Se encontraron {len(conversations)} conversaciones.")
    if conversations:
        print(f"  Primera conversación: {conversations[0]['title']}")
    
    # Paso 6: Obtener mensajes de la conversación
    print("\n5. Obteniendo mensajes de la conversación...")
    messages_response = requests.get(
        f"{BASE_URL}/kula/conversations/{conversation_id}/messages",
        headers=headers
    )
    
    if messages_response.status_code != 200:
        print(f"Error al obtener mensajes: {messages_response.text}")
        return
    
    messages = messages_response.json()
    print(f"Se encontraron {len(messages)} mensajes.")
    for i, message in enumerate(messages):
        print(f"  Mensaje {i+1} ({message['role']}): {message['content'][:50]}...")
    
    # Paso 7: Obtener ayuda sobre un tema específico
    print("\n6. Obteniendo ayuda sobre 'clientes'...")
    help_response = requests.get(
        f"{BASE_URL}/kula/help/clientes",
        headers=headers
    )
    
    if help_response.status_code != 200:
        print(f"Error al obtener ayuda: {help_response.text}")
        return
    
    help_result = help_response.json()
    print(f"Ayuda obtenida correctamente.")
    print(f"Respuesta de Kula:")
    print(f"  {help_result['message'][:150]}...")
    
    # Paso 8: Archivar la conversación
    print("\n7. Archivando conversación...")
    archive_response = requests.delete(
        f"{BASE_URL}/kula/conversations/{conversation_id}",
        headers=headers
    )
    
    if archive_response.status_code != 204:
        print(f"Error al archivar conversación: {archive_response.text}")
        return
    
    print(f"Conversación archivada correctamente.")
    
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
            "last_name": "Kula",
            "organization_name": "Test Organization for Kula"
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