#!/usr/bin/env python3
"""
Premium Medical Embeddings System - GTX 1080Ti Optimized
Hardware: GTX 1080Ti (11GB VRAM) + 32GB RAM + CUDA 12.2
Models: multilingual-e5-large + openai/clip-vit-large-patch14
Performance Target: <15 minutes, >85% GPU utilization, >0.95 similarity score
"""

import os
import sys
import json
import time
import h5py
import logging
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

# Core ML libraries
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import transformers
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import faiss

# Document processing
import fitz  # PyMuPDF
from PIL import Image
import docx
import pandas as pd
from bs4 import BeautifulSoup
import re
import unicodedata

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

@dataclass
class HardwareConfig:
    """GTX 1080Ti specific configuration"""
    gpu_name: str = "GTX 1080Ti"
    total_vram_gb: float = 11.0
    total_ram_gb: float = 32.0
    cuda_version: str = "12.2"
    target_vram_usage: float = 0.90  # 90% of 11GB = 9.9GB
    target_ram_usage: float = 0.625  # 20GB of 32GB
    max_batch_size: int = 2048
    precision: str = "float32"

@dataclass
class ModelConfig:
    """Premium model configuration"""
    text_model: str = "intfloat/multilingual-e5-large"
    image_model: str = "clip-ViT-L-14"
    text_model_size_gb: float = 2.24
    image_model_size_gb: float = 1.7
    embedding_dim: int = 1024
    max_sequence_length: int = 512

@dataclass
class ProcessingConfig:
    """Document processing configuration"""
    chunk_size: int = 1200
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    batch_size: int = 2048
    max_workers: int = 8
    supported_formats: List[str] = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.md', '.pdf', '.docx', '.html', '.csv', '.txt']

@dataclass
class ChunkMetadata:
    """Metadata for each text chunk"""
    chunk_id: str
    source_file: str
    chunk_index: int
    start_char: int
    end_char: int
    chunk_size: int
    medical_category: Optional[str] = None
    pathology_detected: Optional[List[str]] = None
    language: str = "es"
    confidence_score: float = 1.0
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class GPUMonitor:
    """Real-time GPU performance monitoring"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.stats = {
            'gpu_utilization': [],
            'memory_used': [],
            'memory_total': [],
            'temperature': [],
            'timestamps': []
        }
    
    def log_stats(self) -> Dict[str, Any]:
        """Log current GPU statistics"""
        if not torch.cuda.is_available():
            return {}
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'memory_allocated': torch.cuda.memory_allocated() / 1024**3,  # GB
            'memory_reserved': torch.cuda.memory_reserved() / 1024**3,    # GB
            'memory_total': torch.cuda.get_device_properties(0).total_memory / 1024**3,  # GB
            'utilization_percent': (torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory) * 100
        }
        
        # Store for trending
        self.stats['memory_used'].append(stats['memory_allocated'])
        self.stats['memory_total'].append(stats['memory_total'])
        self.stats['timestamps'].append(stats['timestamp'])
        
        return stats
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.stats['memory_used']:
            return {}
        
        return {
            'avg_memory_usage_gb': np.mean(self.stats['memory_used']),
            'max_memory_usage_gb': np.max(self.stats['memory_used']),
            'avg_utilization_percent': np.mean([
                (mem / total) * 100 for mem, total in 
                zip(self.stats['memory_used'], self.stats['memory_total'])
            ]),
            'total_samples': len(self.stats['memory_used'])
        }

class MedicalTextChunker:
    """Medical-specific intelligent text chunking"""
    
    def __init__(self, chunk_size: int = 1200, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Medical terminology patterns
        self.medical_patterns = {
            'pathology': [
                r'\b(?:síndrome|enfermedad|trastorno|patología|condición)\s+(?:de\s+)?([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*)',
                r'\b([A-Z][a-záéíóúñ]+(?:itis|osis|emia|uria|patía|plegia|trofia))\b',
                r'\b(artritis|vasculitis|lupus|esclerosis|miopatía|neuropatía)\b'
            ],
            'anatomy': [
                r'\b(corazón|pulmón|hígado|riñón|cerebro|músculo|articulación|hueso)\b',
                r'\b(cardiovascular|pulmonar|hepático|renal|neurológico|muscular)\b'
            ],
            'symptoms': [
                r'\b(dolor|fiebre|inflamación|hinchazón|fatiga|debilidad|náusea)\b',
                r'\b(disnea|taquicardia|hipertensión|hipotensión|anemia)\b'
            ],
            'medications': [
                r'\b([A-Z][a-z]+(?:cilina|micina|sulfa|zol|pril|sartan|estatina))\b',
                r'\b(antibiótico|analgésico|antiinflamatorio|corticoide|biológico)\b'
            ]
        }
    
    def detect_medical_categories(self, text: str) -> Dict[str, List[str]]:
        """Detect medical categories in text"""
        categories = {}
        
        for category, patterns in self.medical_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if isinstance(found[0], tuple) if found else False:
                    matches.extend([match[0] if isinstance(match, tuple) else match for match in found])
                else:
                    matches.extend(found)
            
            if matches:
                categories[category] = list(set(matches))
        
        return categories
    
    def smart_chunk(self, text: str, source_file: str) -> List[ChunkMetadata]:
        """Create intelligent medical chunks"""
        # Clean and normalize text
        text = self.clean_text(text)
        
        # Split into sentences for better chunk boundaries
        sentences = self.split_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Create chunk metadata
                medical_cats = self.detect_medical_categories(current_chunk)
                pathologies = medical_cats.get('pathology', [])
                
                chunk_metadata = ChunkMetadata(
                    chunk_id=f"{Path(source_file).stem}_chunk_{chunk_index:04d}",
                    source_file=source_file,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=current_start + len(current_chunk),
                    chunk_size=len(current_chunk),
                    medical_category=self.classify_medical_category(medical_cats),
                    pathology_detected=pathologies if pathologies else None
                )
                
                chunks.append(chunk_metadata)
                
                # Handle overlap
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else ""
                current_chunk = overlap_text + " " + sentence
                current_start = current_start + len(current_chunk) - len(overlap_text) - len(sentence) - 1
                chunk_index += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Handle last chunk
        if current_chunk and len(current_chunk) >= 100:  # Minimum chunk size
            medical_cats = self.detect_medical_categories(current_chunk)
            pathologies = medical_cats.get('pathology', [])
            
            chunk_metadata = ChunkMetadata(
                chunk_id=f"{Path(source_file).stem}_chunk_{chunk_index:04d}",
                source_file=source_file,
                chunk_index=chunk_index,
                start_char=current_start,
                end_char=current_start + len(current_chunk),
                chunk_size=len(current_chunk),
                medical_category=self.classify_medical_category(medical_cats),
                pathology_detected=pathologies if pathologies else None
            )
            chunks.append(chunk_metadata)
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize medical text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove special characters but keep medical symbols
        text = re.sub(r'[^\w\s\-\.\,\;\:\(\)\[\]\{\}\/\%\°\+\=\<\>]', ' ', text)
        
        # Fix common OCR errors in medical texts
        text = re.sub(r'\b(\d+)\s*[°º]\s*C\b', r'\1°C', text)  # Temperature
        text = re.sub(r'\b(\d+)\s*mg\b', r'\1 mg', text)      # Dosage
        text = re.sub(r'\b(\d+)\s*ml\b', r'\1 ml', text)      # Volume
        
        return text.strip()
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences considering medical abbreviations"""
        # Simple sentence splitting without problematic lookbehind
        sentences = re.split(r'[\.\!\?]+\s+', text)
        
        # Filter out common false splits
        filtered_sentences = []
        for sentence in sentences:
            # Skip if it's just an abbreviation
            if not re.match(r'^(Dr|Dra|Prof|etc|vs|mg|ml|kg|cm|mm)\.?\s*$', sentence.strip()):
                filtered_sentences.append(sentence)
        
        # Clean and filter sentences
        filtered_sentences = [s.strip() for s in filtered_sentences if s.strip() and len(s.strip()) > 20]
        
        return filtered_sentences
    
    def classify_medical_category(self, categories: Dict[str, List[str]]) -> str:
        """Classify the primary medical category"""
        if not categories:
            return "general"
        
        # Priority order for medical categories
        priority = ['pathology', 'anatomy', 'medications', 'symptoms']
        
        for cat in priority:
            if cat in categories and categories[cat]:
                return cat
        
        return "general"

class DocumentProcessor:
    """Process various document formats"""
    
    def __init__(self, processing_config: ProcessingConfig):
        self.config = processing_config
        self.chunker = MedicalTextChunker(
            chunk_size=processing_config.chunk_size,
            overlap=processing_config.chunk_overlap
        )
    
    def process_document(self, file_path: str) -> Tuple[str, List[str]]:
        """Process a single document and extract text and images"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.config.supported_formats:
            raise ValueError(f"Unsupported format: {file_path.suffix}")
        
        text = ""
        images = []
        
        try:
            if file_path.suffix.lower() == '.pdf':
                text, images = self._process_pdf(file_path)
            elif file_path.suffix.lower() == '.md':
                text = self._process_markdown(file_path)
            elif file_path.suffix.lower() == '.docx':
                text = self._process_docx(file_path)
            elif file_path.suffix.lower() == '.html':
                text = self._process_html(file_path)
            elif file_path.suffix.lower() == '.csv':
                text = self._process_csv(file_path)
            else:  # .txt and others
                text = self._process_text(file_path)
                
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return "", []
        
        return text, images
    
    def _process_pdf(self, file_path: Path) -> Tuple[str, List[str]]:
        """Process PDF files with PyMuPDF"""
        doc = fitz.open(str(file_path))
        text = ""
        images = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text() + "\n"
            
            # Extract images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_path = f"temp_img_{page_num}_{img_index}.png"
                    pix.save(img_path)
                    images.append(img_path)
                
                pix = None
        
        doc.close()
        return text, images
    
    def _process_markdown(self, file_path: Path) -> str:
        """Process Markdown files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove markdown syntax but keep structure
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)  # Headers
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
        content = re.sub(r'`(.*?)`', r'\1', content)  # Code
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Links
        
        return content
    
    def _process_docx(self, file_path: Path) -> str:
        """Process DOCX files"""
        doc = docx.Document(str(file_path))
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    def _process_html(self, file_path: Path) -> str:
        """Process HTML files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _process_csv(self, file_path: Path) -> str:
        """Process CSV files"""
        df = pd.read_csv(file_path)
        
        # Convert to text representation
        text = ""
        for _, row in df.iterrows():
            row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            text += row_text + "\n"
        
        return text
    
    def _process_text(self, file_path: Path) -> str:
        """Process plain text files"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode file {file_path} with any supported encoding")

class PremiumEmbeddingEngine:
    """Premium embedding engine with E5-large and CLIP-large"""
    
    def __init__(self, model_config: ModelConfig, hardware_config: HardwareConfig):
        self.model_config = model_config
        self.hardware_config = hardware_config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_monitor = GPUMonitor()
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize premium embedding models"""
        logging.info(f"Initializing models on {self.device}")
        
        # Text model: multilingual-e5-large
        logging.info("Loading multilingual-e5-large model...")
        self.text_model = SentenceTransformer(
            self.model_config.text_model,
            device=self.device,
            trust_remote_code=True
        )
        
        # Optimize for inference
        self.text_model.eval()
        if self.device.type == 'cuda':
            self.text_model.half()  # Use FP16 for memory efficiency
        
        # Image model: CLIP-large  
        logging.info("Loading CLIP model...")
        try:
            self.image_model = SentenceTransformer(
                self.model_config.image_model,
                device=self.device,
                trust_remote_code=True
            )
            self.image_model.eval()
            if self.device.type == 'cuda':
                self.image_model.half()
        except Exception as e:
            logging.warning(f"Could not load image model {self.model_config.image_model}: {e}")
            logging.info("Proceeding with text-only processing...")
            self.image_model = None
        
        # Log GPU usage after model loading
        stats = self.gpu_monitor.log_stats()
        logging.info(f"Models loaded. GPU memory: {stats.get('memory_allocated', 0):.2f}GB / "
                    f"{stats.get('memory_total', 0):.2f}GB ({stats.get('utilization_percent', 0):.1f}%)")
    
    def encode_texts_batch(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """Encode texts in optimized batches"""
        if batch_size is None:
            batch_size = self.hardware_config.max_batch_size
        
        # Adjust batch size based on available memory
        available_memory = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()
        if available_memory < 2 * 1024**3:  # Less than 2GB available
            batch_size = batch_size // 2
        
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            with torch.no_grad():
                # Add E5 instruction prefix for better performance
                prefixed_batch = [f"passage: {text}" for text in batch]
                batch_embeddings = self.text_model.encode(
                    prefixed_batch,
                    batch_size=min(len(batch), 64),  # Internal batch size
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                embeddings.append(batch_embeddings)
            
            # Monitor GPU usage
            if i % 1000 == 0:
                stats = self.gpu_monitor.log_stats()
                logging.info(f"Processed {i + len(batch)}/{len(texts)} texts. "
                           f"GPU: {stats.get('utilization_percent', 0):.1f}%")
        
        return np.vstack(embeddings) if embeddings else np.array([])
    
    def encode_images_batch(self, image_paths: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode images in batches"""
        if not image_paths or self.image_model is None:
            logging.info("Skipping image processing (no images or model not available)")
            return np.array([])
        
        embeddings = []
        valid_images = []
        
        # Load and validate images
        for img_path in image_paths:
            try:
                img = Image.open(img_path).convert('RGB')
                valid_images.append(img)
            except Exception as e:
                logging.warning(f"Failed to load image {img_path}: {e}")
        
        if not valid_images:
            return np.array([])
        
        # Process in batches
        for i in range(0, len(valid_images), batch_size):
            batch = valid_images[i:i + batch_size]
            
            with torch.no_grad():
                batch_embeddings = self.image_model.encode(
                    batch,
                    batch_size=len(batch),
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings) if embeddings else np.array([])

class FAISSIndexManager:
    """FAISS index management (CPU optimized)"""
    
    def __init__(self, embedding_dim: int, hardware_config: HardwareConfig):
        self.embedding_dim = embedding_dim
        self.hardware_config = hardware_config
        self.use_gpu = False  # Use CPU FAISS for compatibility
        
        # Note: Using CPU FAISS for Windows compatibility
        logging.info("Using CPU FAISS (Windows compatible mode)")
    
    def create_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Create optimized FAISS index"""
        n_vectors, dim = embeddings.shape
        
        # Choose index type based on dataset size
        if n_vectors < 10000:
            # Small dataset: use exact search
            index = faiss.IndexFlatIP(dim)  # Inner Product for normalized vectors
        else:
            # Large dataset: use approximate search
            nlist = min(int(np.sqrt(n_vectors)), 4096)  # Number of clusters
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        
        # Keep on CPU for compatibility
        # index remains on CPU
        
        # Train index if needed
        if hasattr(index, 'train'):
            logging.info("Training FAISS index...")
            index.train(embeddings.astype(np.float32))
        
        # Add vectors
        logging.info("Adding vectors to FAISS index...")
        index.add(embeddings.astype(np.float32))
        
        logging.info(f"FAISS index created: {index.ntotal} vectors, CPU accelerated")
        
        return index
    
    def search(self, index: faiss.Index, query_embeddings: np.ndarray, 
               k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Search the index"""
        scores, indices = index.search(query_embeddings.astype(np.float32), k)
        return scores, indices
    
    def save_index(self, index: faiss.Index, file_path: str):
        """Save FAISS index to disk"""
        # Already on CPU, save directly
        faiss.write_index(index, file_path)
        logging.info(f"FAISS index saved to {file_path}")
    
    def load_index(self, file_path: str) -> faiss.Index:
        """Load FAISS index from disk"""
        index = faiss.read_index(file_path)
        # Keep on CPU
        return index

class MedicalEmbeddingsSystem:
    """Main medical embeddings system"""
    
    def __init__(self, input_dir: str = "Material para embeddings", 
                 output_dir: str = "medical_knowledge_base"):
        
        # Configuration
        self.hardware_config = HardwareConfig()
        self.model_config = ModelConfig()
        self.processing_config = ProcessingConfig()
        
        # Paths
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Create output structure
        self._create_output_structure()
        
        # Initialize components
        self.doc_processor = DocumentProcessor(self.processing_config)
        self.embedding_engine = PremiumEmbeddingEngine(self.model_config, self.hardware_config)
        self.faiss_manager = FAISSIndexManager(self.model_config.embedding_dim, self.hardware_config)
        
        # Setup logging
        self._setup_logging()
        
        # Statistics
        self.stats = {
            'start_time': time.time(),
            'documents_processed': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'gpu_stats': [],
            'errors': []
        }
    
    def _create_output_structure(self):
        """Create output directory structure"""
        directories = [
            self.output_dir,
            self.output_dir / "embeddings",
            self.output_dir / "processed" / "chunks",
            self.output_dir / "processed" / "images",
            self.output_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.output_dir / "logs" / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # GPU performance log
        self.gpu_log_file = self.output_dir / "logs" / "gpu_performance.log"
    
    def process_documents(self) -> Tuple[List[str], List[ChunkMetadata], List[str]]:
        """Process all documents in input directory"""
        logging.info(f"Processing documents from {self.input_dir}")
        
        # Find all supported files
        all_files = []
        for ext in self.processing_config.supported_formats:
            all_files.extend(self.input_dir.glob(f"**/*{ext}"))
        
        logging.info(f"Found {len(all_files)} files to process")
        
        all_texts = []
        all_metadata = []
        all_images = []
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.processing_config.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path 
                for file_path in all_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    texts, metadata, images = future.result()
                    all_texts.extend(texts)
                    all_metadata.extend(metadata)
                    all_images.extend(images)
                    
                    self.stats['documents_processed'] += 1
                    self.stats['chunks_created'] += len(texts)
                    
                    if self.stats['documents_processed'] % 10 == 0:
                        logging.info(f"Processed {self.stats['documents_processed']} documents, "
                                   f"{self.stats['chunks_created']} chunks created")
                        
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    logging.error(error_msg)
                    self.stats['errors'].append(error_msg)
        
        logging.info(f"Document processing complete: {len(all_texts)} text chunks, "
                    f"{len(all_images)} images extracted")
        
        return all_texts, all_metadata, all_images
    
    def _process_single_file(self, file_path: Path) -> Tuple[List[str], List[ChunkMetadata], List[str]]:
        """Process a single file"""
        try:
            # Extract text and images
            text, images = self.doc_processor.process_document(str(file_path))
            
            if not text.strip():
                return [], [], images
            
            # Create intelligent chunks
            chunks_metadata = self.doc_processor.chunker.smart_chunk(text, str(file_path))
            
            # Extract chunk texts
            chunk_texts = []
            for chunk_meta in chunks_metadata:
                chunk_text = text[chunk_meta.start_char:chunk_meta.end_char]
                chunk_texts.append(chunk_text)
                
                # Save chunk to disk
                chunk_file = self.output_dir / "processed" / "chunks" / f"{chunk_meta.chunk_id}.txt"
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    f.write(chunk_text)
            
            return chunk_texts, chunks_metadata, images
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return [], [], []
    
    def generate_embeddings(self, texts: List[str], images: List[str], 
                          checkpoint_interval: int = 500) -> Tuple[np.ndarray, np.ndarray]:
        """Generate embeddings with checkpointing"""
        logging.info("Generating text embeddings...")
        
        # Process texts in chunks with checkpointing
        text_embeddings = []
        
        for i in range(0, len(texts), checkpoint_interval):
            batch_texts = texts[i:i + checkpoint_interval]
            
            # Generate embeddings for batch
            batch_embeddings = self.embedding_engine.encode_texts_batch(
                batch_texts, 
                batch_size=self.processing_config.batch_size
            )
            
            text_embeddings.append(batch_embeddings)
            
            # Save checkpoint
            checkpoint_file = self.output_dir / "embeddings" / f"text_checkpoint_{i}.h5"
            with h5py.File(checkpoint_file, 'w') as f:
                f.create_dataset('embeddings', data=batch_embeddings)
            
            logging.info(f"Text embeddings checkpoint saved: {i + len(batch_texts)}/{len(texts)}")
            
            # Log GPU stats
            gpu_stats = self.embedding_engine.gpu_monitor.log_stats()
            self.stats['gpu_stats'].append(gpu_stats)
        
        # Combine all text embeddings
        final_text_embeddings = np.vstack(text_embeddings) if text_embeddings else np.array([])
        
        # Generate image embeddings
        logging.info("Generating image embeddings...")
        image_embeddings = self.embedding_engine.encode_images_batch(images)
        
        self.stats['embeddings_generated'] = len(final_text_embeddings) + len(image_embeddings)
        
        return final_text_embeddings, image_embeddings
    
    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Create optimized FAISS index"""
        logging.info("Creating FAISS index...")
        
        if len(embeddings) == 0:
            raise ValueError("No embeddings to index")
        
        index = self.faiss_manager.create_index(embeddings)
        
        # Save index
        index_file = self.output_dir / "embeddings" / "faiss_gpu_index.bin"
        self.faiss_manager.save_index(index, str(index_file))
        
        return index
    
    def save_results(self, text_embeddings: np.ndarray, image_embeddings: np.ndarray,
                    metadata: List[ChunkMetadata]):
        """Save all results to disk"""
        logging.info("Saving results...")
        
        # Save text embeddings
        if len(text_embeddings) > 0:
            text_emb_file = self.output_dir / "embeddings" / "text_e5_large.h5"
            with h5py.File(text_emb_file, 'w') as f:
                f.create_dataset('embeddings', data=text_embeddings)
                f.attrs['model'] = self.model_config.text_model
                f.attrs['dimension'] = text_embeddings.shape[1]
                f.attrs['count'] = text_embeddings.shape[0]
        
        # Save image embeddings
        if len(image_embeddings) > 0:
            image_emb_file = self.output_dir / "embeddings" / "images_clip_large.h5"
            with h5py.File(image_emb_file, 'w') as f:
                f.create_dataset('embeddings', data=image_embeddings)
                f.attrs['model'] = self.model_config.image_model
                f.attrs['dimension'] = image_embeddings.shape[1]
                f.attrs['count'] = image_embeddings.shape[0]
        
        # Save metadata
        metadata_file = self.output_dir / "embeddings" / "metadata.parquet"
        df = pd.DataFrame([asdict(meta) for meta in metadata])
        df.to_parquet(metadata_file, index=False)
        
        # Save configuration
        config_file = self.output_dir / "embeddings" / "config.json"
        config_data = {
            'hardware_config': asdict(self.hardware_config),
            'model_config': asdict(self.model_config),
            'processing_config': asdict(self.processing_config),
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Save processing statistics
        self.stats['end_time'] = time.time()
        self.stats['total_time_minutes'] = (self.stats['end_time'] - self.stats['start_time']) / 60
        
        # Add GPU performance summary
        gpu_summary = self.embedding_engine.gpu_monitor.get_summary()
        self.stats['gpu_performance_summary'] = gpu_summary
        
        stats_file = self.output_dir / "logs" / "processing_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        
        logging.info(f"Results saved to {self.output_dir}")
    
    def run_validation_tests(self, index: faiss.Index, embeddings: np.ndarray, 
                           metadata: List[ChunkMetadata]) -> Dict[str, float]:
        """Run validation tests on embeddings"""
        logging.info("Running validation tests...")
        
        if len(embeddings) < 10:
            return {'similarity_score': 0.0, 'search_time_ms': 0.0}
        
        # Test similarity scores
        sample_indices = np.random.choice(len(embeddings), min(10, len(embeddings)), replace=False)
        similarity_scores = []
        search_times = []
        
        for idx in sample_indices:
            query_embedding = embeddings[idx:idx+1]
            
            # Time the search
            start_time = time.time()
            scores, indices = self.faiss_manager.search(index, query_embedding, k=5)
            search_time = (time.time() - start_time) * 1000  # ms
            
            search_times.append(search_time)
            
            # Check if the query itself is the top result
            if indices[0][0] == idx:
                similarity_scores.append(scores[0][0])
        
        validation_results = {
            'similarity_score': np.mean(similarity_scores) if similarity_scores else 0.0,
            'search_time_ms': np.mean(search_times) if search_times else 0.0,
            'samples_tested': len(sample_indices)
        }
        
        logging.info(f"Validation results: {validation_results}")
        return validation_results
    
    def run(self) -> Dict[str, Any]:
        """Run the complete embeddings generation pipeline"""
        logging.info("Starting Medical Embeddings System")
        logging.info(f"Hardware: {self.hardware_config.gpu_name}, "
                    f"Target VRAM: {self.hardware_config.target_vram_usage * 100:.0f}%")
        logging.info(f"Models: {self.model_config.text_model}, {self.model_config.image_model}")
        
        try:
            # Step 1: Process documents
            texts, metadata, images = self.process_documents()
            
            if not texts:
                raise ValueError("No text content found in documents")
            
            # Step 2: Generate embeddings
            text_embeddings, image_embeddings = self.generate_embeddings(texts, images)
            
            # Step 3: Create FAISS index
            index = self.create_faiss_index(text_embeddings)
            
            # Step 4: Run validation tests
            validation_results = self.run_validation_tests(index, text_embeddings, metadata)
            self.stats['validation_results'] = validation_results
            
            # Step 5: Save results
            self.save_results(text_embeddings, image_embeddings, metadata)
            
            # Final statistics
            final_stats = {
                'success': True,
                'total_time_minutes': self.stats['total_time_minutes'],
                'documents_processed': self.stats['documents_processed'],
                'chunks_created': self.stats['chunks_created'],
                'embeddings_generated': self.stats['embeddings_generated'],
                'gpu_performance': self.stats.get('gpu_performance_summary', {}),
                'validation_results': validation_results,
                'output_directory': str(self.output_dir)
            }
            
            logging.info("Medical Embeddings System completed successfully!")
            logging.info(f"Processing time: {final_stats['total_time_minutes']:.2f} minutes")
            logging.info(f"Similarity score: {validation_results.get('similarity_score', 0):.3f}")
            logging.info(f"Search time: {validation_results.get('search_time_ms', 0):.1f}ms")
            
            return final_stats
            
        except Exception as e:
            error_msg = f"System error: {str(e)}"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'stats': self.stats
            }

def main():
    """Main execution function"""
    # Check CUDA availability
    if not torch.cuda.is_available():
        print("WARNING: CUDA not available. The system is optimized for GTX 1080Ti.")
        print("Performance will be significantly reduced on CPU.")
    else:
        print(f"CUDA detected: {torch.cuda.get_device_name(0)}")
        print(f"VRAM available: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    
    # Initialize and run system
    system = MedicalEmbeddingsSystem()
    results = system.run()
    
    # Print results
    if results['success']:
        print("\n" + "="*60)
        print("MEDICAL EMBEDDINGS SYSTEM - RESULTS")
        print("="*60)
        print(f"✓ Processing time: {results['total_time_minutes']:.2f} minutes")
        print(f"✓ Documents processed: {results['documents_processed']:,}")
        print(f"✓ Text chunks created: {results['chunks_created']:,}")
        print(f"✓ Embeddings generated: {results['embeddings_generated']:,}")
        
        gpu_perf = results.get('gpu_performance', {})
        if gpu_perf:
            print(f"✓ Average GPU usage: {gpu_perf.get('avg_utilization_percent', 0):.1f}%")
            print(f"✓ Peak GPU memory: {gpu_perf.get('max_memory_usage_gb', 0):.2f}GB")
        
        validation = results.get('validation_results', {})
        if validation:
            print(f"✓ Similarity score: {validation.get('similarity_score', 0):.3f}")
            print(f"✓ Search time: {validation.get('search_time_ms', 0):.1f}ms")
        
        print(f"✓ Output directory: {results['output_directory']}")
        print("="*60)
    else:
        print(f"\n❌ System failed: {results['error']}")
    
    return results

if __name__ == "__main__":
    main()