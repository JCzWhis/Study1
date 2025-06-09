"""
MedStudy Pro - Utils Package
Utilidades y herramientas auxiliares del sistema
"""

# Importaciones principales para facilitar el uso
try:
    from .config import get_config, load_config
    from .logging import get_logger, setup_logging
    from .diagnostics import perform_system_diagnostics, check_ollama_status
    
    __all__ = [
        'get_config', 'load_config',
        'get_logger', 'setup_logging', 
        'perform_system_diagnostics', 'check_ollama_status'
    ]
    
except ImportError as e:
    # Manejo graceful de errores de importación
    print(f"Warning: Some utils modules could not be imported: {e}")
    __all__ = []

# Metadata del paquete
__version__ = "1.0.0"
__author__ = "Dr. Cruz Migueles"