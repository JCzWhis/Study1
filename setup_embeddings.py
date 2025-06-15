#!/usr/bin/env python3
"""
Script de instalación automática para el Sistema de Procesamiento de Embeddings
Configura el entorno y verifica dependencias
"""

import os
import sys
import subprocess
import platform
import importlib
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    print("Verificando versión de Python...")
    version = sys.version_info
    
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("⚠️  Se requiere Python 3.8 o superior")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_system_requirements():
    """Verifica los requisitos del sistema"""
    print("\nVerificando requisitos del sistema...")
    
    # Información del sistema
    system = platform.system()
    machine = platform.machine()
    
    print(f"Sistema operativo: {system}")
    print(f"Arquitectura: {machine}")
    
    # Verificar memoria
    try:
        if system == "Windows":
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
        else:
            # Linux/macOS
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            memory_kb = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
            memory_gb = memory_kb / (1024**2)
        
        print(f"Memoria RAM: {memory_gb:.1f} GB")
        
        if memory_gb < 8:
            print("⚠️  Se recomienda al menos 8GB de RAM para un rendimiento óptimo")
        else:
            print("✅ Memoria RAM suficiente")
            
    except Exception as e:
        print(f"⚠️  No se pudo verificar la memoria RAM: {e}")
    
    return True

def install_requirements():
    """Instala las dependencias requeridas"""
    print("\nInstalando dependencias...")
    
    requirements_file = Path(__file__).parent / "requirements_embeddings.txt"
    
    if not requirements_file.exists():
        print("❌ Archivo requirements_embeddings.txt no encontrado")
        return False
    
    try:
        # Actualizar pip
        print("Actualizando pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        print("Instalando paquetes...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", str(requirements_file),
            "--no-cache-dir"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print("❌ Error instalando dependencias:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando pip: {e}")
        return False

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("\nVerificando dependencias instaladas...")
    
    dependencies = [
        ("torch", "PyTorch"),
        ("sentence_transformers", "SentenceTransformers"),
        ("transformers", "Transformers"),
        ("faiss", "FAISS"),
        ("fitz", "PyMuPDF"),
        ("bs4", "BeautifulSoup4"),
        ("docx", "python-docx"),
        ("openpyxl", "OpenPyXL"),
        ("PIL", "Pillow"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("h5py", "H5PY"),
        ("chardet", "chardet"),
        ("langdetect", "langdetect"),
        ("tqdm", "tqdm")
    ]
    
    all_good = True
    
    for module_name, display_name in dependencies:
        try:
            importlib.import_module(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - No instalado")
            all_good = False
    
    return all_good

def check_models():
    """Verifica la disponibilidad de los modelos"""
    print("\nVerificando modelos de ML...")
    
    try:
        # Verificar si se pueden importar los modelos
        from sentence_transformers import SentenceTransformer
        from transformers import CLIPModel, CLIPProcessor
        
        print("✅ Librerías de modelos disponibles")
        
        # Nota sobre descarga de modelos
        print("\n📥 Nota sobre modelos:")
        print("  - multilingual-e5-base (~560MB) se descargará al primer uso")
        print("  - openai/clip-vit-base-patch32 (~340MB) se descargará al primer uso")
        print("  - Total de descarga estimada: ~900MB")
        print("  - Los modelos se guardan en cache para usos futuros")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def create_folder_structure():
    """Crea la estructura de carpetas necesaria"""
    print("\nCreando estructura de carpetas...")
    
    base_path = Path(__file__).parent
    folders = [
        "Material para embeddings",
        "knowledge_base",
        "knowledge_base/embeddings", 
        "knowledge_base/extracted",
        "knowledge_base/extracted/chunks",
        "knowledge_base/extracted/images",
        "knowledge_base/logs"
    ]
    
    for folder in folders:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 {folder}")
    
    # Crear archivo README en la carpeta de material
    readme_content = """# Material para Embeddings

Coloca aquí los documentos que quieres procesar:

## Formatos soportados:
- PDF (.pdf)
- HTML (.html, .htm) - Exports de Notion
- Markdown (.md)
- CSV (.csv)
- Word (.docx)
- Excel (.xlsx, .xls)
- Texto plano (.txt)

## Recomendaciones:
- Archivos individuales < 50MB
- Total recomendado: 250MB - 1GB
- Contenido en español/inglés
- Nombres de archivo sin caracteres especiales

## Estructura recomendada:
```
Material para embeddings/
├── medicina_interna/
│   ├── cardiologia/
│   ├── endocrinologia/
│   └── ...
├── documentos_generales/
└── papers_investigacion/
```

Una vez que hayas colocado tus documentos, ejecuta:
```bash
python embeddings_processor.py
```
"""
    
    readme_path = base_path / "Material para embeddings" / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Estructura de carpetas creada")
    return True

def show_usage_instructions():
    """Muestra las instrucciones de uso"""
    print("\n" + "="*60)
    print("🎉 INSTALACIÓN COMPLETADA")
    print("="*60)
    
    print("\n📋 PASOS SIGUIENTES:")
    print("1. Coloca tus documentos en la carpeta 'Material para embeddings'")
    print("2. Ejecuta el procesador:")
    print("   python embeddings_processor.py")
    print("\n⚙️  CONFIGURACIÓN:")
    print("- Edita embeddings_processor.py si necesitas ajustar:")
    print("  • Modelos de embedding")
    print("  • Limitaciones de recursos")
    print("  • Tamaño de chunks")
    print("  • Rutas de entrada/salida")
    
    print("\n📊 RESULTADOS ESPERADOS:")
    print("- Carpeta 'knowledge_base' con embeddings optimizados")
    print("- Índices FAISS para búsqueda rápida")
    print("- Logs detallados del procesamiento")
    print("- Metadata estructurada en formato Parquet")
    
    print("\n⏱️  TIEMPO ESTIMADO:")
    print("- 250MB de documentos: ~15-25 minutos")
    print("- 1GB de documentos: ~60-90 minutos")
    print("- Procesamiento en paralelo optimizado para tu hardware")
    
    print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
    print("- Logs en: knowledge_base/logs/")
    print("- El procesamiento puede reanudarse si se interrumpe")
    print("- Checkpoints automáticos cada 100 archivos")

def main():
    """Función principal de instalación"""
    print("Sistema de Procesamiento de Embeddings - Instalación")
    print("="*60)
    
    # Verificaciones
    if not check_python_version():
        return 1
    
    if not check_system_requirements():
        return 1
    
    # Instalación
    response = input("\n¿Instalar dependencias? (S/n): ").strip().lower()
    if response not in ['n', 'no']:
        if not install_requirements():
            print("\n❌ Error en la instalación. Intenta instalar manualmente:")
            print("pip install -r requirements_embeddings.txt")
            return 1
    
    # Verificaciones post-instalación
    if not check_dependencies():
        print("\n❌ Algunas dependencias no están disponibles")
        print("Intenta ejecutar: pip install -r requirements_embeddings.txt")
        return 1
    
    if not check_models():
        return 1
    
    # Configuración
    if not create_folder_structure():
        return 1
    
    # Instrucciones finales
    show_usage_instructions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())