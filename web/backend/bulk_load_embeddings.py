#!/usr/bin/env python3
"""
Bulk Load Medical Embeddings Script
Loads all markdown files from 'Material para embeddings' folder into ChromaDB
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.medical_rag import medical_rag
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to bulk load all medical embeddings."""
    
    # Path to the embeddings directory
    embeddings_dir = Path(__file__).parent.parent.parent / "Material para embeddings"
    
    logger.info(f"🚀 Starting bulk loading from: {embeddings_dir}")
    logger.info(f"Directory exists: {embeddings_dir.exists()}")
    
    if not embeddings_dir.exists():
        logger.error(f"❌ Directory not found: {embeddings_dir}")
        return
    
    try:
        # Initialize the RAG system
        logger.info("🔧 Initializing medical RAG system...")
        await medical_rag.initialize_knowledge_base()
        
        # Check current collection size
        current_count = medical_rag.collection.count()
        logger.info(f"📊 Current collection size: {current_count} documents")
        
        # Bulk load all markdown files
        logger.info("📚 Starting bulk loading of markdown files...")
        results = await medical_rag.bulk_load_markdown_directory(str(embeddings_dir))
        
        # Display results
        logger.info("="*50)
        logger.info("📋 BULK LOADING RESULTS:")
        logger.info(f"✅ Successfully loaded: {results.get('loaded', 0)} files")
        logger.info(f"❌ Failed to load: {results.get('failed', 0)} files")
        logger.info(f"⏭️ Skipped: {results.get('skipped', 0)} files")
        
        # Check final collection size
        final_count = medical_rag.collection.count()
        new_documents = final_count - current_count
        logger.info(f"📊 Final collection size: {final_count} documents")
        logger.info(f"📈 New documents added: {new_documents}")
        logger.info("="*50)
        
        if results.get('loaded', 0) > 0:
            logger.info("🎉 Bulk loading completed successfully!")
            
            # Test the system with a quick query
            logger.info("🧪 Testing the enhanced system...")
            test_results = await medical_rag.retrieve_relevant_knowledge(
                "artritis reumatoide tratamiento", 
                specialty="reumatologia", 
                n_results=3
            )
            
            if test_results:
                logger.info(f"✅ Test query returned {len(test_results)} results")
                logger.info(f"📄 Sample result: {test_results[0]['content'][:200]}...")
            else:
                logger.warning("⚠️ Test query returned no results")
        else:
            logger.warning("⚠️ No files were loaded successfully")
            
    except Exception as e:
        logger.error(f"💥 Error during bulk loading: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())