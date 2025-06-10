#!/usr/bin/env python3
"""
MedStudy Pro - Main Launcher (VERSIÓN ARREGLADA)
Punto de entrada principal con manejo robusto de errores y importaciones seguras
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# --- CONFIGURACIÓN INICIAL ---
def setup_path():
    """Configura el path del proyecto para importaciones correctas"""
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

def setup_basic_logging():
    """Configura logging básico antes de cargar el sistema completo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('MedStudy.Main')

# --- IMPORTACIONES SEGURAS ---
def safe_import():
    """Importa módulos core de manera segura"""
    imports = {
        'config': None,
        'database': None,
        'utils': None,
        'ui': None,
        'diagnostics': None
    }
    
    logger = logging.getLogger('MedStudy.SafeImport')
    
    # Importar configuración
    try:
        from app.config import config
        imports['config'] = config
        logger.info("✅ Configuration loaded")
    except ImportError as e:
        logger.error(f"❌ Config import failed: {e}")
        try:
            from utils.config import get_config
            imports['config'] = get_config()
            logger.info("✅ Fallback config loaded")
        except ImportError as e2:
            logger.error(f"❌ Fallback config failed: {e2}")
    
    # Importar database
    try:
        from core.database import DatabaseManager, initialize_database
        imports['database'] = (DatabaseManager, initialize_database)
        logger.info("✅ Database components loaded")
    except ImportError as e:
        logger.error(f"❌ Database import failed: {e}")
    
    # Importar utilidades
    try:
        from core.utils import run_system_diagnostic
        imports['utils'] = run_system_diagnostic
        logger.info("✅ Core utilities loaded")
    except ImportError as e:
        logger.error(f"❌ Core utils import failed: {e}")
        try:
            from utils.diagnostics import perform_system_diagnostics
            imports['utils'] = perform_system_diagnostics
            logger.info("✅ Fallback diagnostics loaded")
        except ImportError as e2:
            logger.error(f"❌ Fallback diagnostics failed: {e2}")
    
    # Importar UI
    try:
        from app.ui.main_window import MedStudyMainWindow
        imports['ui'] = MedStudyMainWindow
        logger.info("✅ Main UI loaded")
    except ImportError as e:
        logger.error(f"❌ Main UI import failed: {e}")
        try:
            # Fallback para UI simple
            import customtkinter as ctk
            
            class FallbackWindow(ctk.CTk):
                def __init__(self):
                    super().__init__()
                    self.title("MedStudy Pro - Modo Básico")
                    self.geometry("800x600")
                    
                    label = ctk.CTkLabel(
                        self,
                        text="MedStudy Pro\n\nModo Básico Activo\n\nAlgunos componentes no están disponibles.\nUsa 'python gradio_launcher.py' para la interfaz web.",
                        font=ctk.CTkFont(size=16),
                        justify="center"
                    )
                    label.pack(expand=True)
                    
                    btn = ctk.CTkButton(
                        self,
                        text="Lanzar Interfaz Web",
                        command=self.launch_web
                    )
                    btn.pack(pady=20)
                
                def launch_web(self):
                    import subprocess
                    try:
                        subprocess.Popen([sys.executable, "gradio_launcher.py"])
                        self.destroy()
                    except FileNotFoundError:
                        print("gradio_launcher.py no encontrado")
            
            imports['ui'] = FallbackWindow
            logger.info("✅ Fallback UI loaded")
        except ImportError as e2:
            logger.error(f"❌ Fallback UI failed: {e2}")
    
    return imports

# --- FUNCIONES DE DIAGNÓSTICO ---
def run_diagnostic(diagnostic_func, force_output=False):
    """Ejecuta diagnóstico del sistema"""
    logger = logging.getLogger('MedStudy.Diagnostic')
    
    if not diagnostic_func:
        logger.error("❌ No hay función de diagnóstico disponible")
        return False
    
    logger.info("🔍 Ejecutando diagnóstico del sistema...")
    
    try:
        results = diagnostic_func()
        
        if force_output or logger.level <= logging.INFO:
            print("\n" + "="*60)
            print("🔍 DIAGNÓSTICO DEL SISTEMA")
            print("="*60)
            
            # Python
            python_info = results.get('python_version', results.get('python', {}))
            if python_info:
                status = "✅" if python_info.get('is_compatible', False) else "❌"
                print(f"{status} Python: {python_info.get('version', 'unknown')}")
            
            # Ollama
            ollama_info = results.get('ollama_status', results.get('ollama', {}))
            if ollama_info:
                status = "✅" if ollama_info.get('running', False) else "❌"
                print(f"{status} Ollama: {ollama_info.get('host', 'unknown')}")
                
                model_status = "✅" if ollama_info.get('model_available', False) else "❌"
                print(f"{model_status} Modelo: {ollama_info.get('model', 'unknown')}")
            
            # Dependencias
            deps_info = results.get('dependencies', {})
            if deps_info:
                all_deps = deps_info.get('all_installed', False)
                status = "✅" if all_deps else "⚠️"
                print(f"{status} Dependencias: {'Todas instaladas' if all_deps else 'Algunas faltantes'}")
            
            # Estado general
            overall = results.get('overall_status', 'unknown')
            if overall == 'healthy':
                print("\n🎉 Sistema completamente funcional")
            else:
                print("\n⚠️ Sistema funcional con limitaciones")
                print("💡 Usa 'python setup.py' para resolver problemas")
            
            print("="*60)
        
        return overall == 'healthy' if 'overall_status' in results else True
        
    except Exception as e:
        logger.error(f"❌ Error en diagnóstico: {e}")
        return False

# --- FUNCIONES DE LANZAMIENTO ---
def launch_desktop_app(ui_class, config, force_launch=False):
    """Lanza la aplicación desktop"""
    logger = logging.getLogger('MedStudy.Desktop')
    
    if not ui_class:
        logger.error("❌ Clase UI no disponible")
        return False
    
    try:
        logger.info("🚀 Iniciando aplicación desktop...")
        
        # Verificar CustomTkinter
        try:
            import customtkinter as ctk
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
        except ImportError:
            logger.error("❌ CustomTkinter no disponible")
            return False
        
        # Crear y ejecutar aplicación
        if config:
            app = ui_class(config=config)
        else:
            app = ui_class()
        
        logger.info("✅ Aplicación desktop iniciada")
        app.mainloop()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error lanzando desktop: {e}")
        if not force_launch:
            logger.info("💡 Intenta: python main.py --web")
        return False

def launch_web_app():
    """Lanza la aplicación web como fallback"""
    logger = logging.getLogger('MedStudy.Web')
    
    try:
        logger.info("🌐 Lanzando interfaz web...")
        import subprocess
        
        # Verificar si gradio_launcher.py existe
        gradio_path = Path("gradio_launcher.py")
        if not gradio_path.exists():
            logger.error("❌ gradio_launcher.py no encontrado")
            return False
        
        # Lanzar en proceso separado
        process = subprocess.Popen([sys.executable, "gradio_launcher.py"])
        logger.info("✅ Interfaz web iniciada")
        
        # Esperar a que termine
        process.wait()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error lanzando web: {e}")
        return False

def show_help():
    """Muestra ayuda de uso"""
    help_text = """
🧠 MedStudy Pro - Medical Study Assistant

USO:
    python main.py [opciones]

OPCIONES:
    --diagnostic    Ejecutar diagnóstico del sistema
    --web          Lanzar interfaz web (Gradio)
    --force-launch Forzar lanzamiento ignorando errores
    --config-info  Mostrar información de configuración
    --help, -h     Mostrar esta ayuda

EJEMPLOS:
    python main.py                    # Lanzar aplicación desktop
    python main.py --diagnostic      # Solo diagnóstico
    python main.py --web             # Interfaz web
    python main.py --force-launch    # Forzar lanzamiento

RESOLUCIÓN DE PROBLEMAS:
    1. python setup.py               # Configuración automática
    2. python main.py --diagnostic   # Verificar sistema
    3. python main.py --web          # Interfaz web alternativa

SOPORTE:
    - Issues: GitHub repository
    - Docs: README.md
"""
    print(help_text)

def show_config_info(config):
    """Muestra información de configuración"""
    print("\n" + "="*50)
    print("⚙️ INFORMACIÓN DE CONFIGURACIÓN")
    print("="*50)
    
    if not config:
        print("❌ Configuración no disponible")
        return
    
    try:
        # Ollama config
        if hasattr(config, 'get_ollama_config'):
            ollama_config = config.get_ollama_config()
            print(f"🤖 Ollama Host: {ollama_config.get('host', 'unknown')}")
            print(f"🧠 Modelo: {ollama_config.get('model', 'unknown')}")
            print(f"⏱️ Timeout: {ollama_config.get('timeout', 'unknown')}s")
        
        # Window config
        if hasattr(config, 'get_window_config'):
            window_config = config.get_window_config()
            print(f"🖥️ Ventana: {window_config.get('width')}x{window_config.get('height')}")
        
        # Database
        if hasattr(config, 'get_database_url'):
            db_url = config.get_database_url()
            print(f"💾 Base de datos: {db_url}")
        
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
    
    print("="*50)

# --- FUNCIÓN PRINCIPAL ---
def main():
    """Función principal del launcher"""
    # Configuración inicial
    project_root = setup_path()
    logger = setup_basic_logging()
    
    logger.info("🧠 MedStudy Pro - Iniciando sistema...")
    logger.info(f"📁 Directorio: {project_root}")
    
    # Parse argumentos
    parser = argparse.ArgumentParser(description='MedStudy Pro - Medical Study Assistant')
    parser.add_argument('--diagnostic', action='store_true', help='Ejecutar diagnóstico del sistema')
    parser.add_argument('--web', action='store_true', help='Lanzar interfaz web')
    parser.add_argument('--force-launch', action='store_true', help='Forzar lanzamiento')
    parser.add_argument('--config-info', action='store_true', help='Mostrar información de configuración')
    
    args = parser.parse_args()
    
    # Mostrar ayuda si no hay argumentos
    if len(sys.argv) == 1:
        pass  # Comportamiento normal
    
    # Importaciones seguras
    logger.info("📦 Cargando módulos del sistema...")
    imports = safe_import()
    
    config = imports['config']
    ui_class = imports['ui']
    diagnostic_func = imports['utils']
    
    # Mostrar información de configuración
    if args.config_info:
        show_config_info(config)
        return 0
    
    # Ejecutar diagnóstico
    if args.diagnostic:
        success = run_diagnostic(diagnostic_func, force_output=True)
        return 0 if success else 1
    
    # Lanzar interfaz web
    if args.web:
        success = launch_web_app()
        return 0 if success else 1
    
    # Diagnóstico automático (si no es force-launch)
    if not args.force_launch:
        logger.info("🔍 Ejecutando verificación automática...")
        diagnostic_ok = run_diagnostic(diagnostic_func, force_output=False)
        
        if not diagnostic_ok:
            logger.warning("⚠️ Problemas detectados en el sistema")
            logger.info("💡 Opciones:")
            logger.info("   - python main.py --force-launch  (forzar lanzamiento)")
            logger.info("   - python main.py --web           (interfaz web)")
            logger.info("   - python setup.py               (configurar sistema)")
            
            # Intentar web como fallback
            user_input = input("\n¿Intentar lanzar interfaz web? [Y/n]: ")
            if user_input.lower() != 'n':
                return 0 if launch_web_app() else 1
            else:
                return 1
    
    # Lanzar aplicación desktop
    logger.info("🖥️ Iniciando aplicación desktop...")
    success = launch_desktop_app(ui_class, config, args.force_launch)
    
    if not success:
        logger.error("❌ Fallo al iniciar aplicación desktop")
        logger.info("💡 Intenta: python main.py --web")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        logger = logging.getLogger('MedStudy.Main')
        logger.error(f"💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)