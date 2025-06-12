"""
MedStudy Planner - Main Window
Interfaz principal profesional con diseño médico moderno
"""

import customtkinter as ctk
from typing import Dict, Any, Optional
import threading
from pathlib import Path
import json

# Importaciones locales
try:
    from ..core.planner_engine import PlannerEngine
    from ..core.database import PlannerDatabase
    from .components.dashboard import DashboardFrame
    from .components.plan_creator import PlanCreatorFrame
    from .components.study_session import StudySessionFrame
    from .components.analytics import AnalyticsFrame
    from .themes.medical_theme import MedicalTheme
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

class PlannerMainWindow(ctk.CTk):
    """Ventana principal del MedStudy Planner con diseño profesional"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("🧠 MedStudy Planner - Sistema de Planificación Retrospectiva")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        
        # Tema médico profesional
        self.theme = MedicalTheme()
        self.configure(fg_color=self.theme.colors["background"])
        
        # Estado de la aplicación
        self.current_page = "dashboard"
        self.planner_engine = None
        self.database = None
        
        # Configurar grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Inicializar componentes
        self._initialize_components()
        self._create_layout()
        self._load_data()
        
        # Configurar eventos
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _initialize_components(self):
        """Inicializa los componentes del sistema"""
        try:
            # Inicializar base de datos
            db_path = Path("data/planner.db")
            self.database = PlannerDatabase(db_path)
            
            # Inicializar motor del planificador
            self.planner_engine = PlannerEngine(self.database)
            
            print("✅ Componentes del planificador inicializados")
            
        except Exception as e:
            print(f"⚠️ Usando modo demo: {e}")
            self.database = None
            self.planner_engine = None
    
    def _create_layout(self):
        """Crea el layout principal de la aplicación"""
        # Sidebar de navegación
        self._create_sidebar()
        
        # Área de contenido principal
        self._create_main_content()
        
        # Status bar
        self._create_status_bar()
    
    def _create_sidebar(self):
        """Crea la barra lateral de navegación"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=280,
            corner_radius=0,
            fg_color=self.theme.colors["sidebar"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # Logo y título
        self._create_sidebar_header()
        
        # Navegación principal
        self._create_navigation()
        
        # Estadísticas rápidas
        self._create_quick_stats()
        
        # Configuraciones
        self._create_sidebar_footer()
    
    def _create_sidebar_header(self):
        """Crea el header del sidebar"""
        header_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=80
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 30))
        header_frame.pack_propagate(False)
        
        # Logo (emoji como placeholder)
        logo_label = ctk.CTkLabel(
            header_frame,
            text="🧠",
            font=ctk.CTkFont(size=32)
        )
        logo_label.pack(side="left")
        
        # Título y subtítulo
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True, padx=(15, 0))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="MedStudy Planner",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.theme.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Planificación Retrospectiva",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.colors["text_secondary"],
            anchor="w"
        )
        subtitle_label.pack(anchor="w")
    
    def _create_navigation(self):
        """Crea los botones de navegación"""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(0, 30))
        
        # Definir páginas
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Dashboard", "Vista general y progreso"),
            ("plans", "📋 Planes", "Gestionar planes de estudio"),
            ("study", "📖 Estudiar", "Sesiones de estudio activas"),
            ("analytics", "📈 Analytics", "Estadísticas detalladas"),
        ]
        
        for page_id, title, subtitle in nav_items:
            btn = self._create_nav_button(nav_frame, page_id, title, subtitle)
            self.nav_buttons[page_id] = btn
        
        # Marcar dashboard como activo
        self._set_active_nav_button("dashboard")
    
    def _create_nav_button(self, parent, page_id: str, title: str, subtitle: str):
        """Crea un botón de navegación estilizado"""
        # Contenedor del botón
        btn_frame = ctk.CTkFrame(
            parent,
            height=70,
            fg_color="transparent",
            cursor="hand2"
        )
        btn_frame.pack(fill="x", pady=3)
        btn_frame.pack_propagate(False)
        
        # Botón principal
        btn = ctk.CTkFrame(
            btn_frame,
            height=60,
            corner_radius=12,
            fg_color="transparent",
            cursor="hand2"
        )
        btn.pack(fill="both", padx=5, pady=5)
        
        # Contenido del botón
        content_frame = ctk.CTkFrame(btn, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=self.theme.colors["text_secondary"],
            anchor="w"
        )
        subtitle_label.pack(anchor="w")
        
        # Configurar eventos
        def on_click(event=None):
            self._navigate_to_page(page_id)
        
        def on_enter(event=None):
            if page_id != self.current_page:
                btn.configure(fg_color=self.theme.colors["nav_hover"])
        
        def on_leave(event=None):
            if page_id != self.current_page:
                btn.configure(fg_color="transparent")
        
        # Bind eventos a todos los elementos
        for widget in [btn_frame, btn, content_frame, title_label, subtitle_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        return btn
    
    def _create_quick_stats(self):
        """Crea estadísticas rápidas en el sidebar"""
        stats_frame = ctk.CTkFrame(
            self.sidebar,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Título
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📊 Resumen Rápido",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.colors["text_primary"]
        )
        stats_title.pack(pady=(15, 10))
        
        # Estadísticas
        self.quick_stats = {}
        stats_data = [
            ("plans_active", "Planes Activos", "3", self.theme.colors["primary"]),
            ("due_today", "Pendientes Hoy", "7", self.theme.colors["warning"]),
            ("streak", "Racha de Días", "12", self.theme.colors["success"]),
            ("progress", "Progreso General", "68%", self.theme.colors["accent"]),
        ]
        
        for stat_id, label, value, color in stats_data:
            stat_frame = self._create_quick_stat(stats_frame, label, value, color)
            self.quick_stats[stat_id] = stat_frame
        
        stats_frame.pack_configure(pady=(0, 30))
    
    def _create_quick_stat(self, parent, label: str, value: str, color: str):
        """Crea una estadística rápida"""
        stat_frame = ctk.CTkFrame(parent, fg_color="transparent", height=35)
        stat_frame.pack(fill="x", padx=15, pady=2)
        stat_frame.pack_propagate(False)
        
        # Valor
        value_label = ctk.CTkLabel(
            stat_frame,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color,
            anchor="w"
        )
        value_label.pack(side="left")
        
        # Label
        label_label = ctk.CTkLabel(
            stat_frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=self.theme.colors["text_secondary"],
            anchor="e"
        )
        label_label.pack(side="right")
        
        return {"value": value_label, "label": label_label}
    
    def _create_sidebar_footer(self):
        """Crea el footer del sidebar"""
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # Botón de configuración
        config_btn = ctk.CTkButton(
            footer_frame,
            text="⚙️ Configuración",
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color=self.theme.colors["secondary"],
            hover_color=self.theme.colors["secondary_hover"],
            command=self._open_settings
        )
        config_btn.pack(fill="x", pady=(0, 10))
        
        # Información de versión
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0 - Dr. Cruz Migueles",
            font=ctk.CTkFont(size=10),
            text_color=self.theme.colors["text_secondary"]
        )
        version_label.pack()
    
    def _create_main_content(self):
        """Crea el área de contenido principal"""
        self.main_content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.theme.colors["background"]
        )
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Crear contenedores para cada página
        self.page_frames = {}
        self._create_pages()
        
        # Mostrar página inicial
        self._show_page("dashboard")
    
    def _create_pages(self):
        """Crea todas las páginas de la aplicación"""
        # Dashboard
        self.page_frames["dashboard"] = self._create_dashboard_page()
        
        # Plans
        self.page_frames["plans"] = self._create_plans_page()
        
        # Study
        self.page_frames["study"] = self._create_study_page()
        
        # Analytics
        self.page_frames["analytics"] = self._create_analytics_page()
    
    def _create_dashboard_page(self):
        """Crea la página del dashboard"""
        dashboard_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Header del dashboard
        header_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        # Título de la página
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard - Vista General",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(side="left", anchor="w")
        
        # Fecha actual
        from datetime import datetime
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"📅 {datetime.now().strftime('%d de %B, %Y')}",
            font=ctk.CTkFont(size=14),
            text_color=self.theme.colors["text_secondary"],
            anchor="e"
        )
        date_label.pack(side="right", anchor="e")
        
        # Contenido scrollable
        content_scroll = ctk.CTkScrollableFrame(
            dashboard_frame,
            fg_color="transparent"
        )
        content_scroll.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Tarjetas de métricas principales
        self._create_metric_cards(content_scroll)
        
        # Gráficos de progreso
        self._create_progress_section(content_scroll)
        
        # Temas pendientes
        self._create_pending_section(content_scroll)
        
        return dashboard_frame
    
    def _create_metric_cards(self, parent):
        """Crea las tarjetas de métricas principales"""
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 30))
        
        # Grid de 4 columnas
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Datos de métricas
        metrics_data = [
            {
                "title": "Planes Activos",
                "value": "3",
                "subtitle": "+1 esta semana",
                "icon": "📋",
                "color": self.theme.colors["primary"],
                "bg_color": self.theme.colors["primary_light"]
            },
            {
                "title": "Temas Estudiados",
                "value": "47",
                "subtitle": "+8 este mes",
                "icon": "📚",
                "color": self.theme.colors["success"],
                "bg_color": self.theme.colors["success_light"]
            },
            {
                "title": "Tiempo Total",
                "value": "127h",
                "subtitle": "3.2h promedio/día",
                "icon": "⏱️",
                "color": self.theme.colors["warning"],
                "bg_color": self.theme.colors["warning_light"]
            },
            {
                "title": "Eficiencia",
                "value": "87%",
                "subtitle": "+5% vs mes pasado",
                "icon": "🎯",
                "color": self.theme.colors["accent"],
                "bg_color": self.theme.colors["accent_light"]
            }
        ]
        
        for i, metric in enumerate(metrics_data):
            card = self._create_metric_card(metrics_frame, metric)
            card.grid(row=0, column=i, padx=10, pady=0, sticky="ew")
    
    def _create_metric_card(self, parent, metric: Dict[str, Any]):
        """Crea una tarjeta de métrica individual"""
        card = ctk.CTkFrame(
            parent,
            height=120,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        card.pack_propagate(False)
        
        # Contenido de la tarjeta
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header con icono
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=30)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Icono
        icon_frame = ctk.CTkFrame(
            header_frame,
            width=30,
            height=30,
            corner_radius=8,
            fg_color=metric["bg_color"]
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=metric["icon"],
            font=ctk.CTkFont(size=16)
        )
        icon_label.pack(expand=True)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame,
            text=metric["title"],
            font=ctk.CTkFont(size=12),
            text_color=self.theme.colors["text_secondary"],
            anchor="w"
        )
        title_label.pack(side="left", padx=(10, 0))
        
        # Valor principal
        value_label = ctk.CTkLabel(
            content_frame,
            text=metric["value"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=metric["color"],
            anchor="w"
        )
        value_label.pack(anchor="w", pady=(5, 0))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text=metric["subtitle"],
            font=ctk.CTkFont(size=10),
            text_color=self.theme.colors["text_secondary"],
            anchor="w"
        )
        subtitle_label.pack(anchor="w")
        
        return card
    
    def _create_progress_section(self, parent):
        """Crea la sección de progreso"""
        progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 30))
        progress_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Gráfico de confianza
        confidence_card = self._create_confidence_chart(progress_frame)
        confidence_card.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        # Progreso semanal
        weekly_card = self._create_weekly_progress(progress_frame)
        weekly_card.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
    
    def _create_confidence_chart(self, parent):
        """Crea el gráfico de distribución de confianza"""
        card = ctk.CTkFrame(
            parent,
            height=300,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        card.pack_propagate(False)
        
        # Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎯 Distribución de Confianza",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Contenido del gráfico (simulado)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Barras de confianza simuladas
        confidence_levels = [
            ("🔴 No sé nada", "12", self.theme.colors["error"]),
            ("🟠 Sé poco", "8", self.theme.colors["warning"]),
            ("🟡 Sé algo", "15", self.theme.colors["info"]),
            ("🟢 Sé bastante", "23", self.theme.colors["success"]),
            ("🔵 Lo domino", "7", self.theme.colors["primary"])
        ]
        
        for level, count, color in confidence_levels:
            level_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=30)
            level_frame.pack(fill="x", pady=5)
            level_frame.pack_propagate(False)
            
            # Label
            label = ctk.CTkLabel(
                level_frame,
                text=level,
                font=ctk.CTkFont(size=12),
                text_color=self.theme.colors["text_primary"],
                anchor="w",
                width=120
            )
            label.pack(side="left")
            
            # Barra de progreso simulada
            bar_bg = ctk.CTkFrame(
                level_frame,
                height=15,
                corner_radius=7,
                fg_color=self.theme.colors["background"]
            )
            bar_bg.pack(side="left", fill="x", expand=True, padx=(10, 10))
            
            # Barra de valor
            bar_value = ctk.CTkFrame(
                bar_bg,
                height=11,
                corner_radius=5,
                fg_color=color,
                width=int(count) * 3  # Simular porcentaje
            )
            bar_value.pack(side="left", padx=2, pady=2)
            bar_value.pack_propagate(False)
            
            # Contador
            count_label = ctk.CTkLabel(
                level_frame,
                text=count,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color,
                width=30
            )
            count_label.pack(side="right")
        
        return card
    
    def _create_weekly_progress(self, parent):
        """Crea el progreso semanal"""
        card = ctk.CTkFrame(
            parent,
            height=300,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        card.pack_propagate(False)
        
        # Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Progreso Esta Semana",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Contenido
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Días de la semana
        days = ["L", "M", "X", "J", "V", "S", "D"]
        progress = [80, 95, 60, 100, 75, 40, 85]  # Porcentajes simulados
        
        days_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        days_frame.pack(fill="x", pady=(20, 10))
        days_frame.grid_columnconfigure(tuple(range(7)), weight=1)
        
        for i, (day, prog) in enumerate(zip(days, progress)):
            day_frame = ctk.CTkFrame(days_frame, fg_color="transparent")
            day_frame.grid(row=0, column=i, padx=5)
            
            # Círculo de progreso simulado
            circle_size = 50
            circle = ctk.CTkFrame(
                day_frame,
                width=circle_size,
                height=circle_size,
                corner_radius=circle_size//2,
                fg_color=self.theme.colors["primary"] if prog > 70 else self.theme.colors["background"]
            )
            circle.pack(pady=(0, 5))
            circle.pack_propagate(False)
            
            # Porcentaje
            prog_label = ctk.CTkLabel(
                circle,
                text=f"{prog}%",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="white" if prog > 70 else self.theme.colors["text_secondary"]
            )
            prog_label.pack(expand=True)
            
            # Día
            day_label = ctk.CTkLabel(
                day_frame,
                text=day,
                font=ctk.CTkFont(size=12),
                text_color=self.theme.colors["text_secondary"]
            )
            day_label.pack()
        
        # Resumen
        summary_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        summary_frame.pack(fill="x", pady=(20, 0))
        
        summary_text = "Esta semana: 25.5 horas • Promedio: 3.6h/día • Meta: 30h"
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=12),
            text_color=self.theme.colors["text_secondary"]
        )
        summary_label.pack()
        
        return card
    
    def _create_pending_section(self, parent):
        """Crea la sección de temas pendientes"""
        pending_card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        pending_card.pack(fill="x", pady=(0, 20))
        
        # Header
        header_frame = ctk.CTkFrame(pending_card, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎯 Temas Pendientes para Hoy",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.theme.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(side="left", anchor="w")
        
        # Botón ver todos
        view_all_btn = ctk.CTkButton(
            header_frame,
            text="Ver Todos →",
            font=ctk.CTkFont(size=12),
            height=30,
            width=100,
            fg_color=self.theme.colors["primary"],
            hover_color=self.theme.colors["primary_hover"],
            command=lambda: self._navigate_to_page("plans")
        )
        view_all_btn.pack(side="right")
        
        # Lista de temas pendientes
        content_frame = ctk.CTkFrame(pending_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Temas simulados
        pending_topics = [
            ("Insuficiencia Cardíaca", "Cardiología", "🔴", "Urgente - Vence hoy"),
            ("Artritis Reumatoide", "Reumatología", "🟠", "Pendiente desde ayer"),
            ("Diabetes Mellitus", "Endocrinología", "🟡", "Programado para hoy"),
            ("Hipertensión Arterial", "Medicina Interna", "🟢", "Repaso opcional"),
        ]
        
        for topic, specialty, priority, status in pending_topics:
            topic_frame = self._create_pending_topic(content_frame, topic, specialty, priority, status)
            topic_frame.pack(fill="x", pady=5)
    
    def _create_pending_topic(self, parent, topic: str, specialty: str, priority: str, status: str):
        """Crea un tema pendiente"""
        topic_frame = ctk.CTkFrame(
            parent,
            height=60,
            corner_radius=10,
            fg_color=self.theme.colors["background"]
        )
        topic_frame.pack_propagate(False)
        
        # Contenido del tema
        content_frame = ctk.CTkFrame(topic_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Left side - Prioridad y tema
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Top row - Prioridad y título
        top_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_frame.pack(fill="x")
        
        priority_label = ctk.CTkLabel(
            top_frame,
            text=priority,
            font=ctk.CTkFont(size=14)
        )
        priority_label.pack(side="left")
        
        topic_label = ctk.CTkLabel(
            top_frame,
            text=topic,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.colors["text_primary"]
        )
        topic_label.pack(side="left", padx=(8, 0))
        
        # Bottom row - Especialidad y estado
        bottom_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        bottom_frame.pack(fill="x")
        
        specialty_label = ctk.CTkLabel(
            bottom_frame,
            text=f"📚 {specialty}",
            font=ctk.CTkFont(size=11),
            text_color=self.theme.colors["text_secondary"]
        )
        specialty_label.pack(side="left")
        
        status_label = ctk.CTkLabel(
            bottom_frame,
            text=f"• {status}",
            font=ctk.CTkFont(size=11),
            text_color=self.theme.colors["text_secondary"]
        )
        status_label.pack(side="left", padx=(10, 0))
        
        # Right side - Botón de acción
        action_btn = ctk.CTkButton(
            content_frame,
            text="Estudiar",
            font=ctk.CTkFont(size=12),
            width=80,
            height=35,
            fg_color=self.theme.colors["primary"],
            hover_color=self.theme.colors["primary_hover"],
            command=lambda: self._start_study_session(topic)
        )
        action_btn.pack(side="right", pady=5)
        
        return topic_frame
    
    def _create_plans_page(self):
        """Crea la página de gestión de planes"""
        plans_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Header
        header_frame = ctk.CTkFrame(plans_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 Gestión de Planes",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.colors["text_primary"]
        )
        title_label.pack(side="left")
        
        # Botón nuevo plan
        new_plan_btn = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Plan",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=140,
            fg_color=self.theme.colors["success"],
            hover_color=self.theme.colors["success_hover"],
            command=self._create_new_plan
        )
        new_plan_btn.pack(side="right")
        
        # Contenido
        content_frame = ctk.CTkScrollableFrame(plans_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Placeholder para planes
        placeholder_frame = ctk.CTkFrame(
            content_frame,
            height=400,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        placeholder_frame.pack(fill="both", expand=True)
        placeholder_frame.pack_propagate(False)
        
        placeholder_label = ctk.CTkLabel(
            placeholder_frame,
            text="📋 Gestión de Planes\n\nAquí podrás:\n• Crear nuevos planes de estudio\n• Editar planes existentes\n• Gestionar temas y confianza\n• Ver progreso detallado",
            font=ctk.CTkFont(size=16),
            text_color=self.theme.colors["text_secondary"],
            justify="center"
        )
        placeholder_label.pack(expand=True)
        
        return plans_frame
    
    def _create_study_page(self):
        """Crea la página de sesiones de estudio"""
        study_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Header
        header_frame = ctk.CTkFrame(study_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📖 Sesiones de Estudio",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.colors["text_primary"]
        )
        title_label.pack(side="left")
        
        # Timer display
        timer_label = ctk.CTkLabel(
            header_frame,
            text="⏱️ 00:00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme.colors["accent"]
        )
        timer_label.pack(side="right")
        
        # Contenido
        content_frame = ctk.CTkScrollableFrame(study_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Sesión activa (placeholder)
        session_card = ctk.CTkFrame(
            content_frame,
            height=500,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        session_card.pack(fill="both", expand=True)
        session_card.pack_propagate(False)
        
        session_label = ctk.CTkLabel(
            session_card,
            text="📖 Sesiones de Estudio\n\nFuncionalidades:\n• Timer Pomodoro (45 min)\n• Active Recall integrado\n• Chat tutor lateral\n• Quiz al finalizar\n• Progreso en tiempo real",
            font=ctk.CTkFont(size=16),
            text_color=self.theme.colors["text_secondary"],
            justify="center"
        )
        session_label.pack(expand=True)
        
        return study_frame
    
    def _create_analytics_page(self):
        """Crea la página de analytics"""
        analytics_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Header
        header_frame = ctk.CTkFrame(analytics_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Analytics y Estadísticas",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.theme.colors["text_primary"]
        )
        title_label.pack(side="left")
        
        # Filtros
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        period_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["Última semana", "Último mes", "Últimos 3 meses", "Todo el tiempo"],
            width=150,
            height=35,
            fg_color=self.theme.colors["secondary"],
            button_color=self.theme.colors["secondary_hover"]
        )
        period_menu.pack(side="right")
        
        # Contenido
        content_frame = ctk.CTkScrollableFrame(analytics_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Grid de gráficos
        charts_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True)
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Gráfico de tiempo
        time_chart = ctk.CTkFrame(
            charts_frame,
            height=300,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        time_chart.grid(row=0, column=0, padx=(0, 15), pady=(0, 20), sticky="nsew")
        
        time_label = ctk.CTkLabel(
            time_chart,
            text="📊 Tiempo de Estudio\n\nGráficos interactivos con:\n• Distribución por especialidad\n• Tendencias temporales\n• Comparativas mensuales\n• Eficiencia por tema",
            font=ctk.CTkFont(size=14),
            text_color=self.theme.colors["text_secondary"],
            justify="center"
        )
        time_label.pack(expand=True)
        
        # Gráfico de progreso
        progress_chart = ctk.CTkFrame(
            charts_frame,
            height=300,
            corner_radius=15,
            fg_color=self.theme.colors["card_background"]
        )
        progress_chart.grid(row=0, column=1, padx=(15, 0), pady=(0, 20), sticky="nsew")
        
        progress_label = ctk.CTkLabel(
            progress_chart,
            text="🎯 Progreso General\n\nVisualizaciones de:\n• Evolución de confianza\n• Metas vs realidad\n• Predicciones de estudio\n• Áreas de mejora",
            font=ctk.CTkFont(size=14),
            text_color=self.theme.colors["text_secondary"],
            justify="center"
        )
        progress_label.pack(expand=True)
        
        return analytics_frame
    
    def _create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = ctk.CTkFrame(
            self,
            height=30,
            corner_radius=0,
            fg_color=self.theme.colors["sidebar"]
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_propagate(False)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="✅ Sistema listo - Planificador inicializado correctamente",
            font=ctk.CTkFont(size=10),
            text_color=self.theme.colors["text_secondary"]
        )
        self.status_label.pack(side="left", padx=20, pady=5)
        
        # Connection status
        connection_label = ctk.CTkLabel(
            self.status_bar,
            text="🟢 Base de datos conectada",
            font=ctk.CTkFont(size=10),
            text_color=self.theme.colors["success"]
        )
        connection_label.pack(side="right", padx=20, pady=5)
    
    def _navigate_to_page(self, page_id: str):
        """Navega a una página específica"""
        if page_id == self.current_page:
            return
        
        # Ocultar página actual
        if self.current_page in self.page_frames:
            self.page_frames[self.current_page].pack_forget()
        
        # Mostrar nueva página
        if page_id in self.page_frames:
            self.page_frames[page_id].pack(fill="both", expand=True)
            self.current_page = page_id
            
            # Actualizar navegación
            self._set_active_nav_button(page_id)
            
            # Actualizar status
            page_names = {
                "dashboard": "Dashboard - Vista General",
                "plans": "Gestión de Planes",
                "study": "Sesiones de Estudio",
                "analytics": "Analytics y Estadísticas"
            }
            self.status_label.configure(text=f"📍 {page_names.get(page_id, page_id)}")
    
    def _set_active_nav_button(self, active_page: str):
        """Marca el botón de navegación activo"""
        for page_id, button in self.nav_buttons.items():
            if page_id == active_page:
                button.configure(fg_color=self.theme.colors["nav_active"])
            else:
                button.configure(fg_color="transparent")
    
    def _show_page(self, page_id: str):
        """Muestra una página específica"""
        self._navigate_to_page(page_id)
    
    def _load_data(self):
        """Carga datos iniciales"""
        # Cargar datos del planificador
        threading.Thread(target=self._load_data_background, daemon=True).start()
    
    def _load_data_background(self):
        """Carga datos en segundo plano"""
        try:
            if self.planner_engine:
                # Actualizar estadísticas
                self._update_quick_stats()
            
            print("✅ Datos cargados correctamente")
            
        except Exception as e:
            print(f"⚠️ Error cargando datos: {e}")
    
    def _update_quick_stats(self):
        """Actualiza las estadísticas rápidas"""
        try:
            # Datos simulados por ahora
            stats_data = {
                "plans_active": "3",
                "due_today": "7", 
                "streak": "12",
                "progress": "68%"
            }
            
            # Actualizar UI en el hilo principal
            def update_ui():
                for stat_id, value in stats_data.items():
                    if stat_id in self.quick_stats:
                        self.quick_stats[stat_id]["value"].configure(text=value)
            
            self.after(0, update_ui)
            
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    def _create_new_plan(self):
        """Abre el diálogo para crear un nuevo plan"""
        # Por ahora, navegar a la página de planes
        self._navigate_to_page("plans")
        self.status_label.configure(text="🆕 Crear nuevo plan de estudio")
    
    def _start_study_session(self, topic: str):
        """Inicia una sesión de estudio para un tema"""
        self._navigate_to_page("study")
        self.status_label.configure(text=f"📖 Iniciando estudio: {topic}")
    
    def _open_settings(self):
        """Abre el diálogo de configuración"""
        self.status_label.configure(text="⚙️ Abriendo configuración...")
        # TODO: Implementar diálogo de configuración
    
    def _on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            # Guardar estado
            if self.database:
                print("💾 Guardando estado...")
            
            print("👋 Cerrando MedStudy Planner...")
            self.destroy()
            
        except Exception as e:
            print(f"Error al cerrar: {e}")
            self.destroy()


# Componentes auxiliares para importación fallback
class MedicalTheme:
    """Tema médico profesional"""
    
    def __init__(self):
        self.colors = {
            # Colores principales
            "primary": "#1E3A8A",           # Azul médico profesional
            "primary_hover": "#1E40AF",
            "primary_light": "#DBEAFE",
            
            "secondary": "#3B82F6",         # Azul secundario
            "secondary_hover": "#2563EB",
            
            "success": "#10B981",           # Verde médico
            "success_hover": "#059669",
            "success_light": "#D1FAE5",
            
            "warning": "#F59E0B",           # Naranja cálido
            "warning_hover": "#D97706",
            "warning_light": "#FEF3C7",
            
            "error": "#EF4444",             # Rojo médico
            "error_hover": "#DC2626",
            "error_light": "#FEE2E2",
            
            "accent": "#06B6D4",            # Turquesa
            "accent_hover": "#0891B2",
            "accent_light": "#CFFAFE",
            
            "info": "#8B5CF6",              # Púrpura
            "info_light": "#EDE9FE",
            
            # Colores de interfaz
            "background": "#F8FAFC",        # Fondo principal
            "sidebar": "#FFFFFF",           # Sidebar blanco
            "card_background": "#FFFFFF",   # Fondo de tarjetas
            
            # Navegación
            "nav_active": "#EBF4FF",        # Azul muy claro
            "nav_hover": "#F3F4F6",         # Gris muy claro
            
            # Texto
            "text_primary": "#1F2937",      # Texto principal
            "text_secondary": "#6B7280",    # Texto secundario
            "text_muted": "#9CA3AF",        # Texto deshabilitado
        }


# Clases placeholder para componentes que se crearán después
class PlannerEngine:
    def __init__(self, database):
        self.database = database
        print("🧠 PlannerEngine inicializado (placeholder)")

class PlannerDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        print(f"💾 PlannerDatabase inicializado: {db_path}")


if __name__ == "__main__":
    app = PlannerMainWindow()
    app.mainloop()