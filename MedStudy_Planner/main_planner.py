#!/usr/bin/env python3
"""
MedStudy Planner - Launcher Arreglado
"""

import sys
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    print("🧠 MedStudy Planner - Iniciando (versión arreglada)...")
    
    try:
        # Verificar CustomTkinter
        import customtkinter as ctk
        print("✅ CustomTkinter disponible")
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Importar interfaz
        from planner.ui.main_window import PlannerMainWindow
        print("✅ Interfaz cargada")
        
        # Lanzar aplicación
        print("🚀 Lanzando interfaz profesional...")
        app = PlannerMainWindow()
        app.mainloop()
        
        print("👋 Aplicación cerrada")
        return 0
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        
        # Mostrar guía de solución
        print("\n💡 SOLUCIÓN:")
        print("1. Activar venv correcto:")
        print("   ..\\Study1\\venv\\Scripts\\activate")
        print("2. Verificar que CustomTkinter esté instalado:")
        print("   pip show customtkinter")
        print("3. Si no está instalado:")
        print("   pip install customtkinter")
        
        return 1
    
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
