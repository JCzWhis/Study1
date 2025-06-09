#!/usr/bin/env python3
"""
MedStudy Pro - Medical Study Assistant
Desktop Application for Evidence-Based Medical Learning

Author: Dr. Cruz Migueles
Specialty: Internal Medicine & Rheumatology
Version: 1.0-beta (Enhanced)
"""

import sys
import argparse
import logging
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Import our modules with error handling
def safe_import():
    """Import modules with proper error handling"""
    try:
        from app.config import config
        from core.utils import run_system_diagnostic, SystemChecker
        from core.database import initialize_database
        return config, run_system_diagnostic, SystemChecker, initialize_database
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running from the project root directory")
        print("and all dependencies are installed:")
        print("  1. Run: python setup.py")
        print("  2. Or: pip install -r requirements.txt")
        return None, None, None, None

class MedStudyProLauncher:
    """Main launcher for MedStudy Pro application - Enhanced Version"""
    
    def __init__(self):
        # Try to import safely
        modules = safe_import()
        if not any(modules):
            sys.exit(1)
        
        self.config, self.run_diagnostic, self.SystemChecker, self.initialize_database = modules
        self.logger = self._setup_logging()
        self.system_checker = self.SystemChecker() if self.SystemChecker else None
        
    def _setup_logging(self):
        """Setup application logging"""
        try:
            logger = logging.getLogger('MedStudy.Launcher')
            logger.info("MedStudy Pro launcher initialized")
            return logger
        except Exception as e:
            print(f"Warning: Logging setup failed: {e}")
            return None
    
    def run_diagnostics(self) -> bool:
        """Run system diagnostics and return success status"""
        print("🔍 Running MedStudy Pro System Diagnostics...")
        print("=" * 60)
        
        if not self.run_diagnostic:
            print("❌ Diagnostic module not available")
            return False
        
        try:
            diagnostic = self.run_diagnostic()
        except Exception as e:
            print(f"❌ Diagnostic failed: {e}")
            return False
        
        # Check Python version
        python_info = diagnostic.get('python', {})
        if python_info.get('is_compatible', False):
            print(f"✅ Python: {python_info.get('version', 'unknown')} (Compatible)")
        else:
            print(f"❌ Python: {python_info.get('version', 'unknown')} (Requires {python_info.get('required', '3.11+')})")
            return False
        
        # Check memory
        memory_info = diagnostic.get('memory', {})
        if memory_info.get('is_sufficient', False):
            print(f"✅ Memory: {memory_info.get('available_gb', 'unknown')}GB available")
        else:
            print(f"⚠️  Memory: {memory_info.get('available_gb', 'unknown')}GB (2GB+ recommended)")
        
        # Check disk space
        disk_info = diagnostic.get('disk', {})
        if disk_info.get('is_sufficient', False):
            print(f"✅ Disk Space: {disk_info.get('free_gb', 'unknown')}GB free")
        else:
            print(f"⚠️  Disk Space: {disk_info.get('free_gb', 'unknown')}GB (5GB+ recommended)")
        
        # Check Ollama
        ollama_info = diagnostic.get('ollama', {})
        if ollama_info.get('is_running', False):
            print(f"✅ Ollama: Running at {ollama_info.get('host', 'unknown')}")
            
            # Check model if Ollama is running
            model_info = diagnostic.get('ollama_model', {})
            if model_info.get('is_available', False):
                print(f"✅ AI Model: phi3:mini available")
            else:
                print(f"❌ AI Model: phi3:mini not found")
                print(f"   Run: ollama pull phi3:mini")
                return False
        else:
            print(f"❌ Ollama: Not running ({ollama_info.get('error', 'Unknown error')})")
            print(f"   1. Install Ollama from https://ollama.ai")
            print(f"   2. Run: ollama serve")
            print(f"   3. Run: ollama pull phi3:mini")
            return False
        
        # Check dependencies
        deps_info = diagnostic.get('dependencies', {})
        missing_deps = [pkg for pkg, info in deps_info.items() if not info.get('installed', False)]
        
        if missing_deps:
            print(f"❌ Missing Dependencies: {', '.join(missing_deps)}")
            print(f"   Run: pip install -r requirements.txt")
            return False
        else:
            print(f"✅ Dependencies: All {len(deps_info)} packages installed")
        
        # Platform info
        platform_info = diagnostic.get('platform', {})
        print(f"ℹ️  Platform: {platform_info.get('system', 'unknown')} {platform_info.get('release', '')}")
        
        print("=" * 60)
        
        # Overall assessment
        critical_checks = [
            python_info.get('is_compatible', False),
            ollama_info.get('is_running', False),
            diagnostic.get('ollama_model', {}).get('is_available', False),
            len(missing_deps) == 0
        ]
        
        if all(critical_checks):
            print("🎉 All critical system checks passed! Ready to launch MedStudy Pro.")
            return True
        else:
            print("⚠️  Some critical issues detected. Please resolve them before launching.")
            return False
    
    def initialize_database(self):
        """Initialize database"""
        try:
            if not self.config:
                raise RuntimeError("Configuration not available")
            
            db_url = self.config.get_database_url()
            db_path = db_url.replace('sqlite:///', '')
            
            if self.logger:
                self.logger.info(f"Initializing database at {db_path}")
            else:
                print(f"📄 Initializing database: {db_path}")
            
            db = self.initialize_database(db_path)
            
            # Test database connection
            db_info = db.get_database_info()
            
            if self.logger:
                self.logger.info(f"Database initialized: {db_info.get('table_count', 0)} tables")
            else:
                print(f"✅ Database ready: {db_info.get('table_count', 0)} tables")
            
            return db
            
        except Exception as e:
            error_msg = f"Database initialization failed: {e}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(f"❌ {error_msg}")
            raise
    
    def launch_desktop_app(self):
        """Launch desktop application"""
        try:
            print("🚀 Launching MedStudy Pro Desktop Application...")
            
            # Initialize database
            db = self.initialize_database()
            
            # Import and launch UI
            try:
                from app.ui.main_window import MedStudyMainWindow
                
                print("🖥️  Starting GUI...")
                
                # Create and run application
                app = MedStudyMainWindow(config=self.config, database=db)
                app.run()
                
            except ImportError as e:
                print(f"❌ UI Import Error: {e}")
                print("📋 Fallback options:")
                print("   1. Check if all UI files are present")
                print("   2. Try: python gradio_launcher.py (for web interface)")
                print("   3. Run: python setup.py (to reinstall)")
                
                # Show configuration info as fallback
                self._show_config_info()
                
        except Exception as e:
            error_msg = f"Failed to launch application: {e}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(f"❌ {error_msg}")
            raise
    
    def launch_gradio_interface(self):
        """Launch Gradio web interface as alternative"""
        try:
            print("🌐 Launching Gradio Web Interface...")
            
            # Try to import and launch Gradio interface
            try:
                import gradio_launcher
                gradio_launcher.main()
            except ImportError:
                print("❌ Gradio interface not available")
                print("   Install with: pip install gradio")
            except Exception as e:
                print(f"❌ Gradio launch failed: {e}")
                
        except Exception as e:
            print(f"❌ Web interface error: {e}")
    
    def _show_config_info(self):
        """Show current configuration information"""
        if not self.config:
            print("❌ Configuration not available")
            return
        
        print("\n📋 Current Configuration:")
        print("-" * 40)
        
        try:
            # Ollama config
            ollama_config = self.config.get_ollama_config()
            print(f"🤖 AI Configuration:")
            print(f"   Host: {ollama_config.get('host', 'unknown')}")
            print(f"   Model: {ollama_config.get('model', 'unknown')}")
            print(f"   Timeout: {ollama_config.get('timeout', 'unknown')}s")
            
            # Window config
            window_config = self.config.get_window_config()
            print(f"🖥️  Window Configuration:")
            print(f"   Size: {window_config.get('width', 'unknown')}x{window_config.get('height', 'unknown')}")
            print(f"   Title: {window_config.get('title', 'unknown')}")
            
            # Study config
            study_config = self.config.get_study_config()
            print(f"📚 Study Configuration:")
            print(f"   Session Duration: {study_config.get('session_duration', 'unknown')} minutes")
            print(f"   Active Recall: Every {study_config.get('active_recall_interval', 'unknown')} minutes")
            print(f"   Quiz Questions: {study_config.get('quiz_questions', 'unknown')} per session")
            
            # Database info
            db_url = self.config.get_database_url()
            print(f"💾 Database: {db_url}")
            
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
        
        print("-" * 40)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MedStudy Pro - Medical Study Assistant with Local AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Launch desktop application
  python main.py --diagnostic       # Run system diagnostics
  python main.py --web              # Launch web interface (Gradio)
  python main.py --config-info      # Show configuration
  python main.py --setup            # Run setup wizard

For more information and documentation:
  https://github.com/your-repo/Study1
        """
    )
    
    parser.add_argument(
        '--diagnostic',
        action='store_true',
        help='Run system diagnostics and exit'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Launch web interface instead of desktop'
    )
    
    parser.add_argument(
        '--config-info',
        action='store_true',
        help='Show configuration information and exit'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run setup wizard'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--force-launch',
        action='store_true',
        help='Force launch even if diagnostics fail (use with caution)'
    )
    
    args = parser.parse_args()
    
    # Header
    print("🧠 MedStudy Pro - Medical Study Assistant")
    print("   Evidence-Based Learning with Local AI")
    print("   By Dr. Cruz Migueles - Internal Medicine & Rheumatology")
    print()
    
    # Handle setup mode
    if args.setup:
        try:
            import setup
            setup.main()
            sys.exit(0)
        except ImportError:
            print("❌ Setup script not found")
            print("   Download setup.py or run: python -c 'import setup; setup.main()'")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)
    
    try:
        launcher = MedStudyProLauncher()
        
        # Set debug mode if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            if launcher.logger:
                launcher.logger.debug("Debug mode enabled")
            else:
                print("🔧 Debug mode enabled")
        
        # Handle different modes
        if args.diagnostic:
            success = launcher.run_diagnostics()
            sys.exit(0 if success else 1)
        
        elif args.config_info:
            launcher._show_config_info()
            sys.exit(0)
        
        elif args.web:
            launcher.launch_gradio_interface()
            sys.exit(0)
        
        else:
            # Normal desktop launch mode
            if not args.force_launch:
                # Run diagnostics first
                print("🔍 Running pre-launch diagnostics...\n")
                if not launcher.run_diagnostics():
                    print("\n❌ System diagnostics failed.")
                    print("   Options:")
                    print("   • Use --force-launch to skip diagnostics")
                    print("   • Use --diagnostic for detailed information")
                    print("   • Use --setup to run setup wizard")
                    print("   • Use --web for web interface")
                    sys.exit(1)
                print()  # Add spacing before launch
            
            # Launch application
            launcher.launch_desktop_app()
    
    except KeyboardInterrupt:
        print("\n👋 MedStudy Pro shutdown requested by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        
        print("\n🛠️  Troubleshooting:")
        print("   1. Run: python main.py --setup")
        print("   2. Check: python main.py --diagnostic")
        print("   3. Try web interface: python main.py --web")
        print("   4. Or: python gradio_launcher.py")
        
        sys.exit(1)

if __name__ == "__main__":
    main()