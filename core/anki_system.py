"""
Sistema Anki completo con algoritmo de repetición espaciada (SRS)
"""
import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field
import json

from utils.logging import get_logger

class ReviewResult(Enum):
    """Resultados posibles de una revisión"""
    AGAIN = 1      # Muy difícil, revisar pronto
    HARD = 2       # Difícil, pero recordado
    GOOD = 3       # Recordado sin problemas
    EASY = 4       # Muy fácil

class CardState(Enum):
    """Estados de una tarjeta"""
    NEW = "new"           # Nueva, nunca vista
    LEARNING = "learning" # En proceso de aprendizaje
    REVIEW = "review"     # En revisión regular
    RELEARNING = "relearning" # Re-aprendiendo después de olvido

@dataclass
class StudySettings:
    """Configuración del sistema de estudio"""
    # Límites diarios
    new_cards_per_day: int = 20
    review_cards_per_day: int = 100
    
    # Intervalos iniciales (minutos)
    learning_steps: List[int] = field(default_factory=lambda: [1, 10])
    relearning_steps: List[int] = field(default_factory=lambda: [10])
    
    # Graduación
    graduating_interval: int = 1  # días
    easy_interval: int = 4        # días
    
    # Factores de dificultad
    starting_ease: float = 2.5
    easy_bonus: float = 1.3
    hard_factor: float = 1.2
    new_interval_factor: float = 0.0
    
    # Límites
    minimum_interval: int = 1     # días
    maximum_interval: int = 36500 # ~100 años
    
    # Lapsos
    lapse_multiplier: float = 0.0
    minimum_lapse_interval: int = 1

@dataclass
class ReviewSession:
    """Sesión de revisión activa"""
    id: str
    started_at: datetime
    settings: StudySettings
    cards_studied: int = 0
    cards_new: int = 0
    cards_learning: int = 0
    cards_review: int = 0
    total_time: float = 0.0
    performance_stats: Dict[ReviewResult, int] = field(default_factory=lambda: {
        ReviewResult.AGAIN: 0,
        ReviewResult.HARD: 0,
        ReviewResult.GOOD: 0,
        ReviewResult.EASY: 0
    })

class AnkiSRSEngine:
    """Motor del algoritmo de repetición espaciada de Anki"""
    
    def __init__(self, settings: StudySettings = None):
        self.settings = settings or StudySettings()
        self.logger = get_logger("AnkiSRS")
    
    def calculate_next_interval(self, card, result: ReviewResult, 
                              current_time: datetime = None) -> Tuple[int, float, datetime]:
        """
        Calcula el próximo intervalo basado en el algoritmo SRS de Anki
        
        Returns:
            Tuple[interval_days, ease_factor, next_due_date]
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        # Obtener estado actual
        interval = card.interval
        ease_factor = card.ease_factor
        repetitions = card.repetitions
        
        if result == ReviewResult.AGAIN:
            # Tarjeta olvidada - resetear progreso
            new_interval = self._calculate_lapse_interval(interval)
            ease_factor = max(1.3, ease_factor - 0.2)  # Reducir facilidad
            repetitions = 0
            
        elif result == ReviewResult.HARD:
            # Difícil pero recordada
            new_interval = max(1, int(interval * self.settings.hard_factor))
            ease_factor = max(1.3, ease_factor - 0.15)
            repetitions += 1
            
        elif result == ReviewResult.GOOD:
            # Respuesta correcta normal
            if repetitions == 0:
                new_interval = self.settings.graduating_interval
            elif repetitions == 1:
                new_interval = self.settings.easy_interval
            else:
                new_interval = int(interval * ease_factor)
            repetitions += 1
            
        elif result == ReviewResult.EASY:
            # Muy fácil
            if repetitions == 0:
                new_interval = self.settings.easy_interval
            else:
                new_interval = int(interval * ease_factor * self.settings.easy_bonus)
            ease_factor += 0.15
            repetitions += 1
        
        # Aplicar límites
        new_interval = max(self.settings.minimum_interval, 
                          min(new_interval, self.settings.maximum_interval))
        
        # Calcular fecha de vencimiento
        next_due = current_time + timedelta(days=new_interval)
        
        return new_interval, ease_factor, next_due
    
    def _calculate_lapse_interval(self, previous_interval: int) -> int:
        """Calcula el intervalo después de un lapso (olvido)"""
        return max(
            self.settings.minimum_lapse_interval,
            int(previous_interval * self.settings.lapse_multiplier)
        )
    
    def get_card_state(self, card) -> CardState:
        """Determina el estado actual de una tarjeta"""
        if card.repetitions == 0:
            return CardState.NEW
        elif card.interval < self.settings.graduating_interval:
            return CardState.LEARNING
        else:
            return CardState.REVIEW
    
    def is_card_due(self, card, current_time: datetime = None) -> bool:
        """Verifica si una tarjeta debe ser revisada"""
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        if not card.due_date:
            return True  # Nueva tarjeta
        
        return card.due_date <= current_time
    
    def add_fuzz_to_interval(self, interval: int) -> int:
        """Agrega variación aleatoria al intervalo para evitar patrones"""
        if interval < 2:
            return interval
        
        # Aplicar fuzz del 5% al 25%
        fuzz_factor = 0.05 + (random.random() * 0.20)
        fuzz_amount = int(interval * fuzz_factor)
        
        # Aplicar aleatoriamente hacia arriba o abajo
        if random.choice([True, False]):
            return interval + fuzz_amount
        else:
            return max(1, interval - fuzz_amount)

class AnkiCardManager:
    """Gestor de tarjetas Anki con funcionalidades avanzadas"""
    
    def __init__(self, database_manager, llm_manager=None):
        self.db = database_manager
        self.llm = llm_manager
        self.srs_engine = AnkiSRSEngine()
        self.logger = get_logger("AnkiCardManager")
        
        # Estadísticas de sesión
        self.current_session = None
    
    def start_study_session(self, settings: StudySettings = None) -> ReviewSession:
        """Inicia una nueva sesión de estudio"""
        import uuid
        
        session = ReviewSession(
            id=str(uuid.uuid4()),
            started_at=datetime.now(timezone.utc),
            settings=settings or StudySettings()
        )
        
        self.current_session = session
        self.logger.info(f"Sesión de estudio iniciada: {session.id}")
        
        return session
    
    def end_study_session(self) -> Optional[Dict[str, Any]]:
        """Finaliza la sesión de estudio actual"""
        if not self.current_session:
            return None
        
        session = self.current_session
        session_duration = (datetime.now(timezone.utc) - session.started_at).total_seconds()
        
        # Calcular estadísticas
        stats = {
            'session_id': session.id,
            'duration_seconds': session_duration,
            'cards_studied': session.cards_studied,
            'cards_new': session.cards_new,
            'cards_learning': session.cards_learning,
            'cards_review': session.cards_review,
            'performance': {
                'again': session.performance_stats[ReviewResult.AGAIN],
                'hard': session.performance_stats[ReviewResult.HARD],
                'good': session.performance_stats[ReviewResult.GOOD],
                'easy': session.performance_stats[ReviewResult.EASY]
            }
        }
        
        # Calcular accuracy
        total_answers = sum(session.performance_stats.values())
        if total_answers > 0:
            correct_answers = (session.performance_stats[ReviewResult.HARD] + 
                             session.performance_stats[ReviewResult.GOOD] + 
                             session.performance_stats[ReviewResult.EASY])
            stats['accuracy'] = correct_answers / total_answers
        else:
            stats['accuracy'] = 0.0
        
        # Guardar estadísticas en base de datos
        self._save_session_stats(stats)
        
        self.logger.info(f"Sesión finalizada: {stats}")
        self.current_session = None
        
        return stats
    
    def get_cards_for_study(self, limit: int = 50) -> List:
        """Obtiene tarjetas para estudiar ordenadas por prioridad"""
        # Obtener tarjetas vencidas
        due_cards = self.db.get_due_cards(limit * 2)  # Obtener más para filtrar
        
        if not due_cards:
            return []
        
        # Ordenar por prioridad
        prioritized_cards = self._prioritize_cards(due_cards)
        
        return prioritized_cards[:limit]
    
    def _prioritize_cards(self, cards: List) -> List:
        """Ordena las tarjetas por prioridad de estudio"""
        def priority_score(card):
            state = self.srs_engine.get_card_state(card)
            
            # Días de retraso
            if card.due_date:
                days_overdue = (datetime.now(timezone.utc) - card.due_date).days
            else:
                days_overdue = 0
            
            # Puntuación base por estado
            base_scores = {
                CardState.NEW: 1000,
                CardState.LEARNING: 2000,
                CardState.RELEARNING: 3000,
                CardState.REVIEW: 100
            }
            
            score = base_scores.get(state, 0)
            
            # Agregar penalización por retraso
            score += days_overdue * 10
            
            # Penalizar tarjetas muy fáciles (ease factor alto)
            score -= (card.ease_factor - 2.5) * 50
            
            return score
        
        return sorted(cards, key=priority_score, reverse=True)
    
    def review_card(self, card_id: str, result: ReviewResult, 
                   response_time: float = None) -> Dict[str, Any]:
        """Procesa la revisión de una tarjeta"""
        card = self.db.get_anki_card(card_id)
        if not card:
            raise ValueError(f"Tarjeta no encontrada: {card_id}")
        
        current_time = datetime.now(timezone.utc)
        
        # Calcular próximo intervalo
        new_interval, new_ease, next_due = self.srs_engine.calculate_next_interval(
            card, result, current_time
        )
        
        # Aplicar fuzz al intervalo
        if new_interval > 1:
            new_interval = self.srs_engine.add_fuzz_to_interval(new_interval)
            next_due = current_time + timedelta(days=new_interval)
        
        # Actualizar tarjeta
        card.interval = new_interval
        card.ease_factor = new_ease
        card.repetitions += 1 if result != ReviewResult.AGAIN else 0
        card.due_date = next_due
        card.last_reviewed = current_time
        card.review_count += 1
        
        # Guardar en base de datos
        self.db.update_anki_card(card)
        
        # Actualizar estadísticas de sesión
        if self.current_session:
            self.current_session.cards_studied += 1
            self.current_session.performance_stats[result] += 1
            
            if response_time:
                self.current_session.total_time += response_time
            
            # Clasificar tipo de tarjeta
            state = self.srs_engine.get_card_state(card)
            if state == CardState.NEW:
                self.current_session.cards_new += 1
            elif state == CardState.LEARNING:
                self.current_session.cards_learning += 1
            else:
                self.current_session.cards_review += 1
        
        # Preparar respuesta
        review_info = {
            'card_id': card_id,
            'result': result.name,
            'new_interval': new_interval,
            'new_ease_factor': new_ease,
            'next_due_date': next_due.isoformat(),
            'state': self.srs_engine.get_card_state(card).value,
            'repetitions': card.repetitions
        }
        
        self.logger.debug(f"Tarjeta revisada: {review_info}")
        
        return review_info
    
    def generate_card_with_ai(self, topic: str, difficulty: str = "medium", 
                            card_type: str = "basic") -> Optional[str]:
        """Genera una tarjeta usando IA"""
        if not self.llm:
            self.logger.warning("LLM no disponible para generar tarjetas")
            return None
        
        try:
            card_data = self.llm.generate_anki_card(topic, difficulty)
            
            if card_data and card_data.get('question') and card_data.get('answer'):
                from data.models import AnkiCard
                
                card = AnkiCard(
                    question=card_data['question'],
                    answer=card_data['answer'],
                    card_type=card_type,
                    topic=topic,
                    difficulty=difficulty,
                    source="AI Generated",
                    tags=f"ai,{topic.lower().replace(' ', '_')}"
                )
                
                card_id = self.db.create_anki_card(card)
                self.logger.info(f"Tarjeta generada con IA: {card_id}")
                
                return card_id
            else:
                self.logger.error("IA no pudo generar tarjeta válida")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generando tarjeta con IA: {e}")
            return None
    
    def bulk_generate_cards(self, topics: List[str], cards_per_topic: int = 5,
                          difficulty: str = "medium") -> List[str]:
        """Genera múltiples tarjetas para varios temas"""
        generated_cards = []
        
        for topic in topics:
            self.logger.info(f"Generando {cards_per_topic} tarjetas para: {topic}")
            
            for i in range(cards_per_topic):
                try:
                    card_id = self.generate_card_with_ai(topic, difficulty)
                    if card_id:
                        generated_cards.append(card_id)
                        
                    # Pequeña pausa para no sobrecargar el LLM
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error generando tarjeta {i+1} para {topic}: {e}")
                    continue
        
        self.logger.info(f"Generadas {len(generated_cards)} tarjetas en total")
        return generated_cards
    
    def import_cards_from_text(self, text_content: str, topic: str = "",
                             delimiter: str = "\t") -> List[str]:
        """Importa tarjetas desde texto (formato: pregunta[delimiter]respuesta)"""
        lines = text_content.strip().split('\n')
        imported_cards = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Ignorar líneas vacías y comentarios
                continue
            
            parts = line.split(delimiter)
            if len(parts) != 2:
                self.logger.warning(f"Línea {line_num} mal formateada: {line}")
                continue
            
            question, answer = parts
            question = question.strip()
            answer = answer.strip()
            
            if not question or not answer:
                self.logger.warning(f"Línea {line_num} contiene campos vacíos")
                continue
            
            try:
                from data.models import AnkiCard
                
                card = AnkiCard(
                    question=question,
                    answer=answer,
                    topic=topic,
                    source="Text Import",
                    tags=f"imported,{topic.lower().replace(' ', '_')}" if topic else "imported"
                )
                
                card_id = self.db.create_anki_card(card)
                imported_cards.append(card_id)
                
            except Exception as e:
                self.logger.error(f"Error importando línea {line_num}: {e}")
                continue
        
        self.logger.info(f"Importadas {len(imported_cards)} tarjetas")
        return imported_cards
    
    def export_cards_to_anki_format(self, card_ids: List[str] = None,
                                  topic: str = None) -> str:
        """Exporta tarjetas al formato .txt de Anki"""
        if card_ids:
            cards = [self.db.get_anki_card(cid) for cid in card_ids]
            cards = [c for c in cards if c]  # Filtrar None
        elif topic:
            cards = self.db.get_cards_by_topic(topic)
        else:
            # Exportar todas las tarjetas activas
            with self.db.get_connection() as conn:
                results = conn.execute(
                    "SELECT * FROM anki_cards WHERE is_active = 1"
                ).fetchall()
                cards = [self.db._row_to_anki_card(row) for row in results]
        
        if not cards:
            return ""
        
        # Formato Anki: Front\tBack\tTags
        lines = []
        for card in cards:
            # Escapar tabs y newlines
            front = card.question.replace('\t', ' ').replace('\n', '<br>')
            back = card.answer.replace('\t', ' ').replace('\n', '<br>')
            tags = card.tags.replace('\t', ' ')
            
            lines.append(f"{front}\t{back}\t{tags}")
        
        return '\n'.join(lines)
    
    def get_study_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de estudio"""
        with self.db.get_connection() as conn:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Tarjetas revisadas por día
            daily_reviews = conn.execute("""
                SELECT DATE(last_reviewed) as review_date, COUNT(*) as count
                FROM anki_cards 
                WHERE last_reviewed >= ? AND last_reviewed <= ?
                GROUP BY DATE(last_reviewed)
                ORDER BY review_date
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            # Estadísticas generales
            stats = self.db.get_card_statistics()
            
            # Rendimiento por dificultad
            difficulty_performance = conn.execute("""
                SELECT difficulty, 
                       AVG(ease_factor) as avg_ease,
                       AVG(interval) as avg_interval,
                       COUNT(*) as card_count
                FROM anki_cards 
                WHERE is_active = 1 AND last_reviewed >= ?
                GROUP BY difficulty
            """, (start_date.isoformat(),)).fetchall()
            
            # Streak actual (días consecutivos estudiando)
            current_streak = self._calculate_study_streak()
            
            return {
                'period_days': days,
                'general_stats': stats,
                'daily_reviews': [dict(row) for row in daily_reviews],
                'difficulty_performance': [dict(row) for row in difficulty_performance],
                'current_streak': current_streak,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
    
    def _calculate_study_streak(self) -> int:
        """Calcula la racha actual de días estudiando"""
        with self.db.get_connection() as conn:
            # Obtener últimos 100 días con actividad
      