"""
MedStudy Pro - Logging utilities
Configuración de logging simple y robusta
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# Global flag para evitar configuración múltiple
_logging_configured = False

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado
    """
    global _logging_configured
    
    if not _logging_configured:
        setup_logging()
        _logging_configured = True
    
    return logging.getLogger(name)

def setup_logging(log_level=logging.INFO):
    """Configura logging básico"""
    global _logging_configured
    
    if _logging_configured:
        return
    
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler para archivo
    try:
        file_handler = logging.FileHandler(
            log_dir / "medstudy.log", 
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file logger: {e}")
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    _logging_configured = True

# Configurar automáticamente al importar
if not _logging_configured:
    setup_logging()