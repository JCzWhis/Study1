"""
MedStudy Pro - Main Window (VERSIÓN FINAL CORREGIDA)
Interfaz principal de la aplicación con diseño médico profesional
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
        
        return FallbackConfig()

def safe_import_components():
    """Importa componentes UI de manera segura"""
    components = {}
    
    try:
        from app.ui.components.medical_typography import MedicalTypography
        components['typography'] = MedicalTypography
    except ImportError:
        # Fallback typography
        class FallbackTypography:
            def get_font(self, style):
                size_map = {
                    "heading_24_bold": 24,
                    "heading_20_bold": 20,
                    "heading_18_bold": 18,
                    "heading_16_bold": 16,
                    "body_15_normal": 15,
                    "body_14_normal": 14,
                    "caption_12_normal": 12,
                    "button_14_bold": 14,
                    "code_12_normal": 12
                }
                size = size_map.get(style, 12)
                weight = "bold" if "bold" in style else "normal"
                return ctk.CTkFont(size=size, weight=weight)
        
        components['typography'] = FallbackTypography
    
    try:
        from app.ui.components.medical_cards import MedicalStatsCard, MedicalTopicCard, MedicalContentCard
        components['cards'] = (MedicalStatsCard, MedicalTopicCard, MedicalContentCard)
    except ImportError:
        components['cards'] = None
    
    try:
        from app.ui.components.medical_indicators import SystemStatusIndicator, MedicalProgressRing, MedicalLoadingSpinner
        components['indicators'] = (SystemStatusIndicator, MedicalProgressRing, MedicalLoadingSpinner)
    except ImportError:
        components['indicators'] = None
    
    try:
        from app.ui.components.chat_tutor_manager import ChatTutorPanel
        components['chat'] = ChatTutorPanel
    except ImportError:
        components['chat'] = None
    
    return components

# --- VENTANA PRINCIPAL ---
class MedStudyMainWindow(ctk.CTk):
    """Ventana principal de MedStudy Pro con diseño médico profesional"""

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        
        # Configuración
        self.config = config or safe_import_config()
        self.logger = logging.getLogger('MedStudy.MainWindow')
        
        # Componentes
        components = safe_import_components()
        self.typography = components['typography']()
        self.colors = self.config.colors
        
        # Configurar ventana
        self._setup_window()
        
        # Crear interfaz
        self._create_interface(components)
        
        self.logger.info("MedStudy Pro main window initialized")

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
            
            # Icono (opcional)
            try:
                icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
                if icon_path.exists():
                    self.iconbitmap(str(icon_path))
            except Exception as e:
                self.logger.debug(f"No se pudo cargar icono: {e}")
                
        except Exception as e:
            self.logger.error(f"Error configurando ventana: {e}")

    def _create_interface(self, components):
        """Crea la estructura de la interfaz principal"""
        try:
            self._create_header(components)
            self._create_main_content_area(components)
            self._create_status_bar()
        except Exception as e:
            self.logger.error(f"Error creando interfaz: {e}")
            self._create_fallback_interface()

    def _create_header(self, components):
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
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Contenedor del título
            title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_container.grid(row=0, column=0, padx=25, pady=15, sticky="w")
            
            # Título principal
            title_label = ctk.CTkLabel(
                title_container,
                text="🧠 MedStudy Pro",
                font=self.typography.get_font("heading_20_bold"),
                text_color="#FFFFFF"
            )
            title_label.pack(anchor="w")
            
            # Subtítulo
            subtitle_label = ctk.CTkLabel(
                title_container,
                text="Evidence-Based Medical Learning",
                font=self.typography.get_font("caption_12_normal"),
                text_color="#DBEAFE"
            )
            subtitle_label.pack(anchor="w")
            
            # Indicador de estado (si disponible)
            if components['indicators']:
                SystemStatusIndicator = components['indicators'][0]
                try:
                    status_indicator = SystemStatusIndicator(
                        header_frame, 
                        typography=self.typography, 
                        is_active=True
                    )
                    status_indicator.grid(row=0, column=2, padx=25, pady=15, sticky="e")
                except Exception as e:
                    self.logger.warning(f"No se pudo crear indicador de estado: {e}")
            
        except Exception as e:
            self.logger.error(f"Error creando header: {e}")

    def _create_main_content_area(self, components):
        """Crea el área principal con pestañas - VERSIÓN CORREGIDA"""
        try:
            # TabView principal - SIN configuración de font que causa error
            self.tab_view = ctk.CTkTabview(
                self, 
                corner_radius=10, 
                border_width=1, 
                border_color=self.colors.BORDER_LIGHT
            )
            self.tab_view.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Configurar TabView - SIN FONT para evitar el error
            try:
                self.tab_view.configure(
                    fg_color=self.colors.BACKGROUND_CREAM,
                    segmented_button_fg_color=self.colors.BACKGROUND_CREAM,
                    segmented_button_selected_color=self.colors.PRIMARY_BLUE,
                    segmented_button_unselected_color="#FFFFFF",
                    segmented_button_selected_hover_color=self.colors.ACCENT_TURQUOISE,
                    segmented_button_unselected_hover_color="#F0F9FF"
                )
            except Exception as e:
                self.logger.warning(f"No se pudo configurar TabView styling: {e}")
            
            # Crear pestañas
            tabs = ["📊 Dashboard", "📋 Planner", "📖 Sessions", "🧪 Exams", "💬 Chat", "📈 Progress"]
            for tab_name in tabs:
                self.tab_view.add(tab_name)
                try:
                    self.tab_view.tab(tab_name).configure(fg_color="#FFFFFF")
                except Exception as e:
                    self.logger.debug(f"No se pudo configurar tab {tab_name}: {e}")
            
            # Configurar contenido de pestañas
            self._setup_dashboard_tab(components)
            self._setup_chat_tab(components)
            self._setup_sessions_tab(components)
            self._setup_progress_tab(components)
            self._setup_placeholder_tabs()
            
        except Exception as e:
            self.logger.error(f"Error creando área principal: {e}")
            # Crear TabView básico como fallback
            self._create_basic_tabview(components)

    def _create_basic_tabview(self, components):
        """Crea TabView básico como fallback"""
        try:
            self.tab_view = ctk.CTkTabview(self)
            self.tab_view.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Solo pestañas básicas
            basic_tabs = ["Dashboard", "Chat", "Sessions", "Progress"]
            for tab_name in basic_tabs:
                self.tab_view.add(tab_name)
            
            # Contenido básico
            self._setup_dashboard_tab(components)
            self._setup_chat_tab(components)
            
        except Exception as e:
            self.logger.error(f"Error creando TabView básico: {e}")

    def _setup_dashboard_tab(self, components):
        """Configura el contenido del Dashboard"""
        try:
            tab = self.tab_view.tab("📊 Dashboard")
            tab.grid_columnconfigure(0, weight=1)
            
            # Título de bienvenida
            welcome_label = ctk.CTkLabel(
                tab,
                text="Welcome to your Medical Command Center",
                font=self.typography.get_font("heading_24_bold"),
                text_color=self.colors.TEXT_DARK
            )
            welcome_label.grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")
            
            # Descripción
            desc_label = ctk.CTkLabel(
                tab,
                text="Here's a summary of your study progress and quick actions to get started.",
                font=self.typography.get_font("body_15_normal"),
                text_color=self.colors.TEXT_MEDIUM
            )
            desc_label.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="w")
            
            # Tarjetas de estadísticas (si disponible)
            if components['cards']:
                self._create_stats_cards(tab, components)
            else:
                self._create_simple_stats(tab)
                
        except Exception as e:
            self.logger.error(f"Error configurando dashboard: {e}")

    def _create_stats_cards(self, tab, components):
        """Crea tarjetas de estadísticas"""
        try:
            MedicalStatsCard = components['cards'][0]
            
            stats_frame = ctk.CTkFrame(tab, fg_color="transparent")
            stats_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
            stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            # Crear tarjetas
            stats_data = [
                ("Sessions", "12", "📖", self.colors.PRIMARY_BLUE),
                ("Hours Studied", "4.5h", "⏱️", self.colors.ACCENT_TURQUOISE),
                ("MedCards", "128", "🎴", self.colors.SUCCESS_GREEN),
                ("Current Streak", "8 days", "🔥", self.colors.WARNING_AMBER)
            ]
            
            for i, (title, value, icon, color) in enumerate(stats_data):
                card = MedicalStatsCard(
                    stats_frame, title, value, icon, color, self.typography
                )
                card.grid(row=0, column=i, padx=10, sticky="nsew")
                
        except Exception as e:
            self.logger.error(f"Error creando tarjetas: {e}")
            self._create_simple_stats(tab)

    def _create_simple_stats(self, tab):
        """Crea estadísticas simples como fallback"""
        stats_frame = ctk.CTkFrame(tab)
        stats_frame.grid(row=2, column=0, padx=25, pady=15, sticky="ew")
        
        stats_text = """📊 Estadísticas de Estudio

📖 Sesiones completadas: 12
⏱️ Horas estudiadas: 4.5h
🎴 Tarjetas MedCards: 128
🔥 Racha actual: 8 días

🎯 ¡Excelente progreso! Continúa con tu plan de estudio."""
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=self.typography.get_font("body_14_normal"),
            justify="left"
        )
        stats_label.pack(padx=20, pady=20)

    def _setup_chat_tab(self, components):
        """Configura la pestaña de chat"""
        try:
            tab = self.tab_view.tab("💬 Chat")
            
            if components['chat']:
                # Chat tutor completo
                try:
                    self.chat_panel = components['chat'](
                        tab, 
                        self.config, 
                        db_manager=None,  # Se inicializará después
                        app_colors={
                            "BACKGROUND_COLOR": self.colors.BACKGROUND_CREAM,
                            "TEXT_COLOR": self.colors.TEXT_DARK,
                            "PRIMARY_COLOR": self.colors.PRIMARY_BLUE,
                            "ACCENT_COLOR": self.colors.ACCENT_TURQUOISE
                        }
                    )
                    self.chat_panel.pack(expand=True, fill="both", padx=10, pady=10)
                    
                except Exception as e:
                    self.logger.error(f"Error creando chat panel: {e}")
                    self._create_simple_chat(tab)
            else:
                self._create_simple_chat(tab)
                
        except Exception as e:
            self.logger.error(f"Error configurando chat: {e}")
            # Verificar si el tab existe antes de crear chat simple
            try:
                self._create_simple_chat(tab)
            except:
                pass

    def _create_simple_chat(self, tab):
        """Crea interfaz de chat simple como fallback"""
        # Título
        title_label = ctk.CTkLabel(
            tab,
            text="💬 Chat con IA Médica",
            font=self.typography.get_font("heading_20_bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Área de mensajes
        self.chat_area = ctk.CTkScrollableFrame(tab)
        self.chat_area.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Mensaje inicial
        welcome_frame = ctk.CTkFrame(self.chat_area)
        welcome_frame.pack(fill="x", padx=10, pady=10)
        
        welcome_text = """🤖 Asistente Médico IA

¡Hola! Soy tu asistente de estudio médico. 

✅ La aplicación está funcionando correctamente
⚠️ Para chat completo con IA, asegúrate de que:
• Ollama esté instalado y corriendo (ollama serve)
• El modelo phi3:mini esté descargado (ollama pull phi3:mini)

💡 Alternativamente, usa: python main.py --web"""
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text=welcome_text,
            font=self.typography.get_font("body_14_normal"),
            justify="left"
        )
        welcome_label.pack(padx=15, pady=15)
        
        # Área de entrada simple
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Escribe tu pregunta médica...",
            height=40
        )
        self.message_entry.pack(side="left", expand=True, fill="x", padx=(10, 5), pady=10)
        
        send_button = ctk.CTkButton(
            input_frame,
            text="Enviar",
            command=self._send_simple_message,
            width=100
        )
        send_button.pack(side="right", padx=(5, 10), pady=10)

    def _send_simple_message(self):
        """Maneja envío de mensaje simple"""
        message = self.message_entry.get().strip()
        if not message:
            return
        
        # Limpiar entrada
        self.message_entry.delete(0, 'end')
        
        # Mostrar mensaje en chat
        msg_frame = ctk.CTkFrame(self.chat_area)
        msg_frame.pack(fill="x", padx=10, pady=5)
        
        user_label = ctk.CTkLabel(
            msg_frame,
            text=f"👤 Tú: {message}",
            font=self.typography.get_font("body_14_normal"),
            anchor="w"
        )
        user_label.pack(fill="x", padx=10, pady=5)
        
        # Respuesta del bot
        response_text = """🤖 Para chat interactivo completo, necesitas:

1. Instalar Ollama: https://ollama.ai
2. Ejecutar: ollama serve
3. Descargar modelo: ollama pull phi3:mini
4. Reiniciar la aplicación

💡 Alternativamente: python main.py --web"""
        
        bot_label = ctk.CTkLabel(
            msg_frame,
            text=response_text,
            font=self.typography.get_font("body_14_normal"),
            anchor="w",
            justify="left"
        )
        bot_label.pack(fill="x", padx=10, pady=5)

    def _setup_sessions_tab(self, components):
        """Configura la pestaña de sesiones"""
        try:
            tab = self.tab_view.tab("📖 Sessions")
            
            # Crear contenido básico para sessions
            title_label = ctk.CTkLabel(
                tab,
                text="📖 Study Sessions",
                font=self.typography.get_font("heading_24_bold")
            )
            title_label.pack(pady=(20, 10))
            
            info_text = """🎯 Sesiones de Estudio Estructuradas

• Sesiones de 45 minutos con Active Recall
• Timer Pomodoro integrado
• Generación automática de contenido
• Seguimiento de progreso

🚧 Esta funcionalidad se está desarrollando.
💡 Por ahora, usa el chat para consultas médicas."""
            
            info_label = ctk.CTkLabel(
                tab,
                text=info_text,
                font=self.typography.get_font("body_14_normal"),
                justify="left"
            )
            info_label.pack(padx=20, pady=20)
            
        except Exception as e:
            self.logger.error(f"Error configurando sessions: {e}")

    def _setup_progress_tab(self, components):
        """Configura la pestaña de progreso"""
        try:
            tab = self.tab_view.tab("📈 Progress")
            
            # Título
            title_label = ctk.CTkLabel(
                tab,
                text="📈 Progress Analysis",
                font=self.typography.get_font("heading_24_bold")
            )
            title_label.pack(pady=(20, 10))
            
            # Progreso simple
            progress_text = """📊 Análisis de Progreso Cognitivo

🎯 Retención General: 82%
💓 Cardiología: 65% 
🫘 Nefrología: 91%

📈 Tendencias:
• Mejora constante en conceptos básicos
• Excelente progreso en casos clínicos
• Necesita refuerzo en farmacología

🎯 Recomendaciones:
• Continúa con sesiones regulares
• Enfócate en áreas de menor puntuación
• Usa Active Recall más frecuentemente"""
            
            progress_label = ctk.CTkLabel(
                tab,
                text=progress_text,
                font=self.typography.get_font("body_14_normal"),
                justify="left"
            )
            progress_label.pack(padx=20, pady=20)
            
        except Exception as e:
            self.logger.error(f"Error configurando progress: {e}")

    def _setup_placeholder_tabs(self):
        """Configura pestañas placeholder"""
        placeholders = [
            ("📋 Planner", "Retrospective Study Planner", 
             "Planifica tu estudio basándote en lo que NO sabes."),
            ("🧪 Exams", "Adaptive Exam Generator", 
             "Genera exámenes personalizados de 45 preguntas.")
        ]
        
        for tab_name, title, description in placeholders:
            try:
                tab = self.tab_view.tab(tab_name)
                
                container = ctk.CTkFrame(tab)
                container.pack(expand=True, fill="both", padx=25, pady=25)
                
                # Título
                title_label = ctk.CTkLabel(
                    container,
                    text=f"🚧 {title}",
                    font=self.typography.get_font("heading_20_bold")
                )
                title_label.pack(pady=(50, 10))
                
                # Descripción
                desc_label = ctk.CTkLabel(
                    container,
                    text=f"{description}\n\n Esta funcionalidad está en desarrollo.",
                    font=self.typography.get_font("body_14_normal"),
                    justify="center"
                )
                desc_label.pack(pady=(0, 50))
                
            except Exception as e:
                self.logger.debug(f"Error creando placeholder {tab_name}: {e}")

    def _create_status_bar(self):
        """Crea la barra de estado inferior"""
        try:
            status_frame = ctk.CTkFrame(
                self,
                height=35,
                fg_color="#F8FAFC",
                corner_radius=0,
                border_width=1,
                border_color=self.colors.BORDER_LIGHT
            )
            status_frame.pack(fill="x", side="bottom")
            status_frame.pack_propagate(False)
            
            # Información del sistema
            model_name = self.config.get('Ollama', 'model', 'phi3:mini')
            status_text = f"MedStudy Pro v1.0 | 🧠 Model: {model_name} | © 2024 Dr. Cruz Migueles"
            
            status_label = ctk.CTkLabel(
                status_frame,
                text=status_text,
                font=self.typography.get_font("code_12_normal"),
                text_color="#6B7280"
            )
            status_label.pack(side="left", padx=15, pady=7)
            
        except Exception as e:
            self.logger.error(f"Error creando status bar: {e}")

    def _create_fallback_interface(self):
        """Crea interfaz de emergencia si hay errores"""
        try:
            # Limpiar ventana
            for widget in self.winfo_children():
                widget.destroy()
            
            # Interfaz básica
            main_frame = ctk.CTkFrame(self)
            main_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Título
            title_label = ctk.CTkLabel(
                main_frame,
                text="🧠 MedStudy Pro",
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color=self.colors.PRIMARY_BLUE
            )
            title_label.pack(pady=(50, 20))
            
            # Mensaje de estado
            status_label = ctk.CTkLabel(
                main_frame,
                text="✅ Aplicación Funcionando",
                font=ctk.CTkFont(size=18),
                text_color=self.colors.SUCCESS_GREEN
            )
            status_label.pack(pady=10)
            
            # Información
            info_text = """La aplicación se ha iniciado correctamente.

Algunas funciones avanzadas pueden no estar disponibles debido a:
• Componentes UI opcionales faltantes
• Configuración de Ollama pendiente

Soluciones disponibles:
1. Usa la interfaz web: python main.py --web
2. Instala Ollama para funciones IA completas
3. Ejecuta setup: python setup.py"""
            
            info_label = ctk.CTkLabel(
                main_frame,
                text=info_text,
                font=ctk.CTkFont(size=14),
                justify="center"
            )
            info_label.pack(pady=30)
            
            # Botón para interfaz web
            web_button = ctk.CTkButton(
                main_frame,
                text="🌐 Lanzar Interfaz Web",
                command=self._launch_web_interface,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.colors.SUCCESS_GREEN,
                hover_color="#059669",
                height=50
            )
            web_button.pack(pady=20)
            
        except Exception as e:
            self.logger.critical(f"Error crítico creando interfaz de emergencia: {e}")

    def _launch_web_interface(self):
        """Lanza la interfaz web"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "gradio_launcher.py"])
            self.destroy()
        except Exception as e:
            self.logger.error(f"Error lanzando interfaz web: {e}")

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