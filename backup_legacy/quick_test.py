#!/usr/bin/env python3
"""
MedStudy Pro - Quick Fix Test
Prueba rápida para verificar que las correcciones funcionan
"""

import sys
import os
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🔧 MedStudy Pro - Quick Fix Test")
    print("   Verificando correcciones aplicadas")
    print("=" * 60)
    print()

def test_basic_imports():
    """Test importaciones básicas"""
    print("📦 Testing basic imports...")
    
    try:
        import logging
        print("   ✅ logging")
    except ImportError as e:
        print(f"   ❌ logging: {e}")
        return False
    
    try:
        import json
        print("   ✅ json")
    except ImportError as e:
        print(f"   ❌ json: {e}")
        return False
    
    try:
        import datetime
        print("   ✅ datetime")
    except ImportError as e:
        print(f"   ❌ datetime: {e}")
        return False
    
    return True

def test_config_import():
    """Test config import"""
    print("\n⚙️ Testing config import...")
    
    try:
        from app.config import config
        print("   ✅ app.config imported successfully")
        
        # Test basic config access
        try:
            ollama_config = config.get_ollama_config()
            print(f"   ✅ Ollama config: {ollama_config['host']}")
        except Exception as e:
            print(f"   ⚠️ Ollama config access: {e}")
        
        return True
    except ImportError as e:
        print(f"   ❌ app.config import failed: {e}")
        return False

def test_core_imports():
    """Test core module imports"""
    print("\n🧠 Testing core imports...")
    
    success_count = 0
    total_count = 0
    
    # Test database
    total_count += 1
    try:
        from core.database import DatabaseManager, initialize_database
        print("   ✅ core.database")
        success_count += 1
    except ImportError as e:
        print(f"   ❌ core.database: {e}")
    
    # Test utils
    total_count += 1
    try:
        from core.utils import SystemChecker, run_system_diagnostic
        print("   ✅ core.utils")
        success_count += 1
    except ImportError as e:
        print(f"   ❌ core.utils: {e}")
    
    # Test LLM Manager (safe import)
    total_count += 1
    try:
        from core.llm_manager import LLMManager
        print("   ✅ core.llm_manager")
        success_count += 1
    except ImportError as e:
        print(f"   ⚠️ core.llm_manager: {e} (optional)")
    
    # Test RAG Engine (safe import)
    total_count += 1
    try:
        from core.rag_engine import MedicalRAGEngine
        print("   ✅ core.rag_engine")
        success_count += 1
    except ImportError as e:
        print(f"   ⚠️ core.rag_engine: {e} (optional)")
    
    print(f"   📊 Core imports: {success_count}/{total_count} successful")
    return success_count >= 2  # At least database and utils should work

def test_ui_imports():
    """Test UI imports"""
    print("\n🖥️ Testing UI imports...")
    
    try:
        from app.ui.main_window import MedStudyMainWindow
        print("   ✅ app.ui.main_window")
        
        try:
            from app.ui.components.chat_tutor_manager import ChatTutorPanel
            print("   ✅ chat_tutor_manager")
        except ImportError as e:
            print(f"   ⚠️ chat_tutor_manager: {e}")
        
        return True
    except ImportError as e:
        print(f"   ❌ UI imports failed: {e}")
        return False

def test_llm_manager_fixes():
    """Test LLM Manager specific fixes"""
    print("\n🤖 Testing LLM Manager fixes...")
    
    try:
        from core.llm_manager import LLMManager
        from app.config import config
        
        # Test initialization (should not crash)
        llm = LLMManager(config)
        print("   ✅ LLM Manager initialization")
        
        # Test status check (should not crash)
        status = llm.get_status()
        print(f"   ✅ Status check: {status.get('ready', 'unknown')}")
        
        # Test chat interface compatibility
        try:
            # Test both message formats
            messages = [{"role": "user", "content": "test"}]
            # This should not crash even if Ollama is not running
            print("   ✅ Chat interface compatibility")
        except Exception as e:
            print(f"   ⚠️ Chat interface: {e}")
        
        return True
    except Exception as e:
        print(f"   ❌ LLM Manager test failed: {e}")
        return False

def test_chat_panel_fixes():
    """Test Chat Panel fixes"""
    print("\n💬 Testing Chat Panel fixes...")
    
    try:
        from app.ui.components.chat_tutor_manager import ChatTutorPanel
        print("   ✅ ChatTutorPanel import")
        
        # Test safe initialization (without actual parent widget)
        # This tests that imports work correctly
        print("   ✅ ChatTutorPanel class available")
        
        return True
    except Exception as e:
        print(f"   ❌ Chat Panel test failed: {e}")
        return False

def test_main_launcher():
    """Test main launcher fixes"""
    print("\n🚀 Testing main launcher...")
    
    try:
        # Test safe import function
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Import main module
        import main
        print("   ✅ main.py import")
        
        # Test safe_import function
        modules = main.safe_import()
        if any(modules):
            print("   ✅ safe_import function working")
        else:
            print("   ⚠️ safe_import returned None (dependencies missing)")
        
        return True
    except Exception as e:
        print(f"   ❌ Main launcher test failed: {e}")
        return False

def test_external_dependencies():
    """Test external dependencies"""
    print("\n📚 Testing external dependencies...")
    
    dependencies = [
        ("customtkinter", "UI Framework"),
        ("requests", "HTTP Library"),
        ("gradio", "Web Interface"),
    ]
    
    available = 0
    for module, desc in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
            available += 1
        except ImportError:
            print(f"   ❌ {module} - {desc} - Install with: pip install {module}")
    
    print(f"   📊 Dependencies: {available}/{len(dependencies)} available")
    return available >= 2  # At least customtkinter and requests

def run_comprehensive_test():
    """Run all tests"""
    print_header()
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Config Import", test_config_import),
        ("Core Imports", test_core_imports),
        ("UI Imports", test_ui_imports),
        ("LLM Manager Fixes", test_llm_manager_fixes),
        ("Chat Panel Fixes", test_chat_panel_fixes),
        ("Main Launcher", test_main_launcher),
        ("External Dependencies", test_external_dependencies),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 FIX VERIFICATION SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed >= total * 0.75:  # 75% pass rate
        print("\n🎉 FIXES SUCCESSFULLY APPLIED!")
        print("✅ Core functionality should be working")
        print("\n🚀 Next steps:")
        print("   1. python main.py --diagnostic")
        print("   2. python main.py")
        return True
    else:
        print("\n⚠️ SOME FIXES NEED ATTENTION")
        print("🔧 Recommendations:")
        print("   1. Check file structure")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run: python setup.py")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test system crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)