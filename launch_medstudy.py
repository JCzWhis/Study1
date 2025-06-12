#!/usr/bin/env python3
"""
🧠 MedStudy Pro - Auto Launcher
Inicia toda la aplicación con un solo comando
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path
import signal
import psutil

class MedStudyLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "web" / "backend"
        self.frontend_dir = self.base_dir / "web" / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.ollama_process = None
        
    def print_banner(self):
        print("""
┌──────────────────────────────────────────────────────────┐
│ 🧠 MedStudy Pro - Sistema de Estudio Médico con IA      │
│                                                          │
│ 🚀 Iniciando aplicación automáticamente...              │
│ ⏳ Este proceso puede tomar 30-60 segundos              │
└──────────────────────────────────────────────────────────┘
        """)
    
    def check_dependencies(self):
        """Verificar dependencias y instalar si es necesario"""
        print("🔍 Verificando dependencias...")
        
        # Verificar Python
        if sys.version_info < (3, 8):
            print("❌ Necesitas Python 3.8 o superior")
            return False
            
        # Verificar si ya tenemos las dependencias instaladas
        try:
            import fastapi, uvicorn, chromadb, sentence_transformers
            print("✅ Dependencias Python encontradas")
        except ImportError:
            print("📦 Instalando dependencias Python...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.backend_dir / "requirements.txt")
            ], check=True)
            
        # Verificar Node.js y npm (para desarrollo)
        try:
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
            print("✅ Node.js encontrado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Node.js no encontrado - usando build estático")
            
        return True
    
    def check_ollama(self):
        """Verificar si Ollama está corriendo"""
        print("🤖 Verificando Ollama...")
        
        try:
            # Verificar si Ollama está corriendo
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if "phi3" in result.stdout:
                print("✅ Ollama y phi3:mini encontrados")
                return True
            else:
                print("📥 Descargando modelo phi3:mini...")
                subprocess.run(["ollama", "pull", "phi3:mini"], check=True)
                return True
                
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠️  Ollama no encontrado - usando modo sin IA")
            return False
    
    def start_backend(self):
        """Iniciar backend FastAPI"""
        print("🔧 Iniciando backend...")
        
        # Cambiar al directorio backend
        os.chdir(self.backend_dir)
        
        # Iniciar FastAPI
        self.backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que el backend esté listo
        self.wait_for_service("http://127.0.0.1:8000", "Backend")
        
    def start_frontend(self):
        """Iniciar frontend - usar npm dev o servir archivos estáticos"""
        print("🌐 Iniciando frontend...")
        
        os.chdir(self.frontend_dir)
        
        # Intentar con npm start primero
        try:
            # Verificar si hay node_modules
            if (self.frontend_dir / "node_modules").exists():
                self.frontend_process = subprocess.Popen([
                    "npm", "start"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.wait_for_service("http://127.0.0.1:3000", "Frontend")
                return
        except:
            pass
            
        # Fallback: servir con Python
        print("📁 Sirviendo frontend con Python...")
        os.chdir(self.frontend_dir / "build" if (self.frontend_dir / "build").exists() else self.frontend_dir / "public")
        
        self.frontend_process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.wait_for_service("http://127.0.0.1:3000", "Frontend")
    
    def wait_for_service(self, url, service_name):
        """Esperar a que un servicio esté disponible"""
        import requests
        
        for i in range(30):  # 30 segundos máximo
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {service_name} listo en {url}")
                    return True
            except:
                pass
                
            print(f"⏳ Esperando {service_name}... ({i+1}/30)")
            time.sleep(1)
            
        print(f"❌ {service_name} no pudo iniciarse")
        return False
    
    def open_browser(self):
        """Abrir navegador automáticamente"""
        print("🌍 Abriendo navegador...")
        time.sleep(2)  # Esperar un poco más
        webbrowser.open("http://127.0.0.1:3000")
        
    def cleanup(self):
        """Limpiar procesos al cerrar"""
        print("\n🛑 Cerrando aplicación...")
        
        if self.backend_process:
            self.backend_process.terminate()
            
        if self.frontend_process:
            self.frontend_process.terminate()
            
        # Matar procesos en puertos específicos
        self.kill_port(8000)
        self.kill_port(3000)
        
        print("✅ Aplicación cerrada correctamente")
    
    def kill_port(self, port):
        """Matar proceso en puerto específico"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                for conn in proc.info['connections'] or []:
                    if conn.laddr.port == port:
                        proc.terminate()
                        break
        except:
            pass
    
    def run(self):
        """Ejecutar launcher principal"""
        try:
            self.print_banner()
            
            # 1. Verificar dependencias
            if not self.check_dependencies():
                input("❌ Presiona Enter para salir...")
                return
                
            # 2. Verificar Ollama
            self.check_ollama()
            
            # 3. Iniciar backend
            self.start_backend()
            
            # 4. Iniciar frontend  
            self.start_frontend()
            
            # 5. Abrir navegador
            threading.Thread(target=self.open_browser, daemon=True).start()
            
            print("""
┌──────────────────────────────────────────────────────────┐
│ 🎉 ¡MedStudy Pro está corriendo!                        │
│                                                          │
│ 🌐 Frontend: http://127.0.0.1:3000                      │
│ 🔧 Backend:  http://127.0.0.1:8000                      │
│ 📚 API Docs: http://127.0.0.1:8000/api/docs             │
│                                                          │
│ 💡 Presiona Ctrl+C para cerrar la aplicación            │
└──────────────────────────────────────────────────────────┘
            """)
            
            # 6. Mantener corriendo
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.cleanup()

def main():
    launcher = MedStudyLauncher()
    launcher.run()

if __name__ == "__main__":
    main()