"""
MedStudy Pro - Configuration Management
Centralized configuration for the medical study application
"""

import os
import sys
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ColorScheme:
    """Medical-themed color palette for the application"""
    # Primary colors
    PRIMARY_BLUE = "#1E3A8A"      # Professional medical blue
    SUCCESS_GREEN = "#10B981"     # Medical success/progress
    ACCENT_TURQUOISE = "#06B6D4"  # Info and accents
    
    # Background colors
    BACKGROUND_CREAM = "#FEFCF9"  # Study mode background (concentration)
    BACKGROUND_WHITE = "#FFFFFF"  # Clean white
    BACKGROUND_LIGHT = "#F8FAFC"  # Light gray
    
    # Text colors
    TEXT_DARK = "#1F2937"         # Primary text
    TEXT_MEDIUM = "#4B5563"       # Secondary text
    TEXT_LIGHT = "#9CA3AF"        # Placeholder text
    
    # Status colors
    ERROR_RED = "#EF4444"         # Error states
    WARNING_AMBER = "#F59E0B"     # Warning states
    INFO_BLUE = "#3B82F6"         # Information
    
    # UI Elements
    BORDER_LIGHT = "#E5E7EB"      # Light borders
    BORDER_MEDIUM = "#D1D5DB"     # Medium borders
    HOVER_BLUE = "#DBEAFE"        # Hover states

@dataclass
class StudySettings:
    """Default study session settings"""
    DEFAULT_SESSION_DURATION = 45      # minutes
    DEFAULT_BREAK_DURATION = 15        # minutes
    ACTIVE_RECALL_INTERVAL = 10        # minutes
    POMODORO_STUDY = 25                # minutes
    POMODORO_BREAK = 5                 # minutes
    QUIZ_QUESTIONS_PER_SESSION = 10    # questions
    EXAM_QUESTIONS_TOTAL = 45          # questions

@dataclass
class SRSSettings:
    """Spaced Repetition System settings"""
    INITIAL_INTERVAL = 1               # days
    SUCCESS_MULTIPLIER = 2.5           # multiply interval on success
    FAILURE_MULTIPLIER = 0.6           # multiply interval on failure
    MAX_INTERVAL = 365                 # days
    GRADUATION_INTERVAL = 4            # days to graduate from learning
    EASE_FACTOR_DEFAULT = 2.5          # default ease factor

class AppConfig:
    """Central configuration manager for MedStudy Pro"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.ini"
        self.config_template = "config_template.ini"
        
        # Initialize paths
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / "data"
        self.logs_dir = self.app_dir / "logs"
        
        # Create necessary directories
        self._create_directories()
        
        # Load configuration
        self.config = configparser.ConfigParser()
        self._load_config()
        
        # Initialize theme and settings
        self.colors = ColorScheme()
        self.study = StudySettings()
        self.srs = SRSSettings()
        
        # Setup logging
        self._setup_logging()
    
    def _create_directories(self):
        """Create necessary application directories"""
        directories = [
            self.data_dir,
            self.data_dir / "documents",
            self.data_dir / "images",
            self.data_dir / "embeddings",
            self.data_dir / "user_progress",
            self.data_dir / "backups",
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load configuration from file or create from template"""
        config_path = Path(self.config_file)
        template_path = Path(self.config_template)
        
        if not config_path.exists():
            if template_path.exists():
                # Copy template to config
                import shutil
                shutil.copy2(template_path, config_path)
                logging.info(f"Created config.ini from template")
            else:
                # Create default config
                self._create_default_config(config_path)
                logging.info(f"Created default config.ini")
        
        self.config.read(config_path)
        logging.info(f"Configuration loaded from {config_path}")
    
    def _create_default_config(self, config_path: Path):
        """Create default configuration file"""
        default_config = """[Ollama]
host = http://localhost:11434
model = phi3:mini
timeout = 60

[App]
default_interface = desktop
window_width = 1400
window_height = 900
theme = medical
debug_mode = False

[Paths]
database_file = data/medstudy.db
documents_path = data/documents/
images_path = data/images/
log_file = logs/app.log

[Study]
session_duration = 45
break_duration = 15
active_recall_interval = 10
quiz_questions = 10
exam_questions = 45

[SRS]
initial_interval = 1
success_multiplier = 2.5
failure_multiplier = 0.6
max_interval = 365

[UI]
font_family = Segoe UI
font_size = 12
animation_speed = 200
auto_save_interval = 30
"""
        with open(config_path, 'w') as f:
            f.write(default_config)
    
    def _setup_logging(self):
        """Setup application logging"""
        log_level = self.get('App', 'debug_mode', fallback=False)
        level = logging.DEBUG if log_level else logging.INFO
        
        log_file = self.logs_dir / "medstudy.log"
        
        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Create logger for this module
        self.logger = logging.getLogger('MedStudy.Config')
        self.logger.info("Logging system initialized")
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value with fallback"""
        try:
            value = self.config.get(section, key)
            
            # Try to convert boolean strings
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            
            # Try to convert numbers
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except ValueError:
                return value
                
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
        
        # Save to file
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_database_url(self) -> str:
        """Get SQLite database URL"""
        db_file = self.get('Paths', 'database_file', 'data/medstudy.db')
        db_path = self.app_dir / db_file
        return f"sqlite:///{db_path}"
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration"""
        return {
            'host': self.get('Ollama', 'host', 'http://localhost:11434'),
            'model': self.get('Ollama', 'model', 'phi3:mini'),
            'timeout': self.get('Ollama', 'timeout', 60)
        }
    
    def get_window_config(self) -> Dict[str, Any]:
        """Get window configuration"""
        return {
            'width': self.get('App', 'window_width', 1400),
            'height': self.get('App', 'window_height', 900),
            'title': 'MedStudy Pro',
            'resizable': True
        }
    
    def get_study_config(self) -> Dict[str, Any]:
        """Get study session configuration"""
        return {
            'session_duration': self.get('Study', 'session_duration', 45),
            'break_duration': self.get('Study', 'break_duration', 15),
            'active_recall_interval': self.get('Study', 'active_recall_interval', 10),
            'quiz_questions': self.get('Study', 'quiz_questions', 10),
            'exam_questions': self.get('Study', 'exam_questions', 45)
        }

# Global configuration instance
config = AppConfig()

# Export commonly used items
__all__ = [
    'config',
    'ColorScheme', 
    'StudySettings', 
    'SRSSettings',
    'AppConfig'
]