#!/usr/bin/env python3
"""
Medical Embeddings System Launcher
Easy execution with progress monitoring and error handling
"""

import os
import sys
import json
import time
import signal
from pathlib import Path
from datetime import datetime

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n⚠️  Interruption detected. Saving progress...")
    print("Checkpoint files will be preserved in 'medical_knowledge_base/embeddings/'")
    sys.exit(0)

def check_prerequisites():
    """Check if system is ready"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required (current: {sys.version_info.major}.{sys.version_info.minor})")
        return False
    
    # Check if installation was completed
    try:
        import torch
        import transformers
        import sentence_transformers
        import faiss
        print("✓ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: python install_medical_embeddings.py")
        return False
    
    # Check CUDA
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✓ GPU: {device_name} ({vram_gb:.1f}GB VRAM)")
        
        if "1080" not in device_name:
            print(f"⚠️  System optimized for GTX 1080Ti, detected: {device_name}")
    else:
        print("⚠️  CUDA not available - will use CPU (much slower)")
    
    # Check input directory
    input_dir = Path("Material para embeddings")
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        print("Create the directory and add your medical documents")
        return False
    
    # Count files
    supported_extensions = ['.md', '.pdf', '.docx', '.html', '.csv', '.txt']
    files = []
    for ext in supported_extensions:
        files.extend(list(input_dir.glob(f"**/*{ext}")))
    
    if not files:
        print(f"❌ No supported files found in {input_dir}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return False
    
    print(f"✓ Found {len(files)} files to process")
    
    # Estimate processing time
    total_size_mb = sum(f.stat().st_size for f in files if f.exists()) / 1024**2
    estimated_time = max(5, total_size_mb / 20)  # Rough estimate: 20MB/min
    print(f"✓ Total size: {total_size_mb:.1f}MB")
    print(f"✓ Estimated time: {estimated_time:.1f} minutes")
    
    return True

def show_hardware_info():
    """Display hardware configuration"""
    try:
        import torch
        import psutil
        
        print("\n" + "="*50)
        print("HARDWARE CONFIGURATION")
        print("="*50)
        
        # CPU Info
        print(f"CPU: {psutil.cpu_count()} cores")
        print(f"RAM: {psutil.virtual_memory().total / 1024**3:.1f}GB")
        
        # GPU Info
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {props.total_memory / 1024**3:.1f}GB")
            print(f"CUDA: {torch.version.cuda}")
            print(f"Compute Capability: {props.major}.{props.minor}")
        else:
            print("GPU: Not available")
        
        print("="*50)
        
    except Exception as e:
        print(f"Could not get hardware info: {e}")

def load_config():
    """Load configuration if available"""
    config_file = Path("medical_embeddings_config.json")
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded from {config_file}")
            return config
        except Exception as e:
            print(f"⚠️  Could not load config: {e}")
    
    # Default configuration
    return {
        "hardware": {
            "max_batch_size": 2048
        },
        "processing": {
            "chunk_size": 1200,
            "chunk_overlap": 200
        }
    }

def monitor_progress(system):
    """Monitor and display progress"""
    start_time = time.time()
    
    while True:
        try:
            # Simple progress monitoring
            elapsed = time.time() - start_time
            
            print(f"\r⏱️  Running for {elapsed/60:.1f} minutes...", end="", flush=True)
            
            # Check if process is complete (basic check)
            output_dir = Path("medical_knowledge_base")
            if (output_dir / "embeddings" / "text_e5_large.h5").exists():
                print(f"\n✅ Processing complete in {elapsed/60:.1f} minutes!")
                break
            
            time.sleep(10)  # Update every 10 seconds
            
        except KeyboardInterrupt:
            break

def run_system():
    """Run the medical embeddings system"""
    try:
        # Import and initialize system
        from medical_embeddings_system import MedicalEmbeddingsSystem
        
        print("\n🚀 Initializing Medical Embeddings System...")
        
        # Create system instance
        system = MedicalEmbeddingsSystem()
        
        print("📊 Starting embedding generation...")
        print("This may take 10-20 minutes depending on your document collection.")
        print("Progress will be saved as checkpoints every 500 chunks.")
        print("Press Ctrl+C to stop gracefully.\n")
        
        # Run the system
        results = system.run()
        
        return results
        
    except Exception as e:
        print(f"\n❌ System error: {e}")
        return {"success": False, "error": str(e)}

def display_results(results):
    """Display final results"""
    print("\n" + "="*60)
    print("MEDICAL EMBEDDINGS SYSTEM - RESULTS")
    print("="*60)
    
    if results.get("success", False):
        print("✅ SUCCESS!")
        print(f"📊 Documents processed: {results.get('documents_processed', 0):,}")
        print(f"📝 Text chunks: {results.get('chunks_created', 0):,}")
        print(f"🧠 Embeddings generated: {results.get('embeddings_generated', 0):,}")
        print(f"⏱️  Total time: {results.get('total_time_minutes', 0):.2f} minutes")
        
        # GPU performance
        gpu_perf = results.get('gpu_performance', {})
        if gpu_perf:
            print(f"🎮 Average GPU usage: {gpu_perf.get('avg_utilization_percent', 0):.1f}%")
            print(f"🎮 Peak GPU memory: {gpu_perf.get('max_memory_usage_gb', 0):.2f}GB")
        
        # Validation results
        validation = results.get('validation_results', {})
        if validation:
            print(f"✅ Similarity score: {validation.get('similarity_score', 0):.3f}")
            print(f"⚡ Search speed: {validation.get('search_time_ms', 0):.1f}ms")
        
        print(f"📁 Output: {results.get('output_directory', 'medical_knowledge_base/')}")
        
        # Show structure
        print("\nGenerated files:")
        output_dir = Path(results.get('output_directory', 'medical_knowledge_base'))
        if output_dir.exists():
            key_files = [
                "embeddings/text_e5_large.h5",
                "embeddings/images_clip_large.h5", 
                "embeddings/faiss_gpu_index.bin",
                "embeddings/metadata.parquet",
                "embeddings/config.json"
            ]
            
            for file in key_files:
                file_path = output_dir / file
                if file_path.exists():
                    size_mb = file_path.stat().st_size / 1024**2
                    print(f"  ✓ {file} ({size_mb:.1f}MB)")
        
    else:
        print("❌ FAILED!")
        print(f"Error: {results.get('error', 'Unknown error')}")
        
        if 'stats' in results:
            stats = results['stats']
            print(f"Processed before failure: {stats.get('documents_processed', 0)} documents")
            if 'errors' in stats:
                print("Errors encountered:")
                for error in stats['errors'][-3:]:  # Show last 3 errors
                    print(f"  • {error}")
    
    print("="*60)

def main():
    """Main launcher function"""
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("="*60)
    print("MEDICAL EMBEDDINGS SYSTEM LAUNCHER")
    print("GTX 1080Ti Optimized - Premium Quality")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix the issues above.")
        return False
    
    # Show hardware info
    show_hardware_info()
    
    # Load configuration
    config = load_config()
    
    # Final confirmation
    print(f"\n📋 Configuration:")
    print(f"  • Batch size: {config.get('hardware', {}).get('max_batch_size', 2048)}")
    print(f"  • Chunk size: {config.get('processing', {}).get('chunk_size', 1200)} tokens")
    print(f"  • Models: E5-large + CLIP-large")
    print(f"  • Target: <15 min, >85% GPU, >0.95 similarity")
    
    input("\nPress Enter to start processing or Ctrl+C to cancel...")
    
    # Run the system
    results = run_system()
    
    # Display results
    display_results(results)
    
    return results.get("success", False)

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nFor troubleshooting:")
        print("1. Check logs in medical_knowledge_base/logs/")
        print("2. Verify GPU drivers and CUDA installation")
        print("3. Ensure sufficient disk space (>5GB recommended)")
        sys.exit(1)
    else:
        print("\n🎉 System ready! Your medical knowledge base is complete.")
        print("Use the FAISS index for fast semantic search of medical documents.")