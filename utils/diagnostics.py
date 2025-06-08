import sys
import requests
import importlib.util # For a cleaner way to check module availability

# Assuming these utils are in the same package or sys.path is set up correctly
from .config import get_config
from .logging import get_logger # Use our configured logger

logger = get_logger(__name__) # Get a logger for this module

def check_python_version():
    """Logs the current Python version."""
    logger.info(f"Python version: {sys.version}")
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        logger.warning(f"Python version is {version_info.major}.{version_info.minor}. Recommend Python 3.8+ for broader compatibility.")
    return True # Simple success

def check_ollama_status():
    """Checks connection to Ollama and configured model availability."""
    logger.info("--- Checking Ollama Status ---")
    config = get_config()
    ollama_settings = config.get('Ollama', {})

    ollama_host = ollama_settings.get('host', 'http://localhost:11434')
    model_name = ollama_settings.get('model', 'phi3:mini')
    timeout = ollama_settings.get('timeout', 60)

    logger.info(f"Attempting to connect to Ollama host: {ollama_host}")
    try:
        response = requests.get(ollama_host, timeout=timeout/2) # Shorter timeout for initial ping
        if response.status_code == 200:
            logger.info(f"Ollama connection successful. Response: {response.text.strip()}")

            logger.info(f"Checking for model: '{model_name}' using Ollama API...")
            # More robust check using /api/show
            # Note: Ollama versions before 0.1.15 might not have /api/show in this exact way
            # For broader compatibility, one might need to list all models and check,
            # but /api/show is cleaner if available.
            try:
                show_api_url = f"{ollama_host}/api/show"
                api_response = requests.post(show_api_url, json={"name": model_name}, timeout=timeout)

                if api_response.status_code == 200:
                    logger.info(f"Ollama model '{model_name}' is available and details received.")
                    # You could log model details here: api_response.json()
                    return True
                elif api_response.status_code == 404: # Model not found
                    logger.error(f"Ollama model '{model_name}' NOT FOUND. Please pull it: `ollama pull {model_name}`")
                    return False
                else:
                    logger.error(f"Failed to get model details for '{model_name}'. Status: {api_response.status_code}. Response: {api_response.text[:200]}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Error when trying to check model '{model_name}' via Ollama API: {e}")
                logger.warning("This might indicate an issue with the Ollama API version or network.")
                return False
        else:
            logger.error(f"Ollama connection failed. Status: {response.status_code}. Response: {response.text[:200]}")
            logger.error("Please ensure Ollama service is running and accessible at the configured host.")
            return False
    except requests.exceptions.Timeout:
        logger.error(f"Ollama connection timed out when trying to reach {ollama_host}.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Ollama connection failed. Could not connect to {ollama_host}. Ensure Ollama is running.")
        return False
    except Exception as e: # Catch any other requests-related errors
        logger.error(f"An unexpected error occurred while trying to connect to Ollama: {e}")
        return False

def check_dependencies():
    """Checks for core Python dependencies using importlib."""
    logger.info("--- Checking Core Dependencies ---")
    # Dependencies from requirements.txt / README
    dependencies = [
        "customtkinter",
        "requests",
        "gradio",
        "sentence_transformers",
        "PyPDF2",
        "docx" # python-docx is imported as 'docx'
    ]
    all_found = True
    for dep_name in dependencies:
        spec = importlib.util.find_spec(dep_name)
        if spec is None:
            logger.error(f"Dependency '{dep_name}': NOT FOUND. Please install it (e.g., via requirements.txt).")
            all_found = False
        else:
            logger.info(f"Dependency '{dep_name}': Found.")

    if all_found:
        logger.info("All core dependencies seem to be installed.")
    else:
        logger.warning("Some core dependencies are missing. Please install them to ensure full functionality.")
    return all_found

# Add more checks here as needed, e.g., file permissions, specific tool versions, etc.

def perform_system_diagnostics():
    """Runs all diagnostic checks and logs the results."""
    logger.info("======== Starting System Diagnostics ========")

    results = {
        "python_version": check_python_version(),
        "ollama_status": check_ollama_status(),
        "dependencies": check_dependencies(),
    }

    logger.info("======== System Diagnostics Complete ========")

    all_ok = all(results.values())
    if all_ok:
        logger.info("All diagnostic checks passed successfully!")
    else:
        logger.warning("Some diagnostic checks failed. Please review the logs above for details.")

    return all_ok

if __name__ == '__main__':
    # This allows running diagnostics directly, e.g., python utils/diagnostics.py
    # Ensure logging is set up (it should be by importing .logging)
    print("Running MedStudy Pro System Diagnostics directly...")
    perform_system_diagnostics()
    print("\nDiagnostic run finished. Check console output and log file for details.")
