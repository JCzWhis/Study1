"""
Sistema de base de datos completo para MedStudy Pro
"""
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import logging
import shutil

# Configuración de logging
logger = logging.getLogger("Database")

@dataclass
class AnkiCard:
    """Modelo de tarjeta Anki"""
    id: Optional[str] = None
    question: str = ""
    answer: str = ""
    card_type: str = "basic"  # basic, cloze, multiple_choice
    topic: str = ""
    subtopic: str = ""
    difficulty: str = "medium"  # easy, medium, hard
    tags: str = ""
    source: str = ""
    
    # Anki SRS fields
    ease_factor: float = 2.5
    interval: int = 1
    repetitions: int = 0
    due_date: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.due_date is None:
            self.due_date = datetime.now(timezone.utc)

@dataclass
class StudySession:
    """Modelo de sesión de estudio"""
    id: Optional[str] = None
    session_type: str = "review"  # review, learn, practice
    cards_studied: int = 0
    cards_correct: int = 0
    cards_incorrect: int = 0
    total_time: int = 0  # segundos
    average_response_time: float = 0.0
    topics_covered: str = ""  # JSON array
    difficulty_distribution: str = ""  # JSON object
    
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class Document:
    """Modelo de documento"""
    id: Optional[str] = None
    title: str = ""
    content: str = ""
    document_type: str = "text"  # text, pdf, image, url
    category: str = ""
    tags: str = ""
    file_path: str = ""
    file_size: int = 0
    
    # Procesamiento
    is_processed: bool = False
    embedding_model: str = ""
    chunk_count: int = 0
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class DocumentChunk:
    """Modelo de chunk de documento para RAG"""
    id: Optional[str] = None
    document_id: str = ""
    content: str = ""
    chunk_index: int = 0
    start_char: int = 0
    end_char: int = 0
    
    # Embeddings
    embedding: Optional[str] = None  # JSON array
    embedding_model: str = ""
    
    # Metadata
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class ChatMessage:
    """Modelo de mensaje de chat"""
    id: Optional[str] = None
    session_id: str = ""
    role: str = ""  # user, assistant, system
    content: str = ""
    tokens_used: int = 0
    response_time: float = 0.0
    
    # Metadata
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

class DatabaseManager:
    """Gestor principal de base de datos"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.db_path = config_manager.get_database_path()
        self.backup_dir = config_manager.get_app_directory() / "backups"
        
        # Crear directorios
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado
        self._connection = None
        self._transaction_depth = 0
        
        # Inicializar base de datos
        self._initialize_database()
        
        logger.info(f"Base de datos inicializada: {self.db_path}")
    
    def _initialize_database(self):
        """Inicializa la base de datos y ejecuta migraciones"""
        with self.get_connection() as conn:
            # Habilitar foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Crear tablas base
            self._create_tables(conn)
            
            # Ejecutar migraciones
            self._run_migrations(conn)
            
            # Crear índices
            self._create_indexes(conn)
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión de base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def transaction(self):
        """Context manager para transacciones"""
        with self.get_connection() as conn:
            self._transaction_depth += 1
            try:
                if self._transaction_depth == 1:
                    conn.execute("BEGIN")
                yield conn
                if self._transaction_depth == 1:
                    conn.commit()
            except Exception as e:
                if self._transaction_depth == 1:
                    conn.rollback()
                raise
            finally:
                self._transaction_depth -= 1
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Crea las tablas de la base de datos"""
        
        # Tabla de metadatos de la base de datos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS db_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de tarjetas Anki
        conn.execute("""
            CREATE TABLE IF NOT EXISTS anki_cards (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                card_type TEXT DEFAULT 'basic',
                topic TEXT DEFAULT '',
                subtopic TEXT DEFAULT '',
                difficulty TEXT DEFAULT 'medium',
                tags TEXT DEFAULT '',
                source TEXT DEFAULT '',
                
                -- Campos SRS
                ease_factor REAL DEFAULT 2.5,
                interval INTEGER DEFAULT 1,
                repetitions INTEGER DEFAULT 0,
                due_date TIMESTAMP,
                last_reviewed TIMESTAMP,
                review_count INTEGER DEFAULT 0,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Tabla de sesiones de estudio
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id TEXT PRIMARY KEY,
                session_type TEXT DEFAULT 'review',
                cards_studied INTEGER DEFAULT 0,
                cards_correct INTEGER DEFAULT 0,
                cards_incorrect INTEGER DEFAULT 0,
                total_time INTEGER DEFAULT 0,
                average_response_time REAL DEFAULT 0.0,
                topics_covered TEXT DEFAULT '[]',
                difficulty_distribution TEXT DEFAULT '{}',
                
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de documentos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT DEFAULT '',
                document_type TEXT DEFAULT 'text',
                category TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                file_size INTEGER DEFAULT 0,
                
                -- Procesamiento
                is_processed BOOLEAN DEFAULT 0,
                embedding_model TEXT DEFAULT '',
                chunk_count INTEGER DEFAULT 0,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Tabla de chunks de documentos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER DEFAULT 0,
                start_char INTEGER DEFAULT 0,
                end_char INTEGER DEFAULT 0,
                
                -- Embeddings
                embedding TEXT,
                embedding_model TEXT DEFAULT '',
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de mensajes de chat
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                response_time REAL DEFAULT 0.0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de configuraciones del usuario
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de estadísticas de estudio
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_statistics (
                id TEXT PRIMARY KEY,
                date DATE NOT NULL,
                cards_reviewed INTEGER DEFAULT 0,
                cards_learned INTEGER DEFAULT 0,
                study_time INTEGER DEFAULT 0,
                topics_studied TEXT DEFAULT '[]',
                accuracy_rate REAL DEFAULT 0.0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar versión inicial
        conn.execute("""
            INSERT OR IGNORE INTO db_metadata (key, value) 
            VALUES ('schema_version', '1.0')
        """)
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Crea índices para optimizar consultas"""
        indexes = [
            # Anki cards
            "CREATE INDEX IF NOT EXISTS idx_anki_cards_due_date ON anki_cards(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_anki_cards_topic ON anki_cards(topic)",
            "CREATE INDEX IF NOT EXISTS idx_anki_cards_difficulty ON anki_cards(difficulty)",
            "CREATE INDEX IF NOT EXISTS idx_anki_cards_is_active ON anki_cards(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_anki_cards_created_at ON anki_cards(created_at)",
            
            # Documents
            "CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)",
            "CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type)",
            "CREATE INDEX IF NOT EXISTS idx_documents_is_processed ON documents(is_processed)",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)",
            
            # Document chunks
            "CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id)",
            "CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON document_chunks(chunk_index)",
            
            # Chat messages
            "CREATE INDEX IF NOT EXISTS idx_chat_session_id ON chat_messages(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_messages(created_at)",
            
            # Study sessions
            "CREATE INDEX IF NOT EXISTS idx_study_sessions_created_at ON study_sessions(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_study_sessions_session_type ON study_sessions(session_type)",
            
            # Study statistics
            "CREATE INDEX IF NOT EXISTS idx_study_stats_date ON study_statistics(date)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
            except Exception as e:
                logger.warning(f"Error creando índice: {e}")
    
    def _run_migrations(self, conn: sqlite3.Connection):
        """Ejecuta migraciones de base de datos"""
        current_version = self.get_schema_version(conn)
        logger.info(f"Versión actual del esquema: {current_version}")
        
        # Definir migraciones
        migrations = {
            "1.1": self._migrate_to_1_1,
            "1.2": self._migrate_to_1_2
        }
        
        # Ejecutar migraciones necesarias
        for version, migration_func in migrations.items():
            if self._version_compare(current_version, version) < 0:
                logger.info(f"Ejecutando migración a versión {version}")
                try:
                    migration_func(conn)
                    self.set_schema_version(conn, version)
                    logger.info(f"Migración a {version} completada")
                except Exception as e:
                    logger.error(f"Error en migración a {version}: {e}")
                    raise
    
    def _migrate_to_1_1(self, conn: sqlite3.Connection):
        """Migración a versión 1.1 - Agregar campos de estadísticas"""
        # Agregar campos de estadísticas a anki_cards si no existen
        try:
            conn.execute("ALTER TABLE anki_cards ADD COLUMN streak_count INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Campo ya existe
        
        try:
            conn.execute("ALTER TABLE anki_cards ADD COLUMN last_streak_reset TIMESTAMP")
        except sqlite3.OperationalError:
            pass
    
    def _migrate_to_1_2(self, conn: sqlite3.Connection):
        """Migración a versión 1.2 - Agregar tabla de exportaciones"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exports (
                id TEXT PRIMARY KEY,
                export_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                records_count INTEGER DEFAULT 0,
                file_size INTEGER DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def get_schema_version(self, conn: sqlite3.Connection) -> str:
        """Obtiene la versión actual del esquema"""
        try:
            result = conn.execute(
                "SELECT value FROM db_metadata WHERE key = 'schema_version'"
            ).fetchone()
            return result[0] if result else "1.0"
        except:
            return "1.0"
    
    def set_schema_version(self, conn: sqlite3.Connection, version: str):
        """Establece la versión del esquema"""
        conn.execute("""
            INSERT OR REPLACE INTO db_metadata (key, value, updated_at) 
            VALUES ('schema_version', ?, CURRENT_TIMESTAMP)
        """, (version,))
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compara dos versiones. Retorna -1, 0, o 1"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        
        v1_tuple = version_tuple(v1)
        v2_tuple = version_tuple(v2)
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0
    
    # CRUD para Anki Cards
    def create_anki_card(self, card: AnkiCard) -> str:
        """Crea una nueva tarjeta Anki"""
        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO anki_cards (
                    id, question, answer, card_type, topic, subtopic, difficulty,
                    tags, source, ease_factor, interval, repetitions, due_date,
                    last_reviewed, review_count, created_at, updated_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card.id, card.question, card.answer, card.card_type, card.topic,
                card.subtopic, card.difficulty, card.tags, card.source,
                card.ease_factor, card.interval, card.repetitions, card.due_date,
                card.last_reviewed, card.review_count, card.created_at,
                card.updated_at, card.is_active
            ))
            return card.id
    
    def get_anki_card(self, card_id: str) -> Optional[AnkiCard]:
        """Obtiene una tarjeta Anki por ID"""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT * FROM anki_cards WHERE id = ?", (card_id,)
            ).fetchone()
            
            if result:
                return self._row_to_anki_card(result)
            return None
    
    def update_anki_card(self, card: AnkiCard) -> bool:
        """Actualiza una tarjeta Anki"""
        card.updated_at = datetime.now(timezone.utc)
        
        with self.transaction() as conn:
            cursor = conn.execute("""
                UPDATE anki_cards SET
                    question = ?, answer = ?, card_type = ?, topic = ?, subtopic = ?,
                    difficulty = ?, tags = ?, source = ?, ease_factor = ?,
                    interval = ?, repetitions = ?, due_date = ?, last_reviewed = ?,
                    review_count = ?, updated_at = ?, is_active = ?
                WHERE id = ?
            """, (
                card.question, card.answer, card.card_type, card.topic,
                card.subtopic, card.difficulty, card.tags, card.source,
                card.ease_factor, card.interval, card.repetitions, card.due_date,
                card.last_reviewed, card.review_count, card.updated_at,
                card.is_active, card.id
            ))
            return cursor.rowcount > 0
    
    def delete_anki_card(self, card_id: str) -> bool:
        """Elimina una tarjeta Anki (soft delete)"""
        with self.transaction() as conn:
            cursor = conn.execute(
                "UPDATE anki_ca