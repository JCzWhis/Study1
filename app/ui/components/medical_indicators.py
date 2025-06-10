"""
MedStudy Pro - Componentes de Indicadores Médicos
Contiene clases de componentes reutilizables para indicadores visuales.
- SystemStatusIndicator: Para mostrar el estado de la conexión con la IA.
- MedicalLoadingSpinner: Un spinner de carga profesional.
- MedicalProgressRing: Un anillo de progreso circular estilo Apple/médico.
"""

import customtkinter as ctk
import tkinter as tk
import math
from .medical_typography import MedicalTypography

class SystemStatusIndicator(ctk.CTkFrame):
    """
    Un indicador de estado para el sistema Ollama/IA con colores médicos.
    """
    def __init__(self, master, typography: MedicalTypography, is_active: bool = False):
        """
        Inicializa el indicador de estado.

        Args:
            master: El widget padre.
            typography: Instancia del gestor de tipografía.
            is_active: El estado inicial del sistema.
        """
        super().__init__(master, fg_color="transparent")
        self.typography = typography
        
        self.status_dot = ctk.CTkLabel(self, text="●", font=("Arial", 18))
        self.status_dot.pack(side="left", padx=(0, 8), pady=2)
        
        self.status_label = ctk.CTkLabel(self, font=self.typography.get_font("button_13_bold"))
        self.status_label.pack(side="left")
        
        self.set_status(is_active)

    def set_status(self, is_active: bool):
        """Actualiza el color y texto del indicador basado en el estado."""
        if is_active:
            color = "#10B981"  # SUCCESS_GREEN
            text = "Sistema Activo"
            text_color = "#FFFFFF"
        else:
            color = "#EF4444"  # ERROR_RED
            text = "IA Offline"
            text_color = "#FEE2E2"
        
        self.status_dot.configure(text_color=color)
        self.status_label.configure(text=text, text_color=text_color)


class MedicalLoadingSpinner(ctk.CTkFrame):
    """
    Un spinner profesional de carga para indicar actividad.
    """
    def __init__(self, master, typography: MedicalTypography):
        super().__init__(master, fg_color="transparent")
        
        self.spinner_chars = ["|", "/", "—", "\\"]
        self.spinner_index = 0
        
        self.spinner_label = ctk.CTkLabel(self, text="", font=typography.get_font("heading_20_bold"), text_color="#1E3A8A")
        self.spinner_label.pack(pady=10)
        
        self.loading_text = ctk.CTkLabel(self, text="Generando contenido...", font=typography.get_font("body_14_normal"), text_color="#4B5563")
        self.loading_text.pack(pady=5)
        
        self.is_spinning = False

    def start(self):
        """Comienza la animación del spinner."""
        self.is_spinning = True
        self._animate()

    def stop(self):
        """Detiene la animación del spinner."""
        self.is_spinning = False
        self.spinner_label.configure(text="✅")
        self.loading_text.configure(text="Contenido generado.")

    def _animate(self):
        """Función interna para el bucle de animación."""
        if self.is_spinning:
            self.spinner_label.configure(text=self.spinner_chars[self.spinner_index])
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            self.after(150, self._animate)


class MedicalProgressRing(ctk.CTkFrame):
    """
    Un anillo de progreso circular para mostrar porcentajes de manera visual.
    Utiliza un Canvas de tkinter para el dibujo.
    """
    def __init__(self, master, size: int = 120, progress: int = 0, typography: MedicalTypography = None):
        super().__init__(master, fg_color="transparent")
        
        self.size = size
        self.progress = progress
        self.typography = typography if typography else MedicalTypography()

        self.canvas = tk.Canvas(self, width=self.size, height=self.size, bg="#FEFCF9", highlightthickness=0)
        self.canvas.pack()

        self.text_label = ctk.CTkLabel(
            self.canvas,
            text="",
            font=self.typography.get_font("heading_20_bold"),
            fg_color="transparent",
            text_color="#1E3A8A"
        )
        self.text_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.draw_progress()

    def draw_progress(self):
        """Dibuja y actualiza el anillo de progreso."""
        self.canvas.delete("all")
        
        # Geometría y padding
        padding = self.size * 0.1
        line_width = self.size * 0.08
        
        # Dibuja el arco de fondo
        self.canvas.create_arc(
            padding, padding, self.size - padding, self.size - padding,
            start=90, extent=359.9,
            style="arc",
            outline="#E5E7EB", # BORDER_SOFT
            width=line_width
        )
        
        # Dibuja el arco de progreso
        extent = self.progress * 3.6
        self.canvas.create_arc(
            padding, padding, self.size - padding, self.size - padding,
            start=90, extent=-extent, # Negativo para ir en sentido horario desde arriba
            style="arc",
            outline="#10B981", # SUCCESS_GREEN
            width=line_width
        )
        
        # Actualiza el texto
        self.text_label.configure(text=f"{self.progress}%")
        self.text_label.lift()

    def set(self, value: int):
        """
        Establece un nuevo valor de progreso.
        
        Args:
            value: El nuevo valor de progreso (0-100).
        """
        self.progress = max(0, min(100, value))
        self.draw_progress()