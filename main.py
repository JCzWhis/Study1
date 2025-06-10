"""
MedStudy Pro - Main Window (Rediseño Profesional)
Interfaz principal de la aplicación con un diseño moderno y médico.
Utiliza componentes modulares para construir la UI.
"""

import customtkinter as ctk
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones correctas
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# --- Importaciones de Componentes y Sistema ---
from app.config import config as global_config
from app.ui.components.medical_typography import MedicalTypography
from app.ui.components.medical_cards import MedicalStatsCard, MedicalTopicCard, MedicalContentCard
from app.ui.components.medical_indicators import SystemStatusIndicator, MedicalProgressRing, MedicalLoadingSpinner

# --- Ventana Principal ---
class MedStudyMainWindow(ctk.CTk):
    """Ventana principal de MedStudy Pro con diseño profesional."""

    def __init__(self, config=global_config, **kwargs):
        super().__init__(**kwargs)
        
        self.config = config
        self.typography = MedicalTypography()
        self.colors = self.config.colors

        self._setup_window()
        self._create_interface()
        
        logging.info("MedStudy Pro professional main window initialized with modular components.")

    def _setup_window(self):
        """Configura las propiedades principales de la ventana."""
        self.title("🧠 MedStudy Pro - Medical Study Assistant")
        self.geometry("1400x900")
        self.configure(fg_color=self.colors.BACKGROUND_CREAM)
        self.minsize(1100, 750)
        
        icon_path = project_root / "assets/icon.ico"
        try:
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
            else:
                logging.warning(f"Icon not found at {icon_path}")
        except Exception as e:
            logging.debug(f"Could not load icon: {e}")

    def _create_interface(self):
        """Crea la estructura de la interfaz principal."""
        self._create_header()
        self._create_main_content_area()
        self._create_status_bar()

    def _create_header(self):
        """Crea el header moderno de la aplicación."""
        header_frame = ctk.CTkFrame(self, fg_color=self.colors.PRIMARY_BLUE, height=70, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, padx=25, pady=15)
        
        ctk.CTkLabel(
            title_container, text="🧠 MedStudy Pro", font=self.typography.get_font("heading_20_bold"),
            # --- FIX APPLIED HERE ---
            # Replaced self.colors.CLINICAL_WHITE with its hex code.
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_container, text="Evidence-Based Medical Learning", font=self.typography.get_font("caption_12_normal"),
            text_color="#DBEAFE"
        ).pack(anchor="w")
        
        status_indicator = SystemStatusIndicator(header_frame, typography=self.typography, is_active=True)
        status_indicator.grid(row=0, column=2, padx=25)

    def _create_main_content_area(self):
        """Crea el área principal con el TabView."""
        self.tab_view = ctk.CTkTabview(self, corner_radius=10, border_width=1, border_color=self.colors.BORDER_LIGHT)
        self.tab_view.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.tab_view.configure(
            font=self.typography.get_font("button_14_bold"),
            fg_color=self.colors.BACKGROUND_CREAM,
            segmented_button_fg_color=self.colors.BACKGROUND_CREAM,
            segmented_button_selected_color=self.colors.PRIMARY_BLUE,
            # --- FIX APPLIED HERE ---
            segmented_button_unselected_color="#FFFFFF",
            segmented_button_selected_hover_color=self.colors.ACCENT_TURQUOISE,
            segmented_button_unselected_hover_color="#F0F9FF"
        )
        
        tabs = ["📊 Dashboard", "📋 Planner", "📖 Sessions", "🧪 Exams", "📈 Progress"]
        for tab_name in tabs:
            self.tab_view.add(tab_name)
            # --- FIX APPLIED HERE ---
            self.tab_view.tab(tab_name).configure(fg_color="#FFFFFF")
        
        self._setup_dashboard_tab()
        self._setup_planner_tab()
        self._setup_sessions_tab()
        self._setup_progress_tab()
        self._setup_placeholder_tab("🧪 Exams", "Adaptive Exam Generator", "Crea exámenes personalizados con casos clínicos generados desde tu base de conocimiento personal (RAG).")

    def _setup_dashboard_tab(self):
        """Configura el contenido del tab de Dashboard."""
        tab = self.tab_view.tab("📊 Dashboard")
        tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tab, text="Welcome to your Medical Command Center", font=self.typography.get_font("heading_24_bold"),
                     text_color=self.colors.TEXT_DARK).grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")
        
        ctk.CTkLabel(tab, text="Here's a summary of your study progress and quick actions to get started.",
                     font=self.typography.get_font("body_15_normal"), text_color=self.colors.TEXT_MEDIUM
                     ).grid(row=1, column=0, padx=25, pady=(0, 25), sticky="w")
        
        stats_frame = ctk.CTkFrame(tab, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        MedicalStatsCard(stats_frame, "Sessions", "12", "📖", self.colors.PRIMARY_BLUE, self.typography).grid(row=0, column=0, padx=10, sticky="nsew")
        MedicalStatsCard(stats_frame, "Hours Studied", "4.5h", "⏱️", self.colors.ACCENT_TURQUOISE, self.typography).grid(row=0, column=1, padx=10, sticky="nsew")
        MedicalStatsCard(stats_frame, "MedCards", "128", "🎴", self.colors.SUCCESS_GREEN, self.typography).grid(row=0, column=2, padx=10, sticky="nsew")
        MedicalStatsCard(stats_frame, "Current Streak", "8 days", "🔥", self.colors.WARNING_AMBER, self.typography).grid(row=0, column=3, padx=10, sticky="nsew")

    def _setup_planner_tab(self):
        """Configura el tab del Planner con tarjetas de temas."""
        tab = self.tab_view.tab("📋 Planner")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Retrospective Study Planner", font=self.typography.get_font("heading_24_bold"),
                     text_color=self.colors.TEXT_DARK).grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")
        
        topics_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        topics_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        tab.grid_rowconfigure(1, weight=1)
        topics_frame.grid_columnconfigure(0, weight=1)
        
        MedicalTopicCard(topics_frame, "Glomerulonefritis", "Nefrología", 0.75, self.typography).pack(fill="x", padx=10, pady=8)
        MedicalTopicCard(topics_frame, "Manejo de Sepsis", "Medicina Interna", 0.40, self.typography).pack(fill="x", padx=10, pady=8)
        MedicalTopicCard(topics_frame, "Artritis Reumatoide", "Reumatología", 0.90, self.typography).pack(fill="x", padx=10, pady=8)

    def _setup_sessions_tab(self):
        """Configura el tab de Sesiones con una tarjeta de contenido y un spinner."""
        tab = self.tab_view.tab("📖 Sessions")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        sample_content = "La anemia ferropénica es la causa más común de anemia a nivel mundial...\n\nFisiopatología:\n1. Depleción de los depósitos de hierro.\n2. Eritropoyesis deficiente en hierro.\n3. Anemia microcítica hipocrómica evidente."
        MedicalContentCard(tab, "Anemia Ferropénica: Generalidades", sample_content, self.typography).grid(row=0, column=0, sticky="nsew", padx=10, pady=15)
        
        spinner_frame = ctk.CTkFrame(tab, fg_color="transparent")
        spinner_frame.grid(row=0, column=1, padx=10, pady=15)
        spinner = MedicalLoadingSpinner(spinner_frame, self.typography)
        spinner.pack(pady=50)
        spinner.start()

    def _setup_progress_tab(self):
        """Configura el tab de Progreso con anillos de progreso."""
        tab = self.tab_view.tab("📈 Progress")
        tab.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(tab, text="Cognitive Progress Analysis", font=self.typography.get_font("heading_24_bold"),
                     text_color=self.colors.TEXT_DARK).grid(row=0, column=0, columnspan=3, padx=25, pady=(25, 5), sticky="w")
        
        ring1 = MedicalProgressRing(tab, size=200, progress=82, typography=self.typography)
        ring1.grid(row=1, column=0, pady=40)
        ctk.CTkLabel(tab, text="Retención General", font=self.typography.get_font("heading_16_bold")).grid(row=2, column=0)

        ring2 = MedicalProgressRing(tab, size=200, progress=65, typography=self.typography)
        ring2.grid(row=1, column=1, pady=40)
        ctk.CTkLabel(tab, text="Cardiología", font=self.typography.get_font("heading_16_bold")).grid(row=2, column=1)

        ring3 = MedicalProgressRing(tab, size=200, progress=91, typography=self.typography)
        ring3.grid(row=1, column=2, pady=40)
        ctk.CTkLabel(tab, text="Nefrología", font=self.typography.get_font("heading_16_bold")).grid(row=2, column=2)

    def _setup_placeholder_tab(self, tab_name: str, title: str, description: str):
        """Crea contenido placeholder para los tabs no implementados."""
        tab = self.tab_view.tab(tab_name)
        container = ctk.CTkFrame(tab, fg_color="#F8FAFC", corner_radius=12)
        container.pack(expand=True, fill="both", padx=25, pady=25)
        ctk.CTkLabel(container, text="🚧", font=("Arial", 48)).pack(pady=(60, 10))
        ctk.CTkLabel(container, text=title, font=self.typography.get_font("heading_20_bold"), text_color=self.colors.TEXT_DARK).pack(pady=5)
        ctk.CTkLabel(container, text=description, font=self.typography.get_font("body_14_normal"), text_color=self.colors.TEXT_MEDIUM, wraplength=500).pack(pady=(0, 60))

    def _create_status_bar(self):
        """Crea la barra de estado en la parte inferior."""
        status_frame = ctk.CTkFrame(self, height=35, fg_color="#F8FAFC", corner_radius=0, border_width=1, border_color=self.colors.BORDER_LIGHT)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        ctk.CTkLabel(status_frame, text=f"MedStudy Pro v1.0 | 🧠 Model: {self.config.get('Ollama', 'model', 'phi3:mini')} | © 2024 Dr. Cruz Migueles",
                     font=self.typography.get_font("code_12_normal"), text_color="#6B7280").pack(side="left", padx=15)

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = MedStudyMainWindow()
    app.run()