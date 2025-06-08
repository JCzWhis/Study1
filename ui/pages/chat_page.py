"""
Página de chat mejorada con manejo robusto de errores para Ollama
"""
import customtkinter as ctk
from typing import List, Dict, Optional
import threading
import tkinter as tk
from datetime import datetime
import json
import time

from core.llm_manager import LLMManager
from utils.logging import get_logger

class ChatPage(ctk.CTkFrame):
    """Página de chat con manejo robusto de errores"""

    def __init__(self, parent, config, db_manager):
        super().__init__(parent)
        self.config = config
        self.db_manager = db_manager
        self.logger = get_logger("ChatPage")

        # LLM Manager
        self.llm = LLMManager(config)

        # Estado
        self.chat_history = []
        self.is_generating = False
        self.current_thread = None
        self.llm_status = "unknown"  # unknown, checking, ready, error

        # UI
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_ui()
        self._start_status_monitoring()

    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Header con estado
        self._create_header()

        # Área de chat
        self._create_chat_area()

        # Área de entrada
        self._create_input_area()

        # Mostrar mensaje inicial
        self._add_welcome_message()

    def _create_header(self):
        """Header con indicador de estado"""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)

        # Título
        title = ctk.CTkLabel(
            header,
            text="💬 Chat con IA Médica",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=15)

        # Estado del sistema
        self.status_frame = ctk.CTkFrame(header)
        self.status_frame.grid(row=0, column=2, sticky="e", padx=15, pady=10)

        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color="orange"
        )
        self.status_indicator.pack(side="left", padx=(10, 5))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Verificando sistema...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=(0, 10))

        # Botón diagnóstico
        self.diagnostic_btn = ctk.CTkButton(
            header,
            text="🔧 Diagnóstico",
            command=self._run_diagnostic,
            width=100,
            height=30
        )
        self.diagnostic_btn.grid(row=0, column=3, sticky="e", padx=(5, 15), pady=15)

    def _create_chat_area(self):
        """Área principal del chat"""
        # Scrollable frame para mensajes
        self.chat_area = ctk.CTkScrollableFrame(self)
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.chat_area.grid_columnconfigure(0, weight=1)

    def _create_input_area(self):
        """Área de entrada de mensajes"""
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        input_frame.grid_columnconfigure(0, weight=1)

        # Frame interior
        inner_frame = ctk.CTkFrame(input_frame)
        inner_frame.pack(fill="x", padx=10, pady=10)
        inner_frame.grid_columnconfigure(0, weight=1)

        # Campo de texto
        self.message_entry = ctk.CTkTextbox(
            inner_frame,
            height=80,
            font=ctk.CTkFont(size=13),
            placeholder_text="Escribe tu pregunta médica aquí..."
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Botones
        button_frame = ctk.CTkFrame(inner_frame)
        button_frame.grid(row=0, column=1, sticky="ns")

        self.send_btn = ctk.CTkButton(
            button_frame,
            text="✉️ Enviar",
            command=self._send_message,
            width=100,
            height=35
        )
        self.send_btn.pack(pady=(0, 5))

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹️ Detener",
            command=self._stop_generation,
            width=100,
            height=30,
            state="disabled",
            fg_color="red"
        )
        self.stop_btn.pack()

        # Bind Enter
        self.message_entry.bind("<Return>", self._on_enter)
        self.message_entry.bind("<Shift-Return>", lambda e: None)

    def _add_welcome_message(self):
        """Mensaje de bienvenida"""
        welcome_text = """¡Hola! Soy tu asistente de estudio médico con IA.

Puedo ayudarte con:
• Explicar conceptos médicos complejos
• Crear casos clínicos para practicar
• Generar tarjetas de estudio Anki
• Resolver dudas sobre diagnósticos
• Proporcionar diagnósticos diferenciales
• Información sobre fármacos y tratamientos

💡 **Tip**: Si ves problemas de conexión, usa el botón "Diagnóstico" para verificar el sistema."""

        self._add_message("assistant", welcome_text)

    def _add_message(self, role: str, content: str, save: bool = True):
        """Añade un mensaje al chat"""
        msg_frame = ctk.CTkFrame(self.chat_area)
        msg_frame.pack(fill="x", padx=10, pady=5)
        msg_frame.grid_columnconfigure(0, weight=1)

        # Header del mensaje
        header_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))

        # Icono y nombre
        icon = "👤" if role == "user" else "🤖"
        name = "Tú" if role == "user" else "Asistente IA"
        color = ("blue", "lightblue") if role == "user" else ("green", "lightgreen")

        name_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color
        )
        name_label.pack(side="left")

        # Timestamp
        time_label = ctk.CTkLabel(
            header_frame,
            text=datetime.now().strftime("%H:%M:%S"),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        time_label.pack(side="right")

        # Contenido
        content_label = ctk.CTkLabel(
            msg_frame,
            text=content,
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w",
            wraplength=800
        )
        content_label.pack(fill="x", padx=15, pady=(0, 15))

        # Guardar en historial
        if save:
            self.chat_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })

        # Scroll al final
        self.chat_area.update_idletasks()
        self.chat_area._parent_canvas.yview_moveto(1.0)

    def _send_message(self):
        """Envía mensaje al asistente"""
        if self.is_generating:
            return

        message = self.message_entry.get("1.0", "end-1c").strip()
        if not message:
            return

        # Limpiar entrada
        self.message_entry.delete("1.0", "end")

        # Añadir mensaje del usuario
        self._add_message("user", message)

        # Verificar estado del LLM antes de enviar
        if self.llm_status != "ready":
            self._add_message(
                "assistant",
                "⚠️ El sistema de IA no está listo. Iniciando verificación automática...\n\n"
                "Si el problema persiste, puedes:\n"
                "1. Usar el botón 'Diagnóstico' para verificar el sistema\n"
                "2. Asegurar que Ollama esté instalado y corriendo\n"
                "3. Verificar que el modelo phi3:mini esté descargado"
            )
            self._check_llm_status_sync()
            return

        # Generar respuesta
        self._generate_response(message)

    def _generate_response(self, message: str):
        """Genera respuesta del asistente"""
        def generation_worker():
            try:
                # Cambiar estado
                self.after(0, lambda: self._set_generating_state(True))

                # Preparar contexto
                context = []
                for msg in self.chat_history[-6:]:  # Últimos 3 intercambios
                    context.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

                # Generar respuesta
                response = ""
                try:
                    for chunk in self.llm.chat(message, context, stream=True):
                        if not self.is_generating:  # Verificar si se detuvo
                            break
                        response += chunk
                        # Actualizar UI (simplificado para evitar problemas)
                        if len(response) % 20 == 0:  # Actualizar cada 20 caracteres
                            self.after(0, lambda r=response: self._update_temp_message(r))

                except Exception as e:
                    error_msg = self._format_error_message(str(e))
                    response = error_msg

                # Finalizar
                self.after(0, lambda: self._finish_generation(response))

            except Exception as e:
                self.logger.error(f"Error en generation_worker: {e}")
                error_msg = f"❌ Error inesperado: {str(e)}"
                self.after(0, lambda: self._finish_generation(error_msg))

        # Ejecutar en thread separado
        self.current_thread = threading.Thread(target=generation_worker, daemon=True)
        self.current_thread.start()

    def _format_error_message(self, error: str) -> str:
        """Formatea mensajes de error de manera amigable"""
        error_lower = error.lower()

        if "connection refused" in error_lower or "ollama no está corriendo" in error_lower:
            return """❌ **No se puede conectar con Ollama**

🔧 **Soluciones:**
1. Abre una terminal/cmd
2. Ejecuta: `ollama serve`
3. Mantén la terminal abierta
4. Intenta de nuevo

💡 También puedes usar el botón 'Diagnóstico' para verificar el sistema."""

        elif "model not found" in error_lower or "modelo no disponible" in error_lower:
            return """❌ **Modelo phi3:mini no encontrado**

🔧 **Solución:**
1. Abre una terminal/cmd
2. Ejecuta: `ollama pull phi3:mini`
3. Espera a que termine la descarga (~2GB)
4. Intenta de nuevo

💡 El modelo se descarga solo una vez."""

        elif "timeout" in error_lower:
            return """⏰ **Timeout - El modelo tardó demasiado**

🔧 **Posibles causas:**
- El modelo está sobrecargado
- Tu pregunta es muy compleja
- Recursos del sistema limitados

💡 Intenta con una pregunta más simple o espera un momento."""

        elif "ollama no está listo" in error_lower:
            return """⚠️ **Sistema no está listo**

🔧 **Verificando automáticamente...**
El sistema intentará resolver el problema. Si persiste:

1. Usa el botón 'Diagnóstico'
2. Verifica que Ollama esté instalado
3. Asegúrate de que el servicio esté corriendo"""

        else:
            return f"""❌ **Error técnico**

Detalles: {error}

🔧 **Sugerencias:**
1. Usa el botón 'Diagnóstico' para verificar el sistema
2. Revisa que Ollama esté corriendo: `ollama serve`
3. Si el problema persiste, reinicia la aplicación"""

    def _set_generating_state(self, generating: bool):
        """Cambia el estado de generación"""
        self.is_generating = generating

        if generating:
            self.send_btn.configure(state="disabled", text="⏳ Generando...")
            self.stop_btn.configure(state="normal")
            self._add_temp_message()
        else:
            self.send_btn.configure(state="normal", text="✉️ Enviar")
            self.stop_btn.configure(state="disabled")

    def _add_temp_message(self):
        """Añade mensaje temporal para mostrar generación"""
        self.temp_msg_frame = ctk.CTkFrame(self.chat_area)
        self.temp_msg_frame.pack(fill="x", padx=10, pady=5)

        # Header
        header = ctk.CTkFrame(self.temp_msg_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        name_label = ctk.CTkLabel(
            header,
            text="🤖 Asistente IA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("green", "lightgreen")
        )
        name_label.pack(side="left")

        # Contenido temporal
        self.temp_content_label = ctk.CTkLabel(
            self.temp_msg_frame,
            text="🤔 Pensando...",
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w"
        )
        self.temp_content_label.pack(fill="x", padx=15, pady=(0, 15))

    def _update_temp_message(self, content: str):
        """Actualiza el mensaje temporal"""
        if hasattr(self, 'temp_content_label'):
            # Mostrar solo los primeros 500 caracteres + indicador
            display_content = content[:500]
            if len(content) > 500:
                display_content += "... ⏳"
            else:
                display_content += " ▌"  # Cursor

            self.temp_content_label.configure(text=display_content)
            self.chat_area._parent_canvas.yview_moveto(1.0)

    def _finish_generation(self, final_content: str):
        """Finaliza la generación"""
        # Eliminar mensaje temporal
        if hasattr(self, 'temp_msg_frame'):
            self.temp_msg_frame.destroy()
            delattr(self, 'temp_msg_frame')

        # Añadir mensaje final
        self._add_message("assistant", final_content)

        # Restaurar estado
        self._set_generating_state(False)

        # Enfocar entrada
        self.message_entry.focus()

    def _stop_generation(self):
        """Detiene la generación actual"""
        self.is_generating = False
        self._finish_generation("⏹️ Generación detenida por el usuario.")

    def _on_enter(self, event):
        """Maneja Enter en el campo de entrada"""
        if not (event.state & 0x0001):  # Sin Shift
            self._send_message()
            return "break"

    def _start_status_monitoring(self):
        """Inicia monitoreo del estado del LLM"""
        def monitor_worker():
            while True:
                try:
                    self._check_llm_status_sync()
                    time.sleep(30)  # Verificar cada 30 segundos
                except Exception as e:
                    self.logger.error(f"Error en monitor: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()

        # Verificación inicial
        self._check_llm_status_async()

    def _check_llm_status_async(self):
        """Verifica estado del LLM de forma asíncrona"""
        def check_worker():
            self._check_llm_status_sync()

        threading.Thread(target=check_worker, daemon=True).start()

    def _check_llm_status_sync(self):
        """Verifica estado del LLM sincrónicamente"""
        try:
            self.after(0, lambda: self._update_status("checking", "Verificando sistema..."))

            # Verificar disponibilidad
            if self.llm.is_available():
                # Verificar que esté completamente listo
                if self.llm.ensure_ready():
                    self.after(0, lambda: self._update_status("ready", "Sistema listo"))
                else:
                    self.after(0, lambda: self._update_status("error", "Sistema no listo"))
            else:
                self.after(0, lambda: self._update_status("error", "Ollama no disponible"))

        except Exception as e:
            self.logger.error(f"Error verificando estado: {e}")
            self.after(0, lambda: self._update_status("error", f"Error: {str(e)[:30]}..."))

    def _update_status(self, status: str, message: str):
        """Actualiza el indicador de estado"""
        self.llm_status = status

        # Colores por estado
        colors = {
            "ready": "green",
            "checking": "orange",
            "error": "red",
            "unknown": "gray"
        }

        self.status_indicator.configure(text_color=colors.get(status, "gray"))
        self.status_label.configure(text=message)

        # Habilitar/deshabilitar envío
        if status == "ready":
            self.send_btn.configure(state="normal" if not self.is_generating else "disabled")
        else:
            if not self.is_generating:
                self.send_btn.configure(state="disabled")

    def _run_diagnostic(self):
        """Ejecuta diagnóstico del sistema"""
        def diagnostic_worker():
            try:
                self.after(0, lambda: self._update_status("checking", "Ejecutando diagnóstico..."))

                # Obtener estado detallado
                status = self.llm.get_status()

                # Formatear reporte
                report = self._format_diagnostic_report(status)

                # Mostrar en chat
                self.after(0, lambda: self._add_message("assistant", report, save=False))

                # Actualizar estado
                if status.get("ready", False):
                    self.after(0, lambda: self._update_status("ready", "Sistema listo"))
                else:
                    self.after(0, lambda: self._update_status("error", "Problemas detectados"))

            except Exception as e:
                error_report = f"❌ **Error en diagnóstico**: {str(e)}"
                self.after(0, lambda: self._add_message("assistant", error_report, save=False))
                self.after(0, lambda: self._update_status("error", "Error en diagnóstico"))

        threading.Thread(target=diagnostic_worker, daemon=True).start()

    def _format_diagnostic_report(self, status: Dict) -> str:
        """Formatea el reporte de diagnóstico"""
        report = "🔍 **REPORTE DE DIAGNÓSTICO**\n\n"

        # Estado general
        if status.get("ready", False):
            report += "✅ **Estado general**: Sistema funcionando correctamente\n\n"
        else:
            report += "❌ **Estado general**: Problemas detectados\n\n"

        # Detalles de Ollama
        ollama_status = status.get("ollama_status", {}).get("ollama", {})

        report += "**Ollama:**\n"
        report += f"- Instalado: {'✅' if ollama_status.get('installed') else '❌'}\n"
        report += f"- Servicio corriendo: {'✅' if ollama_status.get('running') else '❌'}\n"
        report += f"- Modelo disponible: {'✅' if ollama_status.get('model_available') else '❌'}\n"

        models = ollama_status.get('models', [])
        if models:
            report += f"- Modelos instalados: {', '.join(models)}\n"

        # Proceso
        process_info = status.get("ollama_status", {}).get("process", {})
        if process_info.get("pid"):
            report += f"- PID del proceso: {process_info['pid']}\n"
            report += f"- Proceso activo: {'✅' if process_info.get('alive') else '❌'}\n"

        # Recomendaciones
        report += "\n**Recomendaciones:**\n"

        if not ollama_status.get('installed'):
            report += "1. Instala Ollama desde https://ollama.ai\n"

        if not ollama_status.get('running'):
            report += "2. Ejecuta en terminal: `ollama serve`\n"

        if not ollama_status.get('model_available'):
            report += "3. Descarga el modelo: `ollama pull phi3:mini`\n"

        if status.get("ready"):
            report += "🎉 ¡Todo está funcionando correctamente!"

        return report

    def get_chat_history(self) -> List[Dict]:
        """Obtiene el historial del chat"""
        return self.chat_history.copy()

    def clear_chat(self):
        """Limpia el chat"""
        # Limpiar mensajes
        for widget in self.chat_area.winfo_children():
            widget.destroy()

        # Limpiar historial
        self.chat_history.clear()

        # Mensaje de bienvenida
        self._add_welcome_message()

    def export_chat(self, filename: str, format: str = "markdown"):
        """Exporta el historial del chat"""
        try:
            if format == "json":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            else:  # markdown
                content = "# Chat - MedStudy Pro\n\n"
                for msg in self.chat_history:
                    role = "**Usuario**" if msg["role"] == "user" else "**Asistente**"
                    timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    content += f"{role} - {timestamp}\n\n{msg['content']}\n\n---\n\n"

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)

            return True
        except Exception as e:
            self.logger.error(f"Error exportando chat: {e}")
            return False
