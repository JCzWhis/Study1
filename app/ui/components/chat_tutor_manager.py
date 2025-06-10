import customtkinter as ctk
from typing import List, Dict, Optional, Callable
import threading
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import json
import time
import logging

# Safe imports with fallbacks
try:
    from core.llm_manager import LLMManager
    LLM_MANAGER_AVAILABLE = True
except ImportError:
    LLM_MANAGER_AVAILABLE = False
    LLMManager = None

# Logging setup
logger = logging.getLogger('MedStudy.ChatTutorPanel')

class ChatTutorPanel(ctk.CTkFrame):
    """Collapsible AI Chat Tutor Panel for MedStudy Pro study sessions."""

    def __init__(self, parent, config, db_manager=None, app_colors: Optional[Dict[str, str]] = None):
        super().__init__(parent, fg_color=app_colors.get("BACKGROUND_COLOR", "#FEFCF9") if app_colors else "#FEFCF9")
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger('MedStudy.ChatTutorPanel')

        self.app_colors = app_colors or {}
        self.text_color = self.app_colors.get("TEXT_COLOR", "#1F2937")
        self.primary_color = self.app_colors.get("PRIMARY_COLOR", "#1E3A8A")
        self.accent_color = self.app_colors.get("ACCENT_COLOR", "#06B6D4")

        # LLM Manager - safe initialization
        self.llm = None
        if LLM_MANAGER_AVAILABLE and config:
            try:
                self.llm = LLMManager(config)
            except Exception as e:
                self.logger.error(f"Failed to initialize LLM Manager: {e}")

        # State
        self.chat_history: List[Dict[str, str]] = []
        self.is_generating: bool = False
        self.current_thread: Optional[threading.Thread] = None
        self.llm_status: str = "unknown"  # unknown, checking, ready, error
        self.current_study_context: Optional[str] = None

        # UI
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_ui()
        self._start_status_monitoring()
        self.logger.info("ChatTutorPanel initialized.")

    def _create_ui(self):
        """Creates the user interface for the chat panel."""
        # Header
        self._create_header()

        # Chat Area
        self._create_chat_area()

        # Quick Action Buttons (placeholder for now)
        self._create_quick_actions_area()

        # Input Area
        self._create_input_area()

        # Initial Message
        self._add_tutor_welcome_message()

    def _create_header(self):
        """Creates the header section with title and status."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="AI Chat Tutor",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.text_color
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(5,0), pady=5)

        status_display_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_display_frame.grid(row=0, column=1, sticky="e", padx=(0,5), pady=5)

        self.status_indicator = ctk.CTkLabel(
            status_display_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        self.status_indicator.pack(side="left", padx=(0, 3))

        self.status_label = ctk.CTkLabel(
            status_display_frame,
            text="Verificando...",
            font=ctk.CTkFont(size=10),
            text_color=self.text_color
        )
        self.status_label.pack(side="left")

    def _create_chat_area(self):
        """Creates the scrollable area for chat messages."""
        self.chat_area = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=6)
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,5))
        self.chat_area.grid_columnconfigure(0, weight=1)

    def _create_quick_actions_area(self):
        """Creates an area for quick action buttons."""
        self.quick_actions_frame = ctk.CTkFrame(self, fg_color="transparent", height=35)
        self.quick_actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,5))

    def _create_input_area(self):
        """Creates the message input field and send/stop buttons."""
        input_outer_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        input_outer_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_outer_frame.grid_columnconfigure(0, weight=1)

        input_inner_frame = ctk.CTkFrame(input_outer_frame, fg_color=self.app_colors.get("ACCENT_COLOR", "#E0E7FF"), corner_radius=10)
        input_inner_frame.pack(fill="x", expand=True)
        input_inner_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = ctk.CTkTextbox(
            input_inner_frame,
            height=60,
            font=ctk.CTkFont(size=12),
            text_color=self.text_color,
            placeholder_text="Pregunta al tutor médico...",
            wrap="word"
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.message_entry.bind("<Return>", self._on_enter)
        self.message_entry.bind("<Shift-Return>", lambda e: "break")

        button_frame = ctk.CTkFrame(input_inner_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="ns", padx=(5,5), pady=5)

        self.send_btn = ctk.CTkButton(
            button_frame,
            text="Enviar",
            command=self._send_message,
            width=70,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.primary_color
        )
        self.send_btn.pack(pady=(0,2))

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="Parar",
            command=self._stop_generation,
            width=70,
            height=28,
            font=ctk.CTkFont(size=11),
            state="disabled",
            fg_color="red"
        )
        self.stop_btn.pack()

    def _add_tutor_welcome_message(self):
        """Adds the initial welcome message from the AI Tutor."""
        welcome_text = """¡Hola! Soy tu Tutor Médico AI. Estoy aquí para ayudarte a:

- Entender conceptos complejos (¡pide que te lo explique como a un niño de 5 años!).
- Explorar casos clínicos.
- Aclarar terminología médica.
- Profundizar con preguntas socráticas.

¿En qué podemos enfocarnos hoy?"""
        self._add_message_to_ui("assistant", welcome_text, is_initial=True)

    def _add_message_to_ui(self, role: str, content: str, save_to_history: bool = True, is_initial: bool = False):
        """Adds a message to the chat UI."""
        # Determine alignment and colors based on role
        justify_anchor = "w" if role == "assistant" else "e"
        frame_anchor = "w" if role == "assistant" else "e"
        
        # Outer frame to control left/right alignment
        outer_msg_frame = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        outer_msg_frame.pack(fill="x", pady=(2,5))

        # Inner message bubble
        bubble_fg_color = self.app_colors.get("ACCENT_COLOR", "#06B6D4") if role == "assistant" else self.primary_color
        bubble_text_color = "white" if role == "assistant" else "white"
        
        # Adjust bubble color for assistant if accent is too dark
        if role == "assistant" and self.accent_color == "#06B6D4":
             bubble_fg_color = "#E0F7FA"
             bubble_text_color = self.text_color

        msg_bubble = ctk.CTkFrame(
            outer_msg_frame,
            fg_color=bubble_fg_color,
            corner_radius=12
        )
        
        # Pack bubble to the left or right within the outer frame
        msg_bubble.pack(anchor=frame_anchor, padx=5, pady=2, ipadx=3, ipady=3, side=tk.LEFT if role == "assistant" else tk.RIGHT)

        # Max width for bubbles
        max_bubble_width = self.chat_area.winfo_width() * 0.8 if self.chat_area.winfo_width() > 50 else 200

        # Timestamp (smaller, less prominent)
        time_str = datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(
            msg_bubble,
            text=time_str,
            font=ctk.CTkFont(size=9),
            text_color=bubble_text_color,
            anchor="e" if role == "user" else "w",
            justify="right" if role == "user" else "left"
        )
        time_label.pack(fill="x", padx=8, pady=(5,0))

        # Content Label
        content_label = ctk.CTkLabel(
            msg_bubble,
            text=content.strip(),
            font=ctk.CTkFont(size=12),
            text_color=bubble_text_color,
            justify=tk.LEFT,
            anchor="w",
            wraplength=max_bubble_width - 20
        )
        content_label.pack(fill="x", expand=True, padx=8, pady=(2,8))
        
        if save_to_history and not is_initial:
            self.chat_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })

        # Scroll to the bottom
        self.chat_area.update_idletasks()
        self.chat_area._parent_canvas.yview_moveto(1.0)

    def set_study_context(self, context_text: Optional[str]):
        """Sets the current study material context for the tutor."""
        self.current_study_context = context_text
        self.logger.info(f"Chat Tutor context updated: {context_text[:100]}..." if context_text else "Context cleared.")
        if context_text:
            self._add_message_to_ui("assistant", f"Contexto de estudio actualizado: '{context_text[:50]}...'", save_to_history=False)

    def _send_message(self, event=None):
        if self.is_generating:
            return "break"

        message_text = self.message_entry.get("1.0", "end-1c").strip()
        if not message_text:
            return "break"

        self.message_entry.delete("1.0", "end")
        self._add_message_to_ui("user", message_text)

        if self.llm_status != "ready":
            self._add_message_to_ui(
                "assistant",
                "⚠️ El Tutor AI no está listo. Verificando sistema...\n"
                "Por favor, asegúrate que Ollama esté corriendo y el modelo phi3:mini descargado.",
                save_to_history=False
            )
            self._check_llm_status_sync()
            return "break"

        self._generate_response(message_text)
        return "break"

    def _generate_response(self, user_message: str):
        """Generates response from the assistant"""
        if not self.llm:
            self._add_message_to_ui("assistant", "❌ LLM Manager no disponible. Verifica la configuración del sistema.")
            return

        self.is_generating = True
        self._set_generating_state(True)
        self._add_temp_streaming_message()

        def generation_worker():
            try:
                # Prepare messages in modern format
                messages = []
                
                # Add system prompt
                messages.append({
                    "role": "system", 
                    "content": "Eres un tutor médico profesional y amigable. Ayuda al estudiante a aprender activamente. Da pistas antes que respuestas directas. Adapta tu lenguaje al nivel de un estudiante de medicina."
                })

                if self.current_study_context:
                    messages.append({
                        "role": "system", 
                        "content": f"Considera el siguiente material de estudio actual: {self.current_study_context}"
                    })
                
                # Add recent chat history
                for msg in self.chat_history[-10:]:
                    messages.append({
                        "role": msg["role"], 
                        "content": msg["content"]
                    })
                
                # Add current user message
                messages.append({
                    "role": "user", 
                    "content": user_message
                })

                full_response_content = ""

                # Stream response
                for chunk_content in self.llm.chat(messages=messages, stream=True):
                    if not self.is_generating:
                        break
                    full_response_content += chunk_content
                    # Update UI every few characters
                    if len(full_response_content) % 20 == 0:
                        self.after(0, lambda c=full_response_content: self._update_temp_streaming_message(c))
                
                if not self.is_generating and not full_response_content:
                    full_response_content = "Generación detenida."

            except Exception as e:
                self.logger.error(f"Error during LLM generation: {e}", exc_info=True)
                full_response_content = f"❌ Error del Tutor AI: {str(e)}"
            finally:
                self.after(0, lambda: self._finalize_generation(full_response_content.strip()))

        self.current_thread = threading.Thread(target=generation_worker, daemon=True)
        self.current_thread.start()

    def _add_temp_streaming_message(self):
        """Adds a temporary message bubble for streaming content."""
        role = "assistant"
        justify_anchor = "w"
        frame_anchor = "w"
        
        outer_msg_frame = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        outer_msg_frame.pack(fill="x", pady=(2,5))

        bubble_fg_color = "#E0F7FA"
        bubble_text_color = self.text_color

        self.temp_streaming_bubble = ctk.CTkFrame(
            outer_msg_frame,
            fg_color=bubble_fg_color,
            corner_radius=12
        )
        self.temp_streaming_bubble.pack(anchor=frame_anchor, padx=5, pady=2, ipadx=3, ipady=3, side=tk.LEFT)
        
        self.temp_streaming_content_label = ctk.CTkLabel(
            self.temp_streaming_bubble,
            text="...",
            font=ctk.CTkFont(size=12),
            text_color=bubble_text_color,
            justify=tk.LEFT,
            anchor="w",
            wraplength=self.chat_area.winfo_width() * 0.8 - 20
        )
        self.temp_streaming_content_label.pack(fill="x", expand=True, padx=8, pady=(2,8))
        self.chat_area._parent_canvas.yview_moveto(1.0)

    def _update_temp_streaming_message(self, content: str):
        """Updates the content of the temporary streaming message bubble."""
        if hasattr(self, 'temp_streaming_content_label') and self.temp_streaming_content_label.winfo_exists():
            self.temp_streaming_content_label.configure(text=content + " ▌")
            self.chat_area._parent_canvas.yview_moveto(1.0)
        elif hasattr(self, 'temp_streaming_bubble') and self.temp_streaming_bubble.winfo_exists():
             self.temp_streaming_bubble.destroy()
             if hasattr(self, 'temp_streaming_content_label'):
                 delattr(self, 'temp_streaming_content_label')

    def _finalize_generation(self, final_content: str):
        """Cleans up temporary streaming messages and adds the final message."""
        # Remove temporary streaming bubble
        if hasattr(self, 'temp_streaming_bubble') and self.temp_streaming_bubble.winfo_exists():
            self.temp_streaming_bubble.destroy()
            delattr(self, 'temp_streaming_bubble')
            if hasattr(self, 'temp_streaming_content_label'):
                 delattr(self, 'temp_streaming_content_label')
        
        if final_content:
            self._add_message_to_ui("assistant", final_content)
        
        self._set_generating_state(False)
        self.message_entry.focus()

    def _set_generating_state(self, is_generating: bool):
        self.is_generating = is_generating
        if is_generating:
            self.send_btn.configure(state="disabled", text="...")
            self.stop_btn.configure(state="normal")
        else:
            self.send_btn.configure(state="normal", text="Enviar")
            self.stop_btn.configure(state="disabled")

    def _stop_generation(self):
        if self.is_generating:
            self.is_generating = False
            if self.current_thread and self.current_thread.is_alive():
                self.logger.info("Stop generation requested. Worker thread will stop on next check.")
            self._finalize_generation("⏹️ Generación detenida.")

    def _on_enter(self, event):
        # Send message on Enter unless Shift is pressed
        if not (event.state & 0x0001):  # Check for Shift key state
            self._send_message()
            return "break"
        return None

    def _start_status_monitoring(self):
        # Initial check
        self._check_llm_status_async()
        
        # Periodic check (every 30s)
        def monitor_worker():
            while True:
                time.sleep(30)
                if not self.winfo_exists():
                    break
                self._check_llm_status_async()
        
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()

    def _check_llm_status_async(self):
        threading.Thread(target=self._check_llm_status_sync, daemon=True).start()

    def _check_llm_status_sync(self):
        if not self.winfo_exists(): 
            return

        self.after(0, lambda: self._update_status_ui("checking", "Verificando..."))
        
        if not self.llm:
            self.after(0, lambda: self._update_status_ui("error", "LLM no disponible"))
            return
        
        try:
            status_details = self.llm.get_status()
            
            if status_details.get("target_model_available"):
                self.after(0, lambda: self._update_status_ui("ready", "Listo"))
            elif status_details.get("ollama_reachable"):
                self.after(0, lambda: self._update_status_ui("error", f"Modelo '{self.llm.model}' no hallado"))
            else:
                self.after(0, lambda: self._update_status_ui("error", "Ollama OFFLINE"))
        except Exception as e:
            self.after(0, lambda: self._update_status_ui("error", f"Error: {str(e)[:20]}..."))

    def _update_status_ui(self, status_key: str, message: str):
        if not self.winfo_exists(): 
            return

        self.llm_status = status_key
        color_map = {"ready": "green", "checking": "orange", "error": "red", "unknown": "grey"}
        
        self.status_indicator.configure(text_color=color_map.get(status_key, "grey"))
        self.status_label.configure(text=message)

        if not self.is_generating:
            self.send_btn.configure(state="normal" if status_key == "ready" else "disabled")

    # Public methods for interaction
    def get_chat_history(self) -> List[Dict[str, str]]:
        return self.chat_history.copy()

    def clear_chat(self):
        for widget in self.chat_area.winfo_children():
            widget.destroy()
        self.chat_history.clear()
        self._add_tutor_welcome_message()
        self.logger.info("Chat history cleared.")

    def export_chat_to_file(self, filename: str, file_format: str = "markdown"):
        try:
            if file_format == "json":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            else:  # markdown
                content = f"# Tutor Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                for msg in self.chat_history:
                    role_name = "Estudiante" if msg["role"] == "user" else "Tutor AI"
                    timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
                    content += f"**{role_name}** ({timestamp}):\n{msg['content']}\n\n---\n\n"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
            self.logger.info(f"Chat exported to {filename} in {file_format} format.")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting chat: {e}", exc_info=True)
            return False
