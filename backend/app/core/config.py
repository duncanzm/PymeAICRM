# backend/app/core/config.py

import os
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración general
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    SERVER_NAME: str = "PymeAI"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Frontend URL para enlaces en correos electrónicos
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Configuración de base de datos
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "pymeai"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Configuración de correo electrónico
    EMAILS_ENABLED: bool = os.getenv("EMAILS_ENABLED", "True").lower() == "true"
    EMAILS_FROM_EMAIL: EmailStr = os.getenv("EMAILS_FROM_EMAIL", "noreply@pymeai.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "PymeAI")
    
    # Configuración SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.mailtrap.io")  # Usa Mailtrap para desarrollo
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()