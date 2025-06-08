"""
LLM Manager mejorado para MedStudy Pro
"""
import time
import threading
from typing import List, Dict, Optional, Generator, Callable
import json

from core.ollama_manager import OllamaManager
from utils.logging import get_logger

class LLMManager:
    """Gestiona las interacciones con el modelo de lenguaje"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("LLMManager")
        
        # Inicializar Ollama Manager
        self.ollama = OllamaManager(config)
        
        # Estado
        self.is_ready = False
        self.last_check = 0
        self.check_interval = 30  # segundos
        
        # Prompts del sistema
        self.system_prompts = {
            "medical_assistant": """Eres un asistente médico especializado que ayuda a estudiantes de medicina. 
Tienes conocimientos profundos en medicina interna, reumatología y otras especialidades médicas.
Siempre proporciona información precisa, actualizada y basada en evidencia.
Cuando sea apropiado, menciona las fuentes o guías clínicas relevantes.
Adapta tu respuesta al nivel del estudiante y sé didáctico en tus explicaciones.""",
            
            "anki_generator": """Eres un experto en crear tarjetas de estudio médicas para Anki.
Crea preguntas y respuestas claras, concisas y educativas.
Usa el formato: PREGUNTA: [pregunta clara] | RESPUESTA: [respuesta completa pero concisa]
Incluye detalles importantes como mecanismos, diagnósticos diferenciales, tratamientos, etc.""",
            
            "case_creator": """Eres un experto en crear casos clínicos para estudiantes de medicina.
Crea casos realistas con presentación clínica, historia, examen físico y estudios complementarios.
Incluye preguntas de razonamiento clínico y diagnóstico diferencial."""
        }
    
    def ensure_ready(self, show_progress: bool = False, progress_callback: Optional[Callable] = None) -> bool:
        """Asegura que el LLM esté listo para usar"""
        current_time = time.time()
        
        # Si ya está listo y la verificación es reciente, retornar
        if self.is_ready and (current_time - self.last_check) < self.check_interval:
            return True
        
        try:
            if progress_callback:
                progress_callback("Verificando sistema de IA...", 10)
            
            # Verificar estado completo
            ready = self.ollama.ensure_ready()
            
            if ready:
                if progress_callback:
                    progress_callback("Sistema de IA listo", 100)
                self.is_ready = True
                self.last_check = current_time
                return True
            else:
                if progress_callback:
                    progress_callback("Sistema de IA no disponible", 100)
                self.is_ready = False
                return False
                
        except Exception as e:
            self.logger.error(f"Error creando caso clínico: {e}")
            raise
    
    def explain_concept(self, concept: str, level: str = "medical_student") -> str:
        """Explica un concepto médico"""
        prompt = f"""
        Explica el siguiente concepto médico de manera didáctica para un {level}:
        {concept}
        
        Incluye:
        - Definición clara
        - Fisiopatología básica (si aplica)
        - Manifestaciones clínicas principales
        - Diagnóstico y tratamiento básicos
        - Puntos clave para recordar
        
        Usa un lenguaje apropiado para el nivel del estudiante.
        """
        
        try:
            return self.generate(prompt, context_type="medical_assistant")
        except Exception as e:
            self.logger.error(f"Error explicando concepto: {e}")
            raise
    
    def differential_diagnosis(self, symptoms: str, specialty: str = "") -> str:
        """Genera diagnóstico diferencial"""
        prompt = f"""
        Basándote en estos síntomas/signos: {symptoms}
        {f"Especialidad: {specialty}" if specialty else ""}
        
        Proporciona un diagnóstico diferencial estructurado:
        
        1. DIAGNÓSTICOS MÁS PROBABLES (3-4):
           - Diagnóstico
           - Justificación
           - Estudios para confirmar
        
        2. DIAGNÓSTICOS A CONSIDERAR (2-3):
           - Diagnósticos menos comunes pero importantes
        
        3. BANDERAS ROJAS:
           - Síntomas de alarma que no se deben pasar por alto
        
        Organiza por probabilidad y gravedad.
        """
        
        try:
            return self.generate(prompt, context_type="medical_assistant")
        except Exception as e:
            self.logger.error(f"Error generando diagnóstico diferencial: {e}")
            raise
    
    def drug_information(self, drug_name: str, context: str = "") -> str:
        """Proporciona información farmacológica"""
        prompt = f"""
        Proporciona información completa sobre el fármaco: {drug_name}
        {f"Contexto clínico: {context}" if context else ""}
        
        Incluye:
        1. MECANISMO DE ACCIÓN
        2. INDICACIONES principales
        3. DOSIFICACIÓN típica
        4. EFECTOS ADVERSOS importantes
        5. CONTRAINDICACIONES
        6. INTERACCIONES medicamentosas relevantes
        7. MONITOREO requerido
        
        Enfócate en información clínicamente relevante.
        """
        
        try:
            return self.generate(prompt, context_type="medical_assistant")
        except Exception as e:
            self.logger.error(f"Error obteniendo información del fármaco: {e}")
            raise
    
    def create_study_plan(self, topic: str, duration_days: int, level: str = "medical_student") -> str:
        """Crea un plan de estudio"""
        prompt = f"""
        Crea un plan de estudio de {duration_days} días para: {topic}
        Nivel: {level}
        
        Estructura el plan con:
        
        DÍA X: TEMA ESPECÍFICO
        - Objetivos de aprendizaje
        - Recursos recomendados
        - Actividades (lectura, casos, preguntas)
        - Tiempo estimado
        
        Haz el plan progresivo, desde conceptos básicos hasta aplicación clínica.
        Incluye tiempo para repaso y autoevaluación.
        """
        
        try:
            return self.generate(prompt, context_type="medical_assistant")
        except Exception as e:
            self.logger.error(f"Error creando plan de estudio: {e}")
            raise
    
    def setup_complete_system(self, progress_callback: Optional[Callable] = None) -> bool:
        """Configura el sistema completo"""
        try:
            return self.ollama.setup_complete_system(progress_callback)
        except Exception as e:
            self.logger.error(f"Error configurando sistema: {e}")
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 100)
            return False
    
    def get_quick_diagnosis_suggestions(self, chief_complaint: str) -> List[str]:
        """Obtiene sugerencias rápidas de diagnóstico"""
        prompt = f"""
        Para el motivo de consulta: "{chief_complaint}"
        
        Lista 5-7 diagnósticos diferenciales principales, ordenados por probabilidad.
        Responde SOLO con la lista, separada por comas:
        Diagnóstico 1, Diagnóstico 2, Diagnóstico 3, etc.
        """
        
        try:
            response = self.generate(prompt, context_type="medical_assistant")
            # Parsear la respuesta para obtener lista
            suggestions = [dx.strip() for dx in response.split(',') if dx.strip()]
            return suggestions[:7]  # Máximo 7 sugerencias
        except Exception as e:
            self.logger.error(f"Error obteniendo sugerencias: {e}")
            return []
    
    def validate_response(self, response: str) -> bool:
        """Valida que la respuesta del LLM sea apropiada"""
        if not response or len(response.strip()) < 10:
            return False
        
        # Verificar que no contenga errores comunes
        error_indicators = [
            "error:", "exception:", "failed to", "connection refused",
            "model not found", "timeout"
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator in response_lower:
                return False
        
        return True
    
    def get_model_info(self) -> Dict[str, any]:
        """Obtiene información del modelo actual"""
        try:
            if self.ollama.is_model_available:
                return {
                    "model_name": self.ollama.model_name,
                    "available": True,
                    "status": "ready" if self.is_ready else "not_ready"
                }
            else:
                return {
                    "model_name": self.ollama.model_name,
                    "available": False,
                    "status": "model_not_found"
                }
        except:
            return {
                "model_name": "unknown",
                "available": False,
                "status": "error"
            }
    
    def cleanup(self):
        """Limpieza al cerrar"""
        try:
            self.ollama.cleanup()
        except:
            pass(f"Error verificando LLM: {e}")
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 100)
            self.is_ready = False
            return False
    
    def is_available(self) -> bool:
        """Verifica rápidamente si el LLM está disponible"""
        try:
            return self.ollama.check_service(timeout=2)
        except:
            return False
    
    def get_status(self) -> Dict[str, any]:
        """Obtiene el estado detallado del sistema"""
        return {
            "ready": self.is_ready,
            "available": self.is_available(),
            "ollama_status": self.ollama.get_detailed_status(),
            "last_check": self.last_check
        }
    
    def generate(self, prompt: str, context_type: str = "medical_assistant", 
                 stream: bool = False, **kwargs) -> str:
        """Genera texto usando el modelo"""
        if not self.ensure_ready():
            raise RuntimeError("El sistema de IA no está disponible")
        
        # Obtener prompt del sistema
        system_prompt = self.system_prompts.get(context_type, self.system_prompts["medical_assistant"])
        
        try:
            return self.ollama.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                stream=stream
            )
        except Exception as e:
            self.logger.error(f"Error generando texto: {e}")
            self.is_ready = False  # Marcar como no listo para re-verificar
            raise
    
    def chat(self, message: str, context: Optional[List[Dict]] = None, 
             stream: bool = False, context_type: str = "medical_assistant") -> str:
        """Chat con el modelo manteniendo contexto"""
        if not self.ensure_ready():
            raise RuntimeError("El sistema de IA no está disponible")
        
        # Preparar mensajes
        messages = []
        
        # Agregar prompt del sistema
        system_prompt = self.system_prompts.get(context_type, self.system_prompts["medical_assistant"])
        messages.append({"role": "system", "content": system_prompt})
        
        # Agregar contexto previo
        if context:
            messages.extend(context)
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": message})
        
        try:
            return self.ollama.chat(messages, stream=stream)
        except Exception as e:
            self.logger.error(f"Error en chat: {e}")
            self.is_ready = False
            raise
    
    def chat_stream(self, message: str, callback: Callable[[str, bool], None], 
                    context: Optional[List[Dict]] = None, 
                    context_type: str = "medical_assistant"):
        """Chat con streaming asíncrono"""
        def stream_worker():
            try:
                response = ""
                for chunk in self.chat(message, context, stream=True, context_type=context_type):
                    response += chunk
                    callback(chunk, False)
                
                # Señalar completado
                callback("", True)
                
            except Exception as e:
                self.logger.error(f"Error en chat stream: {e}")
                callback(f"Error: {str(e)}", True)
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=stream_worker, daemon=True)
        thread.start()
        return thread
    
    def generate_anki_card(self, topic: str, difficulty: str = "intermediate") -> Dict[str, str]:
        """Genera una tarjeta Anki sobre un tema específico"""
        prompt = f"""
        Crea una tarjeta de estudio sobre: {topic}
        Nivel de dificultad: {difficulty}
        
        Formato requerido:
        PREGUNTA: [Una pregunta clara y específica]
        RESPUESTA: [Respuesta completa pero concisa, incluye puntos clave]
        
        La pregunta debe ser específica y la respuesta debe incluir:
        - Definición o concepto principal
        - Detalles importantes (mecanismo, causas, síntomas, tratamiento según corresponda)
        - Datos clínicos relevantes
        """
        
        try:
            response = self.generate(prompt, context_type="anki_generator")
            
            # Parsear la respuesta
            lines = response.split('\n')
            question = ""
            answer = ""
            
            for line in lines:
                if line.startswith("PREGUNTA:"):
                    question = line.replace("PREGUNTA:", "").strip()
                elif line.startswith("RESPUESTA:"):
                    answer = line.replace("RESPUESTA:", "").strip()
                elif answer and line.strip():  # Continuar respuesta multilínea
                    answer += "\n" + line.strip()
            
            return {
                "question": question,
                "answer": answer,
                "topic": topic,
                "difficulty": difficulty
            }
            
        except Exception as e:
            self.logger.error(f"Error generando tarjeta Anki: {e}")
            raise
    
    def create_case_study(self, specialty: str, condition: str = "") -> Dict[str, str]:
        """Crea un caso clínico"""
        prompt = f"""
        Crea un caso clínico detallado para la especialidad de {specialty}.
        {f"Enfócate en: {condition}" if condition else ""}
        
        Incluye:
        1. PRESENTACIÓN: Edad, sexo, motivo de consulta principal
        2. HISTORIA: Antecedentes relevantes, evolución de síntomas
        3. EXAMEN FÍSICO: Hallazgos significativos
        4. ESTUDIOS: Laboratorio e imagenología relevantes
        5. PREGUNTAS: 2-3 preguntas de razonamiento clínico
        
        Haz el caso realista y educativo para estudiantes de medicina.
        """
        
        try:
            response = self.generate(prompt, context_type="case_creator")
            
            # El caso ya viene formateado del LLM
            return {
                "content": response,
                "specialty": specialty,
                "condition": condition or "Caso general"
            }
            
        except Exception as e:
            self.logger.error