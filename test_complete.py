
#!/usr/bin/env python3
"""
MedStudy Pro - Sistema de Testing Completo
Verifica que todos los componentes funcionen correctamente
"""

import sys
import os
import time
from pathlib import Path

def print_header():
    print("=" * 70)
    print("🧪 MedStudy Pro - Sistema de Testing Completo")
    print("   Verificación de funcionalidades críticas")
    print("=" * 70)
    print()

def test_basic_imports():
    """Prueba importaciones básicas"""
    print("📦 Testing basic imports...")
    
    basic_modules = [
        ("sys", "System module"),
        ("os", "Operating system interface"),
        ("pathlib", "Path utilities"),
        ("logging", "Logging system"),
        ("datetime", "Date and time"),
        ("json", "JSON handling")
    ]
    
    failed = []
    for module, desc in basic_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
        except ImportError as e:
            print(f"   ❌ {module} - {desc} - ERROR: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_external_dependencies():
    """Prueba dependencias externas"""
    print("\n🔧 Testing external dependencies...")
    
    dependencies = [
        ("customtkinter", "UI Framework"),
        ("requests", "HTTP library"),
        ("gradio", "Web interface"),
    ]
    
    failed = []
    for module, desc in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
        except ImportError as e:
            print(f"   ⚠️ {module} - {desc} - WARNING: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_core_modules():
    """Prueba módulos core del sistema"""
    print("\n🧠 Testing core modules...")
    
    # Agregar project root al path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    core_modules = [
        ("core.database", "Database Manager"),
        ("core.utils", "System Utilities"),
        ("app.config", "Configuration System"),
        ("utils.logging", "Logging Utilities"),
        ("utils.config", "Config Utilities"),
        ("utils.diagnostics", "Diagnostics System")
    ]
    
    failed = []
    for module, desc in core_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
        except ImportError as e:
            print(f"   ❌ {module} - {desc} - ERROR: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_advanced_modules():
    """Prueba módulos avanzados (opcionales)"""
    print("\n🔬 Testing advanced modules...")
    
    advanced_modules = [
        ("core.llm_manager", "LLM Manager"),
        ("core.rag_engine", "RAG Engine"),
        ("core.medcards_system", "MedCards System"),
        ("core.study_session_manager", "Study Session Manager"),
        ("core.medical_knowledge_analyzer", "Knowledge Analyzer"),
        ("core.exam_generator", "Exam Generator"),
        ("core.study_planner", "Study Planner")
    ]
    
    available = 0
    for module, desc in advanced_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
            available += 1
        except ImportError as e:
            print(f"   ⚠️ {module} - {desc} - Optional: {e}")
    
    print(f"   📊 Advanced modules available: {available}/{len(advanced_modules)}")
    return available > 0

def test_ui_components():
    """Prueba componentes de UI"""
    print("\n🖥️ Testing UI components...")
    
    ui_modules = [
        ("app.ui.main_window", "Main Window"),
        ("app.ui.components.chat_tutor_manager", "Chat Tutor Panel")
    ]
    
    available = 0
    for module, desc in ui_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
            available += 1
        except ImportError as e:
            print(f"   ⚠️ {module} - {desc} - Warning: {e}")
    
    return available > 0

def test_configuration():
    """Prueba sistema de configuración"""
    print("\n⚙️ Testing configuration system...")
    
    try:
        from app.config import config
        
        # Test basic config access
        ollama_config = config.get_ollama_config()
        print(f"   ✅ Ollama config: {ollama_config.get('host', 'unknown')}")
        
        window_config = config.get_window_config()
        print(f"   ✅ Window config: {window_config.get('width')}x{window_config.get('height')}")
        
        db_url = config.get_database_url()
        print(f"   ✅ Database URL: {db_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_database():
    """Prueba sistema de base de datos"""
    print("\n💾 Testing database system...")
    
    try:
        from core.database import DatabaseManager
        import tempfile
        import os
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name
        
        try:
            db = DatabaseManager(test_db_path)
            
            # Test basic operations
            db_info = db.get_database_info()
            print(f"   ✅ Database created: {db_info.get('table_count', 0)} tables")
            
            # Test preference storage
            db.set_preference("test", "key1", "value1")
            value = db.get_preference("test", "key1")
            if value == "value1":
                print("   ✅ Preference storage working")
            else:
                print("   ❌ Preference storage failed")
                return False
            
            return True
            
        finally:
            # Clean up
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_ollama_connection():
    """Prueba conexión con Ollama"""
    print("\n🤖 Testing Ollama connection...")
    
    try:
        from utils.diagnostics import check_ollama_status
        
        status = check_ollama_status()
        
        if status.get('running', False):
            print("   ✅ Ollama service is running")
            
            if status.get('model_available', False):
                print(f"   ✅ Model {status.get('model')} is available")
                return True
            else:
                print(f"   ❌ Model {status.get('model')} not found")
                print("      Run: ollama pull phi3:mini")
                return False
        else:
            print("   ❌ Ollama not running")
            print("      1. Install Ollama from https://ollama.ai")
            print("      2. Run: ollama serve")
            return False
            
    except Exception as e:
        print(f"   ❌ Ollama test failed: {e}")
        return False

def test_core_functionality():
    """Prueba funcionalidad core del sistema"""
    print("\n🎯 Testing core functionality...")
    
    try:
        # Test safe import from core
        from core import DatabaseManager, initialize_database
        print("   ✅ Core database imports working")
        
        # Test utils
        from core.utils import SystemChecker, run_system_diagnostic
        print("   ✅ Core utils imports working")
        
        # Test safe advanced imports
        try:
            from core import LLMManager
            if LLMManager:
                print("   ✅ LLMManager available in core")
            else:
                print("   ⚠️ LLMManager not available (optional)")
        except:
            print("   ⚠️ LLMManager import failed (optional)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Core functionality test failed: {e}")
        return False

def test_file_structure():
    """Verifica estructura de archivos"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "config_template.ini",
        "gradio_launcher.py",
        "setup.py"
    ]
    
    required_dirs = [
        "app",
        "core",
        "utils",
        "ui"  # Should exist if UI components are there
    ]
    
    all_good = True
    
    # Check files
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} - Missing")
            all_good = False
    
    # Check directories
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ⚠️ {dir_name}/ - Missing (may be optional)")
    
    # Check if data directories can be created
    try:
        data_dirs = ["data", "logs", "data/documents", "data/images"]
        for dir_name in data_dirs:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
        print("   ✅ Data directories created/verified")
    except Exception as e:
        print(f"   ⚠️ Could not create data directories: {e}")
    
    return all_good

def run_comprehensive_test():
    """Ejecuta todos los tests"""
    print_header()
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("External Dependencies", test_external_dependencies),
        ("Core Modules", test_core_modules),
        ("Advanced Modules", test_advanced_modules),
        ("UI Components", test_ui_components),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("File Structure", test_file_structure),
        ("Core Functionality", test_core_functionality),
        ("Ollama Connection", test_ollama_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    critical_tests = [
        "Basic Imports", "Core Modules", "Configuration", 
        "Database", "File Structure", "Core Functionality"
    ]
    
    optional_tests = [
        "External Dependencies", "Advanced Modules", 
        "UI Components", "Ollama Connection"
    ]
    
    critical_passed = 0
    critical_total = 0
    optional_passed = 0
    optional_total = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        
        if test_name in critical_tests:
            critical_total += 1
            if result:
                critical_passed += 1
            print(f"   {status} - {test_name} (CRITICAL)")
        else:
            optional_total += 1
            if result:
                optional_passed += 1
            print(f"   {status} - {test_name} (Optional)")
    
    print(f"\n📈 Critical Tests: {critical_passed}/{critical_total} passed")
    print(f"📈 Optional Tests: {optional_passed}/{optional_total} passed")
    
    if critical_passed == critical_total:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("✅ MedStudy Pro core system is functional")
        
        if optional_passed >= optional_total * 0.5:
            print("✨ Most optional features are also working")
        else:
            print("⚠️ Some optional features need attention")
        
        print("\n🚀 Ready to launch:")
        print("   1. python main.py --diagnostic")
        print("   2. python main.py")
        
        return True
    else:
        print("\n❌ CRITICAL TESTS FAILED!")
        print("🔧 Must fix critical issues before proceeding")
        
        print("\n🛠️ Troubleshooting steps:")
        print("   1. Check file structure")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run: python setup.py")
        
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Testing system crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)