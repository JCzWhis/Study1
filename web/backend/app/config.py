"""
Configuration settings for MedStudy Pro
"""

import os
from typing import Optional

class Settings:
    """Application settings and configuration."""
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma2:2b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "90"))
    
    # Alternative models (for easy switching)
    AVAILABLE_MODELS = {
        "gemma2:2b": {
            "name": "Gemma 3-2B",
            "description": "Google's Gemma 3-2B model - Fast and efficient for medical content",
            "timeout": 90,
            "system_prompt_language": "english"
        },
        "phi3:mini": {
            "name": "Phi-3 Mini",
            "description": "Microsoft's Phi-3 Mini model - Compact and capable",
            "timeout": 60,
            "system_prompt_language": "spanish"
        },
        "llama3.2:1b": {
            "name": "Llama 3.2 1B",
            "description": "Meta's Llama 3.2 1B model - Ultra-fast responses",
            "timeout": 45,
            "system_prompt_language": "english"
        },
        "llama3.2:3b": {
            "name": "Llama 3.2 3B", 
            "description": "Meta's Llama 3.2 3B model - Balanced performance",
            "timeout": 75,
            "system_prompt_language": "english"
        }
    }
    
    # RAG Configuration
    RAG_DATA_DIR: str = os.getenv("RAG_DATA_DIR", "./data/medical_rag")
    RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    RAG_N_RESULTS: int = int(os.getenv("RAG_N_RESULTS", "5"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/medstudy.db")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # Application Configuration
    APP_NAME: str = "MedStudy Pro API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema de Planificación Retrospectiva para Medicina con IA Local"
    
    @classmethod
    def get_model_config(cls, model_name: Optional[str] = None) -> dict:
        """Get configuration for a specific model."""
        model = model_name or cls.OLLAMA_MODEL
        return cls.AVAILABLE_MODELS.get(model, cls.AVAILABLE_MODELS["gemma2:2b"])
    
    @classmethod
    def is_model_available(cls, model_name: str) -> bool:
        """Check if a model is in the available models list."""
        return model_name in cls.AVAILABLE_MODELS
    
    @classmethod
    def get_available_models_list(cls) -> list:
        """Get list of available models with details."""
        return [
            {
                "model_id": model_id,
                **config
            }
            for model_id, config in cls.AVAILABLE_MODELS.items()
        ]

# Global settings instance
settings = Settings()