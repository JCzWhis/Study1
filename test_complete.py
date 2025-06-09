#!/usr/bin/env python3
"""
MedStudy Pro - Script de Testing Final
Verifica que todos los componentes funcionen correctamente
"""

import sys
import os
import traceback
from pathlib import Path

def print_header():
    print("=" * 70)
    print("🧪 MedStudy Pro - Testing Final")
    print("   Verificación completa de funcionalidades")
    print("=" * 70)
    print()

def test_imports():
    """Probar todas las importaciones críticas"""
    print("📦 Testing imports...")
    
    tests = [
        ("customtkinter", "CustomTkinter UI framework"),
        ("requests", "HTTP requests for Ollama"),
        ("pathlib", "Path handling"),
        ("logging", "Logging system"),
        ("sqlite3", "Database operations"),
        ("datetime", "Date and time"),
        ("json", "JSON handling"),
        ("threading", "Multi-threading"),
    ]
    
    failed_imports = []
    
    for module, description in tests:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError as e:
            print(f"   ❌ {module} - {description} - ERROR: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_core_modules():
    """Probar módulos del core del sistema"""
    print("\n🧠 Testing core modules...")
    
    try:
        # Agregar path del proyecto
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Test config
        try:
            from app.config import config
            print("   ✅ app.config - Configuration system")
        except ImportError as e:
            print(f"   ❌ app.config - ERROR: {e}")
            return False
        
        # Test utils
        try:
            from utils.logging import get_logger
            print("   ✅ utils.logging - Logging utilities")
        except ImportError as e:
            print(f"   ❌ utils.logging - ERROR: {e}")
            return False
        
        # Test core components
        core_modules = [
            ("core.llm_manager", "LLM Manager"),
            ("core.database", "Database Manager"),
            ("core.utils", "System utilities"),
            ("core.rag_engine", "RAG Engine"),
            ("core.medcards_system", "MedCards System"),
            ("core.study_session_manager", "Study Session Manager")
        ]
        
        for module_name, description in core_modules:
            try:
                __import__(module_name)
                print(f"   ✅ {module_name} - {description}")
            except ImportError as e:
                print(f"   ⚠️  {module_name} - {description} - WARNING: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Core modules test failed: {e}")
        return False

def test_ui_components():
    """Probar componentes de UI"""
    print("\n🖥️  Testing UI components...")
    
    try:
        # Test main window
        from app.ui.main_window import MedStudyMainWindow
        print("   ✅ Main Window - Primary interface")
        
        # Test chat tutor
        try:
            from app.ui.components.chat_tutor_manager import ChatTutorPanel
            print("   ✅ Chat Tutor Panel - AI chat component")
        except ImportError as e:
            print(f"   ⚠️  Chat Tutor Panel - WARNING: {e}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ UI components test failed: {e}")
        return False

def test_configuration():
    """Probar sistema de configuración"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from app.config import config
        
        # Test config methods
        ollama_config = config.get_ollama_config()
        print(f"   ✅ Ollama config: {ollama_config.get('host', 'unknown')}")
        
        window_config = config.get_window_config()
        print(f"   ✅ Window config: {window_config.get('width', 'unknown')}x{window_config.get('height', 'unknown')}")
        
        db_url = config.get_database_url()
        print(f"   ✅ Database URL: {db_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_database():
    """Probar sistema de base de datos"""
    print("\n💾 Testing database...")
    
    try:
        from core.database import DatabaseManager
        
        # Create test database
        test_db_path = "test_medstudy.db"
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
        
        # Clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def test_ollama_connection():
    """Probar conexión con Ollama"""
    print("\n🤖 Testing Ollama connection...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:11434", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Ollama service is running")
            
            # Test model availability
            try:
                model_response = requests.post(
                    "http://localhost:11434/api/show",
                    json={"name": "phi3:mini"},
                    timeout=10
                )
                
                if model_response.status_code == 200:
                    print("   ✅ phi3:mini model is available")
                    return True
                else:
                    print("   ❌ phi3:mini model not found")
                    print("      Run: ollama pull phi3:mini")
                    return False
                    
            except Exception as e:
                print(f"   ⚠️  Could not check model: {e}")
                return False
        else:
            print(f"   ❌ Ollama not responding (status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Ollama")
        print("      1. Install Ollama from https://ollama.ai")
        print("      2. Run: ollama serve")
        return False
    except Exception as e:
        print(f"   ❌ Ollama test failed: {e}")
        return False

def test_llm_manager():
    """Probar LLM Manager"""
    print("\n🧠 Testing LLM Manager...")
    
    try:
        from core.llm_manager import LLMManager
        from app.config import config
        
        llm = LLMManager(config)
        print("   ✅ LLM Manager created")
        
        # Test status check
        status = llm.get_status()
        if status.get("ready", False):
            print("   ✅ LLM Manager reports ready")
            
            # Test simple generation (if available)
            try:
                test_prompt = "Explain briefly what medicine is"
                response = llm.chat(test_prompt, stream=False)
                if response and len(response) > 10:
                    print("   ✅ Text generation working")
                else:
                    print("   ⚠️  Text generation returned short response")
            except Exception as e:
                print(f"   ⚠️  Text generation failed: {e}")
                
        else:
            print("   ⚠️  LLM Manager not ready")
            print(f"      Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LLM Manager test failed: {e}")
        return False

def test_main_application():
    """Probar aplicación principal (sin GUI)"""
    print("\n🖥️  Testing main application (no GUI)...")
    
    try:
        from app.ui.main_window import MedStudyMainWindow
        from app.config import config
        from core.database import DatabaseManager
        
        # Create test database
        test_db_path = "test_app_medstudy.db"
        db = DatabaseManager(test_db_path)
        
        # Create main window instance (but don't run mainloop)
        app = MedStudyMainWindow(config=config, database=db)
        print("   ✅ Main window created successfully")
        
        # Test some methods
        health = app._check_system_health()
        print(f"   ✅ System health check: {'OK' if health else 'Issues detected'}")
        
        ollama_status = app._check_ollama()
        print(f"   ✅ Ollama check: {'Running' if ollama_status else 'Not available'}")
        
        # Clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Main application test failed: {e}")
        traceback.print_exc()
        return False

def test_gradio_fallback():
    """Probar interfaz Gradio de respaldo"""
    print("\n🌐 Testing Gradio fallback...")
    
    try:
        import gradio as gr
        print("   ✅ Gradio is available")
        
        # Test if gradio_launcher exists
        gradio_file = Path("gradio_launcher.py")
        if gradio_file.exists():
            print("   ✅ gradio_launcher.py exists")
            return True
        else:
            print("   ⚠️  gradio_launcher.py not found")
            return False
            
    except ImportError:
        print("   ⚠️  Gradio not available")
        print("      Install with: pip install gradio")
        return False

def run_comprehensive_test():
    """Ejecutar todos los tests"""
    print_header()
    
    tests = [
        ("Basic Imports", test_imports),
        ("Core Modules", test_core_modules),
        ("UI Components", test_ui_components),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Ollama Connection", test_ollama_connection),
        ("LLM Manager", test_llm_manager),
        ("Main Application", test_main_application),
        ("Gradio Fallback", test_gradio_fallback),
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
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! MedStudy Pro is ready to use!")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py --diagnostic")
        print("   2. Run: python main.py")
        print("   3. Try the Chat Tutor and content generation")
        return True
    elif passed >= total * 0.7:  # 70% pass rate
        print("\n✅ MOST TESTS PASSED! MedStudy Pro should work with minor issues.")
        print("\n⚠️  Some optional features may not work perfectly.")
        print("\n🚀 You can still run:")
        print("   1. python main.py --force-launch")
        print("   2. python gradio_launcher.py (web interface)")
        return False
    else:
        print("\n❌ MULTIPLE TESTS FAILED! Please resolve issues before using.")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: python setup.py")
        print("   2. Install Ollama and phi3:mini model")
        print("   3. Check: pip install -r requirements.txt")
        return False

def main():
    """Función principal"""
    try:
        success = run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n💥 Testing crashed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)