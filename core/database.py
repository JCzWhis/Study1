"""
MedStudy Pro - Database Foundation
Base database setup and connection management
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Generator, Dict, Any, List
from datetime import datetime
import json

class DatabaseManager:
    """Manages SQLite database connections and basic operations"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger('MedStudy.Database')
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with basic tables"""
        try:
            with self.get_connection() as conn:
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create basic tables that don't require SQLAlchemy
                self._create_basic_tables(conn)
                
                self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_basic_tables(self, conn: sqlite3.Connection):
        """Create basic tables for immediate use + RAG and MedCards tables"""
        
        # Application metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User preferences table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                data_type TEXT DEFAULT 'string',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        """)
        
        # Session logs for debugging
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL,
                data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Documents table for RAG system
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                pages INTEGER DEFAULT 0,
                file_size INTEGER DEFAULT 0,
                images_count INTEGER DEFAULT 0,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Document images table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                ocr_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (document_id)
            )
        """)
        
        # Study plans table (retrospective planning)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_plans (
                plan_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                specialty TEXT DEFAULT 'general',
                topics TEXT NOT NULL,
                confidence_levels TEXT NOT NULL,
                last_studied TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Study sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                session_id TEXT PRIMARY KEY,
                plan_id TEXT,
                topic TEXT NOT NULL,
                content_generated TEXT,
                duration_minutes INTEGER DEFAULT 45,
                active_recall_responses TEXT,
                quiz_results TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES study_plans (plan_id)
            )
        """)
        
        # MedCards tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medcards (
                card_id TEXT PRIMARY KEY,
                card_type TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                specialty TEXT DEFAULT 'general',
                tags TEXT DEFAULT '[]',
                image_path TEXT,
                interval REAL DEFAULT 1.0,
                ease_factor REAL DEFAULT 2.5,
                repetitions INTEGER DEFAULT 0,
                lapses INTEGER DEFAULT 0,
                due_date TEXT NOT NULL,
                last_reviewed TEXT,
                total_reviews INTEGER DEFAULT 0,
                correct_reviews INTEGER DEFAULT 0,
                average_time REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL
            )
        """)
        
        # MedCard reviews history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medcard_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                time_taken_seconds INTEGER NOT NULL,
                correct BOOLEAN NOT NULL,
                reviewed_at TEXT NOT NULL,
                FOREIGN KEY (card_id) REFERENCES medcards (card_id)
            )
        """)
        
        # MedCard study sessions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medcard_sessions (
                session_id TEXT PRIMARY KEY,
                cards_reviewed INTEGER DEFAULT 0,
                cards_correct INTEGER DEFAULT 0,
                total_time_seconds INTEGER DEFAULT 0,
                session_type TEXT DEFAULT 'review',
                started_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        
        # Exam results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exam_results (
                exam_id TEXT PRIMARY KEY,
                plan_id TEXT,
                exam_type TEXT DEFAULT 'adaptive',
                questions_total INTEGER DEFAULT 45,
                questions_correct INTEGER DEFAULT 0,
                time_taken_seconds INTEGER DEFAULT 0,
                score_percentage REAL DEFAULT 0.0,
                detailed_results TEXT,
                questions_data TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES study_plans (plan_id)
            )
        """)
        
        # User progress analytics
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                specialty TEXT DEFAULT 'general',
                additional_data TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, metric_name, specialty)
            )
        """)
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_processed_at ON documents (processed_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcards_due_date ON medcards (due_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcards_specialty ON medcards (specialty)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_started_at ON study_sessions (started_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_progress_date ON user_progress (date)")
        
        # Insert initial metadata
        conn.execute("""
            INSERT OR IGNORE INTO app_metadata (key, value) 
            VALUES ('database_version', '2.0')
        """)
        
        conn.execute("""
            INSERT OR IGNORE INTO app_metadata (key, value) 
            VALUES ('initialized_at', ?)
        """, (datetime.now().isoformat(),))
        
        conn.execute("""
            INSERT OR IGNORE INTO app_metadata (key, value) 
            VALUES ('schema_version', 'medstudy_pro_v1')
        """)
        
        conn.commit()
        
        # Log successful creation
        self.logger.info("Created complete MedStudy Pro database schema with 12 tables")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            
            # Configure connection
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute UPDATE/INSERT/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
    
    def get_preference(self, category: str, key: str, default: Any = None) -> Any:
        """Get user preference with type conversion"""
        try:
            result = self.execute_query(
                "SELECT value, data_type FROM user_preferences WHERE category = ? AND key = ?",
                (category, key)
            )
            
            if not result:
                return default
            
            value = result[0]['value']
            data_type = result[0]['data_type']
            
            # Convert based on stored type
            if data_type == 'int':
                return int(value)
            elif data_type == 'float':
                return float(value)
            elif data_type == 'bool':
                return value.lower() == 'true'
            elif data_type == 'json':
                return json.loads(value)
            else:
                return value
                
        except Exception as e:
            self.logger.error(f"Error getting preference {category}.{key}: {e}")
            return default
    
    def set_preference(self, category: str, key: str, value: Any) -> bool:
        """Set user preference with automatic type detection"""
        try:
            # Determine data type
            if isinstance(value, bool):
                data_type = 'bool'
                value_str = str(value).lower()
            elif isinstance(value, int):
                data_type = 'int'
                value_str = str(value)
            elif isinstance(value, float):
                data_type = 'float'
                value_str = str(value)
            elif isinstance(value, (dict, list)):
                data_type = 'json'
                value_str = json.dumps(value)
            else:
                data_type = 'string'
                value_str = str(value)
            
            # Insert or update
            self.execute_update("""
                INSERT OR REPLACE INTO user_preferences 
                (category, key, value, data_type, updated_at) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (category, key, value_str, data_type))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting preference {category}.{key}: {e}")
            return False
    
    def log_session(self, session_type: str, data: Optional[Dict[str, Any]] = None):
        """Log session data for analytics"""
        try:
            data_json = json.dumps(data) if data else None
            self.execute_update(
                "INSERT INTO session_logs (session_type, data) VALUES (?, ?)",
                (session_type, data_json)
            )
        except Exception as e:
            self.logger.error(f"Error logging session: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            with self.get_connection() as conn:
                # Get database version
                version_result = conn.execute(
                    "SELECT value FROM app_metadata WHERE key = 'database_version'"
                ).fetchone()
                
                # Get table count
                table_result = conn.execute(
                    "SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'"
                ).fetchone()
                
                # Get database size
                size_result = conn.execute("PRAGMA page_count").fetchone()
                page_size_result = conn.execute("PRAGMA page_size").fetchone()
                
                return {
                    'version': version_result['value'] if version_result else 'unknown',
                    'table_count': table_result['count'],
                    'size_bytes': size_result[0] * page_size_result[0],
                    'path': str(self.db_path),
                    'exists': self.db_path.exists()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {'error': str(e)}
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create database backup"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.db_path.stem}_backup_{timestamp}.db"
            
            backup_path = Path(backup_path)
            
            # Use SQLite backup API
            with self.get_connection() as source:
                with sqlite3.connect(backup_path) as target:
                    source.backup(target)
            
            self.logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            return False
    
    def vacuum_database(self) -> bool:
        """Optimize database (VACUUM)"""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
            
            self.logger.info("Database vacuumed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error vacuuming database: {e}")
            return False


# Database initialization function
def initialize_database(db_path: str) -> DatabaseManager:
    """Initialize database manager"""
    return DatabaseManager(db_path)

# Utility functions for common operations
class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    def dict_factory(cursor, row):
        """Convert row to dictionary"""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    
    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Validate table name for security"""
        import re
        pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
        return bool(pattern.match(table_name))
    
    @staticmethod
    def build_where_clause(conditions: Dict[str, Any]) -> tuple:
        """Build WHERE clause from conditions dictionary"""
        if not conditions:
            return "", ()
        
        clauses = []
        params = []
        
        for key, value in conditions.items():
            if isinstance(value, (list, tuple)):
                placeholders = ','.join('?' * len(value))
                clauses.append(f"{key} IN ({placeholders})")
                params.extend(value)
            else:
                clauses.append(f"{key} = ?")
                params.append(value)
        
        where_clause = " AND ".join(clauses)
        return f"WHERE {where_clause}", tuple(params)

__all__ = ['DatabaseManager', 'initialize_database', 'DatabaseUtils']