"""
MedStudy Pro - Medical Study Application
Desktop application for evidence-based medical learning

This package contains the main application logic, UI components,
and configuration management for MedStudy Pro.
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

# Import main configuration
from .config import config

__all__ = ['config', 'APP_NAME', 'APP_VERSION', 'APP_AUTHOR', 'APP_DESCRIPTION']