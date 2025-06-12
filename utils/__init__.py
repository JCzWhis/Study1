"""
MedStudy Pro - Utils Package
Utilidades y herramientas auxiliares del sistema
"""

# Importaciones seguras
_available_modules = []

try:
    from .config import get_config, load_config
    _available_modules.extend(['get_config', 'load_config'])
except ImportError as e:
    print(f"Warning: Config utilities not available: {e}")

try:
    from .logging import get_logger, setup_logging
    _available_modules.extend(['get_logger', 'setup_logging'])
except ImportError as e:
    print(f"Warning: Logging utilities not available: {e}")

try:
    from .diagnostics import perform_system_diagnostics, check_ollama_status
    _available_modules.extend(['perform_system_diagnostics', 'check_ollama_status'])
except ImportError as e:
    print(f"Warning: Diagnostics utilities not available: {e}")

# Export only what's available
__all__ = _available_modules

# Metadata del paquete
__version__ = "1.0.0"
__author__ = "Dr. Cruz Migueles"

print(f"Utils package loaded with {len(_available_modules)} available modules: {_available_modules}")