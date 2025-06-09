
#!/usr/bin/env python3
"""
MedStudy Pro - Asistente de Lanzamiento
Script inteligente que guía al usuario paso a paso
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🧠 MedStudy Pro                           ║
║              Medical Study Assistant with Local AI          ║
║                                                              ║
║               Asistente de Lanzamiento Inteligente          ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Verifica versión de Python"""
    print("🔍 Verificando versión de Python...")
    
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requiere Python 3.8+")
        print("   📥 Descarga Python desde: https://www.python.org/downloads/")
        return False

def check_dependencies():
    """Verifica dependencias básicas"""
    print("\n📦 Verificando dependencias...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("   ❌ requirements.txt no encontrado")
        return False
    
    # Try to import basic dependencies
    basic_deps = ["customtkinter", "requests"]
    missing = []
    
    for dep in basic_deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - Faltante")
            missing.append(dep)
    
    if missing:
        print(f"\n   🔧 Instalando dependencias faltantes...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("   ✅ Dependencias instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error instalando dependencias: {e}")
            return False
    
    return True

def check_ollama():
    """Verifica Ollama"""
    print("\n🤖 Verificando Ollama...")
    
    try:
        # Check if ollama command exists
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Ollama instalado: {result.stdout.strip()}")
            
            # Check if service is running
            try:
                import requests
                response = requests.get("http://localhost:11434", timeout=3)
                if response.status_code == 200:
                    print("   ✅ Servicio Ollama corriendo")
                    
                    # Check model
                    model_response = requests.post(
                        "http://localhost:11434/api/show",
                        json={"name": "phi3:mini"},
                        timeout=10
                    )
                    
                    if model_response.status_code == 200:
                        print("   ✅ Modelo phi3:mini disponible")
                        return True
                    else:
                        print("   ❌ Modelo phi3:mini no encontrado")
                        return "missing_model"
                else:
                    print("   ❌ Servicio Ollama no responde")
                    return "service_down"
            except:
                print("   ❌ No se puede conectar a Ollama")
                return "service_down"
        else:
            print("   ❌ Ollama no instalado")
            return "not_installed"
            
    except FileNotFoundError:
        print("   ❌ Ollama no encontrado")
        return "not_installed"

def setup_ollama():
    """Guía para configurar Ollama"""
    print("\n🛠️ Configurando Ollama...")
    
    status = check_ollama()
    
    if status == "not_installed":
        print("""
   📋 Para instalar Ollama:
   
   Windows/Mac:
   1. Visita: https://ollama.ai
   2. Descarga e instala Ollama
   3. Reinicia tu terminal
   
   Linux:
   1. Ejecuta: curl https://ollama.ai/install.sh | sh
   
   Después de instalar, vuelve a ejecutar este script.
        """)
        return False
    
    elif status == "service_down":
        print("""
   🚀 Para iniciar Ollama:
   
   1. Abre una nueva terminal/cmd
   2. Ejecuta: ollama serve
   3. Mantén esa terminal abierta
   4. Continúa aquí...
        """)
        
        input("   Presiona Enter cuando hayas iniciado 'ollama serve'...")
        return check_ollama() == True
    
    elif status == "missing_model":
        print("   📥 Descargando modelo phi3:mini (esto puede tomar unos minutos)...")
        
        try:
            result = subprocess.run(["ollama", "pull", "phi3:mini"], 
                                  capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print("   ✅ Modelo phi3:mini descargado exitosamente")
                return True
            else:
                print(f"   ❌ Error descargando modelo: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("   ⏰ Descarga interrumpida por timeout")
            return False
    
    return status == True

def launch_application():
    """Lanza la aplicación"""
    print("\n🚀 Iniciando MedStudy Pro...")
    
    print("   Ejecutando diagnóstico del sistema...")
    
    try:
        # Run diagnostics first
        result = subprocess.run([sys.executable, "main.py", "--diagnostic"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Diagnóstico exitoso")
            
            print("\n🎉 ¡Todo listo! Iniciando aplicación...")
            
            # Launch main application
            subprocess.run([sys.executable, "main.py"])
            
        else:
            print("   ⚠️ Diagnóstico reportó problemas")
            print("\n🌐 Intentando lanzar interfaz web como alternativa...")
            
            try:
                subprocess.run([sys.executable, "gradio_launcher.py"])
            except KeyboardInterrupt:
                print("\n👋 Aplicación cerrada por el usuario")
            except FileNotFoundError:
                print("   ❌ gradio_launcher.py no encontrado")
                
    except subprocess.TimeoutExpired:
        print("   ⏰ Diagnóstico interrumpido por timeout")
        print("   🚀 Intentando lanzar aplicación directamente...")
        
        try:
            subprocess.run([sys.executable, "main.py", "--force-launch"])
        except KeyboardInterrupt:
            print("\n👋 Aplicación cerrada por el usuario")

def interactive_setup():
    """Setup interactivo completo"""
    print_banner()
    
    # Step 1: Python version
    if not check_python_version():
        input("\nPresiona Enter para salir...")
        return False
    
    # Step 2: Dependencies
    if not check_dependencies():
        print("\n❌ No se pudieron instalar las dependencias")
        input("Presiona Enter para salir...")
        return False
    
    # Step 3: Ollama setup
    ollama_ready = setup_ollama()
    
    if not ollama_ready:
        print("\n⚠️ Ollama no está completamente configurado")
        choice = input("¿Continuar sin Ollama? (La IA no funcionará) [y/N]: ")
        
        if choice.lower() != 'y':
            print("👋 Setup cancelado. Configura Ollama y vuelve a intentar.")
            return False
    
    # Step 4: Launch
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*60)
    
    if ollama_ready:
        print("🎯 Sistema completamente funcional con IA")
    else:
        print("⚠️ Sistema funcional sin IA (Ollama no configurado)")
    
    print("\n🚀 ¿Lanzar MedStudy Pro ahora?")
    choice = input("Presiona Enter para continuar o 'n' para salir: ")
    
    if choice.lower() == 'n':
        print("👋 Puedes lanzar MedStudy Pro más tarde con: python main.py")
        return True
    
    launch_application()
    return True

def main():
    """Función principal del asistente"""
    try:
        success = interactive_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())