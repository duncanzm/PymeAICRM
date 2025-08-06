# backend/app/db/base.py
"""
Este archivo configura la conexión a la base de datos PostgreSQL usando SQLAlchemy.
Define el motor de base de datos, la sesión y la clase base para los modelos.
"""

from sqlalchemy import create_engine  # Para crear el motor de la base de datos
from sqlalchemy.ext.declarative import declarative_base  # Para crear la clase base de los modelos
from sqlalchemy.orm import sessionmaker  # Para crear la fábrica de sesiones
import os
from dotenv import load_dotenv  # Para cargar variables de entorno desde .env

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la URL de conexión a la base de datos desde variables de entorno
# Si no está definida, usar una URL por defecto para desarrollo
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pymeai:pymeaidev@localhost:5432/pymeai")

# Por si acaso la URL viene con formato para async, convertirla a formato estándar
if DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

# Crear el motor de base de datos
# Este es el componente central que establece la conexión con la base de datos
engine = create_engine(DATABASE_URL)

# Crear una fábrica de sesiones
# Las sesiones son el medio principal para trabajar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para los modelos declarativos
# Todos los modelos heredarán de esta clase
Base = declarative_base()

# Función para obtener una sesión de base de datos
# Esta función se usará como dependencia en FastAPI
def get_db():
    """
    Crea una nueva sesión de base de datos para cada petición
    y la cierra cuando la petición termina.
    Se usa como dependencia en los endpoints de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db  # La sesión estará disponible durante la ejecución del endpoint
    finally:
        db.close()  # La sesión se cierra automáticamente al terminar