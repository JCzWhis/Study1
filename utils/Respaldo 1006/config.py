import configparser
import os
from pathlib import Path

CONFIG_FILE_NAME = "config.ini"
CONFIG_TEMPLATE_FILE_NAME = "config_template.ini"

# Store loaded config globally to avoid reloading
_config = None
_config_loaded = False

def get_config():
    """
    Returns the loaded configuration dictionary.
    Loads the configuration if it hasn't been loaded yet.
    """
    global _config, _config_loaded
    if not _config_loaded:
        _config = load_config()
        _config_loaded = True
    return _config

def load_config(config_filename=CONFIG_FILE_NAME, template_filename=CONFIG_TEMPLATE_FILE_NAME):
    """
    Loads configuration from the specified INI file.
    Falls back to the template file if the main config file is not found.
    Returns a dictionary representing the configuration.
    """
    parser = configparser.ConfigParser()

    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    config_file_path = project_root / config_filename
    template_file_path = project_root / template_filename

    loaded_path = None
    if config_file_path.exists():
        loaded_path = config_file_path
    elif template_file_path.exists():
        loaded_path = template_file_path
        print(f"INFO: '{config_filename}' not found. Loading from '{template_filename}'.")
    else:
        print(f"WARN: Neither '{config_filename}' nor '{template_filename}' found. Using default values.")
        return get_default_config()

    try:
        parser.read(loaded_path)
        print(f"INFO: Configuration loaded successfully from '{loaded_path}'.")
    except configparser.Error as e:
        print(f"ERROR: Could not parse configuration file '{loaded_path}': {e}")
        return get_default_config()

    # Convert ConfigParser object to a dictionary
    config_dict = {section: dict(parser.items(section)) for section in parser.sections()}

    # Type conversion for known numeric/boolean values
    if 'Ollama' in config_dict:
        try:
            config_dict['Ollama']['timeout'] = int(config_dict['Ollama'].get('timeout', 60))
        except ValueError:
            config_dict['Ollama']['timeout'] = 60

    if 'App' in config_dict:
        try:
            config_dict['App']['default_port'] = int(config_dict['App'].get('default_port', 7860))
        except ValueError:
            config_dict['App']['default_port'] = 7860
        
        debug_mode_str = config_dict['App'].get('debug_mode', 'False').lower()
        config_dict['App']['debug_mode'] = debug_mode_str in ['true', '1', 't', 'yes']

    return config_dict

def get_default_config():
    """Retorna configuración por defecto"""
    return {
        "Ollama": {
            "host": "http://localhost:11434",
            "model": "phi3:mini",
            "timeout": 60
        },
        "App": {
            "default_interface": "desktop",
            "window_width": 1400,
            "window_height": 900,
            "debug_mode": False
        },
        "Paths": {
            "database_file": "data/medstudy.db",
            "documents_path": "data/documents/",
            "images_path": "data/images/",
            "log_file": "logs/app.log"
        },
        "Study": {
            "session_duration": 45,
            "break_duration": 15,
            "active_recall_interval": 10,
            "quiz_questions": 10,
            "exam_questions": 45
        },
        "SRS": {
            "initial_interval": 1,
            "success_multiplier": 2.5,
            "failure_multiplier": 0.6,
            "max_interval": 365
        }
    }