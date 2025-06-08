import configparser
import os

CONFIG_FILE_NAME = "config.ini"
CONFIG_TEMPLATE_FILE_NAME = "config_template.ini" # Fallback if config.ini is not found

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

    # Determine which file to load
    # Prefer config.ini, then config_template.ini
    # Assumes these files are in the root directory relative to where main.py is run

    # Get the directory of the current script (config.py)
    # Then go up one level to get the project root (assuming utils is in the root)
    # This makes it more robust to where the script is called from
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_file_path = os.path.join(project_root, config_filename)
    template_file_path = os.path.join(project_root, template_filename)

    loaded_path = None
    if os.path.exists(config_file_path):
        loaded_path = config_file_path
    elif os.path.exists(template_file_path):
        loaded_path = template_file_path
        print(f"INFO: '{config_filename}' not found. Loading from '{template_filename}'.")
    else:
        print(f"WARN: Neither '{config_filename}' nor '{template_filename}' found in '{project_root}'. Using default values.")
        # Return hardcoded defaults if no config file is found
        return {
            "Ollama": {
                "host": "http://localhost:11434",
                "model": "phi3:mini",
                "timeout": "60" # Keep as string like configparser does, or convert
            },
            "App": {
                "default_interface": "auto",
                "default_port": "7860",
                "debug_mode": "False"
            },
            "Paths": {
                "database_file": "data/medstudy.db",
                "documents_path": "data/documents/",
                "log_file": "logs/app.log"
            },
            "Development": {
                "gemini_api_key": "",
                "anthropic_api_key": ""
            }
        }

    try:
        parser.read(loaded_path)
        print(f"INFO: Configuration loaded successfully from '{loaded_path}'.")
    except configparser.Error as e:
        print(f"ERROR: Could not parse configuration file '{loaded_path}': {e}")
        # Consider raising an exception or returning defaults
        return {} # Or the hardcoded defaults as above

    # Convert ConfigParser object to a dictionary
    config_dict = {section: dict(parser.items(section)) for section in parser.sections()}

    # Type conversion for known numeric/boolean values for convenience
    # This could be made more robust or configurable
    if 'Ollama' in config_dict:
        config_dict['Ollama']['timeout'] = int(config_dict['Ollama'].get('timeout', 60))

    if 'App' in config_dict:
        config_dict['App']['default_port'] = int(config_dict['App'].get('default_port', 7860))
        debug_mode_str = config_dict['App'].get('debug_mode', 'False').lower()
        config_dict['App']['debug_mode'] = debug_mode_str in ['true', '1', 't', 'yes']

    return config_dict

if __name__ == '__main__':
    # For testing purposes
    print("Attempting to load configuration...")
    config = get_config()

    if config:
        print("\nLoaded Configuration:")
        for section, settings in config.items():
            print(f"  [{section}]")
            for key, value in settings.items():
                print(f"    {key} = {value} (type: {type(value).__name__})")

        # Example of accessing a specific value
        print(f"\nOllama host: {config.get('Ollama', {}).get('host')}")
        print(f"App debug mode: {config.get('App', {}).get('debug_mode')}")
    else:
        print("\nConfiguration could not be loaded.")
