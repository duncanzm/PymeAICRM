# backend/tests/test_invitations.py
"""
Script simple para probar la gestión de invitaciones a miembros del equipo.
Ejecutar con: python -m tests.test_invitations
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = "test_invitations@pymeai.com"  # Email específico para este módulo
ADMIN_PASSWORD = "TestInvitations123!"
NEW_USER_EMAIL = f"newmember_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"  # Usando timestamp para hacerlo único

def main():
    print("=== Prueba de Gestión de Invitaciones ===")
    
    # Paso 1: Asegurar que existe un usuario administrador para pruebas
    print("\n1. Asegurando que existe un usuario administrador para pruebas...")
    ensure_admin_exists()
    
    # Paso 2: Iniciar sesión como administrador
    print("\n2. Iniciando sesión como administrador...")
    
    login_data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
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
    
    # Paso 3: Crear una invitación
    print(f"\n3. Creando invitación para {NEW_USER_EMAIL}...")
    
    invitation_data = {
        "email": NEW_USER_EMAIL,
        "role": "user",
        "custom_permissions": {
            "customers": ["read", "write"],
            "opportunities": ["read"]
        }
    }
    
    invitation_response = requests.post(
        f"{BASE_URL}/invitations/",
        headers=headers,
        json=invitation_data
    )
    
    if invitation_response.status_code != 200:
        print(f"Error al crear invitación: {invitation_response.text}")
        return
    
    invitation = invitation_response.json()
    invitation_id = invitation["id"]
    print(f"Invitación creada correctamente. ID: {invitation_id}")
    print(f"Email: {invitation['email']}")
    print(f"Rol: {invitation['role']}")
    print(f"Expira: {invitation['expires_at']}")
    
    # Paso 4: Listar invitaciones activas
    print("\n4. Listando invitaciones activas...")
    
    list_response = requests.get(
        f"{BASE_URL}/invitations/",
        headers=headers
    )
    
    if list_response.status_code != 200:
        print(f"Error al listar invitaciones: {list_response.text}")
        return
    
    invitations = list_response.json()
    print(f"Se encontraron {len(invitations)} invitaciones activas.")
    
    # Buscar el token de la invitación creada
    invitation_token = None
    for inv in invitations:
        if inv["id"] == invitation_id:
            # En un caso real, obtendríamos el token del email
            # Aquí hacemos una trampa y lo obtenemos de la base de datos
            # o pedimos al usuario que lo ingrese manualmente
            print("\nEn un entorno real, el token estaría en el email enviado.")
            print("Para esta prueba, necesitamos obtener el token de la invitación.")
            print("Opciones:")
            print("1. Verificar los logs del servidor para ver el email simulado")
            print("2. Consultar directamente la base de datos")
            token_input = input("\n¿Tienes el token de la invitación? (S/N): ")
            
            if token_input.upper() == "S":
                invitation_token = input("Ingresa el token: ")
            else:
                print("Sin el token, no podemos continuar con la prueba de aceptación.")
                # Aquí podríamos implementar una consulta directa a la base de datos
                # pero eso requeriría configuración adicional
    
    # Paso 5: Verificar la invitación (opcional, solo si tenemos el token)
    if invitation_token:
        print(f"\n5. Verificando la invitación con token: {invitation_token[:10]}...")
        
        verify_response = requests.get(
            f"{BASE_URL}/invitations/verify/{invitation_token}",
        )
        
        if verify_response.status_code != 200:
            print(f"Error al verificar invitación: {verify_response.text}")
        else:
            verify_data = verify_response.json()
            print(f"Invitación válida: {verify_data['valid']}")
            print(f"Email: {verify_data['email']}")
            print(f"Rol: {verify_data['role']}")
            print(f"Organización: {verify_data['organization_name']}")
        
        # Paso 6: Aceptar la invitación
        print("\n6. Aceptando la invitación...")
        
        accept_data = {
            "token": invitation_token,
            "first_name": "Nuevo",
            "last_name": "Miembro",
            "password": "Password123!"
        }
        
        accept_response = requests.post(
            f"{BASE_URL}/invitations/accept",
            json=accept_data
        )
        
        if accept_response.status_code != 200:
            print(f"Error al aceptar invitación: {accept_response.text}")
        else:
            accept_data = accept_response.json()
            print(f"Invitación aceptada: {accept_data['message']}")
            print(f"Nuevo usuario creado: {accept_data['user']['first_name']} {accept_data['user']['last_name']}")
            print(f"Email: {accept_data['user']['email']}")
            print(f"Rol: {accept_data['user']['role']}")
            
            # Probar inicio de sesión con el nuevo usuario
            print("\n7. Probando inicio de sesión con el nuevo usuario...")
            
            new_login_data = {
                "username": NEW_USER_EMAIL,
                "password": "Password123!"
            }
            
            new_login_response = requests.post(f"{BASE_URL}/auth/login", data=new_login_data)
            
            if new_login_response.status_code == 200:
                new_token = new_login_response.json()["access_token"]
                print("¡Éxito! Inicio de sesión correcto con el nuevo usuario.")
                print(f"Token: {new_token[:20]}...")
            else:
                print(f"Error al iniciar sesión con nuevo usuario: {new_login_response.text}")
    
    # Paso 7 (alternativo): Cancelar la invitación
    # Si no tenemos el token o queremos probar la cancelación
    else:
        print(f"\n5. Cancelando la invitación con ID {invitation_id}...")
        
        cancel_response = requests.delete(
            f"{BASE_URL}/invitations/{invitation_id}",
            headers=headers
        )
        
        if cancel_response.status_code != 200:
            print(f"Error al cancelar invitación: {cancel_response.text}")
            return
        
        print("Invitación cancelada correctamente.")
        
        # Verificar que la lista de invitaciones activas ya no incluye la cancelada
        print("\n6. Verificando que la invitación ya no está activa...")
        
        list_response = requests.get(
            f"{BASE_URL}/invitations/",
            headers=headers
        )
        
        if list_response.status_code != 200:
            print(f"Error al listar invitaciones: {list_response.text}")
            return
        
        invitations = list_response.json()
        invitation_found = any(inv["id"] == invitation_id for inv in invitations)
        
        if not invitation_found:
            print("✅ Correcto: La invitación cancelada ya no aparece en la lista de invitaciones activas.")
        else:
            print("❌ Error: La invitación cancelada sigue apareciendo como activa.")
    
    print("\n=== Prueba completa ===")

def ensure_admin_exists():
    """
    Asegurarse de que existe un usuario administrador para pruebas.
    Primero intenta iniciar sesión, si falla, registra un usuario nuevo.
    """
    login_data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print("El usuario administrador de prueba no existe o la contraseña ha cambiado.")
        print("Intentando registrar un usuario nuevo...")
        
        register_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "first_name": "Test",
            "last_name": "Invitations",
            "organization_name": "Test Organization for Invitations"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if register_response.status_code == 200:
            print("Usuario administrador registrado correctamente.")
        else:
            print(f"Error al registrar usuario: {register_response.text}")
            print("Continuando con el usuario existente (posiblemente con otra contraseña).")
    else:
        print("Usuario administrador de prueba existe. Continuando...")

if __name__ == "__main__":
    main()