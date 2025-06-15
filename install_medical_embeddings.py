#!/usr/bin/env python3
"""
Medical Embeddings System Installation Script
GTX 1080Ti + CUDA 12.2 Optimized Setup
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print("❌ Error: Python 3.8+ required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_cuda():
    """Check CUDA installation"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"✓ CUDA version: {torch.version.cuda}")
            print(f"✓ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
            return True
        else:
            print("⚠️  CUDA not available - will use CPU (much slower)")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed - will install with CUDA support")
        return True  # Will be installed

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Base requirements
    base_packages = [
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "transformers>=4.30.0",
        "sentence-transformers>=2.2.0",
        "faiss-gpu>=1.7.4",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "h5py>=3.8.0",
        "Pillow>=9.5.0",
        "PyMuPDF>=1.22.0",
        "python-docx>=0.8.11",
        "beautifulsoup4>=4.12.0",
        "pyarrow>=12.0.0",
        "scikit-learn>=1.3.0"
    ]
    
    # Install PyTorch with CUDA support first
    print("Installing PyTorch with CUDA 12.1 support...")
    torch_cmd = [
        sys.executable, "-m", "pip", "install", 
        "torch", "torchvision", "torchaudio", 
        "--index-url", "https://download.pytorch.org/whl/cu121"
    ]
    
    try:
        subprocess.run(torch_cmd, check=True, capture_output=True)
        print("✓ PyTorch with CUDA installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PyTorch: {e}")
        return False
    
    # Install other packages
    for package in base_packages[3:]:  # Skip torch packages already installed
        print(f"Installing {package}...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"✓ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def verify_installation():
    """Verify all components are working"""
    print("\n🧪 Verifying installation...")
    
    try:
        # Test PyTorch
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        
        # Test CUDA
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA not available")
        
        # Test Transformers
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
        
        # Test Sentence Transformers
        import sentence_transformers
        print(f"✓ Sentence Transformers {sentence_transformers.__version__}")
        
        # Test FAISS
        import faiss
        print(f"✓ FAISS {faiss.get_compile_options()}")
        
        # Test other packages
        packages = [
            ("numpy", "np"),
            ("pandas", "pd"),
            ("h5py", "h5py"),
            ("PIL", "PIL"),
            ("fitz", "fitz"),
            ("docx", "docx"),
            ("bs4", "bs4")
        ]
        
        for package_name, import_name in packages:
            try:
                exec(f"import {import_name}")
                print(f"✓ {package_name}")
            except ImportError:
                print(f"❌ {package_name} not available")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def create_config_file():
    """Create configuration file"""
    config = {
        "hardware": {
            "gpu_name": "GTX 1080Ti",
            "total_vram_gb": 11.0,
            "total_ram_gb": 32.0,
            "cuda_version": "12.2",
            "max_batch_size": 2048
        },
        "models": {
            "text_model": "intfloat/multilingual-e5-large",
            "image_model": "openai/clip-vit-large-patch14"
        },
        "processing": {
            "chunk_size": 1200,
            "chunk_overlap": 200,
            "batch_size": 2048,
            "max_workers": 8
        },
        "paths": {
            "input_dir": "Material para embeddings",
            "output_dir": "medical_knowledge_base"
        }
    }
    
    config_file = Path("medical_embeddings_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration file created: {config_file}")

def download_test_models():
    """Pre-download models to cache"""
    print("\n⬇️  Pre-downloading models...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Download text model
        print("Downloading multilingual-e5-large...")
        text_model = SentenceTransformer("intfloat/multilingual-e5-large")
        print("✓ Text model cached")
        
        # Download image model
        print("Downloading CLIP-vit-large...")
        image_model = SentenceTransformer("openai/clip-vit-large-patch14")
        print("✓ Image model cached")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Model download failed: {e}")
        print("Models will be downloaded during first run")
        return True  # Not critical

def main():
    """Main installation function"""
    print("="*60)
    print("MEDICAL EMBEDDINGS SYSTEM - INSTALLATION")
    print("GTX 1080Ti + CUDA 12.2 Optimized")
    print("="*60)
    
    # Check system requirements
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed at dependency installation")
        return False
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        return False
    
    # Create configuration
    create_config_file()
    
    # Download models
    download_test_models()
    
    print("\n" + "="*60)
    print("✅ INSTALLATION COMPLETE!")
    print("="*60)
    print("Next steps:")
    print("1. Run: python medical_embeddings_system.py")
    print("2. Or use: python launch_medical_embeddings.py")
    print("3. Check 'medical_knowledge_base/' for results")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)