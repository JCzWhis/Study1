"""
MedStudy Pro - Main Application Package
Desktop application for evidence-based medical learning with local AI
"""

__version__ = "1.0.0-beta"
__author__ = "Dr. Cruz Migueles"
__email__ = "your-email@example.com"
__description__ = "Medical Study Assistant with Local AI"

# Application metadata
APP_NAME = "MedStudy Pro"
APP_VERSION = __version__
APP_AUTHOR = __author__
APP_DESCRIPTION = __description__

# Import main configuration with error handling
try:
    from .config import config
    CONFIG_AVAILABLE = True
    print("✅ App configuration loaded successfully")
except ImportError as e:
    print(f"⚠️ App configuration not available: {e}")
    config = None
    CONFIG_AVAILABLE = False

__all__ = ['APP_NAME', 'APP_VERSION', 'APP_AUTHOR', 'APP_DESCRIPTION']

if CONFIG_AVAILABLE:
    __all__.append('config')
