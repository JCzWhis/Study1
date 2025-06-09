"""
MedStudy Pro - LLM Manager
Gestor especializado para IA local médica con Ollama
Optimizado para medicina interna y reumatología
"""

import logging
import json
import requests
import time
from typing import Dict, List, Any, Optional, Iterator, Union
from datetime import datetime
import threading
import subprocess
import psutil
from pathlib import Path

class LLMManager:
    """Gestor de modelos de IA local especializados en medicina"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('MedStudy.LLM')
        
        # Configuración Ollama
        ollama_config = config.get_ollama_config()
        self.host = ollama_config['host']
        self.model = ollama_config['model']
        self.timeout = ollama_config['timeout']
        
        # Estado del sistema
        self.is_ready = False
        self.last_check = None
        self.status_cache = {}
        
        # Prompts médicos especializados
        self._initialize_medical_prompts()
        
        # Verificación inicial
        self._initial_check()
        
        self.logger.info(f"LLM Manager initialized for model: {self.model}")
    
    def _initialize_medical_prompts(self):
        """Inicializa prompts especializados para medicina"""
        self.medical_prompts = {
            "system_base": """Eres un asistente médico especializado en medicina interna y reumatología. 
            Tienes experiencia como internista y fellow de reumatología.
            
            IMPORTANTE:
            - Proporciona información médica precisa y basada en evidencia
            - Siempre recuerda que tus respuestas son para educación médica
            - No reemplazas la consulta médica profesional
            - Usa terminología médica apropiada pero explicativa
            - Incluye diagnósticos diferenciales cuando sea relevante""",
            
            "case_study": """Como especialista en medicina interna y reumatología, analiza este caso clínico:

            METODOLOGÍA:
            1. Resume la presentación clínica
            2. Identifica hallazgos clave
            3. Proporciona diagnóstico diferencial
            4. Sugiere estudios complementarios
            5. Recomienda manejo inicial
            
            Mantén un enfoque sistemático y educativo.""",
            
            "differential": """Proporciona un diagnóstico diferencial completo para:

            ESTRUCTURA:
            1. Diagnósticos más probables (top 3)
            2. Diagnósticos a considerar
            3. Diagnósticos menos probables pero importantes
            4. Red flags que requieren atención inmediata
            
            Para cada diagnóstico incluye criterios diagnósticos relevantes.""",
            
            "pharmacology": """Como especialista, proporciona información farmacológica completa:

            INCLUYE:
            - Mecanismo de acción
            - Indicaciones en medicina interna/reumatología
            - Dosificación típica
            - Contraindicaciones importantes
            - Interacciones relevantes
            - Monitoreo requerido
            - Efectos adversos principales""",
            
            "teaching": """Actúa como profesor de medicina interna. Explica este concepto de manera didáctica:

            ENFOQUE EDUCATIVO:
            - Conceptos fundamentales primero
            - Fisiopatología cuando sea relevante
            - Correlación clínica
            - Casos ejemplo
            - Puntos clave para recordar
            - Errores comunes a evitar"""
        }
    
    def _initial_check(self):
        """Verificación inicial del sistema"""
        try:
            self.logger.info("Verificando estado inicial de Ollama...")
            status = self.get_status()
            self.is_ready = status.get('ready', False)
            
            if self.is_ready:
                self.logger.info("✅ LLM Manager listo")
            else:
                self.logger.warning("⚠️ LLM Manager: problemas detectados")
                
        except Exception as e:
            self.logger.error(f"Error en verificación inicial: {e}")
            self.is_ready = False
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema Ollama"""
        try:
            # Verificar caché (evitar verificaciones muy frecuentes)
            now = time.time()
            if (self.last_check and 
                now - self.last_check < 30 and 
                self.status_cache):
                return self.status_cache
            
            status = {
                'ready': False,
                'timestamp': datetime.now().isoformat(),
                'ollama_status': {},
                'model_status': {},
                'performance': {}
            }
            
            # 1. Verificar conexión Ollama
            ollama_status = self._check_ollama_connection()
            status['ollama_status'] = ollama_status
            
            if not ollama_status.get('running', False):
                status['ready'] = False
                return status
            
            # 2. Verificar modelo específico
            model_status = self._check_model_availability()
            status['model_status'] = model_status
            
            if not model_status.get('available', False):
                status['ready'] = False
                return status
            
            # 3. Verificar rendimiento
            performance = self._check_performance()
            status['performance'] = performance
            
            # 4. Estado general
            status['ready'] = (
                ollama_status.get('running', False) and
                model_status.get('available', False) and
                performance.get('responsive', False)
            )
            
            # Actualizar caché
            self.status_cache = status
            self.last_check = now
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {e}")
            return {
                'ready': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_ollama_connection(self) -> Dict[str, Any]:
        """Verifica conexión y estado de Ollama"""
        try:
            # Verificar conexión HTTP
            response = requests.get(self.host, timeout=5)
            
            if response.status_code == 200:
                ollama_info = {
                    'running': True,
                    'host': self.host,
                    'response_time': response.elapsed.total_seconds(),
                    'message': response.text.strip()
                }
                
                # Verificar proceso del sistema
                process_info = self._get_ollama_process_info()
                ollama_info.update(process_info)
                
                # Listar modelos disponibles
                try:
                    models_response = requests.get(f"{self.host}/api/tags", timeout=10)
                    if models_response.status_code == 200:
                        models_data = models_response.json()
                        models = [model['name'] for model in models_data.get('models', [])]
                        ollama_info['models'] = models
                        ollama_info['model_count'] = len(models)
                    else:
                        ollama_info['models'] = []
                        ollama_info['model_count'] = 0
                except:
                    ollama_info['models'] = []
                    ollama_info['model_count'] = 0
                
                return ollama_info
            
            else:
                return {
                    'running': False,
                    'error': f"HTTP {response.status_code}",
                    'host': self.host
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'running': False,
                'error': 'Connection refused - Ollama not running',
                'host': self.host,
                'suggestion': 'Run: ollama serve'
            }
        except requests.exceptions.Timeout:
            return {
                'running': False,
                'error': 'Connection timeout',
                'host': self.host
            }
        except Exception as e:
            return {
                'running': False,
                'error': str(e),
                'host': self.host
            }
    
    def _get_ollama_process_info(self) -> Dict[str, Any]:
        """Obtiene información del proceso Ollama"""
        try:
            # Buscar proceso ollama
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'ollama' in proc.info['name'].lower():
                        return {
                            'process': {
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'alive': proc.is_running(),
                                'cpu_percent': proc.cpu_percent(),
                                'memory_mb': proc.memory_info().rss / 1024 / 1024
                            }
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {'process': {'found': False}}
            
        except Exception as e:
            return {'process': {'error': str(e)}}
    
    def _check_model_availability(self) -> Dict[str, Any]:
        """Verifica disponibilidad del modelo específico"""
        try:
            # Verificar si el modelo está disponible
            response = requests.post(
                f"{self.host}/api/show",
                json={"name": self.model},
                timeout=15
            )
            
            if response.status_code == 200:
                model_info = response.json()
                return {
                    'available': True,
                    'model': self.model,
                    'size': model_info.get('size', 'unknown'),
                    'format': model_info.get('format', 'unknown'),
                    'family': model_info.get('details', {}).get('family', 'unknown'),
                    'parameters': model_info.get('details', {}).get('parameter_size', 'unknown')
                }
            
            elif response.status_code == 404:
                return {
                    'available': False,
                    'model': self.model,
                    'error': 'Model not found',
                    'suggestion': f'Run: ollama pull {self.model}'
                }
            
            else:
                return {
                    'available': False,
                    'model': self.model,
                    'error': f'HTTP {response.status_code}',
                    'response': response.text[:200]
                }
                
        except Exception as e:
            return {
                'available': False,
                'model': self.model,
                'error': str(e)
            }
    
    def _check_performance(self) -> Dict[str, Any]:
        """Verifica rendimiento del modelo"""
        try:
            start_time = time.time()
            
            # Test simple de generación
            test_prompt = "Responde solo: OK"
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {"max_tokens": 5}
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                return {
                    'responsive': True,
                    'response_time_seconds': round(response_time, 2),
                    'test_response': generated_text,
                    'tokens_per_second': result.get('eval_count', 0) / result.get('eval_duration', 1) * 1e9 if result.get('eval_duration') else 0
                }
            
            else:
                return {
                    'responsive': False,
                    'error': f'HTTP {response.status_code}',
                    'response_time_seconds': round(response_time, 2)
                }
                
        except Exception as e:
            return {
                'responsive': False,
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Verifica rápidamente si el sistema está disponible"""
        try:
            response = requests.get(self.host, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def ensure_ready(self) -> bool:
        """Asegura que el sistema esté listo y intenta solucionarlo si no"""
        try:
            status = self.get_status()
            
            if status.get('ready', False):
                self.is_ready = True
                return True
            
            # Intentar soluciones automáticas
            ollama_status = status.get('ollama_status', {})
            
            if not ollama_status.get('running', False):
                self.logger.info("Intentando iniciar Ollama...")
                if self._try_start_ollama():
                    time.sleep(5)  # Esperar a que inicie
                    status = self.get_status()
                    if status.get('ready', False):
                        self.is_ready = True
                        return True
            
            model_status = status.get('model_status', {})
            if not model_status.get('available', False):
                self.logger.info(f"Intentando descargar modelo {self.model}...")
                if self._try_pull_model():
                    status = self.get_status()
                    if status.get('ready', False):
                        self.is_ready = True
                        return True
            
            self.is_ready = False
            return False
            
        except Exception as e:
            self.logger.error(f"Error en ensure_ready: {e}")
            self.is_ready = False
            return False
    
    def _try_start_ollama(self) -> bool:
        """Intenta iniciar Ollama automáticamente"""
        try:
            # Verificar si ollama está en PATH
            subprocess.run(['ollama', '--version'], 
                         capture_output=True, timeout=5)
            
            # Intentar iniciar en background
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            self.logger.info("Comando 'ollama serve' ejecutado")
            return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            self.logger.warning(f"No se pudo iniciar Ollama automáticamente: {e}")
            return False
    
    def _try_pull_model(self) -> bool:
        """Intenta descargar el modelo automáticamente"""
        try:
            self.logger.info(f"Descargando modelo {self.model}...")
            result = subprocess.run(
                ['ollama', 'pull', self.model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode == 0:
                self.logger.info(f"Modelo {self.model} descargado exitosamente")
                return True
            else:
                self.logger.error(f"Error descargando modelo: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en descarga automática: {e}")
            return False
    
    def chat(self, message: str, context: List[Dict] = None, 
             chat_type: str = "general", stream: bool = False) -> Union[str, Iterator[str]]:
        """Chat principal con contexto médico"""
        
        if not self.is_ready and not self.ensure_ready():
            raise RuntimeError("Ollama no está listo para el chat")
        
        # Preparar prompt según tipo de chat
        system_prompt = self._get_system_prompt(chat_type)
        full_prompt = self._build_chat_prompt(system_prompt, message, context)
        
        try:
            if stream:
                return self._stream_chat(full_prompt)
            else:
                return self._single_chat(full_prompt)
                
        except Exception as e:
            self.logger.error(f"Error en chat: {e}")
            self.is_ready = False  # Marcar como no listo para forzar verificación
            raise
    
    def _get_system_prompt(self, chat_type: str) -> str:
        """Obtiene prompt del sistema según tipo de chat"""
        prompts = {
            "general": self.medical_prompts["system_base"],
            "case_study": self.medical_prompts["case_study"],
            "differential": self.medical_prompts["differential"],
            "pharmacology": self.medical_prompts["pharmacology"],
            "teaching": self.medical_prompts["teaching"]
        }
        
        return prompts.get(chat_type, self.medical_prompts["system_base"])
    
    def _build_chat_prompt(self, system_prompt: str, message: str, 
                          context: List[Dict] = None) -> str:
        """Construye prompt completo con contexto"""
        prompt_parts = [system_prompt]
        
        # Agregar contexto de conversación
        if context:
            prompt_parts.append("\nCONTEXTO DE CONVERSACIÓN:")
            for msg in context[-6:]:  # Últimos 3 intercambios
                role = "Humano" if msg["role"] == "user" else "Asistente"
                prompt_parts.append(f"{role}: {msg['content']}")
        
        # Pregunta actual
        prompt_parts.append(f"\nHumano: {message}")
        prompt_parts.append("Asistente:")
        
        return "\n".join(prompt_parts)
    
    def _single_chat(self, prompt: str) -> str:
        """Chat sin streaming"""
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000,
                    "stop": ["Humano:", "Human:"]
                }
            },
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            raise RuntimeError(f"Error en API Ollama: {response.status_code}")
    
    def _stream_chat(self, prompt: str) -> Iterator[str]:
        """Chat con streaming"""
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000,
                    "stop": ["Humano:", "Human:"]
                }
            },
            timeout=self.timeout,
            stream=True
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Error en API Ollama: {response.status_code}")
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        chunk = data['response']
                        if chunk:
                            yield chunk
                        
                        if data.get('done', False):
                            break
                except json.JSONDecodeError:
                    continue
    
    def generate_study_content(self, topic: str, specialty: str = "medicina_interna",
                             duration_minutes: int = 45) -> Dict[str, Any]:
        """Genera contenido de estudio específico"""
        
        prompt = f"""Como especialista en {specialty}, crea contenido de estudio completo sobre: {topic}

ESPECIFICACIONES:
- Duración objetivo: {duration_minutes} minutos de estudio
- Enfoque: Medicina interna y reumatología
- Nivel: Residente/Fellow

ESTRUCTURA REQUERIDA:
1. **Introducción y relevancia clínica**
2. **Conceptos fundamentales**
3. **Fisiopatología (si aplica)**
4. **Manifestaciones clínicas**
5. **Diagnóstico y estudios**
6. **Tratamiento y manejo**
7. **Casos clínicos ejemplo**
8. **Puntos clave para recordar**
9. **Preguntas de autoevaluación**

ESTILO:
- Académico pero accesible
- Basado en evidencia médica
- Incluye correlaciones clínicas
- Ejemplos prácticos
- Terminología médica precisa

Genera contenido educativo de alta calidad:"""
        
        try:
            content = self.chat(prompt, chat_type="teaching")
            
            return {
                'topic': topic,
                'specialty': specialty,
                'content': content,
                'duration_minutes': duration_minutes,
                'generated_at': datetime.now().isoformat(),
                'word_count': len(content.split()),
                'estimated_reading_time': len(content.split()) // 200  # 200 wpm
            }
            
        except Exception as e:
            self.logger.error(f"Error generando contenido: {e}")
            raise
    
    def create_anki_cards(self, content: str, topic: str, 
                         card_count: int = 10) -> List[Dict[str, str]]:
        """Crea tarjetas Anki desde contenido"""
        
        prompt = f"""Basándote en el siguiente contenido médico sobre {topic}, crea exactamente {card_count} tarjetas tipo Anki:

CONTENIDO:
{content[:2000]}

FORMATO REQUERIDO para cada tarjeta:
TARJETA X:
Pregunta: [pregunta clara y específica]
Respuesta: [respuesta concisa pero completa]

CRITERIOS:
- Preguntas variadas (conceptos, diagnóstico, tratamiento)
- Respuestas precisas y educativas
- Nivel apropiado para residentes/fellows
- Incluye datos importantes y correlaciones clínicas

Genera las {card_count} tarjetas:"""
        
        try:
            response = self.chat(prompt, chat_type="teaching")
            cards = self._parse_anki_cards(response)
            
            return cards
            
        except Exception as e:
            self.logger.error(f"Error creando tarjetas Anki: {e}")
            return []
    
    def _parse_anki_cards(self, response: str) -> List[Dict[str, str]]:
        """Parsea respuesta para extraer tarjetas Anki"""
        cards = []
        lines = response.split('\n')
        
        current_card = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TARJETA'):
                if current_card:
                    cards.append(current_card)
                current_card = {}
            
            elif line.startswith('Pregunta:'):
                current_card['question'] = line.replace('Pregunta:', '').strip()
            
            elif line.startswith('Respuesta:'):
                current_card['answer'] = line.replace('Respuesta:', '').strip()
            
            elif 'question' in current_card and 'answer' not in current_card and line:
                # Continuar pregunta en múltiples líneas
                current_card['question'] += ' ' + line
            
            elif 'answer' in current_card and line and not line.startswith('TARJETA'):
                # Continuar respuesta en múltiples líneas
                current_card['answer'] += ' ' + line
        
        # Agregar última tarjeta
        if current_card and 'question' in current_card and 'answer' in current_card:
            cards.append(current_card)
        
        return cards
    
    def shutdown(self):
        """Cierre limpio del manager"""
        self.logger.info("Cerrando LLM Manager...")
        self.is_ready = False
        self.status_cache.clear()

# Export main class
__all__ = ['LLMManager']