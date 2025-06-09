#!/usr/bin/env python3
"""
Prueba rápida de que los nuevos componentes se importan correctamente
"""

print("🧪 Testing imports of new medical components...")

try:
    print("   📦 Importing core components...")
    from core import (
        LLMManager, 
        StudySessionManager, 
        MedicalKnowledgeAnalyzer,
        SessionStatus,
        ConceptType
    )
    print("   ✅ Core imports successful!")
    
    print("   📦 Importing config...")
    from app.config import config
    print("   ✅ Config import successful!")
    
    print("   🧠 Testing LLM Manager initialization...")
    llm_manager = LLMManager(config)
    print("   ✅ LLM Manager created successfully!")
    
    print("   📊 Testing status check...")
    status = llm_manager.get_status()
    if status.get('ready'):
        print("   ✅ Ollama is ready!")
    else:
        print("   ⚠️  Ollama not ready (this is OK for now)")
    
    print("\n🎉 All imports working! Ready for Jules to integrate with UI.")
    
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("   💡 Make sure you copied all 3 files to core/ directory")
    
except Exception as e:
    print(f"   ⚠️  Runtime error: {e}")
    print("   💡 This might be normal if Ollama isn't running")

print("\n✅ Quick test completed!")