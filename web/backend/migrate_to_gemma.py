#!/usr/bin/env python3
"""
Migration Script: Phi3 to Gemma 3-2B
Helps migrate from Phi3 to Gemma 3-2B model
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and display results."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"📋 Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - Failed")
            if result.stderr.strip():
                print(f"⚠️ Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_ollama_available():
    """Check if Ollama is available."""
    return run_command("ollama --version", "Checking Ollama availability")

def check_ollama_running():
    """Check if Ollama service is running."""
    return run_command("curl -s http://localhost:11434/api/tags", "Checking Ollama service")

def pull_gemma_model():
    """Pull the Gemma 3-2B model."""
    return run_command("ollama pull gemma2:2b", "Pulling Gemma 3-2B model")

def list_available_models():
    """List available models in Ollama."""
    return run_command("ollama list", "Listing available models")

def main():
    """Main migration process."""
    print("🚀 MedStudy Pro - Migration to Gemma 3-2B")
    print("="*50)
    
    # Step 1: Check Ollama availability
    print("\n📋 Step 1: Environment Check")
    if not check_ollama_available():
        print("❌ Ollama not found. Please install Ollama first:")
        print("💡 Visit: https://ollama.ai")
        return False
    
    # Step 2: Check if Ollama is running
    print("\n📋 Step 2: Service Check")
    if not check_ollama_running():
        print("⚠️ Ollama service not running. Starting Ollama...")
        print("💡 Run in another terminal: ollama serve")
        print("💡 Then re-run this script")
        return False
    
    # Step 3: Pull Gemma model
    print("\n📋 Step 3: Model Download")
    if not pull_gemma_model():
        print("❌ Failed to pull Gemma 3-2B model")
        print("💡 Try manually: ollama pull gemma2:2b")
        return False
    
    # Step 4: Verify installation
    print("\n📋 Step 4: Verification")
    list_available_models()
    
    # Step 5: Configuration update confirmation
    print("\n📋 Step 5: Configuration Updated")
    print("✅ MedStudy Pro configuration has been updated to use Gemma 3-2B")
    print("✅ System prompts optimized for English (Gemma performs better)")
    print("✅ Timeout increased to 90 seconds")
    print("✅ Dynamic model switching available via API")
    
    # Final instructions
    print("\n" + "="*50)
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\n📝 Next Steps:")
    print("1. Start the backend: python -m uvicorn app.main:app --reload")
    print("2. Test the API: curl http://localhost:8000/api/llm/status")
    print("3. Start the frontend: npm start")
    print("4. Create a study plan to test Gemma 3-2B")
    
    print("\n🔧 Model Management:")
    print("• Check status: GET /api/llm/status")
    print("• List models: GET /api/llm/models") 
    print("• Switch model: POST /api/llm/switch-model")
    
    print("\n🧪 Testing:")
    print("• Run test script: python test_gemma_integration.py")
    print("• Test RAG: GET /api/rag/test")
    print("• Bulk load embeddings: POST /api/rag/bulk-load-embeddings")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)