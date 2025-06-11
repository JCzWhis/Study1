"""
MedStudy Pro - Study Planner Page
Página funcional para crear y gestionar planes de estudio médico
"""

import customtkinter as ctk
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import uuid
import threading
from tkinter import messagebox

# Safe imports
try:
    from core.database import DatabaseManager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    DatabaseManager = None

try:
    from core.study_planner import RetrospectiveStudyPlanner, ConfidenceLevel, StudyPriority
    PLANNER_AVAILABLE = True
except ImportError:
    PLANNER_AVAILABLE = False
    RetrospectiveStudyPlanner = None
    
    # Fallback enums
    class ConfidenceLevel:
        RED = "red"
        ORANGE = "orange"
        YELLOW = "yellow"
        GREEN = "green"
        BLUE = "blue"
    
    class StudyPriority:
        URGENT = "urgent"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
        OPTIONAL = "optional"

class StudyPlannerPage(ctk.CTkFrame):
    """Página principal del planificador de estudio"""
    
    def __init__(self, parent, config=None, db_manager=None):
        super().__init__(parent)
        self.config = config
        self.db_manager = db_manager
        
        # Colors
        self.colors = {
            "PRIMARY": "#1E3A8A",
            "SUCCESS": "#10B981",
            "WARNING": "#F59E0B",
            "ERROR": "#EF4444",
            "ACCENT": "#06B6D4",
            "BG_LIGHT": "#F8FAFC",
            "TEXT_DARK": "#1F2937",
            "TEXT_MEDIUM": "#6B7280",
            # Confidence colors
            "RED": "#EF4444",
            "ORANGE": "#F97316",
            "YELLOW": "#EAB308",
            "GREEN": "#10B981",
            "BLUE": "#3B82F6"
        }
        
        # Initialize planner
        self.planner = None
        if PLANNER_AVAILABLE and db_manager:
            try:
                self.planner = RetrospectiveStudyPlanner(db_manager)
            except Exception as e:
                print(f"Error initializing planner: {e}")
        
        # State
        self.current_plan_id = None
        self.active_plans = []
        self.selected_topics = []
        
        # UI Setup
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_ui()
        self._load_existing_plans()
        
    def _create_ui(self):
        """Crea la interfaz completa"""
        # Header
        self._create_header()
        
        # Main content area with two columns
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=2)  # Left column wider
        content_frame.grid_columnconfigure(1, weight=1)  # Right column narrower
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left: Plan creation and topics
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        
        self._create_plan_creator(left_frame)
        self._create_topics_manager(left_frame)
        
        # Right: Active plans and progress
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        
        self._create_plans_list(right_frame)
        
    def _create_header(self):
        """Crea el header de la página"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="📋 Planificador de Estudio Retrospectivo",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["TEXT_DARK"]
        )
        title.pack(side="left")
        
        # Quick stats
        self.stats_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        )
        self.stats_label.pack(side="right", padx=20)
        
    def _create_plan_creator(self, parent):
        """Crea el formulario para nuevo plan"""
        creator_frame = ctk.CTkFrame(parent)
        creator_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            creator_frame,
            text="Crear Nuevo Plan de Estudio",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["TEXT_DARK"]
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Form fields
        form_frame = ctk.CTkFrame(creator_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Plan title
        ctk.CTkLabel(
            form_frame,
            text="Título del Plan:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        ).pack(anchor="w", pady=(5, 2))
        
        self.plan_title_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ej: Preparación Examen Cardiología",
            height=35
        )
        self.plan_title_entry.pack(fill="x", pady=(0, 10))
        
        # Two columns for specialty and deadline
        cols_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cols_frame.pack(fill="x", pady=(0, 10))
        cols_frame.grid_columnconfigure(0, weight=1)
        cols_frame.grid_columnconfigure(1, weight=1)
        
        # Specialty
        spec_frame = ctk.CTkFrame(cols_frame, fg_color="transparent")
        spec_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ctk.CTkLabel(
            spec_frame,
            text="Especialidad:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        ).pack(anchor="w", pady=(5, 2))
        
        self.specialty_var = ctk.StringVar(value="medicina_interna")
        self.specialty_menu = ctk.CTkOptionMenu(
            spec_frame,
            values=["medicina_interna", "cardiologia", "reumatologia", "nefrologia", 
                    "endocrinologia", "neurologia", "gastroenterologia", "general"],
            variable=self.specialty_var,
            height=35
        )
        self.specialty_menu.pack(fill="x")
        
        # Deadline
        deadline_frame = ctk.CTkFrame(cols_frame, fg_color="transparent")
        deadline_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        ctk.CTkLabel(
            deadline_frame,
            text="Plazo (días):",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        ).pack(anchor="w", pady=(5, 2))
        
        self.deadline_var = ctk.StringVar(value="30")
        self.deadline_menu = ctk.CTkOptionMenu(
            deadline_frame,
            values=["7", "14", "30", "60", "90"],
            variable=self.deadline_var,
            height=35
        )
        self.deadline_menu.pack(fill="x")
        
        # Profundidad
        ctk.CTkLabel(
            form_frame,
            text="Nivel de Profundidad:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        ).pack(anchor="w", pady=(5, 2))
        
        self.depth_var = ctk.StringVar(value="intermedio")
        self.depth_selector = ctk.CTkSegmentedButton(
            form_frame,
            values=["básico", "intermedio", "avanzado"],
            variable=self.depth_var,
            height=35
        )
        self.depth_selector.pack(fill="x", pady=(0, 15))
        
        # Create button
        self.create_btn = ctk.CTkButton(
            form_frame,
            text="Crear Plan",
            command=self._create_new_plan,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["PRIMARY"]
        )
        self.create_btn.pack(fill="x")
        
    def _create_topics_manager(self, parent):
        """Crea el gestor de temas"""
        topics_frame = ctk.CTkFrame(parent)
        topics_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        topics_frame.grid_columnconfigure(0, weight=1)
        topics_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(topics_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="Temas de Estudio",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["TEXT_DARK"]
        ).grid(row=0, column=0, sticky="w")
        
        # Topic input
        input_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.topic_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Agregar tema (Ej: Insuficiencia Cardíaca)",
            height=35
        )
        self.topic_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.topic_entry.bind("<Return>", lambda e: self._add_topic())
        
        add_btn = ctk.CTkButton(
            input_frame,
            text="+",
            command=self._add_topic,
            width=35,
            height=35,
            font=ctk.CTkFont(size=18),
            fg_color=self.colors["SUCCESS"]
        )
        add_btn.grid(row=0, column=1)
        
        # Topics list
        self.topics_scroll = ctk.CTkScrollableFrame(topics_frame)
        self.topics_scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=(10, 15))
        self.topics_scroll.grid_columnconfigure(0, weight=1)
        
        # Empty state
        self.empty_topics_label = ctk.CTkLabel(
            self.topics_scroll,
            text="No hay temas agregados.\nComienza agregando temas para tu plan de estudio.",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        )
        self.empty_topics_label.grid(row=0, column=0, pady=20)
        
    def _create_plans_list(self, parent):
        """Crea la lista de planes activos"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Planes Activos",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["TEXT_DARK"]
        ).pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄",
            command=self._load_existing_plans,
            width=30,
            height=30,
            fg_color=self.colors["ACCENT"]
        )
        refresh_btn.pack(side="right")
        
        # Plans scroll
        self.plans_scroll = ctk.CTkScrollableFrame(list_frame)
        self.plans_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Empty state
        self.empty_plans_label = ctk.CTkLabel(
            self.plans_scroll,
            text="No hay planes activos.\nCrea tu primer plan de estudio.",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        )
        self.empty_plans_label.pack(pady=20)
        
    def _add_topic(self):
        """Agrega un tema a la lista"""
        topic = self.topic_entry.get().strip()
        if not topic:
            return
            
        if topic in self.selected_topics:
            messagebox.showwarning("Duplicado", "Este tema ya está en la lista.")
            return
            
        self.selected_topics.append(topic)
        self.topic_entry.delete(0, 'end')
        
        # Hide empty state
        self.empty_topics_label.grid_forget()
        
        # Create topic widget
        self._create_topic_widget(topic, len(self.selected_topics) - 1)
        
    def _create_topic_widget(self, topic: str, index: int):
        """Crea un widget para mostrar un tema"""
        topic_frame = ctk.CTkFrame(self.topics_scroll)
        topic_frame.grid(row=index, column=0, sticky="ew", pady=2)
        topic_frame.grid_columnconfigure(0, weight=1)
        
        # Topic name
        topic_label = ctk.CTkLabel(
            topic_frame,
            text=topic,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        topic_label.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            topic_frame,
            text="✕",
            command=lambda t=topic: self._remove_topic(t),
            width=25,
            height=25,
            fg_color=self.colors["ERROR"],
            hover_color="#DC2626"
        )
        delete_btn.grid(row=0, column=1, padx=(5, 10))
        
    def _remove_topic(self, topic: str):
        """Elimina un tema de la lista"""
        if topic in self.selected_topics:
            self.selected_topics.remove(topic)
            self._refresh_topics_list()
            
    def _refresh_topics_list(self):
        """Refresca la lista de temas"""
        # Clear all widgets
        for widget in self.topics_scroll.winfo_children():
            widget.destroy()
            
        if not self.selected_topics:
            self.empty_topics_label = ctk.CTkLabel(
                self.topics_scroll,
                text="No hay temas agregados.\nComienza agregando temas para tu plan de estudio.",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["TEXT_MEDIUM"]
            )
            self.empty_topics_label.grid(row=0, column=0, pady=20)
        else:
            for i, topic in enumerate(self.selected_topics):
                self._create_topic_widget(topic, i)
                
    def _create_new_plan(self):
        """Crea un nuevo plan de estudio"""
        # Validate inputs
        title = self.plan_title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Por favor ingresa un título para el plan.")
            return
            
        if not self.selected_topics:
            messagebox.showerror("Error", "Por favor agrega al menos un tema de estudio.")
            return
            
        # Create plan
        try:
            if self.planner:
                plan_id = self.planner.create_study_plan(
                    title=title,
                    specialty=self.specialty_var.get(),
                    topics=self.selected_topics
                )
                
                # Store additional metadata
                if self.db_manager:
                    self.db_manager.set_preference(
                        "study_plans",
                        f"{plan_id}_metadata",
                        {
                            "deadline_days": int(self.deadline_var.get()),
                            "depth_level": self.depth_var.get(),
                            "created_at": datetime.now().isoformat()
                        }
                    )
                
                messagebox.showinfo("Éxito", f"Plan '{title}' creado exitosamente!")
                
                # Clear form
                self.plan_title_entry.delete(0, 'end')
                self.selected_topics = []
                self._refresh_topics_list()
                
                # Reload plans
                self._load_existing_plans()
                
            else:
                # Fallback without database
                plan_data = {
                    "id": f"plan_{uuid.uuid4().hex[:12]}",
                    "title": title,
                    "specialty": self.specialty_var.get(),
                    "topics": self.selected_topics,
                    "deadline_days": int(self.deadline_var.get()),
                    "depth_level": self.depth_var.get(),
                    "created_at": datetime.now().isoformat()
                }
                
                messagebox.showinfo("Demo", f"Plan '{title}' creado (modo demo sin base de datos)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creando plan: {str(e)}")
            
    def _load_existing_plans(self):
        """Carga los planes existentes"""
        # Clear current plans
        for widget in self.plans_scroll.winfo_children():
            widget.destroy()
            
        if self.db_manager:
            try:
                # Get all plans
                plans = self.db_manager.execute_query(
                    "SELECT * FROM study_plans ORDER BY created_at DESC"
                )
                
                if plans:
                    self.empty_plans_label.pack_forget()
                    for i, plan in enumerate(plans):
                        self._create_plan_widget(plan, i)
                else:
                    self.empty_plans_label.pack(pady=20)
                    
                # Update stats
                self._update_stats(len(plans))
                
            except Exception as e:
                print(f"Error loading plans: {e}")
                self.empty_plans_label.pack(pady=20)
        else:
            # Demo mode
            self.empty_plans_label.pack(pady=20)
            
    def _create_plan_widget(self, plan_data: Dict, index: int):
        """Crea un widget para mostrar un plan"""
        plan_frame = ctk.CTkFrame(self.plans_scroll)
        plan_frame.pack(fill="x", pady=5)
        
        # Header
        header_frame = ctk.CTkFrame(plan_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=plan_data['title'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")
        
        # Specialty badge
        specialty_label = ctk.CTkLabel(
            header_frame,
            text=plan_data['specialty'],
            font=ctk.CTkFont(size=10),
            fg_color=self.colors["ACCENT"],
            text_color="white",
            corner_radius=10
        )
        specialty_label.pack(side="right", padx=5)
        
        # Topics count
        try:
            topics = json.loads(plan_data['topics'])
            topics_text = f"{len(topics)} temas"
        except:
            topics_text = "Sin temas"
            
        info_label = ctk.CTkLabel(
            plan_frame,
            text=topics_text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"],
            anchor="w"
        )
        info_label.pack(fill="x", padx=15, pady=(0, 5))
        
        # Actions
        actions_frame = ctk.CTkFrame(plan_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        view_btn = ctk.CTkButton(
            actions_frame,
            text="Ver Detalles",
            command=lambda p=plan_data: self._view_plan_details(p),
            height=30,
            fg_color=self.colors["PRIMARY"]
        )
        view_btn.pack(side="left", padx=(0, 5))
        
        study_btn = ctk.CTkButton(
            actions_frame,
            text="Estudiar Ahora",
            command=lambda p=plan_data: self._start_study_session(p),
            height=30,
            fg_color=self.colors["SUCCESS"]
        )
        study_btn.pack(side="left")
        
    def _view_plan_details(self, plan_data: Dict):
        """Muestra los detalles de un plan"""
        # Create details window
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Detalles: {plan_data['title']}")
        details_window.geometry("800x600")
        
        # Content
        content_frame = ctk.CTkScrollableFrame(details_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            content_frame,
            text=plan_data['title'],
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Topics with confidence levels
        ctk.CTkLabel(
            content_frame,
            text="Temas y Niveles de Confianza:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(20, 10))
        
        try:
            topics = json.loads(plan_data['topics'])
            
            # Get confidence levels if available
            if self.db_manager:
                topic_details = self.db_manager.execute_query(
                    """SELECT name, confidence_level, last_studied 
                       FROM study_topics 
                       WHERE plan_id = ?""",
                    (plan_data['plan_id'],)
                )
                
                for topic_data in topic_details:
                    self._create_topic_detail_widget(content_frame, topic_data)
            else:
                # Demo mode
                for topic in topics:
                    demo_data = {
                        'name': topic,
                        'confidence_level': 'red',
                        'last_studied': None
                    }
                    self._create_topic_detail_widget(content_frame, demo_data)
                    
        except Exception as e:
            print(f"Error showing topics: {e}")
            
    def _create_topic_detail_widget(self, parent, topic_data: Dict):
        """Crea widget para mostrar detalle de un tema"""
        topic_frame = ctk.CTkFrame(parent)
        topic_frame.pack(fill="x", pady=5)
        topic_frame.grid_columnconfigure(0, weight=1)
        
        # Topic name
        name_label = ctk.CTkLabel(
            topic_frame,
            text=topic_data['name'],
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # Confidence indicator
        confidence = topic_data.get('confidence_level', 'red')
        color = self.colors.get(confidence.upper(), self.colors["RED"])
        
        confidence_frame = ctk.CTkFrame(topic_frame, fg_color=color, width=20, height=20)
        confidence_frame.grid(row=0, column=1, padx=10)
        
        # Last studied
        last_studied = topic_data.get('last_studied')
        if last_studied:
            try:
                date = datetime.fromisoformat(last_studied)
                days_ago = (datetime.now() - date).days
                studied_text = f"Estudiado hace {days_ago} días"
            except:
                studied_text = "Nunca estudiado"
        else:
            studied_text = "Nunca estudiado"
            
        studied_label = ctk.CTkLabel(
            topic_frame,
            text=studied_text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["TEXT_MEDIUM"]
        )
        studied_label.grid(row=0, column=2, sticky="e", padx=15)
        
    def _start_study_session(self, plan_data: Dict):
        """Inicia una sesión de estudio"""
        messagebox.showinfo(
            "Sesión de Estudio",
            f"Iniciando sesión de estudio para:\n{plan_data['title']}\n\n" +
            "Esta función se integrará con el gestor de sesiones."
        )
        
    def _update_stats(self, plan_count: int):
        """Actualiza las estadísticas mostradas"""
        self.stats_label.configure(
            text=f"📊 {plan_count} planes activos"
        )