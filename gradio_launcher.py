"""
Lanzador funcional de Gradio para MedStudy Pro - Versión Corregida
Reemplazar el archivo gradio_launcher.py con este código
"""

import gradio as gr
import requests
import json

def chat_with_ollama(message, history):
    """Función para chat con Ollama"""
    try:
        # Configuración Ollama
        ollama_url = "http://localhost:11434/api/generate"
        
        # Prompt médico especializado
        system_prompt = """Eres un asistente médico especializado en medicina interna y reumatología. 
        Proporciona respuestas precisas, basadas en evidencia médica actualizada. 
        Siempre recuerda que tus respuestas son para fines educativos y no reemplazan la consulta médica profesional."""
        
        full_prompt = f"{system_prompt}\n\nPregunta: {message}\nRespuesta:"
        
        # Petición a Ollama
        payload = {
            "model": "phi3:mini",
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        response = requests.post(ollama_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Sin respuesta del modelo')
        else:
            return f"Error en Ollama: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Error: No se puede conectar con Ollama. ¿Está ejecutándose?"
    except requests.exceptions.Timeout:
        return "⏱️ Timeout: Ollama tardó demasiado en responder"
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"

def check_ollama_status():
    """Verificar estado de Ollama"""
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        if response.status_code == 200:
            return "✅ Ollama está funcionando correctamente"
        else:
            return f"⚠️ Ollama responde pero con estado: {response.status_code}"
    except:
        return "❌ Ollama no está disponible. Ejecuta: ollama serve"

def create_medstudy_app():
    """Crear la aplicación Gradio completa"""
    
    # CSS personalizado
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    """
    
    with gr.Blocks(
        title="🧠 MedStudy Pro",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as app:
        
        # Header
        gr.HTML("""
        <div class="header">
            <h1>🧠 MedStudy Pro</h1>
            <p><em>Asistente de Estudio Médico con IA Local</em></p>
            <p>Especializado en Medicina Interna y Reumatología</p>
        </div>
        """)
        
        # Tabs principales
        with gr.Tabs():
            
            # Tab 1: Chat Médico
            with gr.TabItem("💬 Chat Médico"):
                gr.Markdown("""
                ### Chat con IA Médica Especializada
                Pregunta sobre casos clínicos, diagnósticos, tratamientos, y más.
                """)
                
                # Chat interface compatible
                chatbot = gr.Chatbot(
                    height=500,
                    type="messages"  # Formato moderno
                )
                
                msg = gr.Textbox(
                    placeholder="Escribe tu pregunta médica...",
                    label="Mensaje",
                    lines=2
                )
                
                clear_btn = gr.Button("🗑️ Limpiar Chat")
                
                def respond(message, chat_history):
                    if not message.strip():
                        return chat_history, ""
                    
                    bot_message = chat_with_ollama(message, chat_history)
                    
                    # Formato de mensajes moderno
                    chat_history.append({"role": "user", "content": message})
                    chat_history.append({"role": "assistant", "content": bot_message})
                    
                    return chat_history, ""
                
                def clear_chat():
                    return []
                
                msg.submit(respond, [msg, chatbot], [chatbot, msg])
                clear_btn.click(clear_chat, None, chatbot)
            
            # Tab 2: Sistema Anki
            with gr.TabItem("🎴 Sistema Anki"):
                gr.Markdown("""
                ### Sistema de Tarjetas Inteligentes
                *Funcionalidad en desarrollo*
                """)
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Crear Nueva Tarjeta")
                        question_input = gr.Textbox(
                            label="Pregunta",
                            placeholder="Ej: ¿Cuáles son los criterios EULAR para artritis reumatoide?"
                        )
                        answer_input = gr.Textbox(
                            label="Respuesta",
                            lines=3,
                            placeholder="Escribe la respuesta aquí..."
                        )
                        create_card_btn = gr.Button("📝 Crear Tarjeta", variant="primary")
                        
                        def create_card(question, answer):
                            if question and answer:
                                return f"✅ Tarjeta creada: {question[:50]}..."
                            return "❌ Completa pregunta y respuesta"
                        
                        card_status = gr.Textbox(label="Estado", interactive=False)
                        create_card_btn.click(
                            create_card, 
                            [question_input, answer_input], 
                            card_status
                        )
                    
                    with gr.Column():
                        gr.Markdown("#### Estadísticas")
                        gr.HTML("""
                        <div style="padding: 20px; background: #f3f4f6; border-radius: 10px;">
                            <h4>📊 Progreso de Estudio</h4>
                            <p>🆕 Tarjetas nuevas: 0</p>
                            <p>📖 En aprendizaje: 0</p>
                            <p>✅ Revisadas: 0</p>
                            <p>🔥 Racha actual: 0 días</p>
                        </div>
                        """)
            
            # Tab 3: Documentos
            with gr.TabItem("📚 Gestión de Documentos"):
                gr.Markdown("""
                ### Subir y Procesar Documentos Médicos
                *Funcionalidad en desarrollo*
                """)
                
                with gr.Row():
                    with gr.Column():
                        file_upload = gr.File(
                            label="Subir Documentos",
                            file_count="multiple"
                        )
                        process_btn = gr.Button("🔄 Procesar Documentos", variant="primary")
                        
                        def process_files(files):
                            if files:
                                file_names = [f.name for f in files]
                                return f"📄 Archivos recibidos: {', '.join(file_names)}"
                            return "❌ No se seleccionaron archivos"
                        
                        process_status = gr.Textbox(label="Estado del Procesamiento", interactive=False)
                        process_btn.click(process_files, file_upload, process_status)
                    
                    with gr.Column():
                        gr.Markdown("#### Documentos Procesados")
                        gr.HTML("""
                        <div style="padding: 20px; background: #f3f4f6; border-radius: 10px;">
                            <p>📄 No hay documentos procesados aún</p>
                            <p><em>Los documentos aparecerán aquí después del procesamiento</em></p>
                        </div>
                        """)
            
            # Tab 4: Sistema
            with gr.TabItem("⚙️ Sistema"):
                gr.Markdown("### Estado del Sistema")
                
                with gr.Row():
                    check_btn = gr.Button("🔍 Verificar Ollama", variant="secondary")
                    status_output = gr.Textbox(
                        label="Estado",
                        value="Haz clic en 'Verificar Ollama' para comprobar el estado",
                        interactive=False
                    )
                
                check_btn.click(
                    fn=check_ollama_status,
                    outputs=status_output
                )
                
                gr.Markdown("""
                #### Información del Sistema
                - **Modelo IA**: phi3:mini (Ollama)
                - **Interfaz**: Gradio
                - **Especialización**: Medicina Interna y Reumatología
                - **Estado**: Versión de desarrollo
                """)
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid #e5e7eb;">
            <p><em>MedStudy Pro v1.0 - Desarrollado por médicos para médicos</em></p>
            <p>🔬 IA Local | 🔒 Privado | 📚 Educativo</p>
        </div>
        """)
    
    return app

def main():
    """Función principal"""
    print("🚀 Iniciando MedStudy Pro...")
    print("📋 Verificando Ollama...")
    
    # Verificar Ollama antes de iniciar
    status = check_ollama_status()
    print(f"   {status}")
    
    # Crear y lanzar aplicación
    app = create_medstudy_app()
    
    print("🌐 Iniciando servidor Gradio...")
    print("💡 La aplicación se abrirá en tu navegador")
    print("🔗 URL local: http://localhost:7860")
    print("⏹️ Presiona Ctrl+C para cerrar")
    
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        debug=False,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main()