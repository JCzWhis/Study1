"""
MedStudy Planner - Main Window SIMPLE
Versión simplificada que funciona sin dependencias complejas
"""

import customtkinter as ctk
from pathlib import Path

class PlannerMainWindow(ctk.CTk):
    """Ventana principal del planificador (versión simple)"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("🧠 MedStudy Planner - Sistema de Planificación Retrospectiva")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Colores médicos profesionales
        self.colors = {
            "primary": "#1E3A8A",
            "secondary": "#3B82F6", 
            "success": "#10B981",
            "warning": "#F59E0B",
            "background": "#F8FAFC",
            "card": "#FFFFFF",
            "text_primary": "#1F2937",
            "text_secondary": "#6B7280"
        }
        
        self.configure(fg_color=self.colors["background"])
        
        # Crear interfaz
        self._create_interface()
        
    def _create_interface(self):
        """Crea la interfaz principal"""
        
        # Header principal
        header_frame = ctk.CTkFrame(
            self,
            height=80,
            corner_radius=0,
            fg_color=self.colors["primary"]
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título en header
        title_label = ctk.CTkLabel(
            header_frame,
            text="🧠 MedStudy Planner",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(expand=True)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Sistema de Planificación Retrospectiva para Medicina",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Contenido principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid de 2 columnas
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Dashboard card
        dashboard_card = self._create_card(
            main_frame,
            "📊 Dashboard",
            "Vista general de tu progreso\n\n• 3 planes activos\n• 12 días de racha\n• 67% de progreso general\n• 8 temas pendientes hoy"
        )
        dashboard_card.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")
        
        # Plans card
        plans_card = self._create_card(
            main_frame,
            "📋 Gestión de Planes",
            "Crear y gestionar planes de estudio\n\n• Sistema retrospectivo Ali Abdaal\n• Color-coding de confianza\n• Intervalos adaptativos\n• Seguimiento detallado"
        )
        plans_card.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="nsew")
        
        # Study card
        study_card = self._create_card(
            main_frame,
            "📖 Sesiones de Estudio",
            "Estudiar con metodología científica\n\n• Timer Pomodoro (45 min)\n• Active Recall integrado\n• Quiz al finalizar\n• Chat tutor lateral"
        )
        study_card.grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="nsew")
        
        # Analytics card
        analytics_card = self._create_card(
            main_frame,
            "📈 Analytics",
            "Estadísticas y análisis\n\n• Gráficos de progreso\n• Distribución por especialidad\n• Tendencias temporales\n• Predicciones de estudio"
        )
        analytics_card.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="nsew")
        
        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer_frame.pack(fill="x", padx=20, pady=(0, 10))
        footer_frame.pack_propagate(False)
        
        status_label = ctk.CTkLabel(
            footer_frame,
            text="✅ MedStudy Planner v1.0 - Dr. Cruz Migueles | Medicina Interna y Reumatología",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        )
        status_label.pack(expand=True)
        
    def _create_card(self, parent, title: str, content: str):
        """Crea una tarjeta moderna"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=self.colors["card"]
        )
        
        # Header de la tarjeta
        header_frame = ctk.CTkFrame(card, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Contenido
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        content_label = ctk.CTkLabel(
            content_frame,
            text=content,
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"],
            justify="left",
            anchor="nw"
        )
        content_label.pack(fill="both", expand=True, anchor="nw")
        
        # Botón de acción
        action_btn = ctk.CTkButton(
            content_frame,
            text="Abrir →",
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            command=lambda: self._card_action(title)
        )
        action_btn.pack(anchor="se", pady=(10, 0))
        
        return card
    
    def _card_action(self, card_title: str):
        """Acción al hacer click en una tarjeta"""
        print(f"🚀 Navegando a: {card_title}")
        # TODO: Implementar navegación real


if __name__ == "__main__":
    app = PlannerMainWindow()
    app.mainloop()
