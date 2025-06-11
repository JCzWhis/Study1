"""
MedStudy Pro - Retrospective Study Planner
Sistema de planificación retrospectiva inspirado en Ali Abdaal
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class ConfidenceLevel(Enum):
    """Niveles de confianza en conocimiento (color-coded)"""
    RED = "red"           # No sé nada
    ORANGE = "orange"     # Sé muy poco
    YELLOW = "yellow"     # Sé algo
    GREEN = "green"       # Sé bastante bien
    BLUE = "blue"         # Lo domino completamente

class StudyPriority(Enum):
    """Prioridades de estudio"""
    URGENT = "urgent"         # Rojo - Estudiar hoy
    HIGH = "high"             # Naranja - Esta semana
    MEDIUM = "medium"         # Amarillo - Este mes
    LOW = "low"               # Verde - Cuando sea posible
    OPTIONAL = "optional"     # Azul - Ya dominado

@dataclass
class StudyTopic:
    """Tema de estudio individual"""
    topic_id: str
    name: str
    specialty: str
    confidence_level: ConfidenceLevel
    last_studied: Optional[datetime]
    next_review: Optional[datetime]
    study_count: int
    priority: StudyPriority
    estimated_hours: float
    created_at: datetime

class RetrospectiveStudyPlanner:
    """
    Planificador de estudio retrospectivo basado en Ali Abdaal
    Se enfoca en lo que NO sabes, no en predecir el futuro
    """
    
    def __init__(self, database):
        self.database = database
        self.logger = logging.getLogger('MedStudy.StudyPlanner')
        
        # Intervalos de repetición por nivel de confianza (días)
        self.confidence_intervals = {
            ConfidenceLevel.RED: 1,      # Todos los días
            ConfidenceLevel.ORANGE: 3,   # Cada 3 días
            ConfidenceLevel.YELLOW: 7,   # Semanal
            ConfidenceLevel.GREEN: 21,   # Cada 3 semanas
            ConfidenceLevel.BLUE: 90     # Cada 3 meses (revisión)
        }
        
        # Tiempo estimado de estudio por nivel (horas)
        self.study_time_estimates = {
            ConfidenceLevel.RED: 3.0,     # Estudio intensivo
            ConfidenceLevel.ORANGE: 2.0,  # Estudio regular
            ConfidenceLevel.YELLOW: 1.5,  # Repaso moderado
            ConfidenceLevel.GREEN: 1.0,   # Repaso ligero
            ConfidenceLevel.BLUE: 0.5     # Revisión rápida
        }
        
        self._initialize_tables()
        self.logger.info("Retrospective Study Planner initialized")
    
    def _initialize_tables(self):
        """Inicializa tablas específicas del planificador"""
        try:
            # Tabla de temas de estudio
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS study_topics (
                    topic_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    specialty TEXT DEFAULT 'general',
                    confidence_level TEXT NOT NULL,
                    last_studied TEXT,
                    next_review TEXT,
                    study_count INTEGER DEFAULT 0,
                    priority TEXT NOT NULL,
                    estimated_hours REAL DEFAULT 2.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (plan_id) REFERENCES study_plans (plan_id)
                )
            """)
            
            # Tabla de sesiones de estudio retrospectivo
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS retrospective_sessions (
                    session_id TEXT PRIMARY KEY,
                    topic_id TEXT NOT NULL,
                    old_confidence TEXT NOT NULL,
                    new_confidence TEXT NOT NULL,
                    session_duration_minutes INTEGER DEFAULT 0,
                    notes TEXT,
                    satisfaction_score INTEGER DEFAULT 5,
                    reviewed_at TEXT NOT NULL,
                    FOREIGN KEY (topic_id) REFERENCES study_topics (topic_id)
                )
            """)
            
            # Índices para mejor rendimiento
            self.database.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_study_topics_next_review 
                ON study_topics (next_review)
            """)
            
            self.database.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_study_topics_confidence 
                ON study_topics (confidence_level)
            """)
            
        except Exception as e:
            self.logger.error(f"Error initializing planner tables: {e}")
    
    def create_study_plan(self, title: str, specialty: str, topics: List[str]) -> str:
        """Crea un nuevo plan de estudio retrospectivo"""
        
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        
        try:
            # Crear plan principal
            self.database.execute_update("""
                INSERT INTO study_plans 
                (plan_id, title, specialty, topics, confidence_levels, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                plan_id,
                title,
                specialty,
                json.dumps(topics),
                json.dumps({}),  # Se llenará con los temas individuales
                datetime.now().isoformat()
            ))
            
            # Crear temas individuales con confianza inicial RED
            for topic_name in topics:
                self.add_topic_to_plan(
                    plan_id=plan_id,
                    topic_name=topic_name,
                    specialty=specialty,
                    initial_confidence=ConfidenceLevel.RED
                )
            
            self.logger.info(f"Created study plan: {plan_id} with {len(topics)} topics")
            return plan_id
            
        except Exception as e:
            self.logger.error(f"Error creating study plan: {e}")
            raise
    
    def add_topic_to_plan(self, plan_id: str, topic_name: str, 
                         specialty: str = "general",
                         initial_confidence: ConfidenceLevel = ConfidenceLevel.RED) -> str:
        """Agrega un tema a un plan existente"""
        
        topic_id = f"topic_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        
        # Calcular próxima revisión basada en confianza
        interval_days = self.confidence_intervals[initial_confidence]
        next_review = now + timedelta(days=interval_days)
        
        # Determinar prioridad basada en confianza
        priority = self._calculate_priority(initial_confidence, None)
        
        # Estimar tiempo de estudio
        estimated_hours = self.study_time_estimates[initial_confidence]
        
        try:
            self.database.execute_update("""
                INSERT INTO study_topics 
                (topic_id, plan_id, name, specialty, confidence_level, 
                 next_review, priority, estimated_hours, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                topic_id,
                plan_id,
                topic_name,
                specialty,
                initial_confidence.value,
                next_review.isoformat(),
                priority.value,
                estimated_hours,
                now.isoformat(),
                now.isoformat()
            ))
            
            self.logger.info(f"Added topic {topic_name} to plan {plan_id}")
            return topic_id
            
        except Exception as e:
            self.logger.error(f"Error adding topic to plan: {e}")
            raise
    
    def update_topic_confidence(self, topic_id: str, new_confidence: ConfidenceLevel,
                               session_duration_minutes: int = 0, notes: str = "",
                               satisfaction_score: int = 5) -> bool:
        """
        Actualiza la confianza de un tema después de estudiarlo
        Esta es la función core del sistema retrospectivo
        """
        
        try:
            # Obtener datos actuales del tema
            topic_data = self.database.execute_query(
                "SELECT * FROM study_topics WHERE topic_id = ?",
                (topic_id,)
            )
            
            if not topic_data:
                self.logger.error(f"Topic not found: {topic_id}")
                return False
            
            current_topic = topic_data[0]
            old_confidence = ConfidenceLevel(current_topic['confidence_level'])
            
            # Calcular nueva fecha de revisión
            interval_days = self.confidence_intervals[new_confidence]
            next_review = datetime.now() + timedelta(days=interval_days)
            
            # Calcular nueva prioridad
            new_priority = self._calculate_priority(new_confidence, datetime.now())
            
            # Actualizar tiempo estimado
            new_estimated_hours = self.study_time_estimates[new_confidence]
            
            # Actualizar tema en base de datos
            self.database.execute_update("""
                UPDATE study_topics 
                SET confidence_level = ?,
                    last_studied = ?,
                    next_review = ?,
                    study_count = study_count + 1,
                    priority = ?,
                    estimated_hours = ?,
                    updated_at = ?
                WHERE topic_id = ?
            """, (
                new_confidence.value,
                datetime.now().isoformat(),
                next_review.isoformat(),
                new_priority.value,
                new_estimated_hours,
                datetime.now().isoformat(),
                topic_id
            ))
            
            # Registrar sesión retrospectiva
            self._log_retrospective_session(
                topic_id=topic_id,
                old_confidence=old_confidence,
                new_confidence=new_confidence,
                session_duration_minutes=session_duration_minutes,
                notes=notes,
                satisfaction_score=satisfaction_score
            )
            
            self.logger.info(f"Updated topic {topic_id}: {old_confidence.value} -> {new_confidence.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating topic confidence: {e}")
            return False
    
    def _calculate_priority(self, confidence: ConfidenceLevel, 
                          last_studied: Optional[datetime]) -> StudyPriority:
        """Calcula prioridad basada en confianza y última vez estudiado"""
        
        # Mapeo directo de confianza a prioridad
        confidence_to_priority = {
            ConfidenceLevel.RED: StudyPriority.URGENT,
            ConfidenceLevel.ORANGE: StudyPriority.HIGH,
            ConfidenceLevel.YELLOW: StudyPriority.MEDIUM,
            ConfidenceLevel.GREEN: StudyPriority.LOW,
            ConfidenceLevel.BLUE: StudyPriority.OPTIONAL
        }
        
        base_priority = confidence_to_priority[confidence]
        
        # Ajustar prioridad si hace mucho que no se estudia
        if last_studied:
            days_since = (datetime.now() - last_studied).days
            interval = self.confidence_intervals[confidence]
            
            if days_since > interval * 1.5:  # 150% del intervalo recomendado
                # Aumentar prioridad
                if base_priority == StudyPriority.LOW:
                    return StudyPriority.MEDIUM
                elif base_priority == StudyPriority.MEDIUM:
                    return StudyPriority.HIGH
                elif base_priority == StudyPriority.OPTIONAL:
                    return StudyPriority.LOW
        
        return base_priority
    
    def _log_retrospective_session(self, topic_id: str, old_confidence: ConfidenceLevel,
                                  new_confidence: ConfidenceLevel, session_duration_minutes: int,
                                  notes: str, satisfaction_score: int):
        """Registra una sesión de estudio retrospectivo"""
        
        session_id = f"retro_{uuid.uuid4().hex[:12]}"
        
        try:
            self.database.execute_update("""
                INSERT INTO retrospective_sessions
                (session_id, topic_id, old_confidence, new_confidence,
                 session_duration_minutes, notes, satisfaction_score, reviewed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                topic_id,
                old_confidence.value,
                new_confidence.value,
                session_duration_minutes,
                notes,
                satisfaction_score,
                datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.logger.error(f"Error logging retrospective session: {e}")
    
    def get_topics_due_today(self, plan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene temas que deben estudiarse hoy"""
        
        today = datetime.now().date().isoformat()
        
        try:
            if plan_id:
                query = """
                    SELECT * FROM study_topics 
                    WHERE plan_id = ? AND DATE(next_review) <= ?
                    ORDER BY priority DESC, next_review ASC
                """
                params = (plan_id, today)
            else:
                query = """
                    SELECT * FROM study_topics 
                    WHERE DATE(next_review) <= ?
                    ORDER BY priority DESC, next_review ASC
                """
                params = (today,)
            
            results = self.database.execute_query(query, params)
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting topics due today: {e}")
            return []
    
    def get_plan_overview(self, plan_id: str) -> Dict[str, Any]:
        """Obtiene resumen completo de un plan"""
        
        try:
            # Datos del plan
            plan_data = self.database.execute_query(
                "SELECT * FROM study_plans WHERE plan_id = ?",
                (plan_id,)
            )
            
            if not plan_data:
                return {}
            
            plan = plan_data[0]
            
            # Estadísticas de temas
            topics_stats = self.database.execute_query("""
                SELECT 
                    confidence_level,
                    COUNT(*) as count,
                    AVG(estimated_hours) as avg_hours
                FROM study_topics 
                WHERE plan_id = ?
                GROUP BY confidence_level
            """, (plan_id,))
            
            # Temas pendientes hoy
            due_today = len(self.get_topics_due_today(plan_id))
            
            # Tiempo total estimado
            total_time = self.database.execute_query("""
                SELECT SUM(estimated_hours) as total_hours
                FROM study_topics 
                WHERE plan_id = ? AND confidence_level IN ('red', 'orange', 'yellow')
            """, (plan_id,))
            
            return {
                'plan': plan,
                'topics_by_confidence': {stat['confidence_level']: stat['count'] 
                                       for stat in topics_stats},
                'due_today': due_today,
                'estimated_total_hours': total_time[0]['total_hours'] if total_time else 0,
                'progress_percentage': self._calculate_progress_percentage(plan_id)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting plan overview: {e}")
            return {}
    
    def _calculate_progress_percentage(self, plan_id: str) -> float:
        """Calcula porcentaje de progreso del plan"""
        
        try:
            total_topics = self.database.execute_query(
                "SELECT COUNT(*) as count FROM study_topics WHERE plan_id = ?",
                (plan_id,)
            )
            
            green_blue_topics = self.database.execute_query(
                "SELECT COUNT(*) as count FROM study_topics WHERE plan_id = ? AND confidence_level IN ('green', 'blue')",
                (plan_id,)
            )
            
            if total_topics and total_topics[0]['count'] > 0:
                return (green_blue_topics[0]['count'] / total_topics[0]['count']) * 100
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating progress: {e}")
            return 0.0
    
    def get_study_recommendations(self, plan_id: str, available_hours: float = 2.0) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones de qué estudiar basado en tiempo disponible
        Algoritmo: prioriza por urgencia y distribución equilibrada
        """
        
        try:
            # Obtener todos los temas del plan con sus prioridades
            topics = self.database.execute_query("""
                SELECT * FROM study_topics 
                WHERE plan_id = ?
                ORDER BY 
                    CASE priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        WHEN 'optional' THEN 5
                    END,
                    next_review ASC
            """, (plan_id,))
            
            recommendations = []
            remaining_hours = available_hours
            
            for topic in topics:
                if remaining_hours <= 0:
                    break
                
                estimated_hours = topic['estimated_hours']
                
                # Si el tema cabe en el tiempo disponible
                if estimated_hours <= remaining_hours:
                    recommendations.append({
                        'topic': topic,
                        'recommended_duration_hours': estimated_hours,
                        'reason': self._get_recommendation_reason(topic)
                    })
                    remaining_hours -= estimated_hours
                
                # Si no cabe completo, sugerir sesión parcial para temas urgentes
                elif topic['priority'] in ['urgent', 'high'] and remaining_hours >= 0.5:
                    recommendations.append({
                        'topic': topic,
                        'recommended_duration_hours': remaining_hours,
                        'reason': f"Sesión parcial - tema {topic['priority']}"
                    })
                    remaining_hours = 0
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting study recommendations: {e}")
            return []
    
    def _get_recommendation_reason(self, topic: Dict[str, Any]) -> str:
        """Genera razón para la recomendación"""
        
        confidence = topic['confidence_level']
        priority = topic['priority']
        
        if priority == 'urgent':
            return f"Tema crítico ({confidence}) - requiere atención inmediata"
        elif priority == 'high':
            return f"Alta prioridad ({confidence}) - estudiar esta semana"
        elif priority == 'medium':
            return f"Prioridad media ({confidence}) - estudiar este mes"
        else:
            return f"Repaso de mantenimiento ({confidence})"
    
    def export_plan_data(self, plan_id: str) -> Dict[str, Any]:
        """Exporta todos los datos de un plan para backup"""
        
        try:
            plan_data = self.get_plan_overview(plan_id)
            
            topics = self.database.execute_query(
                "SELECT * FROM study_topics WHERE plan_id = ?",
                (plan_id,)
            )
            
            sessions = self.database.execute_query("""
                SELECT rs.* FROM retrospective_sessions rs
                JOIN study_topics st ON rs.topic_id = st.topic_id
                WHERE st.plan_id = ?
                ORDER BY rs.reviewed_at DESC
            """, (plan_id,))
            
            return {
                'plan_overview': plan_data,
                'topics': topics,
                'sessions': sessions,
                'exported_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting plan data: {e}")
            return {}

# Export main classes
__all__ = ['RetrospectiveStudyPlanner', 'ConfidenceLevel', 'StudyPriority', 'StudyTopic']