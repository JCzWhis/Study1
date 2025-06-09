"""
MedStudy Pro - Main Window (Versión Funcional Integrada)
Combina la interfaz principal con ChatTutorPanel y componentes del sistema
"""

import customtkinter as ctk
import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Agregar el directorio raíz al path si no está
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importaciones del sistema
try:
    from app.ui.components.chat_tutor_manager import ChatTutorPanel
    from core.llm_manager import LLMManager
    from core.database import DatabaseManager
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    ChatTutorPanel = None
    LLMManager = None
    DatabaseManager = None

# Medical Color Palette
PRIMARY_COLOR = "#1E3A8A"
SUCCESS_COLOR = "#10B981"
ACCENT_COLOR = "#06B6D4"
BACKGROUND_COLOR = "#FEFCF9"
TEXT_COLOR = "#1F2937"
BORDER_COLOR = "#E5E7EB"

# Store colors in a dictionary for easier passing
APP_COLORS = {
    "PRIMARY_COLOR": PRIMARY_COLOR,
    "SUCCESS_COLOR": SUCCESS_COLOR,
    "ACCENT_COLOR": ACCENT_COLOR,
    "BACKGROUND_COLOR": BACKGROUND_COLOR,
    "TEXT_COLOR": TEXT_COLOR,
    "BORDER_COLOR": BORDER_COLOR,
}

class MedStudyMainWindow(ctk.CTk):
    """Main application window for MedStudy Pro - Versión Integrada Funcional"""

    def __init__(self, config=None, database=None):
        super().__init__()
        
        self.config = config
        self.database = database
        self.logger = logging.getLogger('MedStudy.MainWindow')
        
        # Estado del ChatTutor
        self.chat_tutor_panel_visible = True
        self.chat_tutor_panel: Optional[ChatTutorPanel] = None
        self.sessions_main_content_frame: Optional[ctk.CTkFrame] = None
        self.chat_panel_frame: Optional[ctk.CTkFrame] = None
        self.chat_toggle_button: Optional[ctk.CTkButton] = None

        # Configurar ventana
        self._setup_window()
        self._setup_appearance()
        
        # Crear interfaz
        self._create_interface()
        
        self.logger.info("MedStudy Pro main window initialized")

    def _setup_window(self):
        """Configurar propiedades de la ventana"""
        self.title("🧠 MedStudy Pro - Medical Study Assistant")
        self.geometry("1400x900")
        self.resizable(True, True)
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.winfo_screenheight() // 2) - (900 // 2)
        self.geometry(f"1400x900+{x}+{y}")
        self.minsize(1000, 700)
        
        # Intentar establecer icono
        try:
            self.iconbitmap("icon.ico")
        except Exception as e:
            self.logger.debug(f"No icon file found: {e}")

    def _setup_appearance(self):
        """Configurar apariencia de CustomTkinter"""
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

    def _create_interface(self):
        """Crear la interfaz principal"""
        # Header
        self._create_header()
        
        # Tab View principal
        self._create_tab_view()
        
        # Status bar
        self._create_status_bar()

    def _create_header(self):
        """Crear header con título y estado del sistema"""
        header_frame = ctk.CTkFrame(
            self, 
            height=70, 
            fg_color=PRIMARY_COLOR, 
            corner_radius=0
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🧠 MedStudy Pro", 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color="white"
        )
        title_label.pack(side="left", padx=25, pady=15)
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Evidence-Based Medical Learning with Local AI", 
            font=ctk.CTkFont(size=13), 
            text_color="#E0E7FF"
        )
        subtitle_label.pack(side="left", padx=(0, 25), pady=15)
        
        # Estado del sistema
        status_text = "🟢 Sistema Activo" if self._check_system_health() else "🔴 Verificar Sistema"
        status_label = ctk.CTkLabel(
            header_frame, 
            text=status_text, 
            font=ctk.CTkFont(size=12), 
            text_color="white"
        )
        status_label.pack(side="right", padx=25, pady=15)

    def _create_tab_view(self):
        """Crear el sistema de tabs principal"""
        self.tab_view = ctk.CTkTabview(
            self, 
            corner_radius=10, 
            width=1380, 
            height=750
        )
        
        # Configurar colores del tab view
        self.tab_view.configure(
            segmented_button_selected_color=PRIMARY_COLOR,
            segmented_button_unselected_color=BACKGROUND_COLOR,
            segmented_button_selected_hover_color=ACCENT_COLOR,
            segmented_button_unselected_hover_color=ACCENT_COLOR
        )
        
        # Crear tabs
        self._create_tabs()
        
        # Empaquetar tab view
        self.tab_view.pack(expand=True, fill="both", padx=15, pady=(15, 50))

    def _create_tabs(self):
        """Crear contenido de todos los tabs"""
        # Agregar tabs
        self.tab_view.add("📊 Dashboard")
        self.tab_view.add("📋 Planificador")
        self.tab_view.add("📖 Sesiones")
        self.tab_view.add("🧪 Exámenes")
        self.tab_view.add("📊 Progreso")
        
        # Configurar contenido de cada tab
        self._setup_dashboard_tab()
        self._setup_planner_tab()
        self._setup_sessions_tab()
        self._setup_exams_tab()
        self._setup_progress_tab()

    def _setup_dashboard_tab(self):
        """Configurar tab de Dashboard"""
        dashboard_tab = self.tab_view.tab("📊 Dashboard")
        
        # Frame de bienvenida
        welcome_frame = ctk.CTkFrame(dashboard_tab, fg_color=BACKGROUND_COLOR)
        welcome_frame.pack(fill="x", padx=25, pady=25)
        
        # Título de bienvenida
        ctk.CTkLabel(
            welcome_frame, 
            text="¡Bienvenido a tu Centro de Estudio Médico!", 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color=TEXT_COLOR
        ).pack(pady=20)
        
        # Descripción
        ctk.CTkLabel(
            welcome_frame, 
            text="Sistema basado en neurociencia cognitiva para optimizar tu aprendizaje médico", 
            font=ctk.CTkFont(size=15), 
            text_color="#6B7280"
        ).pack(pady=(0, 20))
        
        # Grid de estadísticas
        stats_frame = ctk.CTkFrame(dashboard_tab)
        stats_frame.pack(fill="x", padx=25, pady=15)
        self._create_stats_grid(stats_frame)
        
        # Acciones rápidas
        actions_frame = ctk.CTkFrame(dashboard_tab)
        actions_frame.pack(fill="x", padx=25, pady=15)
        
        ctk.CTkLabel(
            actions_frame, 
            text="Acciones Rápidas", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 15))
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 20))
        
        # Botón Nueva Sesión
        ctk.CTkButton(
            buttons_frame, 
            text="📖 Nueva Sesión", 
            width=200, 
            height=45, 
            fg_color=SUCCESS_COLOR, 
            hover_color=ACCENT_COLOR, 
            command=self._start_study_session,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=15)
        
        # Botón Crear Examen
        ctk.CTkButton(
            buttons_frame, 
            text="🧪 Crear Examen", 
            width=200, 
            height=45, 
            fg_color=PRIMARY_COLOR, 
            command=self._create_exam,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=15)
        
        # Botón Subir PDFs
        ctk.CTkButton(
            buttons_frame, 
            text="📚 Subir PDFs", 
            width=200, 
            height=45, 
            fg_color=ACCENT_COLOR, 
            command=self._upload_documents,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=15)

    def _setup_planner_tab(self):
        """Configurar tab de Planificador"""
        planner_tab = self.tab_view.tab("📋 Planificador")
        
        # Contenido del planificador
        content_frame = ctk.CTkFrame(planner_tab, fg_color=BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Título
        ctk.CTkLabel(
            content_frame, 
            text="📋 Planificador Retrospectivo de Estudio", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 15))
        
        # Descripción
        ctk.CTkLabel(
            content_frame, 
            text="Sistema basado en Ali Abdaal's Spaced Repetition Spreadsheet", 
            font=ctk.CTkFont(size=15)
        ).pack(pady=15)
        
        # Estado de desarrollo
        ctk.CTkLabel(
            content_frame, 
            text="🚧 Módulo en desarrollo - Próximamente disponible", 
            font=ctk.CTkFont(size=13), 
            text_color="#6B7280"
        ).pack(pady=15)

    def _setup_sessions_tab(self):
        """Configurar tab de Sesiones con ChatTutor integrado"""
        sessions_tab = self.tab_view.tab("📖 Sesiones")
        
        # Configurar grid del tab
        sessions_tab.grid_columnconfigure(0, weight=7)  # Área principal (70%)
        sessions_tab.grid_columnconfigure(1, weight=0)  # Botón toggle (pequeño)
        sessions_tab.grid_columnconfigure(2, weight=3)  # Chat panel (30%)
        sessions_tab.grid_rowconfigure(0, weight=1)
        
        # Área principal de contenido
        self.sessions_main_content_frame = ctk.CTkFrame(
            sessions_tab, 
            fg_color=BACKGROUND_COLOR, 
            corner_radius=10
        )
        self.sessions_main_content_frame.grid(
            row=0, column=0, sticky="nsew", padx=(15, 8), pady=15
        )
        
        # Contenido del área principal
        self._create_sessions_main_content()
        
        # Botón toggle para el chat
        self.chat_toggle_button = ctk.CTkButton(
            sessions_tab,
            text="<" if self.chat_tutor_panel_visible else ">",
            width=25,
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._toggle_chat_panel,
            fg_color=ACCENT_COLOR,
            hover_color=PRIMARY_COLOR,
            corner_radius=10
        )
        self.chat_toggle_button.grid(row=0, column=1, sticky="ns", pady=120)
        
        # Frame para el ChatTutorPanel
        self.chat_panel_frame = ctk.CTkFrame(
            sessions_tab, 
            fg_color="transparent", 
            corner_radius=0
        )
        self.chat_panel_frame.grid(
            row=0, column=2, sticky="nsew", padx=(8, 15), pady=15
        )
        
        # Crear ChatTutorPanel si está disponible
        if ChatTutorPanel:
            try:
                self.chat_tutor_panel = ChatTutorPanel(
                    self.chat_panel_frame, 
                    config=self.config, 
                    db_manager=self.database,
                    app_colors=APP_COLORS
                )
                self.chat_tutor_panel.pack(expand=True, fill="both")
            except Exception as e:
                self.logger.error(f"Error creating ChatTutorPanel: {e}")
                self._create_chat_placeholder()
        else:
            self._create_chat_placeholder()

    def _create_sessions_main_content(self):
        """Crear contenido principal del área de sesiones"""
        # Título del área
        title_label = ctk.CTkLabel(
            self.sessions_main_content_frame,
            text="📖 Área de Sesión de Estudio",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_COLOR
        )
        title_label.pack(pady=(25, 15))
        
        # Descripción
        desc_label = ctk.CTkLabel(
            self.sessions_main_content_frame,
            text="Aquí se mostrará el contenido de estudio generado por IA\ncon Active Recall integrado y timer Pomodoro",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280",
            justify="center"
        )
        desc_label.pack(pady=15)
        
        # Controles de sesión
        controls_frame = ctk.CTkFrame(self.sessions_main_content_frame)
        controls_frame.pack(pady=25, padx=25, fill="x")
        
        # Input para tema
        ctk.CTkLabel(
            controls_frame,
            text="Tema de estudio:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        self.topic_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Ej: Artritis reumatoide, Insuficiencia cardíaca...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.topic_entry.pack(pady=5, padx=15, fill="x")
        
        # Botón generar contenido
        generate_btn = ctk.CTkButton(
            controls_frame,
            text="🚀 Generar Contenido de Estudio",
            command=self._generate_study_content,
            fg_color=SUCCESS_COLOR,
            hover_color=ACCENT_COLOR,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        generate_btn.pack(pady=20)

    def _create_chat_placeholder(self):
        """Crear placeholder si ChatTutorPanel no está disponible"""
        placeholder = ctk.CTkFrame(self.chat_panel_frame)
        placeholder.pack(expand=True, fill="both")
        
        ctk.CTkLabel(
            placeholder,
            text="💬 Chat Tutor\n\n🚧 Componente en desarrollo\n\nEl ChatTutorPanel se cargará\ncuando esté disponible",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280",
            justify="center"
        ).pack(expand=True)

    def _setup_exams_tab(self):
        """Configurar tab de Exámenes"""
        exams_tab = self.tab_view.tab("🧪 Exámenes")
        
        content_frame = ctk.CTkFrame(exams_tab, fg_color=BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(
            content_frame, 
            text="🧪 Exámenes Adaptativos", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 15))
        
        ctk.CTkLabel(
            content_frame, 
            text="45 preguntas generadas desde tu RAG personal", 
            font=ctk.CTkFont(size=15)
        ).pack(pady=15)
        
        ctk.CTkLabel(
            content_frame, 
            text="🚧 En desarrollo - Casos clínicos adaptativos", 
            font=ctk.CTkFont(size=13), 
            text_color="#6B7280"
        ).pack(pady=15)

    def _setup_progress_tab(self):
        """Configurar tab de Progreso"""
        progress_tab = self.tab_view.tab("📊 Progreso")
        
        content_frame = ctk.CTkFrame(progress_tab, fg_color=BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(
            content_frame, 
            text="📊 Análisis de Progreso", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 15))
        
        ctk.CTkLabel(
            content_frame, 
            text="Analytics basados en curvas de olvido y retención", 
            font=ctk.CTkFont(size=15)
        ).pack(pady=15)
        
        ctk.CTkLabel(
            content_frame, 
            text="🚧 En desarrollo - Dashboard de neurociencia cognitiva", 
            font=ctk.CTkFont(size=13), 
            text_color="#6B7280"
        ).pack(pady=15)

    def _create_stats_grid(self, parent):
        """Crear grid de estadísticas"""
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(pady=20)
        
        # Configurar columnas
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # Crear tarjetas de estadísticas
        self._create_stat_card(grid_frame, "Sesiones\nCompletadas", "0", 0, SUCCESS_COLOR)
        self._create_stat_card(grid_frame, "Horas de\nEstudio", "0h", 1, ACCENT_COLOR)
        self._create_stat_card(grid_frame, "Tarjetas\nRevisadas", "0", 2, PRIMARY_COLOR)
        self._create_stat_card(grid_frame, "Racha\nActual", "0 días", 3, "#F59E0B")

    def _create_stat_card(self, parent, title, value, column, color):
        """Crear tarjeta individual de estadística"""
        card = ctk.CTkFrame(parent, width=160, height=90, corner_radius=10)
        card.grid(row=0, column=column, padx=12, pady=8)
        card.grid_propagate(False)
        
        # Valor
        ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color=color
        ).pack(pady=(18, 3))
        
        # Título
        ctk.CTkLabel(
            card, 
            text=title, 
            font=ctk.CTkFont(size=12), 
            text_color="#6B7280"
        ).pack()

    def _create_status_bar(self):
        """Crear barra de estado"""
        status_frame = ctk.CTkFrame(
            self, 
            height=35, 
            fg_color="#F3F4F6", 
            corner_radius=0
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        # Estado de componentes
        ollama_status = "🟢 Ollama" if self._check_ollama() else "🔴 Ollama"
        db_status = "💾 DB OK" if self.database else "💾 DB Error"
        
        status_text = f"{ollama_status} | {db_status} | 🧠 phi3:mini | MedStudy Pro v1.0-beta"
        
        ctk.CTkLabel(
            status_frame, 
            text=status_text, 
            font=ctk.CTkFont(size=11), 
            text_color="#6B7280"
        ).pack(side="left", padx=15, pady=8)

    def _toggle_chat_panel(self):
        """Toggle la visibilidad del panel de chat"""
        self.chat_tutor_panel_visible = not self.chat_tutor_panel_visible
        
        if self.chat_tutor_panel_visible:
            # Mostrar panel
            self.chat_panel_frame.grid(
                row=0, column=2, sticky="nsew", padx=(8, 15), pady=15
            )
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(0, weight=7)
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(2, weight=3)
            self.chat_toggle_button.configure(text="<")
        else:
            # Ocultar panel
            self.chat_panel_frame.grid_remove()
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(0, weight=10)
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(2, weight=0)
            self.chat_toggle_button.configure(text=">")
        
        self.logger.info(f"Chat panel visibility: {'Visible' if self.chat_tutor_panel_visible else 'Hidden'}")

    def _generate_study_content(self):
        """Generar contenido de estudio"""
        topic = self.topic_entry.get().strip()
        if not topic:
            # Mostrar mensaje de error
            self._show_message("Error", "Por favor ingresa un tema de estudio")
            return
        
        self.logger.info(f"Generating study content for: {topic}")
        
        # Mostrar mensaje de progreso
        self._show_message("Información", f"Generando contenido para: {topic}\n\nEsto puede tomar unos momentos...")
        
        # TODO: Integrar con StudySessionManager cuando esté disponible
        try:
            if self.chat_tutor_panel and hasattr(self.chat_tutor_panel, 'set_study_context'):
                self.chat_tutor_panel.set_study_context(f"Estudiando: {topic}")
        except Exception as e:
            self.logger.error(f"Error setting study context: {e}")

    def _show_message(self, title: str, message: str):
        """Mostrar mensaje al usuario"""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x200")
        popup.transient(self)
        popup.grab_set()
        
        # Centrar popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (400 // 2)
        y = (popup.winfo_screenheight() // 2) - (200 // 2)
        popup.geometry(f"400x200+{x}+{y}")
        
        # Contenido
        ctk.CTkLabel(
            popup,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        ).pack(expand=True, pady=20)
        
        # Botón OK
        ctk.CTkButton(
            popup,
            text="OK",
            command=popup.destroy,
            width=100
        ).pack(pady=(0, 20))

    def _check_system_health(self) -> bool:
        """Verificar salud general del sistema"""
        return self._check_ollama() and self.database is not None

    def _check_ollama(self) -> bool:
        """Verificar si Ollama está disponible"""
        try:
            import requests
            if self.config:
                ollama_config = self.config.get_ollama_config() if hasattr(self.config, 'get_ollama_config') else {}
                host = ollama_config.get('host', 'http://localhost:11434')
                response = requests.get(host, timeout=2)
                return response.status_code == 200
            return False
        except Exception:
            return False

    # Métodos de acciones (placeholders por ahora)
    def _start_study_session(self):
        """Iniciar nueva sesión de estudio"""
        self.logger.info("Study session requested")
        self.tab_view.set("📖 Sesiones")  # Cambiar a tab de sesiones
        
    def _create_exam(self):
        """Crear nuevo examen"""
        self.logger.info("Exam creation requested")
        self.tab_view.set("🧪 Exámenes")  # Cambiar a tab de exámenes
        
    def _upload_documents(self):
        """Subir documentos"""
        self.logger.info("Document upload requested")
        # TODO: Implementar diálogo de selección de archivos
        self._show_message("Información", "Funcionalidad de subida de documentos en desarrollo")

    def run(self):
        """Ejecutar la aplicación"""
        self.logger.info("Starting MedStudy Pro GUI")
        self.mainloop()


# Alias para compatibilidad
MainWindow = MedStudyMainWindow

if __name__ == "__main__":
    # Testing básico
    import sys
    
    # Mock config para testing
    class MockConfig:
        def get(self, section, key, default=None):
            return default
        
        def get_ollama_config(self):
            return {
                'host': 'http://localhost:11434', 
                'model': 'phi3:mini', 
                'timeout': 60
            }
    
    # Configurar logging básico
    logging.basicConfig(level=logging.INFO)
    
    print("🧠 MedStudy Pro - Testing Main Window")
    print("📋 Initializing application...")
    
    try:
        app = MedStudyMainWindow(config=MockConfig())
        print("✅ Application initialized successfully")
        print("🚀 Starting GUI...")
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)