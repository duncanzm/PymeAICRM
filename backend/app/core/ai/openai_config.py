# backend/app/core/ai/openai_config.py
"""
Configuración para la integración con OpenAI.
"""
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Clase para la configuración de OpenAI
class OpenAIConfig:
    """
    Configuración para la API de OpenAI.
    """
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    @classmethod
    def get_config(cls):
        """
        Devuelve la configuración como diccionario.
        """
        return {
            "api_key": cls.api_key,
            "model": cls.model,
            "temperature": cls.temperature,
            "max_tokens": cls.max_tokens
        }
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida que la configuración esté completa.
        """
        return bool(cls.api_key)