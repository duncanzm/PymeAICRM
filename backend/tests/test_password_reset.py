# backend/tests/test_password_reset.py
"""
Script simple para probar el flujo de restablecimiento de contraseña.
Ejecutar con: python -m tests.test_password_reset
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_password_reset@pymeai.com"  # Email específico para este módulo
INITIAL_PASSWORD = "InitialPassword123!"
NEW_PASSWORD = "NewPassword456!"  # Contraseña nueva para probar

def main():
    print("=== Prueba del Flujo de Restablecimiento de Contraseña ===")
    
    # Asegurarnos de que existe un usuario para probar
    ensure_user_exists()
    
    # Paso 1: Solicitar restablecimiento de contraseña
    print("\n1. Solicitando restablecimiento de contraseña...")
    
    request_data = {
        "email": TEST_EMAIL
    }
    
    # En la sección donde solicitas el restablecimiento de contraseña
    request_response = requests.post(
        f"{BASE_URL}/password-reset/request-reset",
        json=request_data
    )

    if request_response.status_code != 200:
        print(f"Error al solicitar restablecimiento: {request_response.text}")
        return

    print(f"Respuesta: {request_response.status_code}")
    print(f"Mensaje: {request_response.json().get('message')}")

    # Obtener el token directamente de la respuesta para desarrollo
    token = request_response.json().get('debug_token')
    if token:
        print(f"\nToken obtenido de la respuesta: {token}")
        print(f"Link de restablecimiento: {request_response.json().get('reset_link')}")
    else:
        # En caso de que el token no esté en la respuesta (producción)
        print("\nEn un entorno real, ahora revisarías tu correo electrónico.")
        print("Para esta prueba, revisa los logs del servidor para ver el token simulado.")
        print("Busca una línea que contenga: [EMAIL] Contenido: ...")
        token = input("\nIngresa el token del correo simulado: ")
        
    # Paso 2: Verificar token y establecer nueva contraseña
    print("\n2. Verificando token y estableciendo nueva contraseña...")
    
    verify_data = {
        "token": token,
        "new_password": NEW_PASSWORD,
        "confirm_password": NEW_PASSWORD
    }
    
    verify_response = requests.post(
        f"{BASE_URL}/password-reset/verify-reset",
        json=verify_data
    )
    
    if verify_response.status_code != 200:
        print(f"Error al verificar token: {verify_response.text}")
        return
    
    print(f"Respuesta: {verify_response.status_code}")
    print(f"Mensaje: {verify_response.json().get('message')}")
    
    # Paso 3: Probar inicio de sesión con nueva contraseña
    print("\n3. Probando inicio de sesión con nueva contraseña...")
    time.sleep(1)  # Pequeña pausa para asegurarnos que todo se ha actualizado
    
    login_data = {
        "username": TEST_EMAIL,
        "password": NEW_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("¡Éxito! Inicio de sesión correcto con la nueva contraseña.")
        print(f"Token: {token[:20]}...")
    else:
        print(f"Error al iniciar sesión: {login_response.text}")
    
    print("\n=== Prueba completa ===")

def ensure_user_exists():
    """
    Asegurarse de que existe un usuario para probar.
    Primero intenta iniciar sesión, si falla, registra un usuario nuevo.
    """
    login_data = {
        "username": TEST_EMAIL,
        "password": INITIAL_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print("El usuario de prueba no existe o la contraseña ha cambiado.")
        print("Intentando registrar un usuario nuevo...")
        
        register_data = {
            "email": TEST_EMAIL,
            "password": INITIAL_PASSWORD,
            "first_name": "Test",
            "last_name": "Password Reset",
            "organization_name": "Test Organization for Password Reset"
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