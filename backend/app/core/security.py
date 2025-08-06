# backend/app/core/security.py
"""
Módulo que proporciona funciones de seguridad para la aplicación.
Incluye hashing de contraseñas y generación/verificación de tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from passlib.context import CryptContext  # Para hash seguro de contraseñas
from jose import jwt  # Para generación y verificación de tokens JWT
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuraciones de seguridad desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "pymeai_secret_key")  # Clave para firmar tokens
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Algoritmo para JWT
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # Tiempo de expiración

# Contexto de hash para contraseñas
# Usamos bcrypt como algoritmo principal, que es seguro y resistente a ataques
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    
    Args:
        plain_password: La contraseña en texto plano
        hashed_password: El hash almacenado de la contraseña
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña.
    
    Args:
        password: La contraseña en texto plano
        
    Returns:
        str: El hash de la contraseña
    """
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso para un usuario.
    
    Args:
        subject: El identificador del usuario (normalmente el ID)
        expires_delta: Tiempo de expiración personalizado (opcional)
        
    Returns:
        str: El token JWT codificado
    """
    # Si no se proporciona un tiempo de expiración, usar el valor por defecto
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Datos a incluir en el token
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Codificar y firmar el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt