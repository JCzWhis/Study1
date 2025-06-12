#!/usr/bin/env python3
"""
MedStudy Pro - Setup Script
Script para configurar automáticamente el entorno de desarrollo
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Mostrar header del setup"""
    print("=" * 60)
    print("🧠 MedStudy Pro - Setup & Installation")
    print("   Medical Study Assistant with Local AI")
    print("   By Dr. Cruz Migueles")
    print("=" * 60)
    print()

def check_python_version():
    """Verificar versión de Python"""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 11):
        print("❌ Python 3.11+ required!")
        print("   Please upgrade Python and try again.")
        return False
    
    print("✅ Python version OK")
    return True

def install_dependencies():
    """Instalar dependencias de Python"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        # Actualizar pip primero
        print("   Updating pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        print("   Installing requirements...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Failed to install dependencies:")
            print(result.stderr)
            return False
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_ollama():
    """Verificar instalación de Ollama"""
    print("\n🤖 Checking Ollama installation...")
    
    try:
        # Verificar si ollama comando existe
        result = subprocess.run(["ollama", "--version"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Ollama found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command not found")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama not installed")
        return False

def install_ollama_instructions():
    """Mostrar instrucciones para instalar Ollama"""
    print("\n📋 Ollama Installation Instructions:")
    print("=" * 40)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("1. Download Ollama from: https://ollama.ai")
        print("2. Run the installer (ollama-windows-amd64.exe)")
        print("3. Restart your terminal/command prompt")
        print("4. Run: ollama serve")
        print("5. In another terminal: ollama pull phi3:mini")
    
    elif system == "darwin":  # macOS
        print("1. Download Ollama from: https://ollama.ai")
        print("2. Install the .dmg file")
        print("3. Open Terminal and run: ollama serve")
        print("4. In another terminal: ollama pull phi3:mini")
    
    else:  # Linux
        print("1. Run: curl https://ollama.ai/install.sh | sh")
        print("2. Start Ollama: ollama serve")
        print("3. Download model: ollama pull phi3:mini")
    
    print("\nAfter installation, run this setup script again.")

def test_ollama_connection():
    """Probar conexión con Ollama"""
    print("\n🔌 Testing Ollama connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except ImportError:
        print("⚠️  Cannot test connection (requests not installed yet)")
        return False

def check_ollama_model():
    """Verificar si el modelo phi3:mini está disponible"""
    print("\n🧠 Checking phi3:mini model...")
    
    try:
        import requests
        response = requests.post(
            "http://localhost:11434/api/show",
            json={"name": "phi3:mini"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ phi3:mini model is available")
            return True
        elif response.status_code == 404:
            print("❌ phi3:mini model not found")
            print("   Run: ollama pull phi3:mini")
            return False
        else:
            print(f"❌ Error checking model: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Cannot check model: {e}")
        return False

def create_directories():
    """Crear directorios necesarios"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "data",
        "data/documents",
        "data/images", 
        "data/embeddings",
        "data/user_progress",
        "data/backups",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print("✅ Directories created")

def create_config_file():
    """Crear archivo de configuración si no existe"""
    print("\n⚙️  Setting up configuration...")
    
    config_file = Path("config.ini")
    template_file = Path("config_template.ini")
    
    if config_file.exists():
        print("✅ config.ini already exists")
        return True
    
    if template_file.exists():
        import shutil
        shutil.copy2(template_file, config_file)
        print("✅ Created config.ini from template")
        return True
    else:
        # Crear config básico
        config_content = """[Ollama]
host = http://localhost:11434
model = phi3:mini
timeout = 60

[App]
default_interface = desktop
window_width = 1400
window_height = 900
theme = medical
debug_mode = False

[Paths]
database_file = data/medstudy.db
documents_path = data/documents/
images_path = data/images/
log_file = logs/app.log

[Study]
session_duration = 45
break_duration = 15
active_recall_interval = 10
quiz_questions = 10
exam_questions = 45

[SRS]
initial_interval = 1
success_multiplier = 2.5
failure_multiplier = 0.6
max_interval = 365
"""
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print("✅ Created basic config.ini")
        return True

def run_quick_test():
    """Ejecutar test rápido del sistema"""
    print("\n🧪 Running quick system test...")
    
    try:
        # Ejecutar quick_test.py si existe
        if Path("quick_test.py").exists():
            result = subprocess.run([sys.executable, "quick_test.py"], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Quick test passed")
                return True
            else:
                print("⚠️  Quick test had issues:")
                print(result.stdout)
                return False
        else:
            print("⚠️  quick_test.py not found, skipping")
            return True
            
    except Exception as e:
        print(f"⚠️  Error running quick test: {e}")
        return False

def print_next_steps():
    """Mostrar próximos pasos"""
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("=" * 30)
    print("1. Start Ollama service:")
    print("   ollama serve")
    print()
    print("2. Download the AI model (in another terminal):")
    print("   ollama pull phi3:mini")
    print()
    print("3. Launch MedStudy Pro:")
    print("   python main.py")
    print()
    print("4. Or run diagnostics first:")
    print("   python main.py --diagnostic")
    print()
    print("🔗 For help: https://github.com/your-repo/Study1")

def main():
    """Función principal del setup"""
    print_header()
    
    success_count = 0
    total_steps = 7
    
    # 1. Verificar Python
    if check_python_version():
        success_count += 1
    
    # 2. Instalar dependencias
    if install_dependencies():
        success_count += 1
    
    # 3. Verificar Ollama
    ollama_installed = check_ollama()
    if ollama_installed:
        success_count += 1
    else:
        install_ollama_instructions()
    
    # 4. Probar conexión Ollama
    if ollama_installed and test_ollama_connection():
        success_count += 1
    elif ollama_installed:
        print("   Note: Start Ollama with 'ollama serve' and try again")
    
    # 5. Verificar modelo
    if ollama_installed and check_ollama_model():
        success_count += 1
    
    # 6. Crear directorios
    create_directories()
    success_count += 1
    
    # 7. Crear configuración
    if create_config_file():
        success_count += 1
    
    # Test rápido
    run_quick_test()
    
    # Resumen
    print(f"\n📊 Setup Summary: {success_count}/{total_steps} steps completed")
    
    if success_count >= 6:  # Todo excepto posiblemente Ollama
        print_next_steps()
    else:
        print("\n⚠️  Some setup steps failed. Please resolve issues and run setup again.")
        sys.exit(1)

if __name__ == "__main__":
    main()