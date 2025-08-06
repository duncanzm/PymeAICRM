# backend/tests/test_sessions.py
"""
Script simple para probar la gestión de sesiones.
Ejecutar con: python -m tests.test_sessions
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_sessions@pymeai.com"  # Email específico para este módulo
TEST_PASSWORD = "TestSessions123!"

def main():
    print("=== Prueba de Gestión de Sesiones ===")
    
    # Asegurarnos de que existe un usuario para pruebas
    ensure_user_exists()
    
    # Paso 1: Iniciar sesión para obtener un token
    print("\n1. Iniciando sesión (primera sesión)...")
    
    session1 = requests.Session()
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = session1.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"Error al iniciar sesión: {login_response.text}")
        return
    
    token1 = login_response.json()["access_token"]
    print(f"Sesión 1 iniciada. Token: {token1[:20]}...")
    
    # Esperar un poco para distinguir las sesiones
    time.sleep(2)
    
    # Paso 2: Iniciar una segunda sesión (simulando otro dispositivo)
    print("\n2. Iniciando una segunda sesión (simulando otro dispositivo)...")
    
    session2 = requests.Session()
    login_response2 = session2.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response2.status_code != 200:
        print(f"Error al iniciar segunda sesión: {login_response2.text}")
        return
    
    token2 = login_response2.json()["access_token"]
    print(f"Sesión 2 iniciada. Token: {token2[:20]}...")
    
    # Paso 3: Listar todas las sesiones activas
    print("\n3. Listando todas las sesiones activas...")
    
    headers1 = {
        "Authorization": f"Bearer {token1}"
    }
    
    sessions_response = session1.get(f"{BASE_URL}/sessions/", headers=headers1)
    
    if sessions_response.status_code != 200:
        print(f"Error al listar sesiones: {sessions_response.text}")
        return
    
    sessions = sessions_response.json()
    print(f"Se encontraron {len(sessions)} sesiones activas:")
    
    for i, session in enumerate(sessions):
        print(f"  Sesión {i+1}:")
        print(f"    ID: {session['id']}")
        print(f"    Dispositivo: {session['device_info']}")
        print(f"    IP: {session['ip_address']}")
        print(f"    Última actividad: {session['last_activity']}")
        print(f"    Creada: {session['created_at']}")
        print(f"    ¿Sesión actual?: {'Sí' if session['is_current'] else 'No'}")
    
    # Obtener IDs de sesión para usar más adelante
    current_session_id = None
    other_session_id = None
    
    for session in sessions:
        if session['is_current']:
            current_session_id = session['id']
        else:
            other_session_id = session['id']
    
    # Paso 4: Cerrar una sesión específica (la segunda)
    if other_session_id:
        print(f"\n4. Cerrando la sesión con ID {other_session_id}...")
        
        close_response = session1.delete(f"{BASE_URL}/sessions/{other_session_id}", headers=headers1)
        
        if close_response.status_code != 200:
            print(f"Error al cerrar sesión: {close_response.text}")
        else:
            print(f"Sesión cerrada: {close_response.json()['message']}")
        
        # Intentar usar el token de la sesión cerrada
        print("\n   Verificando que la sesión cerrada ya no funciona...")
        headers2 = {
            "Authorization": f"Bearer {token2}"
        }
        
        verify_response = session2.get(f"{BASE_URL}/sessions/", headers=headers2)
        
        if verify_response.status_code == 401:
            print("   ✅ Correcto: No se puede usar el token de la sesión cerrada")
        else:
            print(f"   ❌ Error: Se pudo usar el token de la sesión cerrada (status: {verify_response.status_code})")
    
    # Paso 5: Iniciar varias sesiones adicionales
    print("\n5. Iniciando varias sesiones adicionales...")
    sessions = []
    
    for i in range(3):
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            sessions.append((session, token))
            print(f"   Sesión adicional {i+1} iniciada.")
        
        # Pequeña pausa para distinguir las sesiones
        time.sleep(1)
    
    # Listar todas las sesiones para verificar
    sessions_response = session1.get(f"{BASE_URL}/sessions/", headers=headers1)
    
    if sessions_response.status_code == 200:
        active_sessions = sessions_response.json()
        print(f"\n   Ahora hay {len(active_sessions)} sesiones activas.")
    
    # Paso 6: Cerrar todas las sesiones excepto la actual
    print("\n6. Cerrando todas las sesiones excepto la actual...")
    
    close_all_except_response = session1.delete(f"{BASE_URL}/sessions/all/except-current", headers=headers1)
    
    if close_all_except_response.status_code != 200:
        print(f"Error al cerrar sesiones: {close_all_except_response.text}")
    else:
        print(f"Sesiones cerradas: {close_all_except_response.json()['message']}")
    
    # Verificar que solo queda una sesión activa
    sessions_response = session1.get(f"{BASE_URL}/sessions/", headers=headers1)
    
    if sessions_response.status_code == 200:
        active_sessions = sessions_response.json()
        print(f"   Ahora hay {len(active_sessions)} sesiones activas.")
    
    # Paso 7: Cerrar todas las sesiones (incluida la actual)
    print("\n7. Cerrando todas las sesiones (incluida la actual)...")
    
    close_all_response = session1.delete(f"{BASE_URL}/sessions/all", headers=headers1)
    
    if close_all_response.status_code != 200:
        print(f"Error al cerrar todas las sesiones: {close_all_response.text}")
    else:
        print(f"Todas las sesiones cerradas: {close_all_response.json()['message']}")
    
    # Verificar que la sesión actual ya no funciona
    print("\n   Verificando que la sesión actual ya no funciona...")
    verify_response = session1.get(f"{BASE_URL}/sessions/", headers=headers1)
    
    if verify_response.status_code == 401:
        print("   ✅ Correcto: No se puede usar el token de la sesión actual")
    else:
        print(f"   ❌ Error: Se pudo usar el token de la sesión actual (status: {verify_response.status_code})")
    
    print("\n=== Prueba completa ===")

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
            "last_name": "Sessions",
            "organization_name": "Test Organization for Sessions"
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