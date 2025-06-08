"""
Interfaz moderna para MedStudy Pro usando Gradio
Gradio es perfecto para aplicaciones de IA, muy visual y moderno
"""
import gradio as gr
import json
from datetime import datetime
from typing import List, Dict, Optional

# Importar nuestros módulos
from core.llm_manager import LLMManager
from core.anki_system import create_anki_system, ReviewResult
from core.rag_engine import RAGEngine
from data.database import DatabaseManager
# utils.config.ConfigManager likely needs to be imported from utils.config
# Assuming it's a class named ConfigManager in utils/config.py
from utils.config import ConfigManager # Corrected import

class MedStudyGradioApp:
    """Aplicación MedStudy Pro con interfaz Gradio moderna"""

    def __init__(self):
        # Inicializar sistema
        self.config = ConfigManager()
        self.db = DatabaseManager(self.config)
        self.llm = LLMManager(self.config)

        # Sistemas principales
        anki_system = create_anki_system(self.db, self.llm)
        self.card_manager = anki_system['card_manager']
        self.anki_ui = anki_system['ui']
        self.rag_engine = RAGEngine(self.db, self.llm, self.config)

        # Estado de la interfaz
        self.current_card = None
        self.chat_history = []

    def chat_with_ai(self, message: str, history: List) -> tuple:
        """Chat con IA médica"""
        if not message.strip():
            return history, ""

        # Agregar mensaje del usuario
        history.append([message, None])

        try:
            # Generar respuesta con RAG
            rag_response = self.rag_engine.generate_answer(message)
            response = rag_response.generated_response

            # Agregar información de fuentes si las hay
            if rag_response.sources:
                sources_info = f"\n\n📚 **Fuentes consultadas:** {len(rag_response.sources)} documentos"
                response += sources_info

            # Actualizar historial
            history[-1][1] = response

        except Exception as e:
            error_response = f"❌ Error: {str(e)}\n\nIntenta verificar que Ollama esté funcionando."
            history[-1][1] = error_response

        return history, ""

    def generate_anki_card(self, topic: str, difficulty: str) -> tuple:
        """Genera una tarjeta Anki sobre un tema"""
        if not topic.strip():
            return "❌ Por favor ingresa un tema", "", "", ""

        try:
            card_id = self.card_manager.generate_card_with_ai(topic, difficulty)

            if card_id:
                card = self.db.get_anki_card(card_id)
                return (
                    f"✅ Tarjeta generada exitosamente sobre: {topic}",
                    card.question,
                    card.answer,
                    f"Tema: {card.topic} | Dificultad: {card.difficulty}"
                )
            else:
                return "❌ No se pudo generar la tarjeta", "", "", ""

        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""

    def start_study_session(self) -> tuple:
        """Inicia sesión de estudio"""
        try:
            if self.anki_ui.start_study_session():
                card_info = self.anki_ui.get_current_card()
                if card_info:
                    self.current_card = card_info
                    return (
                        f"📚 Sesión iniciada - {card_info['progress']}",
                        card_info['question'],
                        "¿Sabes la respuesta? Haz clic en 'Mostrar Respuesta'",
                        gr.update(visible=True),  # Mostrar botón respuesta
                        gr.update(visible=False), # Ocultar botones de evaluación
                        gr.update(visible=True)   # Mostrar botón mostrar respuesta
                    )

            return (
                "ℹ️ No hay tarjetas para estudiar",
                "No hay tarjetas pendientes de revisión.",
                "Puedes generar nuevas tarjetas en la pestaña de creación.",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False)
            )

        except Exception as e:
            return (
                f"❌ Error: {str(e)}",
                "",
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False)
            )

    def show_answer(self) -> tuple:
        """Muestra la respuesta de la tarjeta actual"""
        if self.current_card:
            return (
                self.current_card['answer'],
                gr.update(visible=False),  # Ocultar botón mostrar respuesta
                gr.update(visible=True)    # Mostrar botones de evaluación
            )
        return "", gr.update(visible=False), gr.update(visible=False)

    def answer_card(self, difficulty: str) -> tuple:
        """Procesa respuesta de la tarjeta"""
        if not self.current_card:
            return "❌ No hay tarjeta activa", "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        try:
            # Mapear respuesta a ReviewResult
            result_map = {
                "Muy Difícil": ReviewResult.AGAIN,
                "Difícil": ReviewResult.HARD,
                "Bien": ReviewResult.GOOD,
                "Fácil": ReviewResult.EASY
            }

            result = result_map.get(difficulty, ReviewResult.GOOD)
            review_info = self.anki_ui.answer_card(result)

            if review_info.get('has_next'):
                # Siguiente tarjeta
                self.current_card = review_info['next_card']
                return (
                    f"✅ Respuesta registrada - {self.current_card['progress']}",
                    self.current_card['question'],
                    "¿Sabes la respuesta?",
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=True)
                )
            else:
                # Sesión completada
                stats = review_info.get('session_stats', {})
                accuracy = stats.get('accuracy', 0) * 100

                self.current_card = None
                return (
                    f"🎉 ¡Sesión completada!\n📊 Precisión: {accuracy:.1f}%\n📚 Tarjetas estudiadas: {stats.get('cards_studied', 0)}",
                    "Sesión de estudio finalizada",
                    "¡Excelente trabajo! Puedes iniciar una nueva sesión cuando quieras.",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False)
                )

        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

    def get_study_stats(self) -> str:
        """Obtiene estadísticas de estudio"""
        try:
            stats = self.card_manager.get_study_statistics(30)
            card_stats = stats['general_stats']

            return f"""
            📊 **Estadísticas de Estudio (últimos 30 días)**

            🎴 **Tarjetas:**
            - Total: {card_stats.get('total_cards', 0)}
            - Pendientes: {card_stats.get('due_cards', 0)}

            🏆 **Rendimiento:**
            - Racha actual: {stats.get('current_streak', 0)} días

            📈 **Por Dificultad:**
            """ + "\n".join([f"- {diff}: {count}" for diff, count in card_stats.get('by_difficulty', {}).items()])

        except Exception as e:
            return f"❌ Error obteniendo estadísticas: {str(e)}"

    def upload_document(self, file, title: str, category: str) -> str:
        """Sube y procesa un documento"""
        if not file or not title.strip():
            return "❌ Por favor selecciona un archivo y proporciona un título"

        try:
            # Leer contenido del archivo
            if file.name.endswith('.txt'):
                with open(file.name, 'r', encoding='utf-8') as f: # Assuming file is a path provided by Gradio
                    content = f.read()
            else:
                return "❌ Solo se soportan archivos .txt por ahora"

            # Crear documento
            from data.models import Document # Assuming Document is in data.models
            doc = Document(
                title=title,
                content=content,
                category=category or "General",
                document_type="text",
                file_path=file.name
            )

            doc_id = self.db.create_document(doc)

            # Procesar para RAG
            if self.rag_engine.process_document(doc_id):
                return f"✅ Documento '{title}' subido y procesado exitosamente"
            else:
                return f"⚠️ Documento subido pero hubo problemas procesándolo"

        except Exception as e:
            return f"❌ Error procesando documento: {str(e)}"

    def create_interface(self):
        """Crea la interfaz Gradio"""

        # Tema personalizado
        theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="cyan",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
        ).set(
            body_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            block_background_fill="rgba(255, 255, 255, 0.95)",
            block_border_width="0",
            block_shadow="0 10px 25px rgba(0,0,0,0.1)",
            button_primary_background_fill="linear-gradient(45deg, #667eea, #764ba2)",
            button_primary_border_color="transparent"
        )

        with gr.Blocks(
            theme=theme,
            title="MedStudy Pro - Asistente de Estudio Médico con IA",
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: auto !important;
            }
            .title-header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 1em;
            }
            .tab-nav > .tab-nav-item {
                font-weight: 600;
                font-size: 1.1em;
            }
            .success-message {
                color: #10b981;
                font-weight: 600;
            }
            .error-message {
                color: #ef4444;
                font-weight: 600;
            }
            """
        ) as interface:

            # Header principal
            gr.HTML("""
                <div class="title-header">
                    🧠 MedStudy Pro
                </div>
                <div style="text-align: center; margin-bottom: 2em; color: #64748b;">
                    Asistente de Estudio Médico Potenciado por IA Local
                </div>
            """)

            with gr.Tabs() as tabs:

                # Tab 1: Chat con IA
                with gr.Tab("💬 Chat Médico", elem_id="chat-tab"):
                    gr.HTML("<h2>🤖 Asistente Médico Inteligente</h2>")
                    gr.Markdown("Haz preguntas médicas y obtén respuestas basadas en tu base de conocimientos")

                    with gr.Row():
                        with gr.Column(scale=4):
                            chatbot = gr.Chatbot(
                                height=500,
                                placeholder="¡Hola! Soy tu asistente médico. Pregúntame sobre cualquier tema de medicina.",
                                container=True,
                                bubble_full_width=False
                            )

                            with gr.Row():
                                chat_input = gr.Textbox(
                                    placeholder="Escribe tu pregunta médica aquí...",
                                    scale=4,
                                    lines=2
                                )
                                chat_submit = gr.Button("Enviar", variant="primary", scale=1)

                        with gr.Column(scale=1):
                            gr.HTML("<h3>💡 Ejemplos de Preguntas</h3>")
                            examples = gr.Examples(
                                examples=[
                                    ["¿Cuáles son los síntomas de la hipertensión?"],
                                    ["Explica la fisiopatología del infarto agudo de miocardio"],
                                    ["¿Qué es la diabetes tipo 2?"],
                                    ["Diferencias entre virus y bacterias"],
                                    ["Tratamiento de la neumonía adquirida en comunidad"]
                                ],
                                inputs=chat_input
                            )

                # Tab 2: Sistema Anki
                with gr.Tab("🎴 Sistema de Tarjetas", elem_id="anki-tab"):
                    with gr.Row():
                        # Columna izquierda: Estudio
                        with gr.Column(scale=2):
                            gr.HTML("<h2>📚 Estudiar Tarjetas</h2>")

                            study_status = gr.Textbox(
                                label="Estado",
                                value="Haz clic en 'Iniciar Sesión' para comenzar",
                                interactive=False
                            )

                            start_session_btn = gr.Button(
                                "🚀 Iniciar Sesión de Estudio",
                                variant="primary",
                                size="lg"
                            )

                            with gr.Group(visible=False) as study_group:
                                question_display = gr.Textbox(
                                    label="❓ Pregunta",
                                    lines=3,
                                    interactive=False
                                )

                                answer_display = gr.Textbox(
                                    label="💡 Respuesta",
                                    lines=4,
                                    interactive=False
                                )

                                show_answer_btn = gr.Button(
                                    "👁️ Mostrar Respuesta",
                                    variant="secondary"
                                )

                                with gr.Row(visible=False) as evaluation_buttons:
                                    very_hard_btn = gr.Button("😰 Muy Difícil", variant="stop")
                                    hard_btn = gr.Button("😓 Difícil", variant="secondary")
                                    good_btn = gr.Button("😊 Bien", variant="primary")
                                    easy_btn = gr.Button("😄 Fácil", variant="secondary")

                        # Columna derecha: Generar tarjetas
                        with gr.Column(scale=1):
                            gr.HTML("<h2>✨ Generar Tarjetas con IA</h2>")

                            topic_input = gr.Textbox(
                                label="📖 Tema",
                                placeholder="Ej: Insuficiencia cardíaca",
                                lines=2
                            )

                            difficulty_select = gr.Dropdown(
                                choices=["easy", "medium", "hard"],
                                value="medium",
                                label="🎯 Dificultad"
                            )

                            generate_btn = gr.Button(
                                "🎴 Generar Tarjeta",
                                variant="primary"
                            )

                            generation_result = gr.Textbox(
                                label="Resultado",
                                interactive=False
                            )

                            with gr.Group():
                                generated_question = gr.Textbox(
                                    label="Pregunta Generada",
                                    lines=2,
                                    interactive=False
                                )
                                generated_answer = gr.Textbox(
                                    label="Respuesta Generada",
                                    lines=3,
                                    interactive=False
                                )
                                generated_metadata = gr.Textbox(
                                    label="Metadatos",
                                    interactive=False
                                )

                            # Estadísticas
                            gr.HTML("<h3>📊 Estadísticas</h3>")
                            stats_display = gr.Textbox(
                                label="Estadísticas de Estudio",
                                lines=8,
                                interactive=False
                            )

                            refresh_stats_btn = gr.Button("🔄 Actualizar Estadísticas")

                # Tab 3: Documentos
                with gr.Tab("📚 Gestión de Documentos", elem_id="docs-tab"):
                    gr.HTML("<h2>📄 Subir y Gestionar Documentos</h2>")
                    gr.Markdown("Sube documentos médicos para enriquecer la base de conocimientos")

                    with gr.Row():
                        with gr.Column():
                            file_upload = gr.File(
                                label="📁 Seleccionar Archivo",
                                file_types=[".txt"],
                                type="binary" # Changed to 'binary' as file.read() is used later
                            )

                            doc_title = gr.Textbox(
                                label="📝 Título del Documento",
                                placeholder="Ej: Manual de Cardiología"
                            )

                            doc_category = gr.Textbox(
                                label="🏷️ Categoría",
                                placeholder="Ej: Cardiología, Neurología, etc."
                            )

                            upload_btn = gr.Button(
                                "📤 Subir y Procesar Documento",
                                variant="primary"
                            )

                            upload_result = gr.Textbox(
                                label="Resultado",
                                interactive=False
                            )

                        with gr.Column():
                            gr.HTML("<h3>ℹ️ Información</h3>")
                            gr.Markdown("""
                            **Formatos soportados:**
                            - Archivos de texto (.txt)

                            **Proceso automático:**
                            1. 📄 Análisis del contenido
                            2. ✂️ División en fragmentos
                            3. 🧠 Generación de embeddings
                            4. 🔍 Indexación para búsqueda

                            **Beneficios:**
                            - Las preguntas del chat usarán este contenido
                            - Respuestas más precisas y contextualizadas
                            - Base de conocimientos personalizada
                            """)

            # Event handlers

            # Chat
            chat_submit.click(
                self.chat_with_ai,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input]
            )

            chat_input.submit(
                self.chat_with_ai,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input]
            )

            # Anki - Generar tarjetas
            generate_btn.click(
                self.generate_anki_card,
                inputs=[topic_input, difficulty_select],
                outputs=[generation_result, generated_question, generated_answer, generated_metadata]
            )

            # Anki - Sesión de estudio
            start_session_btn.click(
                self.start_study_session,
                outputs=[study_status, question_display, answer_display, study_group, evaluation_buttons, show_answer_btn]
            )

            show_answer_btn.click(
                self.show_answer,
                outputs=[answer_display, show_answer_btn, evaluation_buttons]
            )

            # Botones de evaluación
            very_hard_btn.click(
                lambda: self.answer_card("Muy Difícil"),
                outputs=[study_status, question_display, answer_display, study_group, evaluation_buttons, show_answer_btn]
            )

            hard_btn.click(
                lambda: self.answer_card("Difícil"),
                outputs=[study_status, question_display, answer_display, study_group, evaluation_buttons, show_answer_btn]
            )

            good_btn.click(
                lambda: self.answer_card("Bien"),
                outputs=[study_status, question_display, answer_display, study_group, evaluation_buttons, show_answer_btn]
            )

            easy_btn.click(
                lambda: self.answer_card("Fácil"),
                outputs=[study_status, question_display, answer_display, study_group, evaluation_buttons, show_answer_btn]
            )

            # Estadísticas
            refresh_stats_btn.click(
                self.get_study_stats,
                outputs=[stats_display]
            )

            # Al cargar, mostrar estadísticas
            interface.load(
                self.get_study_stats,
                outputs=[stats_display]
            )

            # Documentos
            upload_btn.click(
                self.upload_document,
                inputs=[file_upload, doc_title, doc_category],
                outputs=[upload_result]
            )

        return interface

def main():
    """Función principal para ejecutar la aplicación"""
    print("🚀 Iniciando MedStudy Pro...")

    try:
        app = MedStudyGradioApp()
        interface = app.create_interface()

        print("✅ Aplicación inicializada exitosamente")
        print("🌐 Abriendo interfaz web...")

        interface.launch(
            server_name="0.0.0.0",  # Acceso desde cualquier IP
            server_port=7860,
            share=False,  # Cambiar a True para link público
            show_error=True,
            inbrowser=True,  # Abrir automáticamente en navegador
            favicon_path=None,
            title="MedStudy Pro",
            description="Asistente de Estudio Médico con IA"
        )

    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
