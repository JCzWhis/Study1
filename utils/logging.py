"""
MedStudy Pro - Logging utilities
Configuración de logging mejorada y compatible
"""

import logging
import os
import sys
from pathlib import Path

# Global flag to ensure setup_logging is called only once
_logging_configured = False

def get_config_safe():
    """Obtiene configuración de manera segura sin dependencias circulares"""
    try:
        from .config import get_config
        return get_config()
    except ImportError:
        # Fallback si hay problemas de importación circular
        return {
            "Paths": {"log_file": "logs/app.log"},
            "App": {"debug_mode": False}
        }

def setup_logging():
    """
    Configures the logging for the application based on settings
    from config.ini (via utils.config).
    """
    global _logging_configured
    if _logging_configured:
        return

    config = get_config_safe()
    log_settings = config.get("Paths", {})
    app_settings = config.get("App", {})

    log_file_path = log_settings.get("log_file", "logs/app.log")
    debug_mode = app_settings.get("debug_mode", False)

    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print(f"INFO: Log directory '{log_dir}' created.")
        except OSError as e:
            print(f"ERROR: Could not create log directory '{log_dir}': {e}. Logging to console only.")
            log_file_path = None

    # Basic configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Remove any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler (if path is valid)
    if log_file_path:
        try:
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            print(f"INFO: Logging configured. Level: {logging.getLevelName(log_level)}. File: '{log_file_path}'")
        except Exception as e:
            print(f"ERROR: Could not set up file logger for '{log_file_path}': {e}. Logging to console only.")
    else:
        print(f"INFO: Logging configured. Level: {logging.getLevelName(log_level)}. Console only.")

    _logging_configured = True

def get_logger(name):
    """
    Returns a logger instance with the specified name.
    Ensures logging is set up before returning the logger.
    """
    if not _logging_configured:
        setup_logging()
    return logging.getLogger(name)

# Automatically configure logging when this module is first imported
if not _logging_configured:
    setup_logging()

if __name__ == '__main__':
    print("Testing logging setup...")
    
    logger = get_logger("LoggingTest")
    
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    
    another_logger = get_logger("AnotherModule")
    another_logger.info("Message from another logger.")
    
    print("Logging test completed.")