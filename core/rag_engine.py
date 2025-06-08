"""
Motor RAG (Retrieval-Augmented Generation) completo para MedStudy Pro
"""
import numpy as np
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
import hashlib
from datetime import datetime, timezone
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from utils.logging import get_logger

@dataclass
class DocumentChunk:
    """Chunk de documento con metadatos"""
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SearchResult:
    """Resultado de búsqueda con score de relevancia"""
    chunk: DocumentChunk
    score: float
    document_title: str = ""
    document_type: str = ""
    highlights: List[str] = None
    
    def __post_init__(self):
        if self.highlights is None:
            self.highlights = []

@dataclass
class RAGResponse:
    """Respuesta RAG completa"""
    query: str
    generated_response: str
    sources: List[SearchResult]
    processing_time: float
    tokens_used: int = 0
    confidence_score: float = 0.0

class TextChunker:
    """Divide texto en chunks optimizados para embeddings"""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = get_logger("TextChunker")
    
    def chunk_text(self, text: str, preserve_structure: bool = True) -> List[Dict[str, Any]]:
        """
        Divide texto en chunks manteniendo estructura cuando es posible
        """
        if not text.strip():
            return []
        
        # Limpiar texto
        cleaned_text = self._clean_text(text)
        
        if preserve_structure:
            # Intentar dividir por estructura (párrafos, oraciones)
            chunks = self._chunk_by_structure(cleaned_text)
        else:
            # División simple por caracteres
            chunks = self._chunk_by_characters(cleaned_text)
        
        # Agregar metadatos
        processed_chunks = []
        for i, chunk_data in enumerate(chunks):
            processed_chunks.append({
                'content': chunk_data['content'],
                'start_char': chunk_data['start_char'],
                'end_char': chunk_data['end_char'],
                'chunk_index': i,
                'word_count': len(chunk_data['content'].split()),
                'char_count': len(chunk_data['content'])
            })
        
        self.logger.debug(f"Texto dividido en {len(processed_chunks)} chunks")
        return processed_chunks
    
    def _clean_text(self, text: str) -> str:
        """Limpia y normaliza el texto"""
        # Remover caracteres de control
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espacios al inicio y final
        text = text.strip()
        
        return text
    
    def _chunk_by_structure(self, text: str) -> List[Dict[str, Any]]:
        """Divide texto respetando estructura (párrafos, oraciones)"""
        chunks = []
        
        # Dividir por párrafos primero
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        start_char = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Si el párrafo es muy largo, dividirlo por oraciones
            if len(paragraph) > self.chunk_size:
                # Finalizar chunk actual si existe
                if current_chunk:
                    chunks.append({
                        'content': current_chunk.strip(),
                        'start_char': start_char,
                        'end_char': start_char + len(current_chunk)
                    })
                    current_chunk = ""
                
                # Dividir párrafo largo
                sentences = self._split_into_sentences(paragraph)
                sentence_chunk = ""
                sentence_start = start_char
                
                for sentence in sentences:
                    if len(sentence_chunk + sentence) > self.chunk_size and sentence_chunk:
                        chunks.append({
                            'content': sentence_chunk.strip(),
                            'start_char': sentence_start,
                            'end_char': sentence_start + len(sentence_chunk)
                        })
                        sentence_start += len(sentence_chunk)
                        sentence_chunk = sentence
                    else:
                        sentence_chunk += sentence
                
                if sentence_chunk:
                    chunks.append({
                        'content': sentence_chunk.strip(),
                        'start_char': sentence_start,
                        'end_char': sentence_start + len(sentence_chunk)
                    })
                
                start_char += len(paragraph) + 2  # +2 por \n\n
            else:
                # Agregar párrafo al chunk actual
                if len(current_chunk + paragraph) > self.chunk_size and current_chunk:
                    # Finalizar chunk actual
                    chunks.append({
                        'content': current_chunk.strip(),
                        'start_char': start_char,
                        'end_char': start_char + len(current_chunk)
                    })
                    
                    # Iniciar nuevo chunk con overlap
                    if self.overlap > 0:
                        overlap_text = current_chunk[-self.overlap:]
                        current_chunk = overlap_text + paragraph
                        start_char = start_char + len(current_chunk) - self.overlap - len(paragraph)
                    else:
                        current_chunk = paragraph
                        start_char += len(current_chunk)
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
        
        # Agregar último chunk
        if current_chunk:
            chunks.append({
                'content': current_chunk.strip(),
                'start_char': start_char,
                'end_char': start_char + len(current_chunk)
            })
        
        return chunks
    
    def _chunk_by_characters(self, text: str) -> List[Dict[str, Any]]:
        """División simple por número de caracteres"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Intentar cortar en un espacio para no partir palabras
            if end < len(text):
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunks.append({
                    'content': chunk_content,
                    'start_char': start,
                    'end_char': end
                })
            
            # Aplicar overlap
            start = max(start + 1, end - self.overlap)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones"""
        # Patrón simple para dividir oraciones
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        
        # Limpiar oraciones vacías
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences

class EmbeddingManager:
    """Gestor de embeddings con cache y múltiples modelos"""
    
    def __init__(self, config_manager=None, model_name: str = None):
        self.config = config_manager
        self.logger = get_logger("EmbeddingManager")
        
        # Configuración de modelo
        if model_name:
            self.model_name = model_name
        elif config_manager:
            self.model_name = config_manager.get('EMBEDDINGS', 'model', 'sentence-transformers/all-MiniLM-L6-v2')
        else:
            self.model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        
        self.model = None
        self.dimension = None
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Inicializar modelo
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            
            self.logger.info(f"Cargando modelo de embeddings: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Obtener dimensión del modelo
            test_embedding = self.model.encode(["test"])
            self.dimension = test_embedding.shape[1]
            
            self.logger.info(f"Modelo cargado. Dimensión: {self.dimension}")
            
        except Exception as e:
            self.logger.error(f"Error cargando modelo de embeddings: {e}")
            # Fallback a embeddings aleatorios para testing
            self.model = None
            self.dimension = 384
            self.logger.warning("Usando embeddings aleatorios (solo para pruebas)")
    
    def encode_text(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Genera embedding para un texto"""
        if not text.strip():
            return np.zeros(self.dimension)
        
        # Verificar cache
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        if use_cache and cache_key in self._cache:
            self._cache_hits += 1
            return self._cache[cache_key]
        
        self._cache_misses += 1
        
        # Generar embedding
        if self.model:
            try:
                embedding = self.model.encode([text])[0]
            except Exception as e:
                self.logger.error(f"Error generando embedding: {e}")
                embedding = np.random.random(self.dimension)
        else:
            # Fallback a embedding aleatorio
            embedding = np.random.random(self.dimension)
        
        # Guardar en cache
        if use_cache:
            self._cache[cache_key] = embedding
        
        return embedding
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Genera embeddings para múltiples textos en lotes"""
        if not texts:
            return []
        
        embeddings = []
        
        if self.model:
            try:
                # Procesar en lotes
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    batch_embeddings = self.model.encode(batch)
                    embeddings.extend(batch_embeddings)
                    
                    self.logger.debug(f"Procesado lote {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                    
            except Exception as e:
                self.logger.error(f"Error en encode_batch: {e}")
                # Fallback a embeddings aleatorios
                embeddings = [np.random.random(self.dimension) for _ in texts]
        else:
            embeddings = [np.random.random(self.dimension) for _ in texts]
        
        return embeddings
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calcula similitud coseno entre dos embeddings"""
        try:
            # Normalizar vectores
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Similitud coseno
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            # Asegurar que esté en rango [-1, 1]
            similarity = np.clip(similarity, -1.0, 1.0)
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Error calculando similitud: {e}")
            return 0.0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_size': len(self._cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate,
            'model_name': self.model_name,
            'dimension': self.dimension
        }
    
    def clear_cache(self):
        """Limpia el cache de embeddings"""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self.logger.info("Cache de embeddings limpiado")

class VectorStore:
    """Almacén de vectores con búsqueda por similitud"""
    
    def __init__(self, database_manager, embedding_manager: EmbeddingManager):
        self.db = database_manager
        self.embedding_manager = embedding_manager
        self.logger = get_logger("VectorStore")
        
        # Crear tabla de vectores si no existe
        self._ensure_vector_table()
    
    def _ensure_vector_table(self):
        """Asegura que la tabla de vectores existe"""
        with self.db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_embeddings (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    embedding_model TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chunk_id) REFERENCES document_chunks (id) ON DELETE CASCADE
                )
            """)
            
            # Índice para búsquedas por documento
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_vector_document_id 
                ON vector_embeddings(document_id)
            """)
    
    def store_embedding(self, chunk_id: str, document_id: str, embedding: np.ndarray):
        """Almacena un embedding en la base de datos"""
        try:
            # Serializar embedding a bytes
            embedding_bytes = embedding.tobytes()
            
            with self.db.transaction() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO vector_embeddings 
                    (chunk_id, document_id, embedding, embedding_model)
                    VALUES (?, ?, ?, ?)
                """, (chunk_id, document_id, embedding_bytes, self.embedding_manager.model_name))
            
            self.logger.debug(f"Embedding almacenado para chunk {chunk_id}")
            
        except Exception as e:
            self.logger.error(f"Error almacenando embedding: {e}")
            raise
    
    def get_embedding(self, chunk_id: str) -> Optional[np.ndarray]:
        """Recupera un embedding de la base de datos"""
        try:
            with self.db.get_connection() as conn:
                result = conn.execute("""
                    SELECT embedding FROM vector_embeddings WHERE chunk_id = ?
                """, (chunk_id,)).fetchone()
                
                if result:
                    # Deserializar embedding
                    embedding = np.frombuffer(result[0], dtype=np.float32)
                    return embedding.reshape(-1)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error recuperando embedding: {e}")
            return None
    
    def search_similar(self, query_embedding: np.ndarray, limit: int = 10,
                      similarity_threshold: float = 0.0, 
                      document_ids: List[str] = None) -> List[Tuple[str, float]]:
        """
        Busca chunks similares al query embedding
        
        Returns:
            List[(chunk_id, similarity_score)]
        """
        try:
            with self.db.get_connection() as conn:
                # Construir query SQL
                base_query = """
                    SELECT ve.chunk_id, ve.embedding, dc.content, d.title, d.document_type
                    FROM vector_embeddings ve
                    JOIN document_chunks dc ON ve.chunk_id = dc.id
                    JOIN documents d ON ve.document_id = d.id
                """
                
                params = []
                if document_ids:
                    placeholders = ','.join(['?' for _ in document_ids])
                    base_query += f" WHERE ve.document_id IN ({placeholders})"
                    params.extend(document_ids)
                
                results = conn.execute(base_query, params).fetchall()
                
                # Calcular similitudes
                similarities = []
                for row in results:
                    chunk_id = row[0]
                    stored_embedding = np.frombuffer(row[1], dtype=np.float32)
                    
                    similarity = self.embedding_manager.calculate_similarity(
                        query_embedding, stored_embedding
                    )
                    
                    if similarity >= similarity_threshold:
                        similarities.append((chunk_id, similarity))
                
                # Ordenar por similitud descendente
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                return similarities[:limit]
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda de similitud: {e}")
            return []
    
    def delete_embeddings(self, document_id: str):
        """Elimina embeddings de un documento"""
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute("""
                    DELETE FROM vector_embeddings WHERE document_id = ?
                """, (document_id,))
                
                deleted_count = cursor.rowcount
                self.logger.info(f"Eliminados {deleted_count} embeddings del documento {document_id}")
                
        except Exception as e:
            self.logger.error(f"Error eliminando embeddings: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del vector store"""
        try:
            with self.db.get_connection() as conn:
                # Conteo total
                total_embeddings = conn.execute("""
                    SELECT COUNT(*) FROM vector_embeddings
                """).fetchone()[0]
                
                # Por modelo
                by_model = conn.execute("""
                    SELECT embedding_model, COUNT(*) 
                    FROM vector_embeddings 
                    GROUP BY embedding_model
                """).fetchall()
                
                # Por documento
                by_document = conn.execute("""
                    SELECT d.title, COUNT(*) as chunk_count
                    FROM vector_embeddings ve
                    JOIN documents d ON ve.document_id = d.id
                    GROUP BY ve.document_id, d.title
                    ORDER BY chunk_count DESC
                    LIMIT 10
                """).fetchall()
                
                return {
      