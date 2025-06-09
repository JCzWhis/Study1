#!/usr/bin/env python3
"""
MedStudy Pro - Medical Study Assistant
Desktop Application for Evidence-Based Medical Learning

Author: Dr. Cruz Migueles
Specialty: Internal Medicine & Rheumatology
"""

import sys
import argparse
import logging
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Import our modules
try:
    from app.config import config
    from core.utils import run_system_diagnostic, SystemChecker
    from core.database import initialize_database
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    print("and all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

class MedStudyProLauncher:
    """Main launcher for MedStudy Pro application"""
    
    def __init__(self):
        self.config = config
        self.logger = self._setup_logging()
        self.system_checker = SystemChecker()
        
    def _setup_logging(self):
        """Setup application logging"""
        logger = logging.getLogger('MedStudy.Launcher')
        logger.info("MedStudy Pro launcher initialized")
        return logger
    
    def run_diagnostics(self) -> bool:
        """Run system diagnostics and return success status"""
        print("🔍 Running MedStudy Pro System Diagnostics...")
        print("=" * 60)
        
        diagnostic = run_system_diagnostic()
        
        # Check Python version
        python_info = diagnostic['python']
        if python_info['is_compatible']:
            print(f"✅ Python: {python_info['version']} (Compatible)")
        else:
            print(f"❌ Python: {python_info['version']} (Requires {python_info['required']})")
            return False
        
        # Check memory
        memory_info = diagnostic.get('memory', {})
        if memory_info.get('is_sufficient', False):
            print(f"✅ Memory: {memory_info['available_gb']:.1f}GB available")
        else:
            print(f"⚠️  Memory: {memory_info.get('available_gb', 'unknown')}GB (2GB+ recommended)")
        
        # Check disk space
        disk_info = diagnostic.get('disk', {})
        if disk_info.get('is_sufficient', False):
            print(f"✅ Disk Space: {disk_info['free_gb']:.1f}GB free")
        else:
            print(f"⚠️  Disk Space: {disk_info.get('free_gb', 'unknown')}GB (5GB+ recommended)")
        
        # Check Ollama
        ollama_info = diagnostic['ollama']
        if ollama_info['is_running']:
            print(f"✅ Ollama: Running at {ollama_info['host']}")
            
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
        deps_info = diagnostic['dependencies']
        missing_deps = [pkg for pkg, info in deps_info.items() if not info['installed']]
        
        if missing_deps:
            print(f"❌ Missing Dependencies: {', '.join(missing_deps)}")
            print(f"   Run: pip install -r requirements.txt")
            return False
        else:
            print(f"✅ Dependencies: All {len(deps_info)} packages installed")
        
        # Platform info
        platform_info = diagnostic['platform']
        print(f"ℹ️  Platform: {platform_info['system']} {platform_info['release']}")
        
        print("=" * 60)
        
        if all([
            python_info['is_compatible'],
            ollama_info['is_running'],
            diagnostic.get('ollama_model', {}).get('is_available', False),
            not missing_deps
        ]):
            print("🎉 All system checks passed! Ready to launch MedStudy Pro.")
            return True
        else:
            print("⚠️  Some issues detected. Please resolve them before launching.")
            return False
    
    def initialize_database(self):
        """Initialize database"""
        try:
            db_url = self.config.get_database_url()
            db_path = db_url.replace('sqlite:///', '')
            
            self.logger.info(f"Initializing database at {db_path}")
            db = initialize_database(db_path)
            
            # Test database connection
            db_info = db.get_database_info()
            self.logger.info(f"Database initialized: {db_info['table_count']} tables")
            
            return db
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def launch_desktop_app(self):
        """Launch desktop application"""
        try:
            print("🚀 Launching MedStudy Pro Desktop Application...")
            
            # Initialize database
            db = self.initialize_database()
            
            # Import and launch UI (will be implemented by Jules)
            try:
                from app.ui.main_window import MedStudyMainWindow
                
                # Create and run application
                app = MedStudyMainWindow(config=self.config, database=db)
                app.run()
                
            except ImportError:
                print("❌ Desktop UI not yet implemented")
                print("📋 Next steps:")
                print("   1. Implement app.ui.main_window.MedStudyMainWindow")
                print("   2. Create CustomTkinter interface")
                print("   3. Integrate with Jules-generated components")
                
                # For now, show configuration info
                self._show_config_info()
                
        except Exception as e:
            self.logger.error(f"Failed to launch application: {e}")
            print(f"❌ Launch failed: {e}")
            raise
    
    def _show_config_info(self):
        """Show current configuration information"""
        print("\n📋 Current Configuration:")
        print("-" * 40)
        
        # Ollama config
        ollama_config = self.config.get_ollama_config()
        print(f"🤖 AI Configuration:")
        print(f"   Host: {ollama_config['host']}")
        print(f"   Model: {ollama_config['model']}")
        print(f"   Timeout: {ollama_config['timeout']}s")
        
        # Window config
        window_config = self.config.get_window_config()
        print(f"🖥️  Window Configuration:")
        print(f"   Size: {window_config['width']}x{window_config['height']}")
        print(f"   Title: {window_config['title']}")
        
        # Study config
        study_config = self.config.get_study_config()
        print(f"📚 Study Configuration:")
        print(f"   Session Duration: {study_config['session_duration']} minutes")
        print(f"   Active Recall: Every {study_config['active_recall_interval']} minutes")
        print(f"   Quiz Questions: {study_config['quiz_questions']} per session")
        print(f"   Exam Questions: {study_config['exam_questions']} per exam")
        
        # Database info
        db_url = self.config.get_database_url()
        print(f"💾 Database: {db_url}")
        
        print("-" * 40)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MedStudy Pro - Medical Study Assistant with Local AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Launch application
  python main.py --diagnostic       # Run system diagnostics
  python main.py --config-info      # Show configuration
  python main.py --help             # Show this help

For more information, visit: https://github.com/your-repo/Study1
        """
    )
    
    parser.add_argument(
        '--diagnostic',
        action='store_true',
        help='Run system diagnostics and exit'
    )
    
    parser.add_argument(
        '--config-info',
        action='store_true',
        help='Show configuration information and exit'
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
    print(f"   By Dr. Cruz Migueles - Internal Medicine & Rheumatology")
    print()
    
    try:
        launcher = MedStudyProLauncher()
        
        # Set debug mode if requested
        if args.debug:
            # Logging level is now handled by AppConfig
            launcher.logger.debug("Debug mode enabled by CLI arg --debug")
        
        # Handle different modes
        if args.diagnostic:
            success = launcher.run_diagnostics()
            sys.exit(0 if success else 1)
        
        elif args.config_info:
            launcher._show_config_info()
            sys.exit(0)
        
        else:
            # Normal launch mode
            if not args.force_launch:
                # Run diagnostics first
                if not launcher.run_diagnostics():
                    print("\n❌ System diagnostics failed.")
                    print("   Use --force-launch to skip diagnostics")
                    print("   Use --diagnostic for detailed information")
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
        sys.exit(1)

if __name__ == "__main__":
    main()