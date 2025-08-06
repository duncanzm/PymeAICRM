# backend/alembic/env.py
"""
Este archivo configura el entorno de Alembic para las migraciones.
Se encarga de conectar Alembic con la base de datos y los modelos.
"""

from logging.config import fileConfig  # Para configurar el logging

from sqlalchemy import engine_from_config  # Para crear el motor de base de datos
from sqlalchemy import pool  # Para la gestión de conexiones

from alembic import context  # Contexto de Alembic

# Añadir el directorio raíz al path de Python para poder importar desde app
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la clase Base y los modelos
# Es importante importar todos los modelos para que Alembic los detecte
from app.db.base import Base
from app.models.organization import Organization
from app.models.user import User

# Obtener el objeto de configuración de Alembic
config = context.config

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

# Obtener la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pymeai:pymeaidev@localhost:5432/pymeai")

# Asegurarse de que la URL no tiene el prefijo async
if DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

# Configurar la URL en Alembic
section = config.config_ini_section
config.set_section_option(section, "sqlalchemy.url", DATABASE_URL)

# Configurar el logging según alembic.ini
fileConfig(config.config_file_name)

# Metadata para la detección automática de modelos
# Esto permite a Alembic detectar cambios en los modelos automáticamente
target_metadata = Base.metadata

def run_migrations_offline():
    """
    Ejecuta migraciones en modo 'offline'.
    
    Este modo configura el contexto solo con una URL y no con un motor,
    lo que significa que no necesitamos una conexión DBAPI disponible.
    
    Las llamadas a context.execute() emitirán la cadena dada al script de salida.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Ejecuta migraciones en modo 'online'.
    
    En este escenario, necesitamos crear un motor y asociar una conexión con el contexto.
    """
    # Crear el motor de base de datos
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True  # Detecta cambios en tipos de columnas
        )

        with context.begin_transaction():
            context.run_migrations()

# Determinar el modo y ejecutar las migraciones
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()