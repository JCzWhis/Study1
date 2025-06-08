"""
Sistema de logging avanzado para MedStudy Pro
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import json
import traceback
from contextlib import contextmanager
import threading

class ColoredFormatter(logging.Formatter):
    """Formatter con colores para la consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Verde
        'WARNING': '\033[33m',   # Amarillo
        'ERROR': '\033[31m',     # Rojo
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Agregar color al level name
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """Formatter que produce salida JSON estructurada"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Agregar campos extra
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)

class PerformanceFilter(logging.Filter):
    """Filtro que agrega información de performance"""
    
    def __init__(self):
        super().__init__()
        self._start_times = {}
        self._lock = threading.Lock()
    
    def filter(self, record):
        # Agregar información de thread
        record.thread_name = threading.current_thread().name
        
        # Agregar timestamp más preciso
        record.precise_timestamp = datetime.now().isoformat()
        
        return True

class DatabaseLogHandler(logging.Handler):
    """Handler que guarda logs en base de datos SQLite"""
    
    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa la tabla de logs"""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS application_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    logger TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    function TEXT,
                    line_number INTEGER,
                    thread_name TEXT,
                    exception_type TEXT,
                    exception_message TEXT,
                    traceback_text TEXT,
                    extra_data TEXT
                )
            """)
            
            # Índice para consultas eficientes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
                ON application_logs(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_level 
                ON application_logs(level)
            """)
    
    def emit(self, record):
        """Emite un log record a la base de datos"""
        try:
            import sqlite3
            
            # Preparar datos
            extra_data = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created',
                              'msecs', 'relativeCreated', 'thread', 'threadName',
                              'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                    extra_data[key] = str(value)
            
            # Información de excepción
            exception_type = None
            exception_message = None
            traceback_text = None
            
            if record.exc_info:
                exception_type = record.exc_info[0].__name__
                exception_message = str(record.exc_info[1])
                traceback_text = ''.join(traceback.format_exception(*record.exc_info))
            
            # Insertar en base de datos
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                conn.execute("""
                    INSERT INTO application_logs (
                        timestamp, level, logger, message, module, function, 
                        line_number, thread_name, exception_type, exception_message,
                        traceback_text, extra_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.fromtimestamp(record.created).isoformat(),
                    record.levelname,
                    record.name,
                    record.getMessage(),
                    record.module,
                    record.funcName,
                    record.lineno,
                    getattr(record, 'thread_name', threading.current_thread().name),
                    exception_type,
                    exception_message,
                    traceback_text,
                    json.dumps(extra_data) if extra_data else None
                ))
                
        except Exception as e:
            # No queremos que los errores de logging rompan la aplicación
            print(f"Error en DatabaseLogHandler: {e}", file=sys.stderr)

class LoggingManager:
    """Gestor principal del sistema de logging"""
    
    def __init__(self, config_manager=None):
        self.config = config_manager
        self.loggers = {}
        self._setup_done = False
        
        # Configuración por defecto
        self.default_config = {
            'level': 'INFO',
            'file_logging': True,
            'console_logging': True,
            'database_logging': False,
            'json_format': False,
            'max_log_size': 10,  # MB
            'log_retention': 30,  # días
            'performance_logging': False
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        if self._setup_done:
            return
        
        # Obtener configuración
        if self.config:
            logs_dir = self.config.get_logs_directory()
            level = self.config.get('LOGGING', 'level', 'INFO')
            file_logging = self.config.get('LOGGING', 'file_logging', True)
            console_logging = self.config.get('LOGGING', 'console_logging', True)
            database_logging = self.config.get('LOGGING', 'database_logging', False)
            json_format = self.config.get('LOGGING', 'json_format', False)
            max_log_size = self.config.get('LOGGING', 'max_log_size', 10)
            log_retention = self.config.get('LOGGING', 'log_retention', 30)
            performance_logging = self.config.get('LOGGING', 'performance_logging', False)
        else:
            logs_dir = Path.cwd() / "logs"
            level = self.default_config['level']
            file_logging = self.default_config['file_logging']
            console_logging = self.default_config['console_logging']
            database_logging = self.default_config['database_logging']
            json_format = self.default_config['json_format']
            max_log_size = self.default_config['max_log_size']
            log_retention = self.default_config['log_retention']
            performance_logging = self.default_config['performance_logging']
        
        # Crear directorio de logs
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Limpiar handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Filtros comunes
        filters = []
        if performance_logging:
            filters.append(PerformanceFilter())
        
        # Console handler
        if console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            
            if json_format:
                console_formatter = JSONFormatter()
            else:
                console_formatter = ColoredFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            console_handler.setFormatter(console_formatter)
            
            for filter_obj in filters:
                console_handler.addFilter(filter_obj)
            
            root_logger.addHandler(console_handler)
        
        # File handler
        if file_logging:
            log_file = logs_dir / "medstudy.log"
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_log_size * 1024 * 1024,  # MB a bytes
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            
            if json_format:
                file_formatter = JSONFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
                )
            
            file_handler.setFormatter(file_formatter)
            
            for filter_obj in filters:
                file_handler.addFilter(filter_obj)
            
            root_logger.addHandler(file_handler)
            
            # Error log separado
            error_log_file = logs_dir / "errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=max_log_size * 1024 * 1024,
                backupCount=3,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            
            for filter_obj in filters:
                error_handler.addFilter(filter_obj)
            
            root_logger.addHandler(error_handler)
        
        # Database handler
        if database_logging and self.config:
            db_path = self.config.get_app_directory() / "logs.db"
            db_handler = DatabaseLogHandler(db_path)
            db_handler.setLevel(logging.WARNING)  # Solo warnings y errores en DB
            
            for filter_obj in filters:
                db_handler.addFilter(filter_obj)
            
            root_logger.addHandler(db_handler)
        
        # Configurar loggers específicos
        self._configure_specific_loggers()
        
        # Limpiar logs antiguos
        self._cleanup_old_logs(logs_dir, log_retention)
        
        self._setup_done = True
        
        # Log inicial
        logger = logging.getLogger("LoggingManager")
        logger.info("Sistema de logging inicializado")
        logger.info(f"Nivel: {level}, Archivo: {file_logging}, Consola: {console_logging}")
    
    def _configure_specific_loggers(self):
        """Configura loggers específicos para diferentes módulos"""
        # Logger para requests (reducir verbosidad)
        requests_logger = logging.getLogger("requests")
        requests_logger.setLevel(logging.WARNING)
        
        # Logger para urllib3 (muy verboso)
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_logger.setLevel(logging.WARNING)
        
        # Logger para matplotlib (si se usa)
        matplotlib_logger = logging.getLogger("matplotlib")
        matplotlib_logger.setLevel(logging.WARNING)
        
        # Loggers de la aplicación con niveles específicos
        app_loggers = {
            "OllamaManager": logging.INFO,
            "LLMManager": logging.INFO,
            "DatabaseManager": logging.INFO,
            "ChatPage": logging.INFO,
            "AnkiSystem": logging.INFO,
            "RAGEngine": logging.INFO,
            "DocumentProcessor": logging.INFO
        }
        
        for logger_name, level in app_loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
    
    def _cleanup_old_logs(self, logs_dir: Path, retention_days: int):
        """Limpia logs antiguos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for log_file in logs_dir.glob("*.log*"):
                if log_file.is_file():
                    file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_date < cutoff_date:
                        log_file.unlink()
                        print(f"Log antiguo eliminado: {log_file}")
                        
        except Exception as e:
            print(f"Error limpiando logs antiguos: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Obtiene un logger con el nombre especificado"""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]
    
    def set_level(self, level: str, logger_name: str = None):
        """Cambia el nivel de logging dinámicamente"""
        log_level = getattr(logging, level.upper())
        
        if logger_name:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
        else:
            # Cambiar nivel root
            logging.getLogger().setLevel(log_level)
            
            # Actualizar todos los handlers
            for handler in logging.getLogger().handlers:
                handler.setLevel(log_level)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de los logs"""
        stats = {
            'loggers_count': len(self.loggers),
            'handlers_count': len(logging.getLogger().handlers),
            'current_level': logging.getLogger().level,
            'log_files': []
        }
        
        if self.config:
            logs_dir = self.config.get_logs_directory()
            
            for log_file in logs_dir.glob("*.log*"):
                if log_file.is_file():
                    stats['log_files'].append({
                        'name': log_file.name,
                        'size': log_file.stat().st_size,
                        'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                    })
        
        return stats
    
    def get_recent_logs(self, level: str = "ERROR", limit: int = 100) -> List[Dict]:
        """Obtiene logs recientes de la base de datos"""
        if not self.config:
            return []
        
        try:
            import sqlite3
            db_path = self.config.get_app_directory() / "logs.db"
            
            if not db_path.exists():
                return []
            
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if level:
                    cursor = conn.execute("""
                        SELECT * FROM application_logs 
                        WHERE level = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (level, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM application_logs 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error obteniendo logs: {e}")
            return []
    
    def export_logs(self, output_file: Path, start_date: datetime = None, 
                   end_date: datetime = None, level: str = None) -> bool:
        """Exporta logs a archivo"""
        try:
            if not self.config:
                return False
            
            import sqlite3
            db_path = self.config.get_app_directory() / "logs.db"
            
            if not db_path.exists():
                return False
            
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Construir query
                conditions = []
                params = []
                
                if start_date:
                    conditions.append("timestamp >= ?")
                    params.append(start_date.isoformat())
                
                if end_date:
                    conditions.append("timestamp <= ?")
                    params.append(end_date.isoformat())
                
                if level:
                    conditions.append("level = ?")
                    params.append(level)
                
                where_clause = " AND ".join(conditions)
                if where_clause:
                    where_clause = "WHERE " + where_clause
                
                query = f"""
                    SELECT * FROM application_logs 
                    {where_clause}
                    ORDER BY timestamp DESC
                """
                
                cursor = conn.execute(query, params)
                logs = [dict(row) for row in cursor.fetchall()]
            
            # Exportar como JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exportando logs: {e}")
            return False

class LogContext:
    """Context manager para logging con contexto adicional"""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_context = {}
    
    def __enter__(self):
        # Guardar contexto anterior
        for key, value in self.context.items():
            if hasattr(self.logger, key):
                self.old_context[key] = getattr(self.logger, key)
            setattr(self.logger, key, value)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restaurar contexto anterior
        for key in self.context.keys():
            if key in self.old_context:
                setattr(self.logger, key, self.old_context[key])
            else:
                delattr(self.logger, key)

@contextmanager
def log_performance(logger: logging.Logger, operation: str, level: int = logging.INFO):
    """Context manage
