"""
MedStudy Pro - Main Window
Integrated version of Jules' CustomTkinter interface with our system
"""

import customtkinter as ctk
import logging
from typing import Dict, Any, Optional

# Medical Color Palette (from Jules + our config)
PRIMARY_COLOR = "#1E3A8A"      # Professional medical blue
SUCCESS_COLOR = "#10B981"      # Medical success/progress  
ACCENT_COLOR = "#06B6D4"       # Info and accents
BACKGROUND_COLOR = "#FEFCF9"   # Study mode background
TEXT_COLOR = "#1F2937"         # Primary text

class MedStudyMainWindow(ctk.CTk):
    """Main application window for MedStudy Pro - Integrated Jules + System version"""

    def __init__(self, config=None, database=None):
        super().__init__()
        
        # Store system components
        self.config = config
        self.database = database
        self.logger = logging.getLogger('MedStudy.MainWindow')
        
        # Initialize window
        self._setup_window()
        self._setup_appearance()
        self._create_interface()
        
        self.logger.info("MedStudy Pro main window initialized")

    def _setup_window(self):
        """Setup window properties"""
        self.title("🧠 MedStudy Pro - Medical Study Assistant")
        self.geometry("1400x900")
        self.resizable(True, True)
        
        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.winfo_screenheight() // 2) - (900 // 2)
        self.geometry(f"1400x900+{x}+{y}")
        
        # Set minimum size
        self.minsize(1000, 700)
        
        # Try to set icon (Jules' approach)
        try:
            self.iconbitmap("icon.ico")
        except Exception as e:
            self.logger.debug(f"No icon file found: {e}")
            # Icon is optional

    def _setup_appearance(self):
        """Setup CustomTkinter appearance"""
        ctk.set_appearance_mode("Light")  # Medical professional theme
        ctk.set_default_color_theme("blue")

    def _create_interface(self):
        """Create the main interface"""
        
        # Header frame with medical branding
        self._create_header()
        
        # Main tabview (Jules' approach enhanced)
        self.tab_view = ctk.CTkTabview(
            self, 
            corner_radius=10,
            width=1380,
            height=780
        )
        
        # Configure tab colors (Jules' styling)
        self.tab_view.configure(segmented_button_selected_color=PRIMARY_COLOR)
        self.tab_view.configure(segmented_button_unselected_color=BACKGROUND_COLOR)
        self.tab_view.configure(segmented_button_selected_hover_color=ACCENT_COLOR)
        self.tab_view.configure(segmented_button_unselected_hover_color=ACCENT_COLOR)

        # Create tabs with medical icons
        self._create_tabs()
        
        # Pack tabview
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=(10, 50))
        
        # Status bar
        self._create_status_bar()

    def _create_header(self):
        """Create header with medical branding"""
        header_frame = ctk.CTkFrame(
            self,
            height=60,
            fg_color=PRIMARY_COLOR,
            corner_radius=0
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🧠 MedStudy Pro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Evidence-Based Medical Learning with Local AI",
            font=ctk.CTkFont(size=12),
            text_color="#E0E7FF"
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=15)
        
        # System status indicator
        status_text = "🟢 Sistema Activo" if self._check_system_health() else "🔴 Verificar Sistema"
        status_label = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=ctk.CTkFont(size=11),
            text_color="white"
        )
        status_label.pack(side="right", padx=20, pady=15)

    def _create_tabs(self):
        """Create all application tabs"""
        
        # Dashboard Tab
        self.tab_view.add("📊 Dashboard")
        self._setup_dashboard_tab()
        
        # Planner Tab  
        self.tab_view.add("📋 Planificador")
        self._setup_planner_tab()
        
        # Sessions Tab
        self.tab_view.add("📖 Sesiones")
        self._setup_sessions_tab()
        
        # Exams Tab
        self.tab_view.add("🧪 Exámenes")
        self._setup_exams_tab()
        
        # Progress Tab
        self.tab_view.add("📊 Progreso")
        self._setup_progress_tab()

    def _setup_dashboard_tab(self):
        """Setup Dashboard tab content"""
        dashboard_tab = self.tab_view.tab("📊 Dashboard")
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(dashboard_tab, fg_color=BACKGROUND_COLOR)
        welcome_frame.pack(fill="x", padx=20, pady=20)
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="¡Bienvenido a tu Centro de Estudio Médico!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_COLOR
        )
        welcome_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            welcome_frame,
            text="Sistema basado en neurociencia cognitiva para optimizar tu aprendizaje",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280"
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Quick stats
        stats_frame = ctk.CTkFrame(dashboard_tab)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self._create_stats_grid(stats_frame)
        
        # Quick actions
        actions_frame = ctk.CTkFrame(dashboard_tab)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Acciones Rápidas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        actions_label.pack(pady=(15, 10))
        
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15))
        
        # Action buttons
        study_btn = ctk.CTkButton(
            buttons_frame,
            text="📖 Nueva Sesión",
            width=180,
            height=40,
            fg_color=SUCCESS_COLOR,
            hover_color=ACCENT_COLOR,
            command=self._start_study_session
        )
        study_btn.pack(side="left", padx=10)
        
        exam_btn = ctk.CTkButton(
            buttons_frame,
            text="🧪 Crear Examen",
            width=180,
            height=40,
            fg_color=PRIMARY_COLOR,
            command=self._create_exam
        )
        exam_btn.pack(side="left", padx=10)
        
        upload_btn = ctk.CTkButton(
            buttons_frame,
            text="📚 Subir PDFs",
            width=180,
            height=40,
            fg_color=ACCENT_COLOR,
            command=self._upload_documents
        )
        upload_btn.pack(side="left", padx=10)

    def _setup_planner_tab(self):
        """Setup Planner tab content"""
        planner_tab = self.tab_view.tab("📋 Planificador")
        
        ctk.CTkLabel(
            planner_tab,
            text="📋 Planificador Retrospectivo de Estudio",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            planner_tab,
            text="Sistema basado en Ali Abdaal's Spaced Repetition Spreadsheet",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            planner_tab,
            text="🚧 En desarrollo - Próximamente disponible",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        ).pack(pady=10)

    def _setup_sessions_tab(self):
        """Setup Sessions tab content"""
        sessions_tab = self.tab_view.tab("📖 Sesiones")
        
        ctk.CTkLabel(
            sessions_tab,
            text="📖 Sesiones de Estudio con IA",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            sessions_tab,
            text="45 minutos de contenido + Active Recall + Chat Tutor lateral",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            sessions_tab,
            text="🚧 En desarrollo - Integración con RAG y phi3:mini",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        ).pack(pady=10)

    def _setup_exams_tab(self):
        """Setup Exams tab content"""
        exams_tab = self.tab_view.tab("🧪 Exámenes")
        
        ctk.CTkLabel(
            exams_tab,
            text="🧪 Exámenes Adaptativos",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            exams_tab,
            text="45 preguntas generadas desde tu RAG personal",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            exams_tab,
            text="🚧 En desarrollo - Casos clínicos adaptativos",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        ).pack(pady=10)

    def _setup_progress_tab(self):
        """Setup Progress tab content"""
        progress_tab = self.tab_view.tab("📊 Progreso")
        
        ctk.CTkLabel(
            progress_tab,
            text="📊 Análisis de Progreso",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            progress_tab,
            text="Analytics basados en curvas de olvido y retención",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            progress_tab,
            text="🚧 En desarrollo - Dashboard de neurociencia cognitiva",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        ).pack(pady=10)

    def _create_stats_grid(self, parent):
        """Create statistics grid"""
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(pady=15)
        
        # Configure grid
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # Stat cards
        self._create_stat_card(grid_frame, "Sesiones\nCompletadas", "0", 0)
        self._create_stat_card(grid_frame, "Horas de\nEstudio", "0h", 1)
        self._create_stat_card(grid_frame, "Tarjetas\nRevisadas", "0", 2)
        self._create_stat_card(grid_frame, "Racha\nActual", "0 días", 3)

    def _create_stat_card(self, parent, title, value, column):
        """Create individual stat card"""
        card = ctk.CTkFrame(parent, width=150, height=80)
        card.grid(row=0, column=column, padx=10, pady=5)
        card.grid_propagate(False)
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=SUCCESS_COLOR
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        ).pack()

    def _create_status_bar(self):
        """Create bottom status bar"""
        status_frame = ctk.CTkFrame(
            self,
            height=30,
            fg_color="#F3F4F6",
            corner_radius=0
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        # System status
        ollama_status = "🟢 Ollama" if self._check_ollama() else "🔴 Ollama"
        db_status = "💾 DB OK" if self.database else "💾 DB Error"
        
        status_text = f"{ollama_status} | {db_status} | 🧠 phi3:mini | MedStudy Pro v1.0-beta"
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=10),
            text_color="#6B7280"
        )
        status_label.pack(side="left", padx=10, pady=5)

    def _check_system_health(self) -> bool:
        """Check overall system health"""
        return self._check_ollama() and self.database is not None

    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            if self.config:
                ollama_config = self.config.get_ollama_config()
                response = requests.get(ollama_config['host'], timeout=2)
                return response.status_code == 200
            return False
        except:
            return False

    # Event handlers
    def _start_study_session(self):
        """Start a new study session"""
        self.logger.info("Study session requested")
        # TODO: Implement study session

    def _create_exam(self):
        """Create a new exam"""
        self.logger.info("Exam creation requested")
        # TODO: Implement exam creation

    def _upload_documents(self):
        """Upload medical documents"""
        self.logger.info("Document upload requested")
        # TODO: Implement document upload

    def run(self):
        """Run the application"""
        self.logger.info("Starting MedStudy Pro GUI")
        self.mainloop()

# Compatibility with Jules' original code
MainWindow = MedStudyMainWindow

if __name__ == "__main__":
    app = MedStudyMainWindow()
    app.run()