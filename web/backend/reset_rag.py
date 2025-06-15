"""
Reset and reinitialize the RAG database
"""

import shutil
import os
from pathlib import Path

def reset_rag_database():
    """Reset the RAG database by deleting the data directory"""
    
    data_dir = Path("./data/medical_rag")
    
    if data_dir.exists():
        print(f"🗑️ Removing existing RAG database: {data_dir}")
        shutil.rmtree(data_dir)
        print("✅ Database removed")
    else:
        print("ℹ️ No existing database found")
    
    print("🔄 Ready for fresh initialization")

if __name__ == "__main__":
    reset_rag_database()