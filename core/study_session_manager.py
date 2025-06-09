"""
MedStudy Pro - Study Session Manager
Gestor de sesiones de estudio con Active Recall y Pomodoro
Integrado con RAG y generación de contenido médico
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import threading
import time

class SessionStatus(Enum):
    """Estados de sesión de estudio"""
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    BREAK = "break"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SessionType(Enum):
    """Tipos de sesión de estudio"""
    FOCUSED_STUDY = "focused_study"        # Estudio concentrado
    ACTIVE_RECALL = "active_recall"        # Revisión con Active Recall
    PRACTICE_QUESTIONS = "practice_questions"  # Preguntas de práctica
    CASE_REVIEW = "case_review"            # Revisión de casos clínicos
    RAPID_REVIEW = "rapid_review"          # Repaso rápido

@dataclass
class ActiveRecallPrompt:
    """Prompt de Active Recall"""
    prompt_id: str
    question: str
    topic: str
    expected_points: List[str]
    difficulty: str  # easy, medium, hard
    timestamp: datetime

@dataclass
class StudySegment:
    """Segmento de contenido de estudio"""
    segment_id: str
    title: str
    content: str
    reading_time_minutes: int
    key_concepts: List[str]
    medical_terms: List[str]

class StudySessionManager:
    """Gestor completo de sesiones de estudio médico"""
    
    def __init__(self, config, database, rag_engine, llm_manager):
        self.config = config
        self.database = database
        self.rag_engine = rag_engine
        self.llm_manager = llm_manager
        self.logger = logging.getLogger('MedStudy.SessionManager')
        
        # Estado actual de la sesión
        self.current_session = None
        self.session_status = SessionStatus.PLANNING
        self.start_time = None
        self.pause_time = None
        self.total_paused_time = 0
        
        # Configuración de Active Recall
        self.active_recall_interval = config.get_study_config()['active_recall_interval']  # minutos
        self.last_recall_time = None
        self.recall_prompts_used = []
        
        # Callbacks para UI
        self.status_callback = None
        self.recall_callback = None
        self.break_callback = None
        self.completion_callback = None
        
        # Timer thread
        self.timer_thread = None
        self.timer_running = False
        
        self.logger.info("Study Session Manager initialized")
    
    def create_session(self, topic: str, duration_minutes: int = 45,
                      session_type: SessionType = SessionType.FOCUSED_STUDY,
                      specialty: str = "medicina_interna") -> str:
        """Crea una nueva sesión de estudio"""
        
        if self.current_session and self.session_status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            raise RuntimeError("Ya hay una sesión activa. Completa o cancela la sesión actual.")
        
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        try:
            # Generar contenido de estudio
            self.logger.info(f"Generando contenido para {topic}...")
            study_content = self._generate_study_content(topic, duration_minutes, specialty)
            
            # Crear segmentos de estudio
            segments = self._create_study_segments(study_content, duration_minutes)
            
            # Crear prompts de Active Recall
            recall_prompts = self._generate_recall_prompts(study_content, topic)
            
            # Crear sesión
            session_data = {
                'session_id': session_id,
                'topic': topic,
                'specialty': specialty,
                'session_type': session_type.value,
                'duration_minutes': duration_minutes,
                'content': study_content,
                'segments': [segment.__dict__ for segment in segments],
                'recall_prompts': [prompt.__dict__ for prompt in recall_prompts],
                'created_at': datetime.now().isoformat(),
                'status': SessionStatus.PLANNING.value
            }
            
            # Guardar en base de datos
            self._save_session_to_db(session_data)
            
            # Establecer como sesión actual
            self.current_session = session_data
            self.session_status = SessionStatus.PLANNING
            self.recall_prompts_used = []
            
            self.logger.info(f"Sesión creada: {session_id} - {topic}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creando sesión: {e}")
            raise
    
    def start_session(self) -> bool:
        """Inicia la sesión de estudio"""
        
        if not self.current_session:
            raise RuntimeError("No hay sesión para iniciar")
        
        if self.session_status != SessionStatus.PLANNING:
            raise RuntimeError(f"Sesión en estado incorrecto: {self.session_status}")
        
        try:
            # Inicializar estado
            self.start_time = datetime.now()
            self.last_recall_time = self.start_time
            self.total_paused_time = 0
            self.session_status = SessionStatus.ACTIVE
            
            # Actualizar base de datos
            self._update_session_status(SessionStatus.ACTIVE)
            
            # Iniciar timer para Active Recall
            self._start_session_timer()
            
            # Notificar UI
            if self.status_callback:
                self.status_callback("session_started", self.get_session_progress())
            
            self.logger.info(f"Sesión iniciada: {self.current_session['session_id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando sesión: {e}")
            return False
    
    def pause_session(self) -> bool:
        """Pausa la sesión actual"""
        
        if self.session_status != SessionStatus.ACTIVE:
            return False
        
        self.pause_time = datetime.now()
        self.session_status = SessionStatus.PAUSED
        self.timer_running = False
        
        self._update_session_status(SessionStatus.PAUSED)
        
        if self.status_callback:
            self.status_callback("session_paused", self.get_session_progress())
        
        self.logger.info("Sesión pausada")
        return True
    
    def resume_session(self) -> bool:
        """Reanuda la sesión pausada"""
        
        if self.session_status != SessionStatus.PAUSED:
            return False
        
        if self.pause_time:
            pause_duration = datetime.now() - self.pause_time
            self.total_paused_time += pause_duration.total_seconds()
        
        self.session_status = SessionStatus.ACTIVE
        self.pause_time = None
        
        self._start_session_timer()
        self._update_session_status(SessionStatus.ACTIVE)
        
        if self.status_callback:
            self.status_callback("session_resumed", self.get_session_progress())
        
        self.logger.info("Sesión reanudada")
        return True
    
    def complete_session(self, notes: str = "") -> Dict[str, Any]:
        """Completa la sesión y genera reporte"""
        
        if not self.current_session:
            raise RuntimeError("No hay sesión activa")
        
        # Detener timer
        self.timer_running = False
        
        # Calcular métricas
        completion_data = self._calculate_session_metrics(notes)
        
        # Actualizar estado
        self.session_status = SessionStatus.COMPLETED
        self._update_session_status(SessionStatus.COMPLETED, completion_data)
        
        # Generar tarjetas Anki automáticamente
        anki_cards = self._generate_session_anki_cards()
        completion_data['anki_cards_generated'] = len(anki_cards)
        
        # Notificar UI
        if self.completion_callback:
            self.completion_callback("session_completed", completion_data)
        
        self.logger.info(f"Sesión completada: {self.current_session['session_id']}")
        
        # Limpiar estado
        session_summary = completion_data.copy()
        self.current_session = None
        
        return session_summary
    
    def cancel_session(self) -> bool:
        """Cancela la sesión actual"""
        
        if not self.current_session:
            return False
        
        self.timer_running = False
        self.session_status = SessionStatus.CANCELLED
        self._update_session_status(SessionStatus.CANCELLED)
        
        if self.status_callback:
            self.status_callback("session_cancelled", {})
        
        self.logger.info("Sesión cancelada")
        self.current_session = None
        return True
    
    def get_session_progress(self) -> Dict[str, Any]:
        """Obtiene progreso actual de la sesión"""
        
        if not self.current_session:
            return {}
        
        now = datetime.now()
        
        # Calcular tiempo transcurrido
        if self.start_time:
            if self.session_status == SessionStatus.PAUSED:
                elapsed_seconds = (self.pause_time - self.start_time).total_seconds() - self.total_paused_time
            else:
                elapsed_seconds = (now - self.start_time).total_seconds() - self.total_paused_time
        else:
            elapsed_seconds = 0
        
        elapsed_minutes = elapsed_seconds / 60
        target_minutes = self.current_session['duration_minutes']
        progress_percentage = min(100, (elapsed_minutes / target_minutes) * 100)
        
        # Tiempo para próximo Active Recall
        if self.last_recall_time and self.session_status == SessionStatus.ACTIVE:
            time_since_recall = (now - self.last_recall_time).total_seconds() / 60
            time_to_next_recall = max(0, self.active_recall_interval - time_since_recall)
        else:
            time_to_next_recall = self.active_recall_interval
        
        return {
            'session_id': self.current_session['session_id'],
            'topic': self.current_session['topic'],
            'status': self.session_status.value,
            'elapsed_minutes': round(elapsed_minutes, 1),
            'target_minutes': target_minutes,
            'progress_percentage': round(progress_percentage, 1),
            'time_to_next_recall': round(time_to_next_recall, 1),
            'recalls_completed': len(self.recall_prompts_used),
            'total_recalls_available': len(self.current_session.get('recall_prompts', []))
        }
    
    def _generate_study_content(self, topic: str, duration_minutes: int, specialty: str) -> Dict[str, Any]:
        """Genera contenido de estudio usando RAG + LLM"""
        
        try:
            # Buscar contenido relevante en RAG
            rag_results = self.rag_engine.search_documents(
                query=f"{topic} {specialty}",
                top_k=5
            )
            
            if rag_results:
                # Usar RAG + LLM para contenido enriquecido
                context = "\n\n".join([result['text'] for result in rag_results[:3]])
                
                content_data = self.llm_manager.generate_study_content(
                    topic=topic,
                    specialty=specialty,
                    duration_minutes=duration_minutes
                )
                
                content_data['rag_sources'] = len(rag_results)
                content_data['source_chunks'] = [r['chunk_id'] for r in rag_results[:3]]
                
            else:
                # Solo LLM si no hay contenido RAG
                content_data = self.llm_manager.generate_study_content(
                    topic=topic,
                    specialty=specialty,
                    duration_minutes=duration_minutes
                )
                
                content_data['rag_sources'] = 0
                content_data['source_chunks'] = []
            
            return content_data
            
        except Exception as e:
            self.logger.error(f"Error generando contenido: {e}")
            raise
    
    def _create_study_segments(self, content_data: Dict[str, Any], duration_minutes: int) -> List[StudySegment]:
        """Divide contenido en segmentos manejables"""
        
        content = content_data['content']
        
        # Dividir por secciones (basado en headers ##)
        sections = []
        current_section = ""
        
        for line in content.split('\n'):
            if line.strip().startswith('##') or line.strip().startswith('**'):
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = line
            else:
                current_section += '\n' + line
        
        if current_section.strip():
            sections.append(current_section.strip())
        
        # Crear segmentos
        segments = []
        target_segments = max(3, duration_minutes // 15)  # Un segmento cada 15 minutos
        
        for i, section in enumerate(sections[:target_segments]):
            # Extraer título
            title_line = section.split('\n')[0]
            title = title_line.replace('##', '').replace('**', '').strip()
            
            # Calcular tiempo de lectura
            word_count = len(section.split())
            reading_time = max(5, word_count // 200)  # 200 wpm
            
            # Extraer conceptos clave (términos médicos)
            key_concepts = self._extract_key_concepts(section)
            medical_terms = self._extract_medical_terms(section)
            
            segment = StudySegment(
                segment_id=f"seg_{i+1}",
                title=title,
                content=section,
                reading_time_minutes=reading_time,
                key_concepts=key_concepts,
                medical_terms=medical_terms
            )
            
            segments.append(segment)
        
        return segments
    
    def _generate_recall_prompts(self, content_data: Dict[str, Any], topic: str) -> List[ActiveRecallPrompt]:
        """Genera prompts de Active Recall específicos"""
        
        try:
            content = content_data['content']
            
            # Prompt para generar preguntas de Active Recall
            recall_prompt = f"""Basándote en este contenido médico sobre {topic}, crea 8 preguntas de Active Recall:

CONTENIDO:
{content[:1500]}

FORMATO para cada pregunta:
PREGUNTA X:
Pregunta: [pregunta que estimule el recuerdo activo]
Puntos clave esperados: [3-5 puntos que el estudiante debería recordar]
Dificultad: [easy/medium/hard]

CRITERIOS:
- Preguntas que requieran explicar, no solo recordar
- Progresión de dificultad
- Enfoque en conceptos clave médicos
- Apropiadas para Active Recall (no triviales)

Genera las 8 preguntas:"""
            
            response = self.llm_manager.chat(recall_prompt, chat_type="teaching")
            prompts = self._parse_recall_prompts(response, topic)
            
            return prompts
            
        except Exception as e:
            self.logger.error(f"Error generando prompts de Active Recall: {e}")
            return []
    
    def _parse_recall_prompts(self, response: str, topic: str) -> List[ActiveRecallPrompt]:
        """Parsea respuesta para extraer prompts de Active Recall"""
        
        prompts = []
        lines = response.split('\n')
        
        current_prompt = {}
        collecting_points = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('PREGUNTA'):
                if current_prompt:
                    prompts.append(self._create_recall_prompt(current_prompt, topic))
                current_prompt = {}
                collecting_points = False
            
            elif line.startswith('Pregunta:'):
                current_prompt['question'] = line.replace('Pregunta:', '').strip()
                collecting_points = False
            
            elif line.startswith('Puntos clave esperados:'):
                current_prompt['points'] = []
                points_text = line.replace('Puntos clave esperados:', '').strip()
                if points_text:
                    current_prompt['points'] = [points_text]
                collecting_points = True
            
            elif line.startswith('Dificultad:'):
                difficulty = line.replace('Dificultad:', '').strip().lower()
                current_prompt['difficulty'] = difficulty if difficulty in ['easy', 'medium', 'hard'] else 'medium'
                collecting_points = False
            
            elif collecting_points and line and not line.startswith('PREGUNTA'):
                if 'points' not in current_prompt:
                    current_prompt['points'] = []
                current_prompt['points'].append(line)
        
        # Agregar último prompt
        if current_prompt:
            prompts.append(self._create_recall_prompt(current_prompt, topic))
        
        return prompts
    
    def _create_recall_prompt(self, prompt_data: Dict, topic: str) -> ActiveRecallPrompt:
        """Crea objeto ActiveRecallPrompt"""
        
        return ActiveRecallPrompt(
            prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
            question=prompt_data.get('question', 'Explica los conceptos clave del tema.'),
            topic=topic,
            expected_points=prompt_data.get('points', []),
            difficulty=prompt_data.get('difficulty', 'medium'),
            timestamp=datetime.now()
        )
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extrae conceptos clave del texto"""
        
        # Buscar términos en negritas o con asteriscos
        import re
        
        concepts = []
        
        # Palabras en negritas **palabra**
        bold_matches = re.findall(r'\*\*(.*?)\*\*', text)
        concepts.extend(bold_matches)
        
        # Términos médicos comunes (patrones básicos)
        medical_patterns = [
            r'\b\w+itis\b',      # Inflamaciones
            r'\b\w+osis\b',      # Condiciones
            r'\b\w+pathy\b',     # Enfermedades
            r'\b\w+emia\b',      # Condiciones sanguíneas
        ]
        
        for pattern in medical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend(matches)
        
        # Filtrar y limpiar
        concepts = [c.strip() for c in concepts if len(c.strip()) > 2]
        return list(set(concepts))[:10]  # Top 10
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extrae términos médicos específicos"""
        
        # Lista básica de términos médicos comunes
        medical_terms = [
            'diagnóstico', 'tratamiento', 'síntomas', 'signos', 'manifestaciones',
            'fisiopatología', 'etiología', 'pronóstico', 'complicaciones',
            'farmacológico', 'terapéutico', 'clínico', 'laboratorio',
            'radiológico', 'biopsia', 'histología', 'patología'
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in medical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _start_session_timer(self):
        """Inicia timer para Active Recall"""
        
        self.timer_running = True
        
        def timer_worker():
            while self.timer_running and self.session_status == SessionStatus.ACTIVE:
                time.sleep(60)  # Verificar cada minuto
                
                if not self.timer_running:
                    break
                
                # Verificar si es tiempo para Active Recall
                if self._should_trigger_recall():
                    self._trigger_active_recall()
        
        self.timer_thread = threading.Thread(target=timer_worker, daemon=True)
        self.timer_thread.start()
    
    def _should_trigger_recall(self) -> bool:
        """Verifica si es tiempo para Active Recall"""
        
        if not self.last_recall_time:
            return False
        
        now = datetime.now()
        minutes_since_recall = (now - self.last_recall_time).total_seconds() / 60
        
        return minutes_since_recall >= self.active_recall_interval
    
    def _trigger_active_recall(self):
        """Dispara Active Recall"""
        
        if not self.current_session:
            return
        
        # Obtener próximo prompt no usado
        available_prompts = [
            prompt for prompt in self.current_session.get('recall_prompts', [])
            if prompt['prompt_id'] not in self.recall_prompts_used
        ]
        
        if not available_prompts:
            self.logger.info("No hay más prompts de Active Recall disponibles")
            return
        
        # Seleccionar prompt (rotar dificultades)
        selected_prompt = available_prompts[0]
        self.recall_prompts_used.append(selected_prompt['prompt_id'])
        self.last_recall_time = datetime.now()
        
        # Pausar sesión para Active Recall
        self.pause_session()
        
        # Notificar UI
        if self.recall_callback:
            self.recall_callback("active_recall_triggered", selected_prompt)
        
        self.logger.info("Active Recall disparado")
    
    def complete_active_recall(self, user_response: str, prompt_id: str) -> Dict[str, Any]:
        """Completa sesión de Active Recall"""
        
        # Registrar respuesta
        recall_data = {
            'prompt_id': prompt_id,
            'user_response': user_response,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.current_session['session_id'] if self.current_session else None
        }
        
        # Guardar en base de datos
        self._save_recall_response(recall_data)
        
        # Reanudar sesión
        self.resume_session()
        
        return recall_data
    
    def _calculate_session_metrics(self, notes: str) -> Dict[str, Any]:
        """Calcula métricas de la sesión completada"""
        
        if not self.current_session or not self.start_time:
            return {}
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        active_duration = total_duration - self.total_paused_time
        
        return {
            'session_id': self.current_session['session_id'],
            'completed_at': end_time.isoformat(),
            'total_duration_minutes': round(total_duration / 60, 1),
            'active_duration_minutes': round(active_duration / 60, 1),
            'target_duration_minutes': self.current_session['duration_minutes'],
            'completion_percentage': min(100, (active_duration / 60) / self.current_session['duration_minutes'] * 100),
            'recalls_completed': len(self.recall_prompts_used),
            'notes': notes
        }
    
    def _generate_session_anki_cards(self) -> List[Dict[str, str]]:
        """Genera tarjetas Anki automáticamente de la sesión"""
        
        if not self.current_session:
            return []
        
        try:
            content = self.current_session['content']['content']
            topic = self.current_session['topic']
            
            cards = self.llm_manager.create_anki_cards(content, topic, card_count=8)
            
            # Guardar tarjetas en base de datos
            for card in cards:
                self._save_anki_card(card, self.current_session['session_id'])
            
            return cards
            
        except Exception as e:
            self.logger.error(f"Error generando tarjetas Anki: {e}")
            return []
    
    def _save_session_to_db(self, session_data: Dict[str, Any]):
        """Guarda sesión en base de datos"""
        try:
            self.database.execute_update("""
                INSERT INTO study_sessions 
                (session_id, topic, specialty, session_type, duration_minutes, 
                 content_generated, started_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                session_data['topic'],
                session_data['specialty'],
                session_data['session_type'],
                session_data['duration_minutes'],
                json.dumps(session_data),
                session_data['created_at'],
                session_data['status']
            ))
        except Exception as e:
            self.logger.error(f"Error guardando sesión: {e}")
    
    def _update_session_status(self, status: SessionStatus, completion_data: Dict = None):
        """Actualiza estado de sesión en BD"""
        try:
            if completion_data:
                self.database.execute_update("""
                    UPDATE study_sessions 
                    SET status = ?, completed_at = ?, duration_minutes = ?
                    WHERE session_id = ?
                """, (
                    status.value,
                    completion_data.get('completed_at'),
                    completion_data.get('active_duration_minutes'),
                    self.current_session['session_id']
                ))
            else:
                self.database.execute_update("""
                    UPDATE study_sessions 
                    SET status = ?
                    WHERE session_id = ?
                """, (
                    status.value,
                    self.current_session['session_id']
                ))
        except Exception as e:
            self.logger.error(f"Error actualizando estado: {e}")
    
    def _save_recall_response(self, recall_data: Dict[str, Any]):
        """Guarda respuesta de Active Recall"""
        try:
            # Implementar tabla de respuestas si es necesario
            pass
        except Exception as e:
            self.logger.error(f"Error guardando respuesta Active Recall: {e}")
    
    def _save_anki_card(self, card: Dict[str, str], session_id: str):
        """Guarda tarjeta Anki generada"""
        try:
            # Usar MedCards system para guardar
            pass
        except Exception as e:
            self.logger.error(f"Error guardando tarjeta Anki: {e}")
    
    def set_callbacks(self, status_callback: Callable = None,
                     recall_callback: Callable = None,
                     break_callback: Callable = None,
                     completion_callback: Callable = None):
        """Establece callbacks para eventos de UI"""
        self.status_callback = status_callback
        self.recall_callback = recall_callback
        self.break_callback = break_callback
        self.completion_callback = completion_callback

# Export main classes
__all__ = ['StudySessionManager', 'SessionStatus', 'SessionType', 'ActiveRecallPrompt', 'StudySegment']