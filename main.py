#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MedStudy Pro - Asistente de Estudio Médico con IA Local
Aplicación de escritorio para estudiantes de medicina con LLM integrado
"""

import sys
import os
import logging
import asyncio
from pathlib import Path
from typing import Optional

# Configurar paths antes de importar módulos
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Imports locales
from utils.config import Config, setup_directories
from utils.logging import setup_logging
from data.database import DatabaseManager
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow
from services.setup_service import FirstTimeSetup

# Versión de la aplicación
__version__ = "1.0.0"

class MedStudyProApp:
    """Clase principal de la aplicación MedStudy Pro"""
    
    def __init__(self):
        self.config: Optional[Config] = None
        self.db_manager: Optional[DatabaseManager] = None
        self.main_window: Optional[MainWindow] = None
        self.logger = None
        
    def initialize(self) -> bool:
        """Inicializa la aplicación y sus componentes"""
        try:
            # Configurar directorios
            setup_directories()
            
            # Configurar logging
            self.logger = setup_logging()
            self.logger.info(f"Iniciando MedStudy Pro v{__version__}")
            
            # Cargar configuración
            self.config = Config()
            self.config.load()
            
            # Verificar primera ejecución
            if self.config.is_first_run():
                self.logger.info("Primera ejecución detectada - iniciando setup")
                return self.first_time_setup()
            
            # Inicializar base de datos
            self.db_manager = DatabaseManager(self.config)
            self.db_manager.initialize()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error durante inicialización: {e}", exc_info=True)
            return False
    
    def first_time_setup(self) -> bool:
        """Ejecuta el setup inicial en la primera ejecución"""
        try:
            splash = SplashScreen()
            splash.show()
            
            setup_service = FirstTimeSetup(self.config, splash.update_progress)
            success = asyncio.run(setup_service.run())
            
            splash.close()
            return success
            
        except Exception as e:
            self.logger.error(f"Error en setup inicial: {e}", exc_info=True)
            return False
    
    def run(self):
        """Ejecuta la aplicación principal"""
        try:
            # Inicializar aplicación
            if not self.initialize():
                self.logger.error("Fallo en la inicialización")
                sys.exit(1)
            
            # Crear y mostrar ventana principal
            self.main_window = MainWindow(self.config, self.db_manager)
            self.main_window.run()
            
        except KeyboardInterrupt:
            self.logger.info("Aplicación interrumpida por usuario")
        except Exception as e:
            self.logger.error(f"Error fatal: {e}", exc_info=True)
            sys.exit(1)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpia recursos antes de cerrar"""
        self.logger.info("Cerrando aplicación...")
        if self.db_manager:
            self.db_manager.close()

def main():
    """Punto de entrada principal"""
    app = MedStudyProApp()
    app.run()

if __name__ == "__main__":
    main()
