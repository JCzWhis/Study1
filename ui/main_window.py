"""
MedStudy Pro - Main Window with Functional Planner
Ventana principal actualizada con planificador funcional
"""

import customtkinter as ctk
import logging
import sys
from pathlib import Path

# --- IMPORTACIONES SEGURAS ---
def safe_import_config():
    """Importa configuración de manera segura"""
    try:
        from app.config import config
        return config
    except ImportError:
        # Fallback config
        class FallbackConfig:
            def __init__(self):
                self.colors = self._create_colors()
            
            def _create_colors(self):
                class Colors:
                    PRIMARY_BLUE = "#1E3A8A"
                    SUCCESS_GREEN = "#10B981"
                    ACCENT_TURQUOISE = "#06B6D4"
                    BACKGROUND_CREAM = "#FEFCF9"
                    TEXT_DARK = "#1F2937"
                    TEXT_MEDIUM = "#4B5563"
                    WARNING_AMBER = "#F59E0B"
                    BORDER_LIGHT = "#E5E7EB"
                return Colors()
            
            def get(self, section, key, default=None):
                defaults = {
                    ('Ollama', 'model'): 'phi3:mini',
                    ('App', 'window_width'): 1400,
                    ('App', 'window_height'): 900
                }
                return defaults.get((section, key), default)
            
            def get_database_url(self):
                return "sqlite:///data/medstudy.db"
        
        return FallbackConfig()

def safe_import_database():
    """Importa database manager de manera segura"""
    try:
        from core.database import DatabaseManager
        return DatabaseManager
    except ImportError:
        return None

def safe_import_pages():
    """Importa páginas de manera segura"""
    pages = {}
    
    # Try to import study planner page
    try:
        from ui.pages.study_planner_page import StudyPlannerPage
        pages['planner'] = StudyPlannerPage
    except ImportError:
        pages['planner'] = None
    
    # Try to import other pages
    try:
        from app.ui.components.chat_tutor_manager import ChatTutorPanel
        pages['chat'] = ChatTutorPanel
    except ImportError:
        pages['chat'] = None
    
    return pages

# --- VENTANA PRINCIPAL ---
class MedStudyMainWindow(ctk.CTk):
    """Ventana principal de MedStudy Pro con planificador funcional"""

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        
        # Configuración
        self.config = config or safe_import_config()
        self.logger = logging.getLogger('MedStudy.MainWindow')
        
        # Database
        DatabaseManager = safe_import_database()
        self.db_manager = None
        if DatabaseManager:
            try:
                db_path = self.config.get_database_url().replace('sqlite:///', '')
                self.db_manager = DatabaseManager(db_path)
                self.logger.info("Database initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize database: {e}")
        
        # Import pages
        self.available_pages = safe_import_pages()
        
        # Colors
        self.colors = self.config.colors
        
        # Setup window
        self._setup_window()
        
        # Create interface
        self._create_interface()
        
        self.logger.info("MedStudy Pro main window initialized with functional components")

    def _setup_window(self):
        """Configura las propiedades principales de la ventana"""
        try:
            # Configuración básica
            self.title("🧠 MedStudy Pro - Medical Study Assistant")
            
            # Tamaño desde config o fallback
            width = getattr(self.config, 'get', lambda s,k,d: d)('App', 'window_width', 1400)
            height = getattr(self.config, 'get', lambda s,k,d: d)('App', 'window_height', 900)
            self.geometry(f"{width}x{height}")
            
            # Colores y tema
            self.configure(fg_color=self.colors.BACKGROUND_CREAM)
            self.minsize(1100, 750)
            
            # Configurar CustomTkinter
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
            
        except Exception as e:
            self.logger.error(f"Error configurando ventana: {e}")

    def _create_interface(self):
        """Crea la estructura de la interfaz principal"""
        try:
            self._create_header()
            self._create_main_content_area()
            self._create_status_bar()
        except Exception as e:
            self.logger.error(f"Error creando interfaz: {e}")

    def _create_header(self):
        """Crea el header de la aplicación"""
        try:
            header_frame = ctk.CTkFrame(
                self, 
                fg_color=self.colors.PRIMARY_BLUE, 
                height=70, 
                corner_radius=0
            )
            header_frame.pack(fill="x", side="top")
            header_frame.pack_propagate(False)
            
            # Contenedor del título
            title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_container.pack(side="left", padx=25, pady=15)
            
            # Título principal
            title_label = ctk.CTkLabel(
                title_container,
                text="🧠 MedStudy Pro",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#FFFFFF"
            )
            title_label.pack(anchor="w")
            
            # Subtítulo
            subtitle_label = ctk.CTkLabel(
                title_container,
                text="Sistema de Estudio Médico Inteligente",
                font=ctk.CTkFont(size=12),
                text_color="#DBEAFE"
            )
            subtitle_label.pack(anchor="w")
            
        except Exception as e:
            self.logger.error(f"Error creando header: {e}")

    def _create_main_content_area(self):
        """Crea el área principal con pestañas"""
        try:
            # TabView principal
            self.tab_view = ctk.CTkTabview(
                self, 
                corner_radius=10, 
                border_width=1, 
                border_color=self.colors.BORDER_LIGHT
            )
            self.tab_view.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Configurar colores
            self.tab_view.configure(
                fg_color=self.colors.BACKGROUND_CREAM,
                segmented_button_fg_color=self.colors.BACKGROUND_CREAM,
                segmented_button_selected_color=self.colors.PRIMARY_BLUE,
                segmented_button_unselected_color="#FFFFFF",
                segmented_button_selected_hover_color=self.colors.ACCENT_TURQUOISE,
                segmented_button_unselected_hover_color="#F0F9FF"
            )
            
            # Crear pestañas
            tabs = [
                ("📊 Dashboard", self._setup_dashboard_tab),
                ("📋 Planificador", self._setup_planner_tab),
                ("📖 Sesiones", self._setup_sessions_tab),
                ("💬 Chat IA", self._setup_chat_tab),
                ("📈 Progreso", self._setup_progress_tab)
            ]
            
            for tab_name, setup_func in tabs:
                self.tab_view.add(tab_name)
                try:
                    setup_func()
                except Exception as e:
                    self.logger.error(f"Error setting up {tab_name}: {e}")
                    self._setup_error_tab(tab_name)
            
        except Exception as e:
            self.logger.error(f"Error creando área principal: {e}")

    def _setup_dashboard_tab(self):
        """Configura el dashboard"""
        tab = self.tab_view.tab("📊 Dashboard")
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(scroll_frame)
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="¡Bienvenido a MedStudy Pro!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors.TEXT_DARK
        )
        welcome_label.pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(
            welcome_frame,
            text="Tu centro de comando para el estudio médico efectivo",
            font=ctk.CTkFont(size=14),
            text_color=self.colors.TEXT_MEDIUM
        )
        info_label.pack(pady=(0, 20))
        
        # Quick actions
        actions_frame = ctk.CTkFrame(scroll_frame)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Acciones Rápidas",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors.TEXT_DARK
        )
        actions_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        actions = [
            ("📋 Crear Plan", lambda: self.tab_view.set("📋 Planificador")),
            ("📖 Nueva Sesión", lambda: self.tab_view.set("📖 Sesiones")),
            ("💬 Chat IA", lambda: self.tab_view.set("💬 Chat IA"))
        ]
        
        for text, command in actions:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            btn.pack(side="left", padx=(0, 10))
        
        # Stats overview
        self._create_stats_overview(scroll_frame)

    def _create_stats_overview(self, parent):
        """Crea resumen de estadísticas"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x")
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text="Resumen de Actividad",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors.TEXT_DARK
        )
        stats_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Stats grid
        grid_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 15))
        grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Get stats from database if available
        stats_data = self._get_stats_data()
        
        for i, (title, value, icon, color) in enumerate(stats_data):
            stat_card = self._create_stat_card(grid_frame, title, value, icon, color)
            stat_card.grid(row=0, column=i, padx=5, sticky="ew")

    def _get_stats_data(self):
        """Obtiene datos de estadísticas"""
        if self.db_manager:
            try:
                # Query real data
                plans_count = len(self.db_manager.execute_query("SELECT COUNT(*) FROM study_plans")[0])
                sessions_count = len(self.db_manager.execute_query("SELECT COUNT(*) FROM study_sessions")[0])
                topics_count = len(self.db_manager.execute_query("SELECT COUNT(*) FROM study_topics")[0])
                
                return [
                    ("Planes Activos", str(plans_count), "📋", self.colors.PRIMARY_BLUE),
                    ("Sesiones", str(sessions_count), "📖", self.colors.ACCENT_TURQUOISE),
                    ("Temas", str(topics_count), "📚", self.colors.SUCCESS_GREEN),
                    ("Racha", "0 días", "🔥", self.colors.WARNING_AMBER)
                ]
            except:
                pass
        
        # Demo data
        return [
            ("Planes Activos", "0", "📋", self.colors.PRIMARY_BLUE),
            ("Sesiones", "0", "📖", self.colors.ACCENT_TURQUOISE),
            ("Temas", "0", "📚", self.colors.SUCCESS_GREEN),
            ("Racha", "0 días", "🔥", self.colors.WARNING_AMBER)
        ]

    def _create_stat_card(self, parent, title, value, icon, color):
        """Crea una tarjeta de estadística"""
        card = ctk.CTkFrame(parent)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        )
        value_label.pack()
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=self.colors.TEXT_MEDIUM
        )
        title_label.pack(pady=(5, 15))
        
        return card

    def _setup_planner_tab(self):
        """Configura la pestaña del planificador"""
        tab = self.tab_view.tab("📋 Planificador")
        
        if self.available_pages.get('planner'):
            # Create planner page
            self.planner_page = self.available_pages['planner'](
                tab, 
                self.config, 
                self.db_manager
            )
            self.planner_page.pack(fill="both", expand=True)
        else:
            self._create_placeholder_content(
                tab,
                "📋 Planificador de Estudio",
                "El planificador no está disponible.\nVerifica que el archivo study_planner_page.py esté en ui/pages/"
            )

    def _setup_sessions_tab(self):
        """Configura la pestaña de sesiones"""
        tab = self.tab_view.tab("📖 Sesiones")
        
        self._create_placeholder_content(
            tab,
            "📖 Sesiones de Estudio",
            "Próximamente: Sesiones estructuradas con Active Recall,\nTimer Pomodoro y generación automática de contenido."
        )

    def _setup_chat_tab(self):
        """Configura la pestaña de chat"""
        tab = self.tab_view.tab("💬 Chat IA")
        
        if self.available_pages.get('chat'):
            # Create chat panel
            self.chat_panel = self.available_pages['chat'](
                tab, 
                self.config, 
                db_manager=self.db_manager,
                app_colors={
                    "BACKGROUND_COLOR": self.colors.BACKGROUND_CREAM,
                    "TEXT_COLOR": self.colors.TEXT_DARK,
                    "PRIMARY_COLOR": self.colors.PRIMARY_BLUE,
                    "ACCENT_COLOR": self.colors.ACCENT_TURQUOISE
                }
            )
            self.chat_panel.pack(expand=True, fill="both", padx=10, pady=10)
        else:
            self._create_placeholder_content(
                tab,
                "💬 Chat con IA Médica",
                "Chat no disponible.\nVerifica la instalación de Ollama para habilitar esta función."
            )

    def _setup_progress_tab(self):
        """Configura la pestaña de progreso"""
        tab = self.tab_view.tab("📈 Progreso")
        
        self._create_placeholder_content(
            tab,
            "📈 Análisis de Progreso",
            "Próximamente: Visualización detallada de tu progreso,\nestadísticas de aprendizaje y recomendaciones personalizadas."
        )

    def _setup_error_tab(self, tab_name):
        """Configura una pestaña con error"""
        tab = self.tab_view.tab(tab_name)
        self._create_placeholder_content(
            tab,
            "❌ Error",
            f"Error cargando {tab_name}"
        )

    def _create_placeholder_content(self, parent, title, message):
        """Crea contenido placeholder"""
        frame = ctk.CTkFrame(parent)
        frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors.TEXT_DARK
        )
        title_label.pack(pady=(50, 20))
        
        msg_label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=self.colors.TEXT_MEDIUM,
            justify="center"
        )
        msg_label.pack()

    def _create_status_bar(self):
        """Crea la barra de estado inferior"""
        try:
            status_frame = ctk.CTkFrame(
                self,
                height=35,
                fg_color="#F8FAFC",
                corner_radius=0
            )
            status_frame.pack(fill="x", side="bottom")
            status_frame.pack_propagate(False)
            
            # Status text
            status_text = "MedStudy Pro v1.0 | Sistema Funcional"
            if self.db_manager:
                status_text += " | 💾 Base de datos conectada"
            else:
                status_text += " | ⚠️ Modo demo (sin base de datos)"
            
            status_label = ctk.CTkLabel(
                status_frame,
                text=status_text,
                font=ctk.CTkFont(size=11),
                text_color="#6B7280"
            )
            status_label.pack(side="left", padx=15, pady=7)
            
        except Exception as e:
            self.logger.error(f"Error creando status bar: {e}")

    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.mainloop()
        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")

# --- FUNCIÓN PARA TESTING ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Configurar CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    try:
        app = MedStudyMainWindow()
        app.run()
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()