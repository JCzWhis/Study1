import sys
import requests
import importlib.util
from pathlib import Path

def get_logger_safe():
    """Obtiene logger de manera segura"""
    try:
        from .logging import get_logger
        return get_logger(__name__)
    except ImportError:
        import logging
        return logging.getLogger(__name__)

def get_config_safe():
    """Obtiene config de manera segura"""
    try:
        from .config import get_config
        return get_config()
    except ImportError:
        return {
            "Ollama": {
                "host": "http://localhost:11434",
                "model": "phi3:mini",
                "timeout": 60
            }
        }

logger = get_logger_safe()

def check_python_version():
    """Verifica la versión de Python."""
    logger.info(f"Python version: {sys.version}")
    version_info = sys.version_info
    
    is_compatible = version_info >= (3, 8)
    
    return {
        'version': f"{version_info.major}.{version_info.minor}.{version_info.micro}",
        'is_compatible': is_compatible,
        'major': version_info.major,
        'minor': version_info.minor,
        'micro': version_info.micro
    }

def check_ollama_status():
    """Verifica conexión a Ollama y disponibilidad del modelo."""
    logger.info("--- Checking Ollama Status ---")
    config = get_config_safe()
    ollama_settings = config.get('Ollama', {})

    ollama_host = ollama_settings.get('host', 'http://localhost:11434')
    model_name = ollama_settings.get('model', 'phi3:mini')
    timeout = ollama_settings.get('timeout', 60)

    result = {
        'host': ollama_host,
        'model': model_name,
        'running': False,
        'model_available': False,
        'error': None
    }

    logger.info(f"Attempting to connect to Ollama host: {ollama_host}")
    
    try:
        response = requests.get(ollama_host, timeout=min(timeout/2, 10))
        if response.status_code == 200:
            logger.info(f"Ollama connection successful. Response: {response.text.strip()}")
            result['running'] = True

            # Check model availability
            logger.info(f"Checking for model: '{model_name}' using Ollama API...")
            try:
                show_api_url = f"{ollama_host}/api/show"
                api_response = requests.post(
                    show_api_url, 
                    json={"name": model_name}, 
                    timeout=timeout
                )

                if api_response.status_code == 200:
                    logger.info(f"Ollama model '{model_name}' is available.")
                    result['model_available'] = True
                elif api_response.status_code == 404:
                    logger.error(f"Ollama model '{model_name}' NOT FOUND.")
                    result['error'] = f"Model {model_name} not found"
                else:
                    logger.error(f"Failed to get model details. Status: {api_response.status_code}")
                    result['error'] = f"Model check failed: {api_response.status_code}"
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking model '{model_name}': {e}")
                result['error'] = f"Model check error: {str(e)}"
        else:
            logger.error(f"Ollama connection failed. Status: {response.status_code}")
            result['error'] = f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.error(f"Ollama connection timed out.")
        result['error'] = "Connection timeout"
    except requests.exceptions.ConnectionError:
        logger.error(f"Ollama connection failed. Could not connect to {ollama_host}")
        result['error'] = "Connection refused"
    except Exception as e:
        logger.error(f"Unexpected error connecting to Ollama: {e}")
        result['error'] = str(e)

    return result

def check_dependencies():
    """Verifica dependencias core de Python."""
    logger.info("--- Checking Core Dependencies ---")
    
    dependencies = [
        "customtkinter",
        "requests",
        "gradio",
        "sentence_transformers",
        "PIL",  # Pillow
        "fitz",  # PyMuPDF
        "chromadb"
    ]
    
    results = {}
    
    for dep_name in dependencies:
        try:
            spec = importlib.util.find_spec(dep_name)
            if spec is None:
                logger.error(f"Dependency '{dep_name}': NOT FOUND")
                results[dep_name] = {'installed': False, 'error': 'Not found'}
            else:
                logger.info(f"Dependency '{dep_name}': Found")
                results[dep_name] = {'installed': True}
        except Exception as e:
            logger.error(f"Error checking '{dep_name}': {e}")
            results[dep_name] = {'installed': False, 'error': str(e)}

    all_found = all(dep.get('installed', False) for dep in results.values())
    
    if all_found:
        logger.info("All core dependencies are installed.")
    else:
        logger.warning("Some core dependencies are missing.")
    
    return {
        'all_installed': all_found,
        'dependencies': results
    }

def check_file_structure():
    """Verifica estructura de archivos del proyecto"""
    logger.info("--- Checking File Structure ---")
    
    project_root = Path.cwd()
    
    required_files = [
        "main.py",
        "requirements.txt",
        "config_template.ini"
    ]
    
    required_dirs = [
        "app",
        "core", 
        "utils",
        "data",
        "logs"
    ]
    
    results = {
        'files': {},
        'directories': {},
        'all_present': True
    }
    
    # Check files
    for file_name in required_files:
        file_path = project_root / file_name
        exists = file_path.exists()
        results['files'][file_name] = exists
        if not exists:
            results['all_present'] = False
            logger.warning(f"Required file missing: {file_name}")
        else:
            logger.info(f"Found: {file_name}")
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        results['directories'][dir_name] = exists
        if not exists:
            results['all_present'] = False
            logger.warning(f"Required directory missing: {dir_name}")
        else:
            logger.info(f"Found directory: {dir_name}")
    
    return results

def perform_system_diagnostics():
    """Ejecuta todos los chequeos de diagnóstico."""
    logger.info("======== Starting System Diagnostics ========")

    results = {
        "python_version": check_python_version(),
        "ollama_status": check_ollama_status(),
        "dependencies": check_dependencies(),
        "file_structure": check_file_structure()
    }

    logger.info("======== System Diagnostics Complete ========")

    # Determine overall health
    checks = [
        results["python_version"]["is_compatible"],
        results["ollama_status"]["running"],
        results["dependencies"]["all_installed"],
        results["file_structure"]["all_present"]
    ]
    
    all_ok = all(checks)
    
    if all_ok:
        logger.info("All diagnostic checks passed successfully!")
    else:
        logger.warning("Some diagnostic checks failed. Please review the logs.")

    results["overall_status"] = "healthy" if all_ok else "issues_detected"
    return results
