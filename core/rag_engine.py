"""
MedStudy Pro - RAG Engine for Medical Documents
Retrieval-Augmented Generation system optimized for medical education
"""

import os
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import io
import requests

# Safe imports from core
try:
    from .utils import FileUtils, DataUtils, MedicalUtils, PerformanceUtils
except ImportError:
    # Fallback implementations
    class FileUtils:
        @staticmethod
        def get_file_hash(file_path):
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        
        @staticmethod
        def get_file_size(file_path):
            return Path(file_path).stat().st_size
    
    class DataUtils:
        @staticmethod
        def sanitize_medical_text(text):
            import re
            return re.sub(r'\s+', ' ', text.strip())
        
        @staticmethod
        def chunk_text_for_study(text, max_chunk_size=1000):
            if len(text) <= max_chunk_size:
                return [text]
            
            chunks = []
            words = text.split()
            current_chunk = []
            current_size = 0
            
            for word in words:
                if current_size + len(word) + 1 > max_chunk_size:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_size = len(word)
                else:
                    current_chunk.append(word)
                    current_size += len(word) + 1
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        
        @staticmethod
        def extract_medical_entities(text):
            return {
                'medications': [],
                'symptoms': [],
                'conditions': [],
                'procedures': []
            }
        
        @staticmethod
        def calculate_reading_time(text, wpm=200):
            word_count = len(text.split())
            return max(1, round(word_count / wpm))
    
    class MedicalUtils:
        @staticmethod
        def validate_medical_specialty(specialty):
            return True
    
    class PerformanceUtils:
        @staticmethod
        def measure_time(func):
            def wrapper(*args, **kwargs):
                import time
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                logger = logging.getLogger('MedStudy.Performance')
                logger.debug(f"{func.__name__} took {end - start:.3f} seconds")
                return result
            return wrapper

class MedicalRAGEngine:
    """RAG engine specialized for medical documents and education"""
    
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.logger = logging.getLogger('MedStudy.RAG')
        
        # Check dependencies
        self._check_dependencies()
        
        # Initialize paths
        self.documents_path = Path(self._get_config_value('Paths', 'documents_path', 'data/documents'))
        self.images_path = Path(self._get_config_value('Paths', 'images_path', 'data/images'))
        self.embeddings_path = Path(self._get_config_value('Paths', 'embeddings_path', 'data/embeddings'))
        
        # Create directories
        for path in [self.documents_path, self.images_path, self.embeddings_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.ollama_host = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_embedding_model()
        
        if CHROMADB_AVAILABLE:
            self._initialize_vector_db()
        
        self._initialize_ollama()
        
        self.logger.info("Medical RAG Engine initialized")
    
    def _get_config_value(self, section, key, default):
        """Safely get configuration value"""
        try:
            if hasattr(self.config, 'get'):
                return self.config.get(section, key, default)
            elif hasattr(self.config, section):
                section_data = getattr(self.config, section)
                if isinstance(section_data, dict):
                    return section_data.get(key, default)
            return default
        except:
            return default
    
    def _check_dependencies(self):
        """Check and log dependency availability"""
        deps = {
            'PyMuPDF (fitz)': PYMUPDF_AVAILABLE,
            'ChromaDB': CHROMADB_AVAILABLE,
            'SentenceTransformers': SENTENCE_TRANSFORMERS_AVAILABLE,
            'NumPy': NUMPY_AVAILABLE,
            'PIL': PIL_AVAILABLE
        }
        
        for dep, available in deps.items():
            if available:
                self.logger.info(f"✅ {dep} available")
            else:
                self.logger.warning(f"❌ {dep} not available - some features disabled")
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer model for medical texts"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.warning("SentenceTransformers not available, embedding features disabled")
            return
        
        try:
            # Use a model optimized for medical/scientific texts
            model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Good balance of speed/quality
            
            self.logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            
            # Test the model
            test_embedding = self.embedding_model.encode("medical test")
            self.logger.info(f"Embedding model loaded successfully. Dimension: {len(test_embedding)}")
            
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB for vector storage"""
        if not CHROMADB_AVAILABLE:
            self.logger.warning("ChromaDB not available, vector search disabled")
            return
        
        try:
            # Configure ChromaDB
            chroma_settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.embeddings_path),
                anonymized_telemetry=False
            )
            
            self.chroma_client = chromadb.Client(chroma_settings)
            
            # Get or create collection for medical documents
            self.collection = self.chroma_client.get_or_create_collection(
                name="medical_documents",
                metadata={"description": "Medical documents for RAG system"}
            )
            
            self.logger.info(f"Vector database initialized. Documents: {self.collection.count()}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _initialize_ollama(self):
        """Initialize Ollama client for text generation"""
        try:
            ollama_config = self._get_ollama_config()
            self.ollama_host = ollama_config['host']
            self.ollama_model = ollama_config['model']
            self.ollama_timeout = ollama_config['timeout']
            
            # Test connection
            response = requests.get(self.ollama_host, timeout=5)
            if response.status_code == 200:
                self.logger.info(f"Ollama connected: {self.ollama_host}")
            else:
                self.logger.warning(f"Ollama connection issue: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama: {e}")
            self.ollama_host = None
    
    def _get_ollama_config(self):
        """Get Ollama configuration safely"""
        try:
            if hasattr(self.config, 'get_ollama_config'):
                return self.config.get_ollama_config()
            else:
                return {
                    'host': self._get_config_value('Ollama', 'host', 'http://localhost:11434'),
                    'model': self._get_config_value('Ollama', 'model', 'phi3:mini'),
                    'timeout': self._get_config_value('Ollama', 'timeout', 60)
                }
        except:
            return {
                'host': 'http://localhost:11434',
                'model': 'phi3:mini',
                'timeout': 60
            }
    
    @PerformanceUtils.measure_time
    def process_pdf_document(self, pdf_path: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Process a PDF document and extract content for RAG"""
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF not available. Install with: pip install PyMuPDF")
        
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        self.logger.info(f"Processing PDF: {pdf_path.name}")
        
        try:
            # Generate document ID
            doc_hash = FileUtils.get_file_hash(pdf_path)
            doc_id = f"pdf_{doc_hash[:12]}"
            
            # Check if already processed
            existing = self._get_document_by_id(doc_id)
            if existing:
                self.logger.info(f"Document already processed: {pdf_path.name}")
                return existing
            
            # Extract content
            doc_info = self._extract_pdf_content(pdf_path, doc_id, title)
            
            # Process and chunk text
            chunks = self._create_medical_chunks(doc_info['text'], doc_id)
            
            # Generate embeddings and store (only if components available)
            if self.embedding_model and self.collection:
                self._store_document_chunks(chunks, doc_info)
            else:
                self.logger.warning("Embeddings/vector storage not available, storing text only")
            
            # Store document metadata
            self._store_document_metadata(doc_info)
            
            self.logger.info(f"Successfully processed {pdf_path.name}: {len(chunks)} chunks")
            
            return {
                'document_id': doc_id,
                'title': doc_info['title'],
                'chunks_count': len(chunks),
                'images_count': len(doc_info['images']),
                'pages': doc_info['pages'],
                'file_size': doc_info['file_size']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF {pdf_path.name}: {e}")
            raise
    
    def _extract_pdf_content(self, pdf_path: Path, doc_id: str, title: Optional[str]) -> Dict[str, Any]:
        """Extract text and images from PDF"""
        doc = fitz.open(pdf_path)
        
        full_text = ""
        images = []
        
        for page_num, page in enumerate(doc):
            # Extract text
            text = page.get_text()
            full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            
            # Extract images if PIL is available
            if PIL_AVAILABLE:
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # Extract image
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            
                            # Save image
                            img_filename = f"{doc_id}_page{page_num + 1}_img{img_index + 1}.png"
                            img_path = self.images_path / img_filename
                            
                            with open(img_path, "wb") as f:
                                f.write(img_data)
                            
                            images.append({
                                'filename': img_filename,
                                'page': page_num + 1,
                                'path': str(img_path),
                                'size': len(img_data)
                            })
                        
                        pix = None  # Free memory
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
        
        doc.close()
        
        # Clean and sanitize text
        full_text = DataUtils.sanitize_medical_text(full_text)
        
        return {
            'document_id': doc_id,
            'title': title or pdf_path.stem,
            'text': full_text,
            'images': images,
            'pages': len(doc),
            'file_size': FileUtils.get_file_size(pdf_path),
            'file_path': str(pdf_path),
            'processed_at': datetime.now().isoformat()
        }
    
    def _create_medical_chunks(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """Create optimized chunks for medical content"""
        
        # Use medical-aware chunking
        base_chunks = DataUtils.chunk_text_for_study(text, max_chunk_size=800)
        
        chunks = []
        for i, chunk_text in enumerate(base_chunks):
            # Extract medical entities
            entities = DataUtils.extract_medical_entities(chunk_text)
            
            # Calculate reading time
            reading_time = DataUtils.calculate_reading_time(chunk_text)
            
            chunk = {
                'chunk_id': f"{doc_id}_chunk_{i}",
                'document_id': doc_id,
                'text': chunk_text,
                'chunk_index': i,
                'word_count': len(chunk_text.split()),
                'reading_time_minutes': reading_time,
                'medical_entities': entities,
                'created_at': datetime.now().isoformat()
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def _store_document_chunks(self, chunks: List[Dict[str, Any]], doc_info: Dict[str, Any]):
        """Store document chunks in vector database"""
        
        if not self.embedding_model or not self.collection:
            self.logger.warning("Embedding model or vector database not available")
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            documents.append(chunk['text'])
            ids.append(chunk['chunk_id'])
            
            metadata = {
                'document_id': chunk['document_id'],
                'chunk_index': chunk['chunk_index'],
                'word_count': chunk['word_count'],
                'reading_time': chunk['reading_time_minutes'],
                'document_title': doc_info['title'],
                'document_pages': doc_info['pages'],
                'medications': json.dumps(chunk['medical_entities']['medications']),
                'created_at': chunk['created_at']
            }
            metadatas.append(metadata)
        
        # Generate embeddings
        self.logger.info(f"Generating embeddings for {len(documents)} chunks...")
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        self.logger.info(f"Stored {len(chunks)} chunks in vector database")
    
    def _store_document_metadata(self, doc_info: Dict[str, Any]):
        """Store document metadata in SQLite database"""
        try:
            # Store in database
            self.database.execute_update("""
                INSERT OR REPLACE INTO documents 
                (document_id, title, file_path, pages, file_size, images_count, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_info['document_id'],
                doc_info['title'],
                doc_info['file_path'],
                doc_info['pages'],
                doc_info['file_size'],
                len(doc_info['images']),
                doc_info['processed_at']
            ))
            
            # Store images metadata
            for img in doc_info['images']:
                self.database.execute_update("""
                    INSERT OR REPLACE INTO document_images
                    (document_id, filename, page_number, file_path, file_size)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    doc_info['document_id'],
                    img['filename'],
                    img['page'],
                    img['path'],
                    img['size']
                ))
            
        except Exception as e:
            self.logger.error(f"Failed to store document metadata: {e}")
    
    def _get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Check if document is already processed"""
        try:
            result = self.database.execute_query(
                "SELECT * FROM documents WHERE document_id = ?",
                (doc_id,)
            )
            return result[0] if result else None
        except:
            return None
    
    @PerformanceUtils.measure_time
    def search_documents(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search documents using semantic similarity"""
        
        if not query.strip():
            return []
        
        if not self.embedding_model or not self.collection:
            self.logger.warning("Embedding model or vector database not available for search")
            return self._fallback_search(query, top_k)
        
        self.logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k,
                where=filter_dict
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'chunk_id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'distance': results['distances'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity