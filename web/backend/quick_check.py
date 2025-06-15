#!/usr/bin/env python3
"""
Quick Check Script - Verify MedStudy Pro Setup
Checks system status without needing external dependencies
"""

import os
import sys
from pathlib import Path

def check_file(file_path, description):
    """Check if a file exists and show status."""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_directory(dir_path, description):
    """Check if a directory exists and count files."""
    if os.path.exists(dir_path):
        files = list(Path(dir_path).glob("*"))
        print(f"✅ {description}: {dir_path} ({len(files)} items)")
        return True
    else:
        print(f"❌ {description}: {dir_path} - NOT FOUND")
        return False

def main():
    """Quick system check."""
    print("🔍 MedStudy Pro - Quick System Check")
    print("="*50)
    
    base_dir = Path(__file__).parent
    
    # Check updated core files
    print("\n🔧 Core Files (Updated for Gemma):")
    check_file(base_dir / "app/core/llm_service.py", "LLM Service")
    check_file(base_dir / "app/config.py", "Configuration")
    check_file(base_dir / "app/main.py", "Main API")
    check_file(base_dir / "app/core/medical_rag.py", "Medical RAG")
    
    # Check new scripts
    print("\n🧪 New Testing Scripts:")
    check_file(base_dir / "test_gemma_integration.py", "Gemma Integration Test")
    check_file(base_dir / "migrate_to_gemma.py", "Migration Script")
    check_file(base_dir / "simple_test_embeddings.py", "Simple Embedding Test")
    check_file(base_dir / "bulk_load_embeddings.py", "Bulk Load Script")
    
    # Check requirements
    print("\n📦 Dependencies:")
    check_file(base_dir / "requirements.txt", "Requirements File")
    
    # Check medical embeddings
    print("\n📚 Medical Content:")
    embeddings_dir = base_dir.parent.parent / "Material para embeddings"
    if check_directory(embeddings_dir, "Medical Embeddings Directory"):
        md_files = list(embeddings_dir.glob("*.md"))
        print(f"📄 Markdown files found: {len(md_files)}")
        
        # Sample file check
        if md_files:
            sample_file = md_files[0]
            try:
                with open(sample_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                print(f"📖 Sample file ({sample_file.name}): {len(content)} characters")
            except Exception as e:
                print(f"⚠️ Error reading sample file: {e}")
    
    # Check frontend
    print("\n💻 Frontend:")
    frontend_dir = base_dir.parent / "frontend"
    check_file(frontend_dir / "package.json", "Frontend Package.json")
    check_directory(frontend_dir / "src", "Frontend Source")
    
    # Documentation
    print("\n📋 Documentation:")
    docs_dir = base_dir.parent.parent
    check_file(docs_dir / "README.md", "Main README")
    check_file(docs_dir / "GEMMA_MIGRATION.md", "Migration Guide")
    check_file(base_dir / "../GUIA_TESTING.md", "Testing Guide")
    
    # Configuration summary
    print("\n⚙️ Current Configuration:")
    print("🤖 Default Model: gemma2:2b (Gemma 3-2B)")
    print("🌐 Ollama URL: http://localhost:11434")
    print("⏱️ Timeout: 90 seconds")
    print("🗣️ Prompts: English (optimized for Gemma)")
    print("📊 RAG Chunk Size: 1000 characters")
    
    # Next steps
    print("\n" + "="*50)
    print("📋 NEXT STEPS:")
    print("="*50)
    print("1. 📖 Read the testing guide: cat GUIA_TESTING.md")
    print("2. 🔧 Install Ollama: https://ollama.ai")
    print("3. 🤖 Pull Gemma model: ollama pull gemma2:2b")
    print("4. 🧪 Run integration test: python test_gemma_integration.py")
    print("5. 🚀 Start backend: python -m uvicorn app.main:app --reload")
    print("6. 💻 Start frontend: cd ../frontend && npm start")
    
    print("\n🎯 Quick Test Commands:")
    print("• python simple_test_embeddings.py")
    print("• python migrate_to_gemma.py")
    print("• curl http://localhost:8000/api/llm/status")
    
    print("\n🎉 System appears ready for testing!")

if __name__ == "__main__":
    main()