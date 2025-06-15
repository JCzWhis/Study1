#!/usr/bin/env python3
"""
🧠 MedStudy Pro - Auto Installer
Configura toda la aplicación automáticamente
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil
import requests
import zipfile
import json

class MedStudyInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "web" / "backend"
        self.frontend_dir = self.base_dir / "web" / "frontend"
        self.system = platform.system().lower()
        
    def print_banner(self):
        print("""
┌──────────────────────────────────────────────────────────┐
│ 🧠 MedStudy Pro - Instalador Automático                 │
│                                                          │
│ Este script configurará todo automáticamente:           │
│ • Python dependencies                                   │
│ • Node.js y React (si está disponible)                  │
│ • Ollama y modelo phi3:mini                             │
│ • Base de datos y configuración                         │
│                                                          │
│ ⏳ Esto puede tomar 5-10 minutos...                     │
└──────────────────────────────────────────────────────────┘
        """)
    
    def install_python_deps(self):
        """Instalar dependencias Python"""
        print("📦 Instalando dependencias Python...")
        
        try:
            # Crear venv si no existe
            venv_path = self.base_dir / "venv"
            if not venv_path.exists():
                print("🔧 Creando entorno virtual...")
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            
            # Activar venv y instalar
            if self.system == "windows":
                pip_path = venv_path / "Scripts" / "pip.exe"
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
            
            # Instalar requirements
            subprocess.run([
                str(pip_path), "install", "-r", 
                str(self.backend_dir / "requirements.txt")
            ], check=True)
            
            print("✅ Dependencias Python instaladas")
            return str(python_path)
            
        except Exception as e:
            print(f"⚠️  Error instalando Python deps: {e}")
            return sys.executable
    
    def install_nodejs(self):
        """Verificar/instalar Node.js"""
        print("🟢 Verificando Node.js...")
        
        try:
            # Verificar si npm existe
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
            print("✅ Node.js ya está instalado")
            
            # Instalar dependencias React
            print("📦 Instalando dependencias React...")
            os.chdir(self.frontend_dir)
            subprocess.run(["npm", "install"], check=True)
            
            # Build para producción
            print("🔨 Compilando frontend...")
            subprocess.run(["npm", "run", "build"], check=True)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Node.js no encontrado - usando fallback estático")
            self.create_static_frontend()
            return False
    
    def create_static_frontend(self):
        """Crear frontend estático simple si no hay Node.js"""
        print("📁 Creando frontend estático...")
        
        static_dir = self.frontend_dir / "static"
        static_dir.mkdir(exist_ok=True)
        
        # HTML básico que conecta con la API
        html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedStudy Pro</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        function App() {
            const [data, setData] = useState(null);
            
            useEffect(() => {
                fetch('/api/health')
                    .then(res => res.json())
                    .then(setData);
            }, []);
            
            return (
                <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                    <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
                        <h1 className="text-3xl font-bold text-blue-600 mb-4">
                            🧠 MedStudy Pro
                        </h1>
                        <p className="text-gray-600 mb-4">
                            Sistema de Estudio Médico con IA Local
                        </p>
                        {data ? (
                            <div className="text-green-600">
                                ✅ Conectado al backend
                                <br />
                                Versión: {data.api_version}
                            </div>
                        ) : (
                            <div className="text-yellow-600">
                                ⏳ Conectando al backend...
                            </div>
                        )}
                        <div className="mt-4 space-y-2">
                            <a href="/api/docs" className="block text-blue-500 hover:underline">
                                📚 Ver API Documentation
                            </a>
                            <a href="/api/dashboard" className="block text-blue-500 hover:underline">
                                📊 Ver Dashboard Data
                            </a>
                        </div>
                    </div>
                </div>
            );
        }
        
        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>"""
        
        (static_dir / "index.html").write_text(html_content, encoding='utf-8')
        print("✅ Frontend estático creado")
    
    def install_ollama(self):
        """Instalar Ollama y modelo phi3"""
        print("🤖 Configurando Ollama...")
        
        try:
            # Verificar si Ollama ya está instalado
            result = subprocess.run(["ollama", "--version"], capture_output=True)
            if result.returncode == 0:
                print("✅ Ollama ya está instalado")
            else:
                raise FileNotFoundError
                
        except FileNotFoundError:
            print("📥 Descargando Ollama...")
            
            if self.system == "windows":
                print("🪟 Para Windows: Por favor descarga Ollama desde https://ollama.ai")
                print("   Después ejecuta: ollama serve")
                return False
            elif self.system == "darwin":  # macOS
                print("🍎 Para macOS: Por favor descarga Ollama desde https://ollama.ai")
                return False
            else:  # Linux
                try:
                    subprocess.run([
                        "curl", "-fsSL", "https://ollama.ai/install.sh"
                    ], shell=True, check=True)
                except:
                    print("⚠️  No se pudo instalar Ollama automáticamente")
                    return False
        
        # Descargar modelo phi3:mini
        try:
            print("📥 Descargando modelo phi3:mini (puede tomar varios minutos)...")
            subprocess.run(["ollama", "pull", "phi3:mini"], check=True)
            print("✅ Modelo phi3:mini instalado")
            return True
        except:
            print("⚠️  No se pudo descargar el modelo - se usará modo sin IA")
            return False
    
    def create_launcher_shortcuts(self, python_path):
        """Crear accesos directos para facilitar el uso"""
        print("🔗 Creando accesos directos...")
        
        # Script de Windows
        if self.system == "windows":
            bat_content = f"""@echo off
cd /d "{self.base_dir}"
"{python_path}" launch_medstudy.py
pause
"""
            (self.base_dir / "MedStudy.bat").write_text(bat_content)
            print("✅ Creado MedStudy.bat")
        
        # Script Unix
        else:
            sh_content = f"""#!/bin/bash
cd "{self.base_dir}"
"{python_path}" launch_medstudy.py
"""
            sh_file = self.base_dir / "MedStudy.sh"
            sh_file.write_text(sh_content)
            sh_file.chmod(0o755)
            print("✅ Creado MedStudy.sh")
    
    def create_config_files(self):
        """Crear archivos de configuración básicos"""
        print("⚙️  Creando configuración...")
        
        # .env para backend
        env_content = """# MedStudy Configuration
DATABASE_URL=sqlite:///./data/medstudy.db
SECRET_KEY=dev_secret_key_change_in_production
OLLAMA_BASE_URL=http://localhost:11434
EMBED_MODEL=paraphrase-multilingual-MiniLM-L12-v2
"""
        (self.backend_dir / ".env").write_text(env_content)
        
        # Crear directorio de datos
        (self.base_dir / "data").mkdir(exist_ok=True)
        (self.base_dir / "logs").mkdir(exist_ok=True)
        
        print("✅ Configuración creada")
    
    def run(self):
        """Ejecutar instalación completa"""
        try:
            self.print_banner()
            
            # 1. Python dependencies
            python_path = self.install_python_deps()
            
            # 2. Node.js (opcional)
            self.install_nodejs()
            
            # 3. Ollama
            self.install_ollama()
            
            # 4. Config files
            self.create_config_files()
            
            # 5. Shortcuts
            self.create_launcher_shortcuts(python_path)
            
            print("""
┌──────────────────────────────────────────────────────────┐
│ 🎉 ¡Instalación completada!                             │
│                                                          │
│ Para iniciar MedStudy Pro:                              │
│                                                          │""")
            
            if self.system == "windows":
                print("│ 🖱️  Doble clic en: MedStudy.bat                        │")
            else:
                print("│ 🖱️  Ejecuta: ./MedStudy.sh                             │")
                
            print("""│                                                          │
│ O ejecuta manualmente:                                  │
│ python launch_medstudy.py                               │
│                                                          │
│ 🌐 La app se abrirá en tu navegador automáticamente     │
└──────────────────────────────────────────────────────────┘
            """)
            
        except Exception as e:
            print(f"❌ Error durante la instalación: {e}")
            print("💡 Ejecuta: python launch_medstudy.py para intentar manualmente")

def main():
    installer = MedStudyInstaller()
    installer.run()

if __name__ == "__main__":
    main()