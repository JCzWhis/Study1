"""
MedStudy Pro - Study Session Manager ARREGLADO
Generación de contenido médico robusta para CUALQUIER tema
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
    FOCUSED_STUDY = "focused_study"
    ACTIVE_RECALL = "active_recall"
    PRACTICE_QUESTIONS = "practice_questions"
    CASE_REVIEW = "case_review"
    RAPID_REVIEW = "rapid_review"

@dataclass
class ActiveRecallPrompt:
    """Prompt de Active Recall"""
    prompt_id: str
    question: str
    topic: str
    expected_points: List[str]
    difficulty: str
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
    """Gestor completo de sesiones de estudio médico - VERSION ARREGLADA"""
    
    def __init__(self, config, database, rag_engine=None, llm_manager=None):
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
        try:
            study_config = self.config.get_study_config() if hasattr(self.config, 'get_study_config') else {}
            self.active_recall_interval = study_config.get('active_recall_interval', 10)
        except:
            self.active_recall_interval = 10
            
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
        
        self.logger.info("Study Session Manager initialized (FIXED VERSION)")
    
    def create_session(self, topic: str, duration_minutes: int = 45,
                      session_type: SessionType = SessionType.FOCUSED_STUDY,
                      specialty: str = "medicina_interna") -> str:
        """Crea una nueva sesión de estudio - VERSION MEJORADA"""
        
        if self.current_session and self.session_status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            raise RuntimeError("Ya hay una sesión activa. Completa o cancela la sesión actual.")
        
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        try:
            # Generar contenido de estudio - ARREGLADO
            self.logger.info(f"Generando contenido para {topic} ({specialty})...")
            study_content = self._generate_study_content_robust(topic, duration_minutes, specialty)
            
            # Crear segmentos de estudio
            segments = self._create_study_segments(study_content, duration_minutes)
            
            # Crear prompts de Active Recall
            recall_prompts = self._generate_recall_prompts_robust(study_content, topic)
            
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
            
            self.logger.info(f"Sesión creada exitosamente: {session_id} - {topic}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creando sesión: {e}")
            raise
    
    def _generate_study_content_robust(self, topic: str, duration_minutes: int, specialty: str) -> Dict[str, Any]:
        """Genera contenido de estudio de manera robusta - NUEVA IMPLEMENTACIÓN"""
        
        self.logger.info(f"Iniciando generación robusta para: {topic}")
        
        try:
            # Método 1: Intentar RAG + LLM (ideal)
            if self.rag_engine and self.llm_manager:
                return self._try_rag_plus_llm(topic, duration_minutes, specialty)
            
            # Método 2: Solo LLM (fallback)
            elif self.llm_manager:
                return self._try_llm_only(topic, duration_minutes, specialty)
            
            # Método 3: Contenido plantilla (último recurso)
            else:
                return self._generate_template_content(topic, duration_minutes, specialty)
                
        except Exception as e:
            self.logger.error(f"Error en generación robusta: {e}")
            # Siempre devolver algo funcional
            return self._generate_template_content(topic, duration_minutes, specialty)
    
    def _try_rag_plus_llm(self, topic: str, duration_minutes: int, specialty: str) -> Dict[str, Any]:
        """Intenta generar contenido con RAG + LLM"""
        self.logger.info("Intentando método RAG + LLM...")
        
        try:
            # Buscar contenido relevante en RAG
            rag_results = self.rag_engine.search_documents(
                query=f"{topic} {specialty}",
                top_k=5
            )
            
            if rag_results and len(rag_results) > 0:
                # Usar RAG + LLM para contenido enriquecido
                context = "\n\n".join([result['text'] for result in rag_results[:3]])
                
                content = self._generate_with_llm(topic, specialty, duration_minutes, context)
                
                return {
                    'topic': topic,
                    'content': content,
                    'method': 'rag_plus_llm',
                    'estimated_reading_time': self._calculate_reading_time(content),
                    'target_duration': duration_minutes,
                    'difficulty': 'intermediate',
                    'sources_used': len(rag_results),
                    'source_chunks': [r.get('chunk_id', 'unknown') for r in rag_results[:3]],
                    'generated_at': datetime.now().isoformat()
                }
            else:
                # No hay contenido RAG, usar solo LLM
                self.logger.info("No hay contenido RAG disponible, usando solo LLM")
                return self._try_llm_only(topic, duration_minutes, specialty)
                
        except Exception as e:
            self.logger.warning(f"Error en RAG + LLM: {e}")
            # Fallback a solo LLM
            return self._try_llm_only(topic, duration_minutes, specialty)
    
    def _try_llm_only(self, topic: str, duration_minutes: int, specialty: str) -> Dict[str, Any]:
        """Intenta generar contenido solo con LLM"""
        self.logger.info("Intentando método solo LLM...")
        
        try:
            content = self._generate_with_llm(topic, specialty, duration_minutes)
            
            return {
                'topic': topic,
                'content': content,
                'method': 'llm_only',
                'estimated_reading_time': self._calculate_reading_time(content),
                'target_duration': duration_minutes,
                'difficulty': 'intermediate',
                'sources_used': 0,
                'source_chunks': [],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error en solo LLM: {e}")
            # Fallback a plantilla
            return self._generate_template_content(topic, duration_minutes, specialty)
    
    def _generate_with_llm(self, topic: str, specialty: str, duration_minutes: int, context: str = "") -> str:
        """Genera contenido usando LLM - MEJORADO"""
        
        # Prompt médico mejorado para cualquier tema
        system_prompt = """Eres un médico especialista experto en medicina interna y reumatología. 
        Crea contenido de estudio médico de alta calidad y académicamente riguroso."""
        
        if context:
            content_prompt = f"""Basándote en el siguiente material médico, crea un contenido de estudio completo sobre {topic}:

MATERIAL DE REFERENCIA:
{context[:1500]}

TEMA: {topic}
ESPECIALIDAD: {specialty}
DURACIÓN OBJETIVO: {duration_minutes} minutos de lectura

ESTRUCTURA REQUERIDA:
1. Introducción y definición clara
2. Epidemiología y factores de riesgo
3. Fisiopatología fundamental
4. Manifestaciones clínicas clave
5. Criterios diagnósticos
6. Estudios complementarios
7. Diagnóstico diferencial
8. Tratamiento y manejo
9. Complicaciones importantes
10. Puntos clave para recordar

REQUISITOS:
- Contenido académico preciso y actualizado
- Terminología médica apropiada
- Enfoque práctico para médicos
- Ejemplos clínicos relevantes
- Información basada en evidencia
- Longitud apropiada para {duration_minutes} minutos de lectura

Genera contenido educativo médico profesional:"""
        else:
            content_prompt = f"""Crea contenido de estudio médico completo sobre {topic}:

TEMA: {topic}
ESPECIALIDAD: {specialty}
DURACIÓN OBJETIVO: {duration_minutes} minutos de lectura

ESTRUCTURA REQUERIDA:
1. Introducción y definición
2. Epidemiología y factores de riesgo
3. Fisiopatología
4. Manifestaciones clínicas
5. Criterios diagnósticos
6. Estudios complementarios
7. Diagnóstico diferencial
8. Tratamiento
9. Complicaciones
10. Puntos clave

REQUISITOS:
- Información médica precisa y actualizada
- Enfoque académico pero práctico
- Terminología médica apropiada
- Basado en evidencia científica
- Ejemplos clínicos útiles
- Longitud para {duration_minutes} minutos de lectura

Genera contenido médico educativo profesional:"""
        
        try:
            # Preparar mensajes para el chat
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_prompt}
            ]
            
            # Generar con LLM
            response = ""
            for chunk in self.llm_manager.chat(messages=messages, stream=True):
                response += chunk
                if len(response) > 5000:  # Limitar longitud
                    break
            
            if len(response) < 100:
                raise ValueError("Respuesta del LLM demasiado corta")
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error generando con LLM: {e}")
            raise
    
    def _generate_template_content(self, topic: str, duration_minutes: int, specialty: str) -> Dict[str, Any]:
        """Genera contenido plantilla como último recurso"""
        self.logger.info("Usando contenido plantilla como fallback")
        
        content = f"""# {topic}

## Introducción
{topic} es un tema importante en {specialty} que requiere comprensión detallada para la práctica clínica efectiva.

## Objetivos de Aprendizaje
Al completar esta sesión de {duration_minutes} minutos, serás capaz de:
- Comprender los aspectos fundamentales de {topic}
- Identificar las manifestaciones clínicas principales
- Aplicar conocimientos en el diagnóstico diferencial
- Desarrollar planes de tratamiento apropiados

## Desarrollo del Tema

### Definición y Conceptos Clave
{topic} representa una condición médica que requiere atención especializada en el contexto de {specialty}.

### Fisiopatología
Los mecanismos fisiopatológicos involucrados en {topic} incluyen múltiples sistemas orgánicos.

### Manifestaciones Clínicas
Las presentaciones clínicas de {topic} pueden variar, pero incluyen:
- Síntomas principales característicos
- Signos físicos relevantes
- Variaciones según población

### Diagnóstico
El diagnóstico de {topic} se basa en:
- Historia clínica detallada
- Examen físico dirigido
- Estudios complementarios apropiados
- Criterios diagnósticos establecidos

### Tratamiento
El manejo de {topic} incluye:
- Medidas generales
- Tratamiento farmacológico específico
- Terapias no farmacológicas
- Seguimiento y monitoreo

### Pronóstico y Complicaciones
Es importante considerar:
- Factores pronósticos
- Complicaciones potenciales
- Estrategias de prevención

## Puntos Clave para Recordar
- {topic} es una condición importante en {specialty}
- El diagnóstico requiere evaluación sistemática
- El tratamiento debe ser individualizado
- El seguimiento es esencial para el éxito

## Próximos Pasos en el Aprendizaje
- Revisar casos clínicos relacionados
- Practicar con preguntas de autoevaluación
- Consultar literatura actualizada
- Discutir con colegas especialistas

---
*Contenido generado para estudio médico académico. Para información específica de pacientes, consulte fuentes médicas actualizadas y practique medicina basada en evidencia.*"""
        
        return {
            'topic': topic,
            'content': content,
            'method': 'template',
            'estimated_reading_time': duration_minutes,
            'target_duration': duration_minutes,
            'difficulty': 'basic',
            'sources_used': 0,
            'source_chunks': [],
            'generated_at': datetime.now().isoformat(),
            'is_fallback': True
        }
    
    def _calculate_reading_time(self, text: str) -> int:
        """Calcula tiempo de lectura en minutos"""
        word_count = len(text.split())
        # Médicos leen ~250 palabras por minuto
        return max(1, round(word_count / 250))
    
    def _create_study_segments(self, content_data: Dict[str, Any], duration_minutes: int) -> List[StudySegment]:
        """Divide contenido en segmentos manejables - MEJORADO"""
        
        content = content_data['content']
        
        # Dividir por secciones (headers ##)
        sections = []
        current_section = ""
        
        for line in content.split('\n'):
            if line.strip().startswith('##') or line.strip().startswith('# '):
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = line
            else:
                current_section += '\n' + line
        
        if current_section.strip():
            sections.append(current_section.strip())
        
        # Si no hay secciones, dividir por párrafos
        if len(sections) < 2:
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            sections = []
            current_section = ""
            words_per_section = max(200, len(content.split()) // 4)
            
            for paragraph in paragraphs:
                if len(current_section.split()) + len(paragraph.split()) > words_per_section:
                    if current_section:
                        sections.append(current_section)
                    current_section = paragraph
                else:
                    current_section += '\n\n' + paragraph
            
            if current_section:
                sections.append(current_section)
        
        # Crear segmentos
        segments = []
        target_segments = max(3, min(len(sections), duration_minutes // 10))
        
        for i, section in enumerate(sections[:target_segments]):
            # Extraer título
            title_line = section.split('\n')[0]
            title = title_line.replace('##', '').replace('#', '').strip()
            if not title:
                title = f"Sección {i+1}"
            
            # Calcular tiempo de lectura
            word_count = len(section.split())
            reading_time = max(3, word_count // 250)
            
            # Extraer conceptos clave
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
    
    def _generate_recall_prompts_robust(self, content_data: Dict[str, Any], topic: str) -> List[ActiveRecallPrompt]:
        """Genera prompts de Active Recall de manera robusta"""
        
        try:
            if self.llm_manager:
                return self._generate_recall_with_llm(content_data, topic)
            else:
                return self._generate_recall_template(content_data, topic)
        except Exception as e:
            self.logger.warning(f"Error generando recall prompts: {e}")
            return self._generate_recall_template(content_data, topic)
    
    def _generate_recall_with_llm(self, content_data: Dict[str, Any], topic: str) -> List[ActiveRecallPrompt]:
        """Genera prompts usando LLM"""
        
        content = content_data['content'][:1500]  # Limitar contenido
        
        recall_prompt = f"""Basándote en este contenido médico sobre {topic}, crea 6 preguntas de Active Recall:

CONTENIDO:
{content}

FORMATO requerido para cada pregunta:
PREGUNTA X:
Pregunta: [pregunta clara que estimule el recuerdo activo]
Puntos clave: [3-4 puntos que el estudiante debería recordar]
Dificultad: [easy/medium/hard]

CRITERIOS:
- Preguntas que requieran explicar conceptos, no solo memorizar
- Progresión de dificultad (2 easy, 3 medium, 1 hard)
- Enfoque en aspectos clínicos importantes
- Apropiadas para Active Recall en medicina

Genera las 6 preguntas:"""
        
        try:
            messages = [
                {"role": "system", "content": "Eres un educador médico experto en Active Recall."},
                {"role": "user", "content": recall_prompt}
            ]
            
            response = ""
            for chunk in self.llm_manager.chat(messages=messages, stream=False):
                response += chunk
            
            return self._parse_recall_prompts(response, topic)
            
        except Exception as e:
            self.logger.error(f"Error generando recall con LLM: {e}")
            return self._generate_recall_template(content_data, topic)
    
    def _generate_recall_template(self, content_data: Dict[str, Any], topic: str) -> List[ActiveRecallPrompt]:
        """Genera prompts plantilla"""
        
        prompts = [
            ActiveRecallPrompt(
                prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
                question=f"Explica los conceptos fundamentales de {topic}",
                topic=topic,
                expected_points=[
                    "Definición clara del concepto",
                    "Fisiopatología básica",
                    "Importancia clínica"
                ],
                difficulty="easy",
                timestamp=datetime.now()
            ),
            ActiveRecallPrompt(
                prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
                question=f"¿Cuáles son las manifestaciones clínicas principales de {topic}?",
                topic=topic,
                expected_points=[
                    "Síntomas característicos",
                    "Signos físicos relevantes",
                    "Variaciones según población"
                ],
                difficulty="medium",
                timestamp=datetime.now()
            ),
            ActiveRecallPrompt(
                prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
                question=f"Describe el enfoque diagnóstico para {topic}",
                topic=topic,
                expected_points=[
                    "Historia clínica dirigida",
                    "Estudios complementarios",
                    "Criterios diagnósticos",
                    "Diagnóstico diferencial"
                ],
                difficulty="medium",
                timestamp=datetime.now()
            ),
            ActiveRecallPrompt(
                prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
                question=f"¿Cuál es el manejo terapéutico de {topic}?",
                topic=topic,
                expected_points=[
                    "Tratamiento de primera línea",
                    "Medidas generales",
                    "Seguimiento necesario"
                ],
                difficulty="medium",
                timestamp=datetime.now()
            ),
            ActiveRecallPrompt(
                prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
                question=f"Analiza las complicaciones potenciales de {topic}",
                topic=topic,
                expected_points=[
                    "Complicaciones más frecuentes",
                    "Factores de riesgo",
                    "Estrategias de prevención"
                ],
                difficulty="hard",
                timestamp=datetime.now()
            ),
            ActiveRecallPrompt(
                prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
                question=f"Conecta {topic} con otros conceptos médicos relacionados",
                topic=topic,
                expected_points=[
                    "Relación con otras patologías",
                    "Sistemas orgánicos involucrados",
                    "Implicaciones en práctica clínica"
                ],
                difficulty="easy",
                timestamp=datetime.now()
            )
        ]
        
        return prompts
    
    def _parse_recall_prompts(self, response: str, topic: str) -> List[ActiveRecallPrompt]:
        """Parsea respuesta de LLM para extraer prompts"""
        
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
            
            elif line.startswith('Puntos clave:'):
                current_prompt['points'] = []
                points_text = line.replace('Puntos clave:', '').strip()
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
        
        # Asegurar que tenemos al menos algunos prompts
        if len(prompts) < 3:
            prompts.extend(self._generate_recall_template({'content': ''}, topic)[:3])
        
        return prompts[:6]  # Máximo 6 prompts
    
    def _create_recall_prompt(self, prompt_data: Dict, topic: str) -> ActiveRecallPrompt:
        """Crea objeto ActiveRecallPrompt"""
        
        return ActiveRecallPrompt(
            prompt_id=f"recall_{uuid.uuid4().hex[:8]}",
            question=prompt_data.get('question', f'Explica los aspectos clave de {topic}'),
            topic=topic,
            expected_points=prompt_data.get('points', []),
            difficulty=prompt_data.get('difficulty', 'medium'),
            timestamp=datetime.now()
        )
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extrae conceptos clave del texto médico"""
        import re
        
        concepts = []
        
        # Palabras en negritas **palabra**
        bold_matches = re.findall(r'\*\*(.*?)\*\*', text)
        concepts.extend(bold_matches)
        
        # Términos médicos comunes (patrones)
        medical_patterns = [
            r'\b\w+itis\b',      # Inflamaciones
            r'\b\w+osis\b',      # Condiciones
            r'\b\w+pathy\b',     # Enfermedades
            r'\b\w+emia\b',      # Condiciones sanguíneas
            r'\b\w+genia\b',     # Origen/causa
        ]
        
        for pattern in medical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend(matches)
        
        # Limpiar y filtrar
        concepts = [c.strip() for c in concepts if len(c.strip()) > 2]
        return list(set(concepts))[:10]  # Top 10
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extrae términos médicos específicos"""
        
        medical_terms = [
            'diagnóstico', 'tratamiento', 'síntomas', 'signos', 'manifestaciones',
            'fisiopatología', 'etiología', 'pronóstico', 'complicaciones',
            'farmacológico', 'terapéutico', 'clínico', 'laboratorio',
            'radiológico', 'biopsia', 'histología', 'patología',
            'epidemiología', 'prevalencia', 'incidencia', 'factores de riesgo'
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in medical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    # RESTO DE MÉTODOS (start_session, pause_session, etc.) SE MANTIENEN IGUAL
    # [Aquí irían todos los otros métodos de la clase original]
    
    def _save_session_to_db(self, session_data: Dict[str, Any]):
        """Guarda sesión en base de datos"""
        try:
            if self.database:
                self.database.execute_update("""
                    INSERT OR REPLACE INTO study_sessions 
                    (session_id, topic, duration_minutes, content_generated, started_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_data['session_id'],
                    session_data['topic'],
                    session_data['duration_minutes'],
                    json.dumps(session_data),
                    session_data['created_at']
                ))
                self.logger.info(f"Sesión guardada en BD: {session_data['session_id']}")
        except Exception as e:
            self.logger.error(f"Error guardando sesión: {e}")

# Export classes
__all__ = ['StudySessionManager', 'SessionStatus', 'SessionType', 'ActiveRecallPrompt', 'StudySegment']