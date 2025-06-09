import customtkinter as ctk
import logging
from typing import Dict, Any, Optional

# Assuming ChatTutorPanel is now in this path
from app.ui.components.chat_tutor_panel import ChatTutorPanel 

# Medical Color Palette
PRIMARY_COLOR = "#1E3A8A"
SUCCESS_COLOR = "#10B981"
ACCENT_COLOR = "#06B6D4"
BACKGROUND_COLOR = "#FEFCF9"
TEXT_COLOR = "#1F2937"

# Store colors in a dictionary for easier passing
APP_COLORS = {
    "PRIMARY_COLOR": PRIMARY_COLOR,
    "SUCCESS_COLOR": SUCCESS_COLOR,
    "ACCENT_COLOR": ACCENT_COLOR,
    "BACKGROUND_COLOR": BACKGROUND_COLOR,
    "TEXT_COLOR": TEXT_COLOR,
}

class MedStudyMainWindow(ctk.CTk):
    """Main application window for MedStudy Pro - Integrated Jules + System version"""

    def __init__(self, config=None, database=None):
        super().__init__()
        
        self.config = config
        self.database = database
        self.logger = logging.getLogger('MedStudy.MainWindow')
        
        # For Chat Tutor Panel
        self.chat_tutor_panel_visible = True # Default to visible
        self.chat_tutor_panel: Optional[ChatTutorPanel] = None
        self.sessions_main_content_frame: Optional[ctk.CTkFrame] = None
        self.chat_panel_frame: Optional[ctk.CTkFrame] = None # Frame to hold the ChatTutorPanel
        self.chat_toggle_button: Optional[ctk.CTkButton] = None

        self._setup_window()
        self._setup_appearance()
        self._create_interface()
        
        self.logger.info("MedStudy Pro main window initialized")

    def _setup_window(self):
        self.title("🧠 MedStudy Pro - Medical Study Assistant")
        self.geometry("1400x900")
        self.resizable(True, True)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.winfo_screenheight() // 2) - (900 // 2)
        self.geometry(f"1400x900+{x}+{y}")
        self.minsize(1000, 700)
        try:
            self.iconbitmap("icon.ico")
        except Exception as e:
            self.logger.debug(f"No icon file found: {e}")

    def _setup_appearance(self):
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

    def _create_interface(self):
        self._create_header()
        self.tab_view = ctk.CTkTabview(
            self, corner_radius=10, width=1380, height=780
        )
        self.tab_view.configure(
            segmented_button_selected_color=PRIMARY_COLOR,
            segmented_button_unselected_color=BACKGROUND_COLOR,
            segmented_button_selected_hover_color=ACCENT_COLOR,
            segmented_button_unselected_hover_color=ACCENT_COLOR
        )
        self._create_tabs()
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=(10, 50))
        self._create_status_bar()

    def _create_header(self):
        header_frame = ctk.CTkFrame(self, height=60, fg_color=PRIMARY_COLOR, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame, text="🧠 MedStudy Pro", font=ctk.CTkFont(size=24, weight="bold"), text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame, text="Evidence-Based Medical Learning with Local AI", font=ctk.CTkFont(size=12), text_color="#E0E7FF"
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=15)
        
        status_text = "🟢 Sistema Activo" if self._check_system_health() else "🔴 Verificar Sistema"
        status_label = ctk.CTkLabel(
            header_frame, text=status_text, font=ctk.CTkFont(size=11), text_color="white"
        )
        status_label.pack(side="right", padx=20, pady=15)

    def _create_tabs(self):
        self.tab_view.add("📊 Dashboard")
        self._setup_dashboard_tab()
        self.tab_view.add("📋 Planificador")
        self._setup_planner_tab()
        self.tab_view.add("📖 Sesiones")
        self._setup_sessions_tab() # This will be changed
        self.tab_view.add("🧪 Exámenes")
        self._setup_exams_tab()
        self.tab_view.add("📊 Progreso")
        self._setup_progress_tab()

    def _setup_dashboard_tab(self):
        dashboard_tab = self.tab_view.tab("📊 Dashboard")
        welcome_frame = ctk.CTkFrame(dashboard_tab, fg_color=BACKGROUND_COLOR)
        welcome_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            welcome_frame, text="¡Bienvenido a tu Centro de Estudio Médico!", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR
        ).pack(pady=15)
        ctk.CTkLabel(
            welcome_frame, text="Sistema basado en neurociencia cognitiva para optimizar tu aprendizaje", font=ctk.CTkFont(size=14), text_color="#6B7280"
        ).pack(pady=(0, 15))
        stats_frame = ctk.CTkFrame(dashboard_tab)
        stats_frame.pack(fill="x", padx=20, pady=10)
        self._create_stats_grid(stats_frame)
        actions_frame = ctk.CTkFrame(dashboard_tab)
        actions_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            actions_frame, text="Acciones Rápidas", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15))
        ctk.CTkButton(
            buttons_frame, text="📖 Nueva Sesión", width=180, height=40, fg_color=SUCCESS_COLOR, hover_color=ACCENT_COLOR, command=self._start_study_session
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            buttons_frame, text="🧪 Crear Examen", width=180, height=40, fg_color=PRIMARY_COLOR, command=self._create_exam
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            buttons_frame, text="📚 Subir PDFs", width=180, height=40, fg_color=ACCENT_COLOR, command=self._upload_documents
        ).pack(side="left", padx=10)

    def _setup_planner_tab(self):
        planner_tab = self.tab_view.tab("📋 Planificador")
        ctk.CTkLabel(planner_tab, text="📋 Planificador Retrospectivo de Estudio", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(planner_tab, text="Sistema basado en Ali Abdaal's Spaced Repetition Spreadsheet", font=ctk.CTkFont(size=14)).pack(pady=10)
        ctk.CTkLabel(planner_tab, text="🚧 En desarrollo - Próximamente disponible", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(pady=10)

    def _setup_sessions_tab(self):
        """Setup Sessions tab content with main area and collapsible Chat Tutor."""
        sessions_tab = self.tab_view.tab("📖 Sesiones")
        sessions_tab.grid_columnconfigure(0, weight=7) # Main content area (70%)
        sessions_tab.grid_columnconfigure(1, weight=0) # Toggle button column (small)
        sessions_tab.grid_columnconfigure(2, weight=3) # Chat panel area (30%)
        sessions_tab.grid_rowconfigure(0, weight=1)

        # Main Content Area (Placeholder)
        self.sessions_main_content_frame = ctk.CTkFrame(sessions_tab, fg_color=BACKGROUND_COLOR, corner_radius=10)
        self.sessions_main_content_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        
        ctk.CTkLabel(
            self.sessions_main_content_frame,
            text="Área Principal de Sesión de Estudio\n(Contenido del estudio aquí)",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_COLOR
        ).pack(expand=True, padx=20, pady=20)
        
        # Toggle Button
        self.chat_toggle_button = ctk.CTkButton(
            sessions_tab,
            text=">", # Initially shows ">" to expand (panel starts visible, so button means "collapse")
            width=25,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._toggle_chat_panel,
            fg_color=ACCENT_COLOR,
            hover_color=PRIMARY_COLOR,
            corner_radius=8
        )
        self.chat_toggle_button.grid(row=0, column=1, sticky="ns", pady=100) # Centered vertically somewhat

        # Frame to hold ChatTutorPanel
        self.chat_panel_frame = ctk.CTkFrame(sessions_tab, fg_color="transparent", corner_radius=0)
        self.chat_panel_frame.grid(row=0, column=2, sticky="nsew", padx=(5,10), pady=10)
        
        # Instantiate ChatTutorPanel
        # Pass self.config (for LLMManager) and APP_COLORS
        self.chat_tutor_panel = ChatTutorPanel(
            self.chat_panel_frame, 
            config=self.config, 
            db_manager=self.database, # Pass database if ChatTutorPanel uses it
            app_colors=APP_COLORS
        )
        self.chat_tutor_panel.pack(expand=True, fill="both")
        
        # Initial state of toggle button based on panel visibility
        self._update_chat_toggle_button_text()


    def _toggle_chat_panel(self):
        """Toggles the visibility of the chat tutor panel."""
        self.chat_tutor_panel_visible = not self.chat_tutor_panel_visible
        
        if self.chat_tutor_panel_visible:
            self.chat_panel_frame.grid(row=0, column=2, sticky="nsew", padx=(5,10), pady=10)
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(0, weight=7) # Main content 70%
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(2, weight=3) # Chat panel 30%
        else:
            self.chat_panel_frame.grid_remove()
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(0, weight=10) # Main content 100%
            self.tab_view.tab("📖 Sesiones").grid_columnconfigure(2, weight=0)
            
        self._update_chat_toggle_button_text()
        self.logger.info(f"Chat panel visibility toggled to: {'Visible' if self.chat_tutor_panel_visible else 'Hidden'}")

    def _update_chat_toggle_button_text(self):
        if self.chat_toggle_button:
            if self.chat_tutor_panel_visible:
                self.chat_toggle_button.configure(text=">") # Button action: will collapse
            else:
                self.chat_toggle_button.configure(text="<") # Button action: will expand


    def _setup_exams_tab(self):
        exams_tab = self.tab_view.tab("🧪 Exámenes")
        ctk.CTkLabel(exams_tab, text="🧪 Exámenes Adaptativos", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(exams_tab, text="45 preguntas generadas desde tu RAG personal", font=ctk.CTkFont(size=14)).pack(pady=10)
        ctk.CTkLabel(exams_tab, text="🚧 En desarrollo - Casos clínicos adaptativos", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(pady=10)

    def _setup_progress_tab(self):
        progress_tab = self.tab_view.tab("📊 Progreso")
        ctk.CTkLabel(progress_tab, text="📊 Análisis de Progreso", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(progress_tab, text="Analytics basados en curvas de olvido y retención", font=ctk.CTkFont(size=14)).pack(pady=10)
        ctk.CTkLabel(progress_tab, text="🚧 En desarrollo - Dashboard de neurociencia cognitiva", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(pady=10)

    def _create_stats_grid(self, parent):
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(pady=15)
        for i in range(4): grid_frame.grid_columnconfigure(i, weight=1)
        self._create_stat_card(grid_frame, "Sesiones\nCompletadas", "0", 0)
        self._create_stat_card(grid_frame, "Horas de\nEstudio", "0h", 1)
        self._create_stat_card(grid_frame, "Tarjetas\nRevisadas", "0", 2)
        self._create_stat_card(grid_frame, "Racha\nActual", "0 días", 3)

    def _create_stat_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, width=150, height=80)
        card.grid(row=0, column=column, padx=10, pady=5)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color=SUCCESS_COLOR).pack(pady=(15, 5))
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#6B7280").pack()

    def _create_status_bar(self):
        status_frame = ctk.CTkFrame(self, height=30, fg_color="#F3F4F6", corner_radius=0)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        ollama_status = "🟢 Ollama" if self._check_ollama() else "🔴 Ollama"
        db_status = "💾 DB OK" if self.database else "💾 DB Error"
        status_text = f"{ollama_status} | {db_status} | 🧠 phi3:mini | MedStudy Pro v1.0-beta"
        ctk.CTkLabel(status_frame, text=status_text, font=ctk.CTkFont(size=10), text_color="#6B7280").pack(side="left", padx=10, pady=5)

    def _check_system_health(self) -> bool:
        return self._check_ollama() and self.database is not None

    def _check_ollama(self) -> bool:
        try:
            import requests # Ensure requests is imported
            if self.config:
                ollama_config = self.config.get_ollama_config() if hasattr(self.config, 'get_ollama_config') else self.config.get('ollama', {})
                host = ollama_config.get('host')
                if host:
                    response = requests.get(host, timeout=2)
                    return response.status_code == 200
            return False
        except Exception: # Catch all exceptions for robustness
            return False

    def _start_study_session(self): self.logger.info("Study session requested")
    def _create_exam(self): self.logger.info("Exam creation requested")
    def _upload_documents(self): self.logger.info("Document upload requested")

    def run(self):
        self.logger.info("Starting MedStudy Pro GUI")
        self.mainloop()

MainWindow = MedStudyMainWindow

if __name__ == "__main__":
    # This basic config is for standalone testing if needed.
    # In the actual app, config would be loaded from a file or passed.
    class MockConfig:
        def get(self, section, key, default=None):
            if section == 'Paths':
                return default
            if section == 'ollama': # For LLMManager
                 return {'host': 'http://localhost:11434', 'model': 'phi3:mini', 'timeout': 60}
            return default
        def get_ollama_config(self): # For MainWindow _check_ollama and LLMManager
            return {'host': 'http://localhost:11434', 'model': 'phi3:mini', 'timeout': 60}

    logging.basicConfig(level=logging.DEBUG)
    app = MedStudyMainWindow(config=MockConfig())
    app.run()
