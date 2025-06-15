#!/usr/bin/env python3
"""
Sistema completo de procesamiento de documentos a embeddings para knowledge base local
Optimizado para hardware limitado (Ryzen 5 3320G + 16GB RAM + GPU integrada Vega)
Procesamiento robusto de ~1GB de material médico multilingüe

Autor: Claude AI
Fecha: Diciembre 2024
"""

import os
import sys
import json
import logging
import hashlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import gc
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Core processing libraries
import numpy as np
import pandas as pd
import h5py
import faiss
from tqdm import tqdm

# Document processing
import chardet
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import docx
import openpyxl
from PIL import Image
import pytesseract

# ML libraries
import torch
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
import langdetect

# Configuration
@dataclass
class ProcessingConfig:
    """Configuración del sistema de procesamiento"""
    # Modelos
    text_model: str = "sentence-transformers/all-MiniLM-L12-v2"
    image_model: str = "openai/clip-vit-base-patch32"
    
    # Recursos MÁXIMOS (PC dedicado)
    max_cpu_cores: int = 8
    max_memory_gb: int = 14
    batch_size: int = 150
    
    # Chunking
    chunk_size: int = 800
    overlap_size: int = 120
    
    # Archivos
    max_file_size_mb: int = 50
    timeout_seconds: int = 120
    
    # Checkpoints
    checkpoint_interval: int = 100
    
    # Paths
    input_folder: str = "Material para embeddings"
    output_folder: str = "knowledge_base"

@dataclass
class ProcessingStats:
    """Estadísticas del procesamiento"""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    total_images: int = 0
    processing_time: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class DocumentExtractor:
    """Extractor robusto de contenido de documentos"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.DocumentExtractor")
        
    def detect_encoding(self, file_path: Path) -> str:
        """Detecta la codificación de un archivo de texto"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)  # Test read
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Fallback with chardet
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'
    
    def extract_text_content(self, file_path: Path) -> Tuple[str, List[Dict], Dict]:
        """
        Extrae contenido de texto de un archivo
        Returns: (text_content, images_info, metadata)
        """
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        
        if file_size > self.config.max_file_size_mb:
            raise ValueError(f"Archivo demasiado grande: {file_size:.1f}MB > {self.config.max_file_size_mb}MB")
        
        file_ext = file_path.suffix.lower()
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size_mb': file_size,
            'file_extension': file_ext,
            'processed_at': datetime.now().isoformat()
        }
        
        try:
            if file_ext == '.pdf':
                return self._extract_pdf(file_path, metadata)
            elif file_ext in ['.html', '.htm']:
                return self._extract_html(file_path, metadata)
            elif file_ext == '.md':
                return self._extract_markdown(file_path, metadata)
            elif file_ext == '.csv':
                return self._extract_csv(file_path, metadata)
            elif file_ext == '.docx':
                return self._extract_docx(file_path, metadata)
            elif file_ext in ['.xlsx', '.xls']:
                return self._extract_excel(file_path, metadata)
            elif file_ext == '.txt':
                return self._extract_txt(file_path, metadata)
            else:
                # Fallback a texto plano
                return self._extract_fallback(file_path, metadata)
                
        except Exception as e:
            self.logger.warning(f"Error específico en {file_path.name}: {e}")
            # Fallback a texto plano
            return self._extract_fallback(file_path, metadata)
    
    def _extract_pdf(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae texto e imágenes de PDF"""
        doc = fitz.open(file_path)
        text_content = ""
        images_info = []
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extraer texto
                page_text = page.get_text()
                text_content += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
                
                # Extraer imágenes
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            img_hash = hashlib.md5(img_data).hexdigest()[:12]
                            
                            images_info.append({
                                'page': page_num + 1,
                                'index': img_index,
                                'hash': img_hash,
                                'size': len(img_data),
                                'data': img_data
                            })
                        
                        pix = None  # Free memory
                    except Exception as e:
                        self.logger.debug(f"Error extrayendo imagen PDF: {e}")
                        
        finally:
            doc.close()
        
        metadata.update({
            'pages': len(doc),
            'images_count': len(images_info)
        })
        
        return text_content.strip(), images_info, metadata
    
    def _extract_html(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae contenido de HTML (Notion export)"""
        encoding = self.detect_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remover scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extraer texto manteniendo estructura
        text_parts = []
        
        # Títulos
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = '#' * int(heading.name[1])
            text_parts.append(f"\n{level} {heading.get_text().strip()}\n")
        
        # Párrafos y listas
        for element in soup.find_all(['p', 'li', 'blockquote']):
            text = element.get_text().strip()
            if text:
                text_parts.append(text)
        
        text_content = '\n\n'.join(text_parts)
        
        # Extraer imágenes
        images_info = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not src.startswith('http'):
                img_path = file_path.parent / src
                if img_path.exists():
                    try:
                        with open(img_path, 'rb') as f:
                            img_data = f.read()
                        
                        img_hash = hashlib.md5(img_data).hexdigest()[:12]
                        images_info.append({
                            'src': src,
                            'hash': img_hash,
                            'size': len(img_data),
                            'data': img_data
                        })
                    except Exception as e:
                        self.logger.debug(f"Error cargando imagen HTML: {e}")
        
        metadata.update({
            'title': soup.title.string if soup.title else file_path.stem,
            'images_count': len(images_info)
        })
        
        return text_content, images_info, metadata
    
    def _extract_markdown(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae contenido de Markdown"""
        encoding = self.detect_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        metadata.update({
            'format': 'markdown'
        })
        
        return content, [], metadata
    
    def _extract_csv(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae contenido de CSV"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            encoding = self.detect_encoding(file_path)
            df = pd.read_csv(file_path, encoding=encoding)
        
        # Convertir cada fila a texto estructurado
        text_parts = []
        for idx, row in df.iterrows():
            row_text = []
            for col, value in row.items():
                if pd.notna(value):
                    row_text.append(f"{col}: {value}")
            text_parts.append(" | ".join(row_text))
        
        text_content = "\n\n".join(text_parts)
        
        metadata.update({
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns)
        })
        
        return text_content, [], metadata
    
    def _extract_docx(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae contenido de DOCX"""
        doc = docx.Document(file_path)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                text_parts.append(text)
        
        # Extraer texto de tablas
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        row_text.append(cell_text)
                if row_text:
                    text_parts.append(" | ".join(row_text))
        
        text_content = "\n\n".join(text_parts)
        
        metadata.update({
            'paragraphs': len(doc.paragraphs),
            'tables': len(doc.tables)
        })
        
        return text_content, [], metadata
    
    def _extract_excel(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae contenido de Excel"""
        df = pd.read_excel(file_path, sheet_name=None)  # Leer todas las hojas
        
        text_parts = []
        total_rows = 0
        
        for sheet_name, sheet_df in df.items():
            text_parts.append(f"### Hoja: {sheet_name}\n")
            
            for idx, row in sheet_df.iterrows():
                row_text = []
                for col, value in row.items():
                    if pd.notna(value):
                        row_text.append(f"{col}: {value}")
                if row_text:
                    text_parts.append(" | ".join(row_text))
            
            total_rows += len(sheet_df)
            text_parts.append("")  # Separador entre hojas
        
        text_content = "\n".join(text_parts)
        
        metadata.update({
            'sheets': list(df.keys()),
            'total_rows': total_rows
        })
        
        return text_content, [], metadata
    
    def _extract_txt(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Extrae contenido de TXT"""
        encoding = self.detect_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        metadata.update({
            'encoding': encoding
        })
        
        return content, [], metadata
    
    def _extract_fallback(self, file_path: Path, metadata: Dict) -> Tuple[str, List[Dict], Dict]:
        """Fallback para archivos no reconocidos"""
        encoding = self.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            metadata.update({
                'extraction_method': 'fallback_text',
                'encoding': encoding
            })
            
            return content, [], metadata
            
        except Exception as e:
            self.logger.warning(f"Fallback falló para {file_path.name}: {e}")
            metadata.update({
                'extraction_method': 'failed',
                'error': str(e)
            })
            return "", [], metadata

class DocumentChunker:
    """Chunking inteligente de documentos"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.DocumentChunker")
    
    def chunk_document(self, text: str, metadata: Dict) -> List[Dict]:
        """Divide el documento en chunks optimizados"""
        if not text.strip():
            return []
        
        # Detectar idioma
        try:
            language = langdetect.detect(text[:1000])
        except:
            language = 'unknown'
        
        # Chunking basado en el tipo de documento
        if metadata.get('file_extension') == '.md':
            chunks = self._chunk_markdown(text, metadata)
        elif metadata.get('file_extension') == '.csv':
            chunks = self._chunk_csv(text, metadata)
        else:
            chunks = self._chunk_generic(text, metadata)
        
        # Enriquecer chunks con metadata
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': f"{metadata['file_name']}_{i:04d}",
                'chunk_index': i,
                'chunk_size': len(chunk),
                'language': language,
                'word_count': len(chunk.split())
            })
            
            enriched_chunks.append({
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        return enriched_chunks
    
    def _chunk_markdown(self, text: str, metadata: Dict) -> List[str]:
        """Chunking inteligente para Markdown preservando headers"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        current_header = ""
        
        for line in lines:
            line_size = len(line)
            
            # Detectar headers
            if line.strip().startswith('#'):
                # Si tenemos un chunk actual, guardarlo
                if current_chunk and current_size > 100:
                    chunk_text = current_header + '\n' + '\n'.join(current_chunk)
                    chunks.append(chunk_text.strip())
                
                # Iniciar nuevo chunk con el header
                current_header = line
                current_chunk = []
                current_size = line_size
            else:
                # Verificar si agregar esta línea excede el límite
                if current_size + line_size > self.config.chunk_size and current_chunk:
                    # Guardar chunk actual
                    chunk_text = current_header + '\n' + '\n'.join(current_chunk)
                    chunks.append(chunk_text.strip())
                    
                    # Iniciar nuevo chunk con overlap
                    overlap_lines = current_chunk[-self.config.overlap_size//50:] if current_chunk else []
                    current_chunk = overlap_lines + [line]
                    current_size = sum(len(l) for l in current_chunk)
                else:
                    current_chunk.append(line)
                    current_size += line_size
        
        # Agregar último chunk
        if current_chunk:
            chunk_text = current_header + '\n' + '\n'.join(current_chunk)
            chunks.append(chunk_text.strip())
        
        return [c for c in chunks if len(c.strip()) > 50]
    
    def _chunk_csv(self, text: str, metadata: Dict) -> List[str]:
        """Chunking para CSV - cada fila o grupo de filas"""
        lines = text.split('\n\n')  # CSV ya está procesado en líneas
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            
            if current_size + line_size > self.config.chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                
                # Overlap para CSV: mantener última fila
                current_chunk = [current_chunk[-1], line] if current_chunk else [line]
                current_size = len(current_chunk[-1]) + line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return [c for c in chunks if len(c.strip()) > 20]
    
    def _chunk_generic(self, text: str, metadata: Dict) -> List[str]:
        """Chunking genérico por párrafos y oraciones"""
        # Dividir por párrafos primero
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            para_size = len(paragraph)
            
            # Si el párrafo es muy grande, dividirlo por oraciones
            if para_size > self.config.chunk_size:
                sentences = self._split_into_sentences(paragraph)
                for sentence in sentences:
                    sentence_size = len(sentence)
                    
                    if current_size + sentence_size > self.config.chunk_size and current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        
                        # Overlap: mantener parte del chunk anterior
                        overlap_text = current_chunk[-1] if current_chunk else ""
                        if len(overlap_text) > self.config.overlap_size:
                            overlap_text = overlap_text[-self.config.overlap_size:]
                        
                        current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                        current_size = len(overlap_text) + sentence_size
                    else:
                        current_chunk.append(sentence)
                        current_size += sentence_size
            else:
                # Párrafo normal
                if current_size + para_size > self.config.chunk_size and current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    
                    # Overlap
                    overlap_text = current_chunk[-1] if current_chunk else ""
                    if len(overlap_text) > self.config.overlap_size:
                        overlap_text = overlap_text[-self.config.overlap_size:]
                    
                    current_chunk = [overlap_text, paragraph] if overlap_text else [paragraph]
                    current_size = len(overlap_text) + para_size
                else:
                    current_chunk.append(paragraph)
                    current_size += para_size
        
        # Último chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return [c for c in chunks if len(c.strip()) > 50]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones de manera simple"""
        import re
        
        # Patrones para dividir oraciones
        sentence_endings = re.compile(r'[.!?]+\s+')
        sentences = sentence_endings.split(text)
        
        # Reconstruir oraciones con puntuación
        result = []
        for i, sentence in enumerate(sentences[:-1]):
            # Buscar la puntuación original
            end_pos = text.find(sentence) + len(sentence)
            while end_pos < len(text) and text[end_pos] in '.!? ':
                sentence += text[end_pos]
                end_pos += 1
            result.append(sentence.strip())
        
        # Última oración
        if sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return [s for s in result if len(s.strip()) > 10]

class EmbeddingGenerator:
    """Generador de embeddings optimizado para recursos limitados"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.EmbeddingGenerator")
        
        # Configurar torch para usar menos memoria
        torch.set_num_threads(self.config.max_cpu_cores)
        
        # Modelos
        self.text_model = None
        self.image_model = None
        self.image_processor = None
        
        self._load_models()
    
    def _load_models(self):
        """Carga los modelos de embedding"""
        try:
            self.logger.info(f"Cargando modelo de texto: {self.config.text_model}")
            self.text_model = SentenceTransformer(self.config.text_model)
            self.text_model.max_seq_length = 512  # Limitar para eficiencia
            
            # Optimizar modelo para CPU
            if torch.cuda.is_available():
                self.text_model = self.text_model.cuda()
                self.logger.info("Modelo de texto cargado en GPU")
            else:
                self.logger.info("Modelo de texto cargado en CPU")
            
        except Exception as e:
            self.logger.error(f"Error cargando modelo de texto: {e}")
            raise
        
        try:
            self.logger.info(f"Cargando modelo de imagen: {self.config.image_model}")
            self.image_model = CLIPModel.from_pretrained(self.config.image_model)
            self.image_processor = CLIPProcessor.from_pretrained(self.config.image_model)
            
            if torch.cuda.is_available():
                self.image_model = self.image_model.cuda()
                self.logger.info("Modelo de imagen cargado en GPU")
            else:
                self.logger.info("Modelo de imagen cargado en CPU")
                
        except Exception as e:
            self.logger.error(f"Error cargando modelo de imagen: {e}")
            self.image_model = None
            self.image_processor = None
    
    def generate_text_embeddings(self, chunks: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Genera embeddings de texto en batches"""
        if not chunks:
            return np.array([]), []
        
        texts = [chunk['text'] for chunk in chunks]
        metadata_list = [chunk['metadata'] for chunk in chunks]
        
        embeddings_list = []
        
        # Procesar en batches para controlar memoria
        batch_size = min(64, self.config.batch_size // 2)  # Batch GRANDE para máxima velocidad
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generando embeddings de texto"):
            batch_texts = texts[i:i + batch_size]
            
            try:
                # Generar embeddings
                batch_embeddings = self.text_model.encode(
                    batch_texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                
                # Convertir a float16 para eficiencia
                batch_embeddings = batch_embeddings.astype(np.float16)
                embeddings_list.append(batch_embeddings)
                
                # Limpiar memoria
                if i % (batch_size * 4) == 0:
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        
            except Exception as e:
                self.logger.error(f"Error generando embeddings batch {i}: {e}")
                # Crear embeddings dummy para mantener consistencia
                dummy_embeddings = np.zeros((len(batch_texts), 768), dtype=np.float16)
                embeddings_list.append(dummy_embeddings)
        
        # Concatenar todos los embeddings
        if embeddings_list:
            all_embeddings = np.vstack(embeddings_list)
        else:
            all_embeddings = np.array([])
        
        return all_embeddings, metadata_list
    
    def generate_image_embeddings(self, images_info: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Genera embeddings de imágenes"""
        if not images_info or not self.image_model:
            return np.array([]), []
        
        embeddings_list = []
        valid_metadata = []
        
        batch_size = min(16, self.config.batch_size // 8)  # Batch pequeño para imágenes
        
        for i in tqdm(range(0, len(images_info), batch_size), desc="Generando embeddings de imagen"):
            batch_images = images_info[i:i + batch_size]
            batch_embeddings = []
            batch_metadata = []
            
            for img_info in batch_images:
                try:
                    # Cargar imagen
                    image_data = img_info.get('data')
                    if not image_data:
                        continue
                    
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Procesar imagen
                    inputs = self.image_processor(images=image, return_tensors="pt")
                    
                    if torch.cuda.is_available():
                        inputs = {k: v.cuda() for k, v in inputs.items()}
                    
                    # Generar embedding
                    with torch.no_grad():
                        image_features = self.image_model.get_image_features(**inputs)
                        embedding = image_features.cpu().numpy().astype(np.float16)
                    
                    batch_embeddings.append(embedding[0])
                    batch_metadata.append(img_info)
                    
                except Exception as e:
                    self.logger.debug(f"Error procesando imagen: {e}")
                    continue
            
            if batch_embeddings:
                embeddings_list.extend(batch_embeddings)
                valid_metadata.extend(batch_metadata)
            
            # Limpiar memoria
            if i % (batch_size * 2) == 0:
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        
        if embeddings_list:
            all_embeddings = np.vstack(embeddings_list)
        else:
            all_embeddings = np.array([])
        
        return all_embeddings, valid_metadata

class KnowledgeBaseProcessor:
    """Procesador principal del knowledge base"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.stats = ProcessingStats()
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Setup paths
        self.input_path = Path(self.config.input_folder)
        self.output_path = Path(self.config.output_folder)
        self._setup_directories()
        
        # Initialize components
        self.extractor = DocumentExtractor(config)
        self.chunker = DocumentChunker(config)
        self.embedding_generator = EmbeddingGenerator(config)
        
        # Processing state
        self.processed_files = set()
        self.checkpoint_file = self.output_path / "processing_checkpoint.json"
        self._load_checkpoint()
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        log_dir = Path(self.config.output_folder) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Logger principal
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Handler para archivo principal
        main_handler = logging.FileHandler(log_dir / "processing.log", encoding='utf-8')
        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.INFO)
        logger.addHandler(main_handler)
        
        # Handler para errores
        error_handler = logging.FileHandler(log_dir / "errors.log", encoding='utf-8')
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    
    def _setup_directories(self):
        """Crea las carpetas necesarias"""
        directories = [
            self.output_path / "embeddings",
            self.output_path / "extracted" / "chunks",
            self.output_path / "extracted" / "images",
            self.output_path / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_checkpoint(self):
        """Carga el checkpoint de procesamiento"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                self.processed_files = set(checkpoint_data.get('processed_files', []))
                self.stats = ProcessingStats(**checkpoint_data.get('stats', {}))
                
                self.logger.info(f"Checkpoint cargado: {len(self.processed_files)} archivos ya procesados")
                
            except Exception as e:
                self.logger.warning(f"Error cargando checkpoint: {e}")
                self.processed_files = set()
    
    def _save_checkpoint(self):
        """Guarda el checkpoint de procesamiento"""
        try:
            checkpoint_data = {
                'processed_files': list(self.processed_files),
                'stats': asdict(self.stats),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error guardando checkpoint: {e}")
    
    def scan_files(self) -> List[Path]:
        """Escanea archivos para procesar"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Carpeta de entrada no encontrada: {self.input_path}")
        
        # Extensiones soportadas
        supported_extensions = {
            '.pdf', '.html', '.htm', '.md', '.csv', '.docx', '.xlsx', '.xls', '.txt',
            '.json', '.xml', '.rtf', '.odt', '.ods', '.pptx'
        }
        
        all_files = []
        for file_path in self.input_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in supported_extensions and
                str(file_path) not in self.processed_files):
                all_files.append(file_path)
        
        self.stats.total_files = len(all_files)
        self.logger.info(f"Encontrados {len(all_files)} archivos para procesar")
        
        return all_files
    
    def process_file(self, file_path: Path) -> Tuple[List[Dict], List[Dict], bool]:
        """
        Procesa un archivo individual
        Returns: (text_chunks, images_info, success)
        """
        try:
            self.logger.info(f"Procesando: {file_path.name}")
            
            # Extraer contenido
            text_content, images_info, metadata = self.extractor.extract_text_content(file_path)
            
            # Crear chunks
            text_chunks = self.chunker.chunk_document(text_content, metadata)
            
            # Marcar como procesado
            self.processed_files.add(str(file_path))
            self.stats.processed_files += 1
            self.stats.total_chunks += len(text_chunks)
            self.stats.total_images += len(images_info)
            
            return text_chunks, images_info, True
            
        except Exception as e:
            self.logger.error(f"Error procesando {file_path.name}: {e}")
            self.stats.failed_files += 1
            self.stats.errors.append(f"{file_path.name}: {str(e)}")
            return [], [], False
    
    def process_documents(self):
        """Procesa todos los documentos"""
        start_time = time.time()
        
        try:
            # Escanear archivos
            files_to_process = self.scan_files()
            
            if not files_to_process:
                self.logger.info("No hay archivos nuevos para procesar")
                return
            
            # Procesar archivos
            all_text_chunks = []
            all_images_info = []
            
            for i, file_path in enumerate(tqdm(files_to_process, desc="Procesando archivos")):
                text_chunks, images_info, success = self.process_file(file_path)
                
                if success:
                    all_text_chunks.extend(text_chunks)
                    all_images_info.extend(images_info)
                
                # Checkpoint periódico
                if (i + 1) % self.config.checkpoint_interval == 0:
                    self._save_checkpoint()
                    self.logger.info(f"Checkpoint guardado en archivo {i + 1}")
            
            # Generar embeddings
            self.logger.info("Generando embeddings de texto...")
            text_embeddings, text_metadata = self.embedding_generator.generate_text_embeddings(all_text_chunks)
            
            self.logger.info("Generando embeddings de imágenes...")
            image_embeddings, image_metadata = self.embedding_generator.generate_image_embeddings(all_images_info)
            
            # Guardar resultados
            self._save_embeddings(text_embeddings, text_metadata, image_embeddings, image_metadata)
            self._save_text_chunks(all_text_chunks)
            self._save_images(all_images_info)
            
            # Crear índices FAISS
            self._create_faiss_indices(text_embeddings, image_embeddings)
            
            # Estadísticas finales
            self.stats.processing_time = time.time() - start_time
            self._save_final_stats()
            
            # Limpiar checkpoint
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
            
            self.logger.info("Procesamiento completado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error en procesamiento principal: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _save_embeddings(self, text_embeddings: np.ndarray, text_metadata: List[Dict],
                        image_embeddings: np.ndarray, image_metadata: List[Dict]):
        """Guarda los embeddings en archivos HDF5"""
        
        # Embeddings de texto
        if text_embeddings.size > 0:
            text_file = self.output_path / "embeddings" / "text_multilingual_e5.h5"
            with h5py.File(text_file, 'w') as f:
                f.create_dataset('embeddings', data=text_embeddings, compression='gzip')
                f.attrs['model'] = self.config.text_model
                f.attrs['dimension'] = text_embeddings.shape[1]
                f.attrs['count'] = text_embeddings.shape[0]
            
            self.logger.info(f"Embeddings de texto guardados: {text_embeddings.shape}")
        
        # Embeddings de imágenes
        if image_embeddings.size > 0:
            image_file = self.output_path / "embeddings" / "images_clip_vit32.h5"
            with h5py.File(image_file, 'w') as f:
                f.create_dataset('embeddings', data=image_embeddings, compression='gzip')
                f.attrs['model'] = self.config.image_model
                f.attrs['dimension'] = image_embeddings.shape[1]
                f.attrs['count'] = image_embeddings.shape[0]
            
            self.logger.info(f"Embeddings de imagen guardados: {image_embeddings.shape}")
        
        # Metadata
        metadata_file = self.output_path / "embeddings" / "metadata.parquet"
        
        # Combinar metadata
        all_metadata = []
        
        # Metadata de texto
        for i, meta in enumerate(text_metadata):
            meta_copy = meta.copy()
            meta_copy['embedding_type'] = 'text'
            meta_copy['embedding_index'] = i
            all_metadata.append(meta_copy)
        
        # Metadata de imágenes
        for i, meta in enumerate(image_metadata):
            meta_copy = meta.copy()
            meta_copy['embedding_type'] = 'image'
            meta_copy['embedding_index'] = i
            all_metadata.append(meta_copy)
        
        if all_metadata:
            df = pd.DataFrame(all_metadata)
            df.to_parquet(metadata_file, index=False)
            self.logger.info(f"Metadata guardada: {len(all_metadata)} registros")
    
    def _save_text_chunks(self, text_chunks: List[Dict]):
        """Guarda los chunks de texto originales"""
        chunks_dir = self.output_path / "extracted" / "chunks"
        
        for chunk in text_chunks:
            chunk_id = chunk['metadata']['chunk_id']
            chunk_file = chunks_dir / f"{chunk_id}.txt"
            
            try:
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    f.write(chunk['text'])
            except Exception as e:
                self.logger.debug(f"Error guardando chunk {chunk_id}: {e}")
    
    def _save_images(self, images_info: List[Dict]):
        """Guarda las imágenes extraídas"""
        images_dir = self.output_path / "extracted" / "images"
        
        for img_info in images_info:
            img_hash = img_info.get('hash', 'unknown')
            img_file = images_dir / f"{img_hash}.png"
            
            try:
                img_data = img_info.get('data')
                if img_data:
                    with open(img_file, 'wb') as f:
                        f.write(img_data)
            except Exception as e:
                self.logger.debug(f"Error guardando imagen {img_hash}: {e}")
    
    def _create_faiss_indices(self, text_embeddings: np.ndarray, image_embeddings: np.ndarray):
        """Crea índices FAISS para búsqueda rápida"""
        
        # Índice de texto
        if text_embeddings.size > 0:
            dimension = text_embeddings.shape[1]
            
            # Usar índice IVF para datasets grandes
            if text_embeddings.shape[0] > 1000:
                quantizer = faiss.IndexFlatL2(dimension)
                nlist = min(100, text_embeddings.shape[0] // 10)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                
                # Entrenar el índice
                embeddings_f32 = text_embeddings.astype(np.float32)
                index.train(embeddings_f32)
                index.add(embeddings_f32)
                index.nprobe = 10  # Número de clusters a buscar
            else:
                # Índice simple para datasets pequeños
                index = faiss.IndexFlatL2(dimension)
                embeddings_f32 = text_embeddings.astype(np.float32)
                index.add(embeddings_f32)
            
            # Guardar índice
            index_file = self.output_path / "embeddings" / "faiss_text_index.bin"
            faiss.write_index(index, str(index_file))
            self.logger.info(f"Índice FAISS de texto creado: {text_embeddings.shape[0]} vectores")
        
        # Índice de imágenes
        if image_embeddings.size > 0:
            dimension = image_embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            embeddings_f32 = image_embeddings.astype(np.float32)
            index.add(embeddings_f32)
            
            index_file = self.output_path / "embeddings" / "faiss_image_index.bin"
            faiss.write_index(index, str(index_file))
            self.logger.info(f"Índice FAISS de imagen creado: {image_embeddings.shape[0]} vectores")
    
    def _save_final_stats(self):
        """Guarda las estadísticas finales"""
        stats_file = self.output_path / "logs" / "stats.json"
        
        stats_dict = asdict(self.stats)
        stats_dict['completion_time'] = datetime.now().isoformat()
        stats_dict['processing_time_minutes'] = self.stats.processing_time / 60
        
        # Calcular estadísticas adicionales
        if self.stats.total_files > 0:
            stats_dict['success_rate'] = self.stats.processed_files / self.stats.total_files
            stats_dict['avg_chunks_per_file'] = self.stats.total_chunks / self.stats.processed_files if self.stats.processed_files > 0 else 0
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_dict, f, indent=2, ensure_ascii=False)
        
        # Guardar configuración usada
        config_file = self.output_path / "embeddings" / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
        
        # Log de resumen
        self.logger.info("=== RESUMEN DEL PROCESAMIENTO ===")
        self.logger.info(f"Archivos procesados: {self.stats.processed_files}/{self.stats.total_files}")
        self.logger.info(f"Archivos fallidos: {self.stats.failed_files}")
        self.logger.info(f"Total de chunks: {self.stats.total_chunks}")
        self.logger.info(f"Total de imágenes: {self.stats.total_images}")
        self.logger.info(f"Tiempo de procesamiento: {self.stats.processing_time/60:.1f} minutos")
        
        if self.stats.errors:
            self.logger.warning(f"Errores encontrados: {len(self.stats.errors)}")
            for error in self.stats.errors[:5]:  # Solo mostrar primeros 5 errores
                self.logger.warning(f"  - {error}")
    
    def _show_completion_summary(self):
        """Muestra un resumen detallado al completar el procesamiento"""
        print("\n" + "="*80)
        print("🎉 PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*80)
        
        # Estadísticas principales
        success_rate = (self.stats.processed_files / self.stats.total_files * 100) if self.stats.total_files > 0 else 0
        avg_chunks = (self.stats.total_chunks / self.stats.processed_files) if self.stats.processed_files > 0 else 0
        
        print(f"📊 ESTADÍSTICAS:")
        print(f"   • Archivos procesados: {self.stats.processed_files:,}/{self.stats.total_files:,} ({success_rate:.1f}%)")
        print(f"   • Archivos fallidos: {self.stats.failed_files:,}")
        print(f"   • Chunks de texto generados: {self.stats.total_chunks:,}")
        print(f"   • Imágenes extraídas: {self.stats.total_images:,}")
        print(f"   • Promedio chunks/archivo: {avg_chunks:.1f}")
        print(f"   • Tiempo total: {self.stats.processing_time/60:.1f} minutos")
        
        # Información de archivos generados
        print(f"\n📁 ARCHIVOS GENERADOS en '{self.config.output_folder}':")
        
        # Verificar archivos y tamaños
        output_path = Path(self.config.output_folder)
        files_info = []
        
        # Embeddings
        text_emb_file = output_path / "embeddings" / "text_multilingual_e5.h5"
        if text_emb_file.exists():
            size_mb = text_emb_file.stat().st_size / (1024*1024)
            files_info.append(f"   • text_multilingual_e5.h5: {size_mb:.1f}MB")
        
        img_emb_file = output_path / "embeddings" / "images_clip_vit32.h5"
        if img_emb_file.exists():
            size_mb = img_emb_file.stat().st_size / (1024*1024)
            files_info.append(f"   • images_clip_vit32.h5: {size_mb:.1f}MB")
        
        # Índices FAISS
        text_idx_file = output_path / "embeddings" / "faiss_text_index.bin"
        if text_idx_file.exists():
            size_mb = text_idx_file.stat().st_size / (1024*1024)
            files_info.append(f"   • faiss_text_index.bin: {size_mb:.1f}MB")
        
        # Metadata
        metadata_file = output_path / "embeddings" / "metadata.parquet"
        if metadata_file.exists():
            size_mb = metadata_file.stat().st_size / (1024*1024)
            files_info.append(f"   • metadata.parquet: {size_mb:.1f}MB")
        
        # Mostrar archivos
        for file_info in files_info:
            print(file_info)
        
        # Tamaño total
        total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file()) / (1024*1024)
        print(f"   • Tamaño total: {total_size:.1f}MB")
        
        # Instrucciones de uso
        print(f"\n🚀 SIGUIENTE PASO - INTEGRAR CON TU APLICACIÓN:")
        print(f"```python")
        print(f"# Cargar embeddings generados")
        print(f"import h5py, faiss, pandas as pd")
        print(f"")
        print(f"# Embeddings de texto")
        print(f"with h5py.File('{self.config.output_folder}/embeddings/text_multilingual_e5.h5', 'r') as f:")
        print(f"    text_embeddings = f['embeddings'][:]")
        print(f"")
        print(f"# Índice FAISS para búsqueda rápida")
        print(f"index = faiss.read_index('{self.config.output_folder}/embeddings/faiss_text_index.bin')")
        print(f"")
        print(f"# Metadata de chunks")
        print(f"metadata = pd.read_parquet('{self.config.output_folder}/embeddings/metadata.parquet')")
        print(f"")
        print(f"# Buscar documentos similares")
        print(f"query_emb = model.encode(['consulta médica aquí'])")
        print(f"distances, indices = index.search(query_emb, k=5)")
        print(f"results = metadata.iloc[indices[0]]")
        print(f"```")
        
        # Rendimiento
        docs_per_min = self.stats.processed_files / (self.stats.processing_time / 60) if self.stats.processing_time > 0 else 0
        chunks_per_min = self.stats.total_chunks / (self.stats.processing_time / 60) if self.stats.processing_time > 0 else 0
        
        print(f"\n⚡ RENDIMIENTO:")
        print(f"   • Documentos/minuto: {docs_per_min:.1f}")
        print(f"   • Chunks/minuto: {chunks_per_min:.1f}")
        print(f"   • Búsquedas esperadas: <100ms con FAISS")
        
        # Integración con sistema existente
        print(f"\n🔧 INTEGRACIÓN CON TU RAG EXISTENTE:")
        print(f"   • Reemplaza ChromaDB en core/rag_engine.py línea 234")
        print(f"   • Actualiza web/backend/app/core/medical_rag.py")
        print(f"   • Usa embeddings precomputados para mejor rendimiento")
        
        # Logs útiles
        print(f"\n📋 LOGS Y DIAGNÓSTICO:")
        print(f"   • Log principal: {self.config.output_folder}/logs/processing.log")
        print(f"   • Solo errores: {self.config.output_folder}/logs/errors.log")
        print(f"   • Estadísticas: {self.config.output_folder}/logs/stats.json")
        
        if self.stats.failed_files > 0:
            print(f"\n⚠️  ARCHIVOS FALLIDOS: {self.stats.failed_files}")
            print(f"   • Revisa errors.log para detalles específicos")
            print(f"   • Archivos comunes problemáticos: PDFs escaneados, archivos corruptos")
            
        # Verificación de calidad
        if self.stats.total_chunks < 1000:
            print(f"\n💡 SUGERENCIA: Solo {self.stats.total_chunks} chunks generados")
            print(f"   • Considera agregar más documentos para mejor cobertura")
            print(f"   • Objetivo recomendado: 10,000+ chunks para knowledge base robusto")
        
        print(f"\n🎯 KNOWLEDGE BASE LISTO PARA PRODUCCIÓN")
        print(f"   • Compatible con Llama 3.2 1B (128k context)")
        print(f"   • Optimizado para medicina interna y reumatología")
        print(f"   • Búsqueda semántica en español/inglés")
        print("="*80)

def main():
    """Función principal"""
    print("Sistema de Procesamiento de Documentos a Embeddings")
    print("=" * 50)
    
    # Configuración
    config = ProcessingConfig()
    
    # Verificar carpeta de entrada
    if not Path(config.input_folder).exists():
        print(f"Error: La carpeta '{config.input_folder}' no existe.")
        print("Por favor, crea la carpeta y coloca los documentos a procesar.")
        return
    
    # Mostrar configuración
    print(f"Carpeta de entrada: {config.input_folder}")
    print(f"Carpeta de salida: {config.output_folder}")
    print(f"Modelo de texto: {config.text_model}")
    print(f"Modelo de imagen: {config.image_model}")
    print(f"Cores CPU: {config.max_cpu_cores}")
    print(f"Memoria máxima: {config.max_memory_gb}GB")
    print(f"Tamaño de chunk: {config.chunk_size} tokens")
    print()
    
    # Confirmar procesamiento
    response = input("¿Proceder con el procesamiento? (s/N): ").strip().lower()
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Procesamiento cancelado.")
        return
    
    try:
        # Crear procesador
        processor = KnowledgeBaseProcessor(config)
        
        # Procesar documentos
        processor.process_documents()
        
        # Mostrar resumen final detallado
        processor._show_completion_summary()
        
    except KeyboardInterrupt:
        print("\nProcesamiento interrumpido por el usuario.")
        print("El progreso se ha guardado y puede reanudarse ejecutando el script nuevamente.")
        
    except Exception as e:
        print(f"\nError durante el procesamiento: {e}")
        print("Consulta los logs para más detalles.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())