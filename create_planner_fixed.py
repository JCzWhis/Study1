#!/usr/bin/env python3
"""
Script para crear MedStudy Planner - Sin problemas de codificación
Ejecutar desde Study1: python create_planner_fixed.py
"""

import os
from pathlib import Path

def create_planner():
    print("MedStudy Planner - Creador Automatico")
    print("=" * 50)
    
    # Verificar directorio actual
    current_dir = Path.cwd()
    if not (current_dir / "venv").exists():
        print("Error: Ejecuta desde Study1 (donde esta el venv)")
        return False
    
    # Crear directorio del planificador
    planner_dir = current_dir.parent / "MedStudy_Planner"
    print(f"Creando: {planner_dir}")
    
    # Crear estructura de directorios
    directories = [
        "planner",
        "planner/core", 
        "planner/ui",
        "planner/ui/components",
        "planner/ui/themes",
        "planner/utils",
        "data",
        "logs",
        "exports"
    ]
    
    print("\nCreando directorios...")
    for directory in directories:
        dir_path = planner_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  OK {directory}")
    
    # Crear archivos __init__.py
    init_files = [
        "planner/__init__.py",
        "planner/core/__init__.py", 
        "planner/ui/__init__.py",
        "planner/ui/components/__init__.py",
        "planner/ui/themes/__init__.py",
        "planner/utils/__init__.py"
    ]
    
    print("\nCreando archivos __init__.py...")
    for init_file in init_files:
        file_path = planner_dir / init_file
        file_path.write_text('"""MedStudy Planner Module"""', encoding='utf-8')
        print(f"  OK {init_file}")
    
    # config.ini
    print("\nCreando archivos de configuracion...")
    config_content = """[App]
name = MedStudy Planner
version = 1.0.0
theme = medical_professional

[Window]
width = 1400
height = 900
min_width = 1000
min_height = 700
resizable = true

[Database]
path = data/planner.db
backup_interval = 24

[Study]
default_session_duration = 45
break_duration = 15
long_break_duration = 30

[Colors]
primary = #1E3A8A
secondary = #3B82F6
success = #10B981
warning = #F59E0B
error = #EF4444
accent = #06B6D4
"""
    
    (planner_dir / "config.ini").write_text(config_content, encoding='utf-8')
    print("  OK config.ini")
    
    # requirements_planner.txt
    requirements_content = """# MedStudy Planner - Dependencias Minimas
customtkinter>=5.2.0
pillow>=10.0.0
matplotlib>=3.7.0
plotly>=5.17.0
pandas>=2.1.0
"""
    
    (planner_dir / "requirements_planner.txt").write_text(requirements_content, encoding='utf-8')
    print("  OK requirements_planner.txt")
    
    # main_planner.py
    main_content = '''#!/usr/bin/env python3
"""
MedStudy Planner - Launcher Principal
Sistema de Planificacion Retrospectiva para Medicina
"""

import sys
import os
from pathlib import Path
import logging

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """Configura el sistema de logging"""
    log_dir = current_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "planner.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('MedStudy.Planner')

def main():
    """Funcion principal del planificador"""
    logger = setup_logging()
    
    logger.info("MedStudy Planner - Iniciando...")
    logger.info(f"Directorio: {current_dir}")
    
    try:
        # Verificar dependencias
        import customtkinter as ctk
        logger.info("CustomTkinter disponible")
        
        # Configurar CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana basica (sera reemplazada)
        app = ctk.CTk()
        app.title("MedStudy Planner")
        app.geometry("1200x800")
        
        # Contenido temporal
        main_frame = ctk.CTkFrame(app)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="MedStudy Planner",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(50, 20))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Sistema de Planificacion Retrospectiva para Medicina",
            font=ctk.CTkFont(size=18)
        )
        subtitle_label.pack(pady=(0, 30))
        
        status_label = ctk.CTkLabel(
            main_frame,
            text="Estructura creada exitosamente!\\n\\nProximamente:\\n• Interfaz completa del planificador\\n• Sistema retrospectivo Ali Abdaal\\n• Dashboard visual con estadisticas\\n• Timer Pomodoro integrado",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        status_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            main_frame,
            text="Esta ventana sera reemplazada por la interfaz completa",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=(50, 20))
        
        logger.info("Interfaz basica lanzada")
        app.mainloop()
        
        logger.info("Aplicacion cerrada")
        
    except ImportError as e:
        logger.error(f"Error de dependencias: {e}")
        print("\\nInstala las dependencias con:")
        print("pip install -r requirements_planner.txt")
        return 1
    
    except Exception as e:
        logger.error(f"Error critico: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    (planner_dir / "main_planner.py").write_text(main_content, encoding='utf-8')
    print("  OK main_planner.py")
    
    # README.md
    readme_content = """# MedStudy Planner

> Sistema de Planificacion Retrospectiva para Educacion Medica

## Inicio Rapido

```bash
# Activar entorno virtual
../Study1/venv/Scripts/activate  # Windows
# source ../Study1/venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements_planner.txt

# Ejecutar
python main_planner.py
```

## Caracteristicas

- Planificacion Retrospectiva: Basada en Ali Abdaal
- Diseno Moderno: Interfaz profesional medica
- Dashboard Visual: Progreso y estadisticas
- Active Recall: Sistema integrado
- Timer Pomodoro: Sesiones optimizadas

## Metodologia

### Sistema de Confianza (Color-Coding)
- Rojo: No se nada (estudiar hoy)
- Naranja: Se muy poco (cada 3 dias)
- Amarillo: Se algo (semanal)
- Verde: Se bastante (cada 3 semanas)
- Azul: Lo domino (cada 3 meses)
"""
    
    (planner_dir / "README.md").write_text(readme_content, encoding='utf-8')
    print("  OK README.md")
    
    # Launcher para Windows
    launcher_bat = f"""@echo off
echo MedStudy Planner Launcher
cd /d "{planner_dir}"
echo Activando entorno virtual...
call "..\\Study1\\venv\\Scripts\\activate.bat"
echo Iniciando planificador...
python main_planner.py
pause
"""
    
    (planner_dir / "launch_planner.bat").write_text(launcher_bat, encoding='utf-8')
    print("  OK launch_planner.bat")
    
    print("\nEstructura creada exitosamente!")
    print(f"Ubicacion: {planner_dir}")
    
    print("\nProximos pasos:")
    print("1. cd ../MedStudy_Planner")
    print("2. ../Study1/venv/Scripts/activate")
    print("3. pip install -r requirements_planner.txt")
    print("4. python main_planner.py")
    
    print("\nO usa el launcher automatico:")
    print("   Windows: doble-click en launch_planner.bat")
    
    return True

if __name__ == "__main__":
    success = create_planner()
    if success:
        print("\nProyecto creado exitosamente!")
        input("\nPresiona Enter para continuar...")
    else:
        print("\nError creando el proyecto")
        input("\nPresiona Enter para continuar...")