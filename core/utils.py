"""
MedStudy Pro - System Utilities
Common utilities and helper functions
"""

import os
import sys
import time
import json
import hashlib
import logging
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests

@dataclass
class SystemInfo:
    """System information dataclass"""
    platform: str
    python_version: str
    memory_gb: float
    disk_space_gb: float
    cpu_count: int
    
class SystemChecker:
    """System requirements and health checker"""
    
    def __init__(self):
        self.logger = logging.getLogger('MedStudy.SystemChecker')
    
    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version compatibility"""
        version = sys.version_info
        is_compatible = version >= (3, 11)
        
        return {
            'version': f"{version.major}.{version.minor}.{version.micro}",
            'is_compatible': is_compatible,
            'required': '3.11+',
            'details': sys.version
        }
    
    def check_memory(self) -> Dict[str, Any]:
        """Check available memory"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                'total_gb': round(memory.total / 1024**3, 2),
                'available_gb': round(memory.available / 1024**3, 2),
                'percent_used': memory.percent,
                'is_sufficient': memory.available > 2 * 1024**3  # 2GB minimum
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    def check_disk_space(self, path: str = ".") -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            
            return {
                'total_gb': round(total / 1024**3, 2),
                'used_gb': round(used / 1024**3, 2),
                'free_gb': round(free / 1024**3, 2),
                'is_sufficient': free > 5 * 1024**3  # 5GB minimum
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_ollama_connection(self, host: str = "http://localhost:11434") -> Dict[str, Any]:
        """Check Ollama service availability"""
        try:
            response = requests.get(host, timeout=5)
            is_running = response.status_code == 200
            
            result = {
                'host': host,
                'is_running': is_running,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
            if is_running:
                result['message'] = response.text.strip()
            
            return result
            
        except requests.exceptions.ConnectionError:
            return {
                'host': host,
                'is_running': False,
                'error': 'Connection refused - Ollama not running'
            }
        except requests.exceptions.Timeout:
            return {
                'host': host,
                'is_running': False,
                'error': 'Connection timeout'
            }
        except Exception as e:
            return {
                'host': host,
                'is_running': False,
                'error': str(e)
            }
    
    def check_ollama_model(self, model: str = "phi3:mini", 
                          host: str = "http://localhost:11434") -> Dict[str, Any]:
        """Check if Ollama model is available"""
        try:
            response = requests.post(
                f"{host}/api/show",
                json={"name": model},
                timeout=30
            )
            
            if response.status_code == 200:
                model_info = response.json()
                return {
                    'model': model,
                    'is_available': True,
                    'size': model_info.get('size', 'unknown'),
                    'details': model_info
                }
            else:
                return {
                    'model': model,
                    'is_available': False,
                    'error': f"HTTP {response.status_code}",
                    'suggestion': f"Run: ollama pull {model}"
                }
                
        except Exception as e:
            return {
                'model': model,
                'is_available': False,
                'error': str(e)
            }
    
    def check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check required Python dependencies"""
        required_packages = {
            'customtkinter': '5.2.0',
            'requests': '2.31.0',
            'PIL': '10.0.0',              # Nombre de import correcto
            'sentence-transformers': '2.2.2',
            'fitz': '1.23.0',             # Nombre de import correcto para PyMuPDF
            'chromadb': '0.4.15'
        }
        
        results = {}
        
        for package, min_version in required_packages.items():
            try:
                module = __import__(package.replace('-', '_'))
                version = getattr(module, '__version__', 'unknown')
                
                results[package] = {
                    'installed': True,
                    'version': version,
                    'required': min_version
                }
                
            except ImportError:
                results[package] = {
                    'installed': False,
                    'version': None,
                    'required': min_version,
                    'install_command': f"pip install {package}>={min_version}"
                }
        
        return results
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete system diagnostic"""
        self.logger.info("Running full system diagnostic...")
        
        diagnostic = {
            'timestamp': datetime.now().isoformat(),
            'python': self.check_python_version(),
            'memory': self.check_memory(),
            'disk': self.check_disk_space(),
            'ollama': self.check_ollama_connection(),
            'dependencies': self.check_dependencies(),
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
        }
        
        # Check Ollama model if Ollama is running
        if diagnostic['ollama'].get('is_running'):
            diagnostic['ollama_model'] = self.check_ollama_model()
        
        return diagnostic

class FileUtils:
    """File and path utilities"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if necessary"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path]) -> str:
        """Get SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Create safe filename by removing/replacing invalid characters"""
        import re
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Trim and ensure not empty
        filename = filename.strip('_')
        return filename or 'unnamed'
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Get file size in bytes"""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

class TimeUtils:
    """Time and date utilities"""
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes}m"
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours}h"
            return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def time_until_next_review(last_review: datetime, interval_days: int) -> timedelta:
        """Calculate time until next review"""
        next_review = last_review + timedelta(days=interval_days)
        return next_review - datetime.now()
    
    @staticmethod
    def is_study_time(current_time: datetime = None) -> bool:
        """Check if current time is good for studying (6 AM - 11 PM)"""
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        return 6 <= hour <= 23
    
    @staticmethod
    def get_study_session_end_time(duration_minutes: int) -> datetime:
        """Calculate when study session will end"""
        return datetime.now() + timedelta(minutes=duration_minutes)

class DataUtils:
    """Data processing and validation utilities"""
    
    @staticmethod
    def sanitize_medical_text(text: str) -> str:
        """Sanitize medical text for processing"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Preserve medical abbreviations (don't split on periods)
        # Common medical abbreviations
        medical_abbrevs = [
            'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'vs.', 'etc.', 'i.e.', 'e.g.',
            'mg.', 'ml.', 'kg.', 'cm.', 'mm.', 'mcg.', 'IV.', 'IM.', 'PO.',
            'BID.', 'TID.', 'QID.', 'PRN.', 'STAT.', 'NPO.', 'DNR.'
        ]
        
        # Protect abbreviations temporarily
        for abbrev in medical_abbrevs:
            text = text.replace(abbrev, abbrev.replace('.', '<!DOT!>'))
        
        # Clean up and restore
        text = text.replace('<!DOT!>', '.')
        
        return text
    
    @staticmethod
    def extract_medical_entities(text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text (basic version)"""
        import re
        
        entities = {
            'medications': [],
            'symptoms': [],
            'conditions': [],
            'procedures': []
        }
        
        # Basic medication patterns
        med_patterns = [
            r'\b\w+cillin\b',  # Antibiotics ending in cillin
            r'\b\w+azole\b',   # Antifungals ending in azole
            r'\b\w+pril\b',    # ACE inhibitors ending in pril
            r'\b\w+sartan\b',  # ARBs ending in sartan
            r'\b\w+statin\b'   # Statins ending in statin
        ]
        
        for pattern in med_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['medications'].extend(matches)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    @staticmethod
    def calculate_reading_time(text: str, wpm: int = 200) -> int:
        """Calculate reading time in minutes"""
        word_count = len(text.split())
        return max(1, round(word_count / wpm))
    
    @staticmethod
    def chunk_text_for_study(text: str, max_chunk_size: int = 1000) -> List[str]:
        """Chunk text into study-friendly segments"""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Try to split on sentences first
        import re
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence exceeds limit
            if len(current_chunk) + len(sentence) + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += (" " if current_chunk else "") + sentence
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class PerformanceUtils:
    """Performance monitoring and optimization utilities"""
    
    @staticmethod
    def measure_time(func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            logger = logging.getLogger('MedStudy.Performance')
            logger.debug(f"{func.__name__} took {end_time - start_time:.3f} seconds")
            
            return result
        return wrapper
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    @staticmethod
    def optimize_for_study_session():
        """Optimize system for study session"""
        # Disable automatic garbage collection during study
        import gc
        gc.disable()
        
        # Set higher thread priority if possible
        try:
            import psutil
            process = psutil.Process(os.getpid())
            if platform.system() == "Windows":
                process.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                process.nice(-5)  # Higher priority on Unix systems
        except:
            pass  # Ignore if can't set priority
    
    @staticmethod
    def cleanup_after_session():
        """Cleanup after study session"""
        import gc
        gc.enable()
        gc.collect()

class MedicalUtils:
    """Medical education specific utilities"""
    
    @staticmethod
    def validate_medical_specialty(specialty: str) -> bool:
        """Validate medical specialty name"""
        valid_specialties = {
            'internal_medicine', 'cardiology', 'rheumatology', 'neurology',
            'endocrinology', 'gastroenterology', 'pulmonology', 'nephrology',
            'hematology', 'oncology', 'infectious_disease', 'emergency_medicine',
            'family_medicine', 'pediatrics', 'surgery', 'orthopedics',
            'dermatology', 'ophthalmology', 'psychiatry', 'radiology',
            'pathology', 'anesthesiology', 'obstetrics_gynecology'
        }
        
        return specialty.lower().replace(' ', '_') in valid_specialties
    
    @staticmethod
    def get_study_difficulty(topic: str, user_level: str = 'resident') -> str:
        """Estimate study difficulty for medical topic"""
        # Advanced topics typically more difficult
        advanced_keywords = [
            'pathophysiology', 'mechanism', 'molecular', 'genetic',
            'biochemistry', 'pharmacokinetics', 'immunology'
        ]
        
        basic_keywords = [
            'symptoms', 'signs', 'diagnosis', 'treatment', 'management'
        ]
        
        topic_lower = topic.lower()
        
        advanced_count = sum(1 for keyword in advanced_keywords if keyword in topic_lower)
        basic_count = sum(1 for keyword in basic_keywords if keyword in topic_lower)
        
        if advanced_count > basic_count:
            return 'advanced'
        elif basic_count > 0:
            return 'intermediate'
        else:
            return 'basic'
    
    @staticmethod
    def generate_case_study_template() -> Dict[str, str]:
        """Generate template for medical case studies"""
        return {
            'chief_complaint': '',
            'history_present_illness': '',
            'past_medical_history': '',
            'medications': '',
            'allergies': '',
            'family_history': '',
            'social_history': '',
            'physical_examination': '',
            'laboratory_findings': '',
            'imaging': '',
            'assessment': '',
            'plan': '',
            'learning_objectives': ''
        }

# Diagnostic function for system health
def run_system_diagnostic() -> Dict[str, Any]:
    """Run comprehensive system diagnostic"""
    checker = SystemChecker()
    return checker.run_full_diagnostic()

# Export utilities
__all__ = [
    'SystemChecker', 'FileUtils', 'TimeUtils', 'DataUtils', 
    'PerformanceUtils', 'MedicalUtils', 'SystemInfo',
    'run_system_diagnostic'
]