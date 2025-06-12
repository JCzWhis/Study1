"""
MedStudy Pro - Componentes de Tarjetas Médicas
Contiene clases de componentes reutilizables para mostrar información en tarjetas.
- MedicalStatsCard: Para estadísticas clave en el dashboard.
- MedicalTopicCard: Para mostrar temas de estudio.
- MedicalContentCard: Para presentar contenido médico generado.
"""

import customtkinter as ctk
from .medical_typography import MedicalTypography

class MedicalStatsCard(ctk.CTkFrame):
    """
    Una tarjeta para mostrar una estadística clave en el Dashboard.
    Incluye un título, un valor, y un ícono.
    """
    def __init__(self, master, title: str, value: str, icon: str, color: str, typography: MedicalTypography):
        """
        Inicializa la tarjeta de estadísticas.
        
        Args:
            master: El widget padre.
            title: El título de la estadística (ej. "Sessions").
            value: El valor de la estadística (ej. "12").
            icon: Un emoji o caracter para representar la estadística.
            color: El color para el ícono.
            typography: La instancia del gestor de tipografía.
        """
        super().__init__(master, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E5E7EB")
        
        self.typography = typography

        # Layout responsivo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(True)

        # Contenedor del ícono
        icon_frame = ctk.CTkFrame(self, fg_color=color, width=64, corner_radius=10)
        icon_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ns")
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text=icon, font=("Arial", 28)).pack(expand=True)

        # Contenedor del texto
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="ew")

        value_label = ctk.CTkLabel(
            text_frame, 
            text=value, 
            font=self.typography.get_font("display_32_bold"), 
            text_color="#1F2937"
        )
        value_label.pack(anchor="w")

        title_label = ctk.CTkLabel(
            text_frame, 
            text=title, 
            font=self.typography.get_font("body_14_normal"), 
            text_color="#6B7280"
        )
        title_label.pack(anchor="w")


class MedicalTopicCard(ctk.CTkFrame):
    """
    Una tarjeta para representar un tema de estudio en el Planner o en la lista de Sesiones.
    """
    def __init__(self, master, topic_name: str, specialty: str, progress: float, typography: MedicalTypography):
        """
        Inicializa la tarjeta de tema de estudio.

        Args:
            master: El widget padre.
            topic_name: El nombre del tema (ej. "Glomerulonefritis").
            specialty: La especialidad a la que pertenece (ej. "Nefrología").
            progress: El progreso de estudio del tema (0.0 a 1.0).
            typography: La instancia del gestor de tipografía.
        """
        super().__init__(master, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E5E7EB", height=120)
        
        self.typography = typography
        
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        # Frame superior con título y especialidad
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            top_frame, text=topic_name, font=self.typography.get_font("heading_16_bold"), text_color="#1F2937"
        ).pack(anchor="w")
        ctk.CTkLabel(
            top_frame, text=specialty.upper(), font=self.typography.get_font("caption_11_normal"), text_color="#1E3A8A"
        ).pack(anchor="w", pady=(2, 0))

        # Barra de progreso
        progress_bar = ctk.CTkProgressBar(
            self,
            fg_color="#E5E7EB",
            progress_color="#10B981",
            height=8,
            corner_radius=4
        )
        progress_bar.set(progress)
        progress_bar.pack(fill="x", padx=20, pady=10)

        # Botón de acción
        action_button = ctk.CTkButton(
            self,
            text="Estudiar Tema",
            font=self.typography.get_font("button_13_bold"),
            height=30
        )
        action_button.pack(anchor="e", padx=20, pady=(0, 15))


class MedicalContentCard(ctk.CTkFrame):
    """
    Una tarjeta diseñada para mostrar contenido médico generado por la IA.
    Incluye un título, un área de contenido desplazable y acciones.
    """
    def __init__(self, master, title: str, content: str, typography: MedicalTypography):
        """
        Inicializa la tarjeta de contenido.

        Args:
            master: El widget padre.
            title: El título del contenido (ej. "Fisiopatología de la Anemia Ferropénica").
            content: El texto generado por la IA.
            typography: La instancia del gestor de tipografía.
        """
        super().__init__(master, fg_color="#F8FAFC", corner_radius=12, border_width=1, border_color="#E5E7EB")

        self.typography = typography

        # Título
        ctk.CTkLabel(
            self, text=title, font=self.typography.get_font("heading_18_bold"), text_color="#1F2937"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Área de texto con scroll
        text_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        text_frame.pack(expand=True, fill="both", padx=20, pady=5)
        
        textbox = ctk.CTkTextbox(
            text_frame,
            font=self.typography.get_font("body_15_normal"),
            text_color="#374151",
            wrap="word",
            activate_scrollbars=True,
            fg_color="transparent"
        )
        textbox.insert("1.0", content)
        textbox.configure(state="disabled") # Hacerlo de solo lectura
        textbox.pack(expand=True, fill="both", padx=10, pady=10)

        # Barra de acciones inferior
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(10, 15))
        
        ctk.CTkButton(
            action_bar, text="➕ Añadir a MedCards", font=self.typography.get_font("button_13_bold"), height=30
        ).pack(side="left")
        ctk.CTkButton(
            action_bar, text="✅ Marcar como Aprendido", fg_color="#10B981", hover_color="#059669", 
            font=self.typography.get_font("button_13_bold"), height=30
        ).pack(side="right")