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
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database {self.db_path}: {e}")
            raise
        except Exception as e_gen: # Catch any other unexpected error during init
            self.logger.error(f"Unexpected error during database initialization for {self.db_path}: {e_gen}")
            raise
    
    def _create_basic_tables(self, conn: sqlite3.Connection):
        """Create basic tables for immediate use + RAG and MedCards tables"""
        
        # Application metadata table
        # Application metadata table: Stores key-value pairs for application settings & info.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_metadata (
                key         TEXT PRIMARY KEY,
                value       TEXT NOT NULL,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Auto-updates on record change (SQLite specific behavior for TIMESTAMP)
            )
        """)
        
        # User preferences table: Stores user-specific settings.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category    TEXT NOT NULL,
                key         TEXT NOT NULL,
                value       TEXT NOT NULL,
                data_type   TEXT DEFAULT 'string', -- Expected data type: 'string', 'int', 'float', 'bool', 'json'
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Auto-updates on record change
                UNIQUE(category, key)
            )
        """)
        
        # Session logs for debugging & analytics.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type    TEXT NOT NULL, -- E.g., 'study', 'quiz', 'app_lifecycle'
                data            TEXT,          -- JSON string with session-specific data
                timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Documents table for RAG system: Stores metadata about imported documents.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id     TEXT PRIMARY KEY, -- E.g., UUID or hash of the document
                title           TEXT NOT NULL,
                file_path       TEXT NOT NULL UNIQUE, -- Ensure unique file paths
                pages           INTEGER DEFAULT 0,
                file_size       INTEGER DEFAULT 0,    -- In bytes
                images_count    INTEGER DEFAULT 0,
                processed_at    TIMESTAMP,            -- Timestamp of when processing (e.g., embedding) was completed
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Document images table: Stores extracted images from documents.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_images (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id     TEXT NOT NULL,
                filename        TEXT NOT NULL,        -- Original filename or generated name
                page_number     INTEGER NOT NULL,
                file_path       TEXT NOT NULL UNIQUE, -- Path to the extracted image file
                file_size       INTEGER DEFAULT 0,    -- In bytes
                ocr_text        TEXT,                 -- OCR-extracted text from the image
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
            )
        """)
        
        # Study plans table: Defines user-created study plans.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_plans (
                plan_id             TEXT PRIMARY KEY, -- E.g., UUID
                title               TEXT NOT NULL,
                specialty           TEXT DEFAULT 'general',
                topics              TEXT NOT NULL, -- JSON list of topics or keywords
                confidence_levels   TEXT NOT NULL, -- JSON map of topic to confidence level
                last_studied        TEXT,          -- ISO8601 timestamp of the last study session for this plan
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Auto-updates on record change
            )
        """)
        
        # Study sessions table: Logs individual study sessions.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                session_id                  TEXT PRIMARY KEY, -- E.g., UUID
                plan_id                     TEXT,             -- Optional link to a study plan
                topic                       TEXT NOT NULL,
                content_generated           TEXT,             -- JSON data of content shown to user
                duration_minutes            INTEGER DEFAULT 45,
                active_recall_responses     TEXT,             -- JSON list of active recall questions and answers
                quiz_results                TEXT,             -- JSON data of quiz performance
                started_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at                TIMESTAMP,        -- ISO8601 timestamp when session was completed
                FOREIGN KEY (plan_id) REFERENCES study_plans (plan_id) ON DELETE SET NULL
            )
        """)
        
        # MedCards table: Stores flashcards (SRS items).
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medcards (
                card_id             TEXT PRIMARY KEY, -- E.g., UUID
                card_type           TEXT NOT NULL CHECK(card_type IN ('qa', 'cloze', 'image_occlusion', 'comprehension', 'custom')), -- Type of card
                question            TEXT NOT NULL,
                answer              TEXT NOT NULL,
                specialty           TEXT DEFAULT 'general',
                tags                TEXT DEFAULT '[]',    -- JSON list of string tags
                image_path          TEXT,                 -- Path to an associated image, if any
                -- SRS Algorithm Fields
                interval            REAL DEFAULT 1.0,     -- Current interval in days
                ease_factor         REAL DEFAULT 2.5,     -- Factor affecting interval changes
                repetitions         INTEGER DEFAULT 0,    -- Number of times successfully recalled
                lapses              INTEGER DEFAULT 0,    -- Number of times forgotten after first success
                -- Scheduling Fields
                due_date            TEXT NOT NULL,        -- ISO8601 date (YYYY-MM-DD) when card is next due
                last_reviewed       TEXT,                 -- ISO8601 timestamp of last review
                -- Statistics
                total_reviews       INTEGER DEFAULT 0,
                correct_reviews     INTEGER DEFAULT 0,
                average_time        REAL DEFAULT 0.0,     -- Average time spent on this card in seconds
                -- Timestamps
                created_at          TEXT NOT NULL,        -- ISO8601 timestamp
                modified_at         TEXT NOT NULL         -- ISO8601 timestamp
            )
        """)
        
        # MedCard reviews history: Logs each review interaction with a flashcard.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medcard_reviews (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id                 TEXT NOT NULL,
                difficulty              TEXT NOT NULL CHECK(difficulty IN ('again', 'hard', 'good', 'easy')), -- User's perceived difficulty
                time_taken_seconds      INTEGER NOT NULL,
                correct                 INTEGER NOT NULL, -- Boolean: 0 for incorrect, 1 for correct
                reviewed_at             TEXT NOT NULL,    -- ISO8601 timestamp of the review
                FOREIGN KEY (card_id) REFERENCES medcards (card_id) ON DELETE CASCADE
            )
        """)
        
        # MedCard study sessions: Logs specific study sessions for flashcards.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medcard_sessions (
                session_id          TEXT PRIMARY KEY, -- E.g., UUID
                cards_reviewed      INTEGER DEFAULT 0,
                cards_correct       INTEGER DEFAULT 0,
                total_time_seconds  INTEGER DEFAULT 0,
                session_type        TEXT DEFAULT 'review' CHECK(session_type IN ('new', 'review', 'learn', 'custom')), -- Type of session
                started_at          TEXT NOT NULL,    -- ISO8601 timestamp
                completed_at        TEXT              -- ISO8601 timestamp
            )
        """)
        
        # Exam results table: Stores results from practice exams.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exam_results (
                exam_id             TEXT PRIMARY KEY, -- E.g., UUID
                plan_id             TEXT,             -- Optional link to a study plan
                exam_type           TEXT DEFAULT 'adaptive' CHECK(exam_type IN ('adaptive', 'standard', 'topic_focused', 'custom')),
                questions_total     INTEGER DEFAULT 45,
                questions_correct   INTEGER DEFAULT 0,
                time_taken_seconds  INTEGER DEFAULT 0,
                score_percentage    REAL DEFAULT 0.0,
                detailed_results    TEXT,             -- JSON string containing detailed question-by-question results
                started_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at        TIMESTAMP,        -- ISO8601 timestamp
                FOREIGN KEY (plan_id) REFERENCES study_plans (plan_id) ON DELETE SET NULL
            )
        """)
        
        # User progress analytics: Stores aggregated progress metrics over time.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                date                TEXT NOT NULL,        -- Date of the metric (YYYY-MM-DD)
                metric_name         TEXT NOT NULL,        -- E.g., 'cards_reviewed', 'active_study_hours', 'topic_mastery'
                metric_value        REAL NOT NULL,
                specialty           TEXT DEFAULT 'general', -- Medical specialty context, if any
                additional_data     TEXT,                 -- JSON for extra unstructured data
                recorded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, metric_name, specialty)
            )
        """)
        
        # Create indexes for better performance
        # Existing indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_processed_at ON documents (processed_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcards_due_date ON medcards (due_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcards_specialty ON medcards (specialty)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_started_at ON study_sessions (started_at)") # Often queried by time
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_progress_date ON user_progress (date)")
        
        # New indexes for Foreign Keys and frequently queried columns
        conn.execute("CREATE INDEX IF NOT EXISTS idx_document_images_document_id ON document_images (document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_plan_id ON study_sessions (plan_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcard_reviews_card_id ON medcard_reviews (card_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_exam_results_plan_id ON exam_results (plan_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcards_last_reviewed ON medcards (last_reviewed)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medcard_reviews_reviewed_at ON medcard_reviews (reviewed_at)")

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
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database connection error for {self.db_path}: {e}")
            raise
        except Exception as e_gen: # Catch any other unexpected error during connection
            if conn:
                conn.rollback()
            self.logger.error(f"Unexpected error establishing database connection for {self.db_path}: {e_gen}")
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
        except sqlite3.Error as e_db:
            self.logger.error(f"Database error in get_preference(category='{category}', key='{key}'): {e_db}")
            return default
        except (ValueError, json.JSONDecodeError) as e_conv:
            self.logger.error(f"Conversion error in get_preference(category='{category}', key='{key}', value_str='{value}', data_type='{data_type}'): {e_conv}")
            return default
        except Exception as e_gen: # Catch any other unexpected error
            self.logger.error(f"Unexpected error in get_preference(category='{category}', key='{key}'): {e_gen}")
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
        except (sqlite3.Error, TypeError, ValueError) as e_db_json: # TypeError for json.dumps, ValueError for other issues
            # Note: Including 'value' in log might be verbose/sensitive for some data.
            self.logger.error(f"Error in set_preference(category='{category}', key='{key}', value_type='{type(value).__name__}'): {e_db_json}")
            return False
        except Exception as e_gen:
            self.logger.error(f"Unexpected error in set_preference(category='{category}', key='{key}', value_type='{type(value).__name__}'): {e_gen}")
            return False
    
    def log_session(self, session_type: str, data: Optional[Dict[str, Any]] = None):
        """Log session data for analytics"""
        try:
            data_json = json.dumps(data) if data else None
            self.execute_update(
                "INSERT INTO session_logs (session_type, data) VALUES (?, ?)",
                (session_type, data_json)
            )
        except (sqlite3.Error, TypeError) as e_db_json: # TypeError for json.dumps
            self.logger.error(f"Error in log_session(session_type='{session_type}'): {e_db_json}")
        except Exception as e_gen:
            self.logger.error(f"Unexpected error in log_session(session_type='{session_type}'): {e_gen}")
    
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
        except sqlite3.Error as e_db:
            self.logger.error(f"Error getting database info for {self.db_path}: {e_db}")
            return {'error': str(e_db)}
        except Exception as e_gen:
            self.logger.error(f"Unexpected error getting database info for {self.db_path}: {e_gen}")
            return {'error': str(e_gen)}
    
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
        except sqlite3.Error as e_db:
            actual_backup_path = backup_path or f"{self.db_path.stem}_backup_*.db"
            self.logger.error(f"Database error during backup of {self.db_path} to {actual_backup_path}: {e_db}")
            return False
        except IOError as e_io:
            actual_backup_path = backup_path or f"{self.db_path.stem}_backup_*.db"
            self.logger.error(f"IO error during backup of {self.db_path} to {actual_backup_path}: {e_io}")
            return False
        except Exception as e_gen:
            actual_backup_path = backup_path or f"{self.db_path.stem}_backup_*.db"
            self.logger.error(f"Unexpected error during backup of {self.db_path} to {actual_backup_path}: {e_gen}")
            return False
    
    def vacuum_database(self) -> bool:
        """Optimize database (VACUUM)"""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
            
            self.logger.info("Database vacuumed successfully")
            return True
        except sqlite3.Error as e_db:
            self.logger.error(f"Error vacuuming database {self.db_path}: {e_db}")
            return False
        except Exception as e_gen:
            self.logger.error(f"Unexpected error vacuuming database {self.db_path}: {e_gen}")
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
    

    _db_utils_logger = logging.getLogger('MedStudy.DatabaseUtils')

    @staticmethod
    def _validate_identifier(identifier: str) -> bool:
        """
        Validate SQL identifier (table or column name) for security.
        Allows names starting with a letter, followed by letters, numbers, or underscores.
        """
        if not identifier: # Should not be empty
            return False
        import re
        # Regex ensures the identifier starts with a letter and contains only alphanumeric chars or underscores.
        # This helps prevent SQL injection through identifiers like "col; DROP TABLE users" or "1=1 --"
        pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
        return bool(pattern.match(identifier))

    @staticmethod
    def build_where_clause(conditions: Dict[str, Any]) -> tuple:
        """Build WHERE clause from conditions dictionary, safely."""
        if not conditions:
            return "", ()
        
        clauses = []
        params = []
        
        for key, value in conditions.items():
            if not DatabaseUtils._validate_identifier(key):
                DatabaseUtils._db_utils_logger.error(
                    f"Invalid column name '{key}' provided to build_where_clause. "
                    "Column names must be alphanumeric and start with a letter."
                )
                raise ValueError(f"Invalid character or format in column name: {key}")

            if isinstance(value, (list, tuple)):
                if not value: # Handle empty list/tuple for IN clause
                    # SQL syntax for `IN ()` is invalid. Caller should handle or prevent.
                    # Alternatively, could translate to a clause that's always false, e.g., `1=0`.
                    # For now, raising an error as this indicates a likely issue in caller logic.
                    DatabaseUtils._db_utils_logger.error(
                        f"Empty list/tuple provided for IN clause with column '{key}' in build_where_clause."
                    )
                    raise ValueError(f"Empty list/tuple for IN clause is not allowed for column: {key}")
                placeholders = ','.join('?' * len(value))
                clauses.append(f"`{key}` IN ({placeholders})") # Use backticks for safety, though validation helps
                params.extend(value)
            else:
                clauses.append(f"`{key}` = ?") # Use backticks for safety
                params.append(value)
        
        where_clause = " AND ".join(clauses)
        return f"WHERE {where_clause}", tuple(params)

__all__ = ['DatabaseManager', 'initialize_database', 'DatabaseUtils']