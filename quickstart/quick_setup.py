#!/usr/bin/env python3
"""
🚀 MedStudy Pro - Quick Setup Script
Configura todo el sistema en un comando
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# Colors for console output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Print colored message"""
    print(f"{color}{message}{Colors.END}")

def run_command(command, cwd=None, shell=True):
    """Run command and return success status"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_command(command):
    """Check if command exists"""
    return shutil.which(command) is not None

def main():
    print_colored("🏥 MedStudy Pro - Quick Setup", Colors.BOLD + Colors.BLUE)
    print_colored("=" * 40, Colors.BLUE)
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print_colored(f"📍 Project root: {project_root}", Colors.CYAN)
    
    # Step 1: Check dependencies
    print_colored("\n🔍 Checking dependencies...", Colors.YELLOW)
    
    dependencies = {
        "python3": "Python 3.11+",
        "node": "Node.js 16+",
        "npm": "npm package manager",
        "ollama": "Ollama AI runtime"
    }
    
    missing_deps = []
    for cmd, desc in dependencies.items():
        if check_command(cmd):
            print_colored(f"✅ {desc} found", Colors.GREEN)
        else:
            print_colored(f"❌ {desc} not found", Colors.RED)
            missing_deps.append(desc)
    
    if missing_deps:
        print_colored(f"\n❌ Missing dependencies: {', '.join(missing_deps)}", Colors.RED)
        print_colored("Please install them and run setup again.", Colors.YELLOW)
        return False
    
    # Step 2: Setup Django backend
    print_colored("\n🚀 Setting up Django backend...", Colors.YELLOW)
    
    django_dir = project_root / "medstudy_app"
    setup_script = django_dir / "setup_django_medstudy.py"
    
    if setup_script.exists():
        success, stdout, stderr = run_command(
            f"python {setup_script}",
            cwd=django_dir
        )
        if success:
            print_colored("✅ Django backend setup completed", Colors.GREEN)
        else:
            print_colored(f"❌ Django setup failed: {stderr}", Colors.RED)
            return False
    else:
        print_colored("⚠️  Django setup script not found", Colors.YELLOW)
    
    # Step 3: Setup React frontend
    print_colored("\n🌐 Setting up React frontend...", Colors.YELLOW)
    
    frontend_dir = project_root / "frontend"
    if frontend_dir.exists():
        # Install npm dependencies
        success, stdout, stderr = run_command(
            "npm install",
            cwd=frontend_dir
        )
        if success:
            print_colored("✅ Frontend dependencies installed", Colors.GREEN)
        else:
            print_colored(f"❌ Frontend setup failed: {stderr}", Colors.RED)
            return False
    else:
        print_colored("⚠️  Frontend directory not found", Colors.YELLOW)
    
    # Step 4: Setup Ollama
    print_colored("\n🤖 Setting up Ollama AI...", Colors.YELLOW)
    
    # Check if Ollama is running
    success, stdout, stderr = run_command("ollama list")
    if not success:
        print_colored("🔄 Starting Ollama service...", Colors.CYAN)
        # Try to start Ollama
        if platform.system() == "Windows":
            subprocess.Popen("ollama serve", shell=True)
        else:
            subprocess.Popen("ollama serve", shell=True)
        
        # Wait a bit for Ollama to start
        import time
        time.sleep(3)
    
    # Check if Gemma2 model is available
    success, stdout, stderr = run_command("ollama list")
    if success and "gemma2:2b" not in stdout:
        print_colored("📥 Downloading Gemma2 model (this may take a while)...", Colors.CYAN)
        success, stdout, stderr = run_command("ollama pull gemma2:2b")
        if success:
            print_colored("✅ Gemma2 model downloaded", Colors.GREEN)
        else:
            print_colored(f"❌ Failed to download model: {stderr}", Colors.RED)
            return False
    else:
        print_colored("✅ Gemma2 model already available", Colors.GREEN)
    
    # Step 5: Create startup scripts
    print_colored("\n📝 Creating startup scripts...", Colors.YELLOW)
    
    quickstart_dir = project_root / "quickstart"
    quickstart_dir.mkdir(exist_ok=True)
    
    # Windows batch script
    windows_script = quickstart_dir / "START_MEDSTUDY.bat"
    if not windows_script.exists():
        windows_content = """@echo off
echo 🏥 MedStudy Pro - Starting...

cd /d "%~dp0\.."

echo 🚀 Starting Django backend...
start /d "medstudy_app" python manage.py runserver 8000

echo 🌐 Starting React frontend...
start /d "frontend" npm start

echo 🤖 Ensuring Ollama is running...
start ollama serve

timeout /t 10 /nobreak >nul

echo 🌍 Opening browser...
start http://localhost:3000

echo 🎉 MedStudy Pro is starting!
echo 📊 Available at: http://localhost:3000
pause
"""
        windows_script.write_text(windows_content)
        print_colored("✅ Windows startup script created", Colors.GREEN)
    
    # Final success message
    print_colored("\n🎉 Setup completed successfully!", Colors.BOLD + Colors.GREEN)
    print_colored("\n📊 Quick start options:", Colors.CYAN)
    print_colored("  • Windows: quickstart\\START_MEDSTUDY.bat", Colors.WHITE)
    print_colored("  • Linux/Mac: ./quickstart/start_medstudy.sh", Colors.WHITE)
    print_colored("  • Manual: python quickstart/quick_setup.py", Colors.WHITE)
    
    print_colored("\n🌍 Access points:", Colors.CYAN)
    print_colored("  • Frontend:     http://localhost:3000", Colors.WHITE)
    print_colored("  • Django Admin: http://localhost:8000/admin/", Colors.WHITE)
    print_colored("  • API Docs:     http://localhost:8000/api/v1/", Colors.WHITE)
    print_colored("  • Health Check: http://localhost:8000/health/", Colors.WHITE)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Setup interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)