"""
MedStudy Pro - MedCards System
Spaced Repetition System optimized for medical education
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import random
import math

class CardDifficulty(Enum):
    """Card difficulty levels"""
    EASY = "easy"
    GOOD = "good"
    HARD = "hard"
    AGAIN = "again"

class CardType(Enum):
    """Types of medical cards"""
    BASIC = "basic"                    # Simple Q&A
    CLOZE = "cloze"                   # Fill in the blank
    IMAGE = "image"                   # Image identification
    CASE_STUDY = "case_study"         # Clinical scenarios
    DIFFERENTIAL = "differential"      # Differential diagnosis
    MECHANISM = "mechanism"           # Pathophysiology

@dataclass
class ReviewResult:
    """Result of a card review"""
    card_id: str
    difficulty: CardDifficulty
    time_taken_seconds: int
    correct: bool
    timestamp: datetime

class SRSAlgorithm:
    """Spaced Repetition Algorithm (based on Anki's SM-2 with medical optimizations)"""
    
    # Default intervals for medical content
    INITIAL_INTERVALS = {
        CardDifficulty.AGAIN: 0.0416,  # 1 hour (for medical facts)
        CardDifficulty.HARD: 1.0,      # 1 day
        CardDifficulty.GOOD: 1.0,      # 1 day
        CardDifficulty.EASY: 4.0       # 4 days
    }
    
    # Multipliers for different card types
    TYPE_MULTIPLIERS = {
        CardType.BASIC: 1.0,
        CardType.CLOZE: 1.1,
        CardType.IMAGE: 0.9,
        CardType.CASE_STUDY: 1.3,      # Longer intervals for complex cases
        CardType.DIFFERENTIAL: 1.2,
        CardType.MECHANISM: 1.4        # Longest for complex mechanisms
    }
    
    def __init__(self):
        self.logger = logging.getLogger('MedStudy.SRS')
    
    def calculate_next_interval(self, card_data: Dict[str, Any], 
                              difficulty: CardDifficulty,
                              card_type: CardType = CardType.BASIC) -> float:
        """Calculate next review interval in days"""
        
        current_interval = card_data.get('interval', 1.0)
        ease_factor = card_data.get('ease_factor', 2.5)
        repetitions = card_data.get('repetitions', 0)
        lapses = card_data.get('lapses', 0)
        
        # Get type multiplier
        type_mult = self.TYPE_MULTIPLIERS.get(card_type, 1.0)
        
        if difficulty == CardDifficulty.AGAIN:
            # Reset card to beginning
            new_interval = self.INITIAL_INTERVALS[CardDifficulty.AGAIN]
            new_ease_factor = max(1.3, ease_factor - 0.2)
            new_repetitions = 0
            new_lapses = lapses + 1
            
        elif difficulty == CardDifficulty.HARD:
            new_interval = current_interval * 1.2 * type_mult
            new_ease_factor = max(1.3, ease_factor - 0.15)
            new_repetitions = repetitions + 1
            new_lapses = lapses
            
        elif difficulty == CardDifficulty.GOOD:
            if repetitions == 0:
                new_interval = self.INITIAL_INTERVALS[CardDifficulty.GOOD]
            elif repetitions == 1:
                new_interval = 6.0  # 6 days for medical content
            else:
                new_interval = current_interval * ease_factor * type_mult
            
            new_ease_factor = ease_factor
            new_repetitions = repetitions + 1
            new_lapses = lapses
            
        elif difficulty == CardDifficulty.EASY:
            if repetitions == 0:
                new_interval = self.INITIAL_INTERVALS[CardDifficulty.EASY]
            else:
                new_interval = current_interval * ease_factor * 1.3 * type_mult
            
            new_ease_factor = ease_factor + 0.15
            new_repetitions = repetitions + 1
            new_lapses = lapses
        
        # Medical-specific adjustments
        if card_type in [CardType.CASE_STUDY, CardType.MECHANISM]:
            # More frequent reviews for complex medical concepts
            new_interval = min(new_interval, 30.0)  # Max 30 days
        
        # Adjust for lapses (medical facts need reinforcement)
        if lapses > 0:
            lapse_penalty = 0.8 ** min(lapses, 4)  # Max penalty at 4 lapses
            new_interval *= lapse_penalty
        
        return {
            'interval': max(0.0416, new_interval),  # Minimum 1 hour
            'ease_factor': new_ease_factor,
            'repetitions': new_repetitions,
            'lapses': new_lapses
        }

class MedCard:
    """Individual medical flashcard"""
    
    def __init__(self, card_id: str, card_type: CardType, question: str, 
                 answer: str, specialty: str = "general", 
                 tags: List[str] = None, image_path: str = None):
        self.card_id = card_id
        self.card_type = card_type
        self.question = question
        self.answer = answer
        self.specialty = specialty
        self.tags = tags or []
        self.image_path = image_path
        
        # SRS data
        self.interval = 1.0
        self.ease_factor = 2.5
        self.repetitions = 0
        self.lapses = 0
        self.due_date = datetime.now()
        self.last_reviewed = None
        
        # Statistics
        self.total_reviews = 0
        self.correct_reviews = 0
        self.average_time = 0.0
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for storage"""
        return {
            'card_id': self.card_id,
            'card_type': self.card_type.value,
            'question': self.question,
            'answer': self.answer,
            'specialty': self.specialty,
            'tags': json.dumps(self.tags),
            'image_path': self.image_path,
            'interval': self.interval,
            'ease_factor': self.ease_factor,
            'repetitions': self.repetitions,
            'lapses': self.lapses,
            'due_date': self.due_date.isoformat(),
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'total_reviews': self.total_reviews,
            'correct_reviews': self.correct_reviews,
            'average_time': self.average_time,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MedCard':
        """Create card from dictionary"""
        card = cls(
            card_id=data['card_id'],
            card_type=CardType(data['card_type']),
            question=data['question'],
            answer=data['answer'],
            specialty=data['specialty'],
            tags=json.loads(data.get('tags', '[]')),
            image_path=data.get('image_path')
        )
        
        # Load SRS data
        card.interval = data.get('interval', 1.0)
        card.ease_factor = data.get('ease_factor', 2.5)
        card.repetitions = data.get('repetitions', 0)
        card.lapses = data.get('lapses', 0)
        card.due_date = datetime.fromisoformat(data['due_date'])
        card.last_reviewed = datetime.fromisoformat(data['last_reviewed']) if data.get('last_reviewed') else None
        
        # Load statistics
        card.total_reviews = data.get('total_reviews', 0)
        card.correct_reviews = data.get('correct_reviews', 0)
        card.average_time = data.get('average_time', 0.0)
        card.created_at = datetime.fromisoformat(data['created_at'])
        card.modified_at = datetime.fromisoformat(data['modified_at'])
        
        return card
    
    def is_due(self) -> bool:
        """Check if card is due for review"""
        return datetime.now() >= self.due_date
    
    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.total_reviews == 0:
            return 0.0
        return (self.correct_reviews / self.total_reviews) * 100

class MedCardsSystem:
    """Complete MedCards system for spaced repetition learning"""
    
    def __init__(self, database):
        self.database = database
        self.srs = SRSAlgorithm()
        self.logger = logging.getLogger('MedStudy.MedCards')
        
        # Initialize database tables
        self._initialize_tables()
        
        self.logger.info("MedCards system initialized")
    
    def _initialize_tables(self):
        """Initialize database tables for MedCards"""
        try:
            # Cards table
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS medcards (
                    card_id TEXT PRIMARY KEY,
                    card_type TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    specialty TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '[]',
                    image_path TEXT,
                    interval REAL DEFAULT 1.0,
                    ease_factor REAL DEFAULT 2.5,
                    repetitions INTEGER DEFAULT 0,
                    lapses INTEGER DEFAULT 0,
                    due_date TEXT NOT NULL,
                    last_reviewed TEXT,
                    total_reviews INTEGER DEFAULT 0,
                    correct_reviews INTEGER DEFAULT 0,
                    average_time REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL
                )
            """)
            
            # Review history table
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS medcard_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    time_taken_seconds INTEGER NOT NULL,
                    correct BOOLEAN NOT NULL,
                    reviewed_at TEXT NOT NULL,
                    FOREIGN KEY (card_id) REFERENCES medcards (card_id)
                )
            """)
            
            # Study sessions table
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS medcard_sessions (
                    session_id TEXT PRIMARY KEY,
                    cards_reviewed INTEGER DEFAULT 0,
                    cards_correct INTEGER DEFAULT 0,
                    total_time_seconds INTEGER DEFAULT 0,
                    session_type TEXT DEFAULT 'review',
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            
            self.logger.info("MedCards database tables initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MedCards tables: {e}")
            raise
    
    def create_card(self, question: str, answer: str, card_type: CardType = CardType.BASIC,
                   specialty: str = "general", tags: List[str] = None, 
                   image_path: str = None) -> str:
        """Create a new MedCard"""
        
        # Generate unique card ID
        import uuid
        card_id = f"medcard_{uuid.uuid4().hex[:12]}"
        
        # Create card object
        card = MedCard(
            card_id=card_id,
            card_type=card_type,
            question=question,
            answer=answer,
            specialty=specialty,
            tags=tags or [],
            image_path=image_path
        )
        
        # Store in database
        try:
            card_data = card.to_dict()
            placeholders = ', '.join(['?' for _ in card_data])
            columns = ', '.join(card_data.keys())
            values = tuple(card_data.values())
            
            self.database.execute_update(
                f"INSERT INTO medcards ({columns}) VALUES ({placeholders})",
                values
            )
            
            self.logger.info(f"Created MedCard: {card_id} ({card_type.value})")
            return card_id
            
        except Exception as e:
            self.logger.error(f"Failed to create MedCard: {e}")
            raise
    
    def get_card(self, card_id: str) -> Optional[MedCard]:
        """Get a specific card by ID"""
        try:
            result = self.database.execute_query(
                "SELECT * FROM medcards WHERE card_id = ?",
                (card_id,)
            )
            
            if result:
                return MedCard.from_dict(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get card {card_id}: {e}")
            return None
    
    def get_due_cards(self, limit: int = 20, specialty: str = None) -> List[MedCard]:
        """Get cards that are due for review"""
        try:
            now = datetime.now().isoformat()
            
            if specialty:
                query = """
                    SELECT * FROM medcards 
                    WHERE due_date <= ? AND specialty = ?
                    ORDER BY due_date ASC 
                    LIMIT ?
                """
                params = (now, specialty, limit)
            else:
                query = """
                    SELECT * FROM medcards 
                    WHERE due_date <= ?
                    ORDER BY due_date ASC 
                    LIMIT ?
                """
                params = (now, limit)
            
            results = self.database.execute_query(query, params)
            return [MedCard.from_dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Failed to get due cards: {e}")
            return []
    
    def get_new_cards(self, limit: int = 10, specialty: str = None) -> List[MedCard]:
        """Get new cards that haven't been reviewed yet"""
        try:
            if specialty:
                query = """
                    SELECT * FROM medcards 
                    WHERE total_reviews = 0 AND specialty = ?
                    ORDER BY created_at ASC 
                    LIMIT ?
                """
                params = (specialty, limit)
            else:
                query = """
                    SELECT * FROM medcards 
                    WHERE total_reviews = 0
                    ORDER BY created_at ASC 
                    LIMIT ?
                """
                params = (limit,)
            
            results = self.database.execute_query(query, params)
            return [MedCard.from_dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Failed to get new cards: {e}")
            return []
    
    def review_card(self, card_id: str, difficulty: CardDifficulty, 
                   time_taken_seconds: int, correct: bool) -> bool:
        """Process a card review and update SRS data"""
        
        try:
            # Get current card
            card = self.get_card(card_id)
            if not card:
                self.logger.error(f"Card not found: {card_id}")
                return False
            
            # Calculate new SRS values
            card_data = {
                'interval': card.interval,
                'ease_factor': card.ease_factor,
                'repetitions': card.repetitions,
                'lapses': card.lapses
            }
            
            new_srs_data = self.srs.calculate_next_interval(
                card_data, difficulty, card.card_type
            )
            
            # Update card
            card.interval = new_srs_data['interval']
            card.ease_factor = new_srs_data['ease_factor']
            card.repetitions = new_srs_data['repetitions']
            card.lapses = new_srs_data['lapses']
            
            # Calculate new due date
            card.due_date = datetime.now() + timedelta(days=card.interval)
            card.last_reviewed = datetime.now()
            
            # Update statistics
            card.total_reviews += 1
            if correct:
                card.correct_reviews += 1
            
            # Update average time (weighted average)
            if card.total_reviews == 1:
                card.average_time = time_taken_seconds
            else:
                # Weighted average with more weight on recent reviews
                weight = 0.3
                card.average_time = (weight * time_taken_seconds + 
                                   (1 - weight) * card.average_time)
            
            card.modified_at = datetime.now()
            
            # Update in database
            self._update_card_in_db(card)
            
            # Log review
            self._log_review(card_id, difficulty, time_taken_seconds, correct)
            
            self.logger.info(f"Reviewed card {card_id}: {difficulty.value}, next in {card.interval:.1f} days")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to review card {card_id}: {e}")
            return False
    
    def _update_card_in_db(self, card: MedCard):
        """Update card data in database"""
        card_data = card.to_dict()
        
        # Remove card_id from data (it's the primary key)
        card_id = card_data.pop('card_id')
        
        # Build update query
        set_clause = ', '.join([f"{key} = ?" for key in card_data.keys()])
        values = list(card_data.values()) + [card_id]
        
        self.database.execute_update(
            f"UPDATE medcards SET {set_clause} WHERE card_id = ?",
            tuple(values)
        )
    
    def _log_review(self, card_id: str, difficulty: CardDifficulty, 
                   time_taken: int, correct: bool):
        """Log review in history table"""
        self.database.execute_update("""
            INSERT INTO medcard_reviews 
            (card_id, difficulty, time_taken_seconds, correct, reviewed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            card_id,
            difficulty.value,
            time_taken,
            correct,
            datetime.now().isoformat()
        ))
    
    def start_review_session(self, session_type: str = "review") -> str:
        """Start a new review session"""
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        self.database.execute_update("""
            INSERT INTO medcard_sessions (session_id, session_type, started_at)
            VALUES (?, ?, ?)
        """, (session_id, session_type, datetime.now().isoformat()))
        
        self.logger.info(f"Started review session: {session_id}")
        return session_id
    
    def complete_review_session(self, session_id: str, cards_reviewed: int, 
                              cards_correct: int, total_time: int):
        """Complete a review session"""
        self.database.execute_update("""
            UPDATE medcard_sessions 
            SET cards_reviewed = ?, cards_correct = ?, total_time_seconds = ?, completed_at = ?
            WHERE session_id = ?
        """, (
            cards_reviewed,
            cards_correct,
            total_time,
            datetime.now().isoformat(),
            session_id
        ))
        
        self.logger.info(f"Completed session {session_id}: {cards_reviewed} cards, {cards_correct} correct")
    
    def get_cards_by_specialty(self, specialty: str) -> List[MedCard]:
        """Get all cards for a specific medical specialty"""
        try:
            results = self.database.execute_query(
                "SELECT * FROM medcards WHERE specialty = ? ORDER BY created_at DESC",
                (specialty,)
            )
            return [MedCard.from_dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Failed to get cards for specialty {specialty}: {e}")
            return []
    
    def search_cards(self, query: str) -> List[MedCard]:
        """Search cards by question or answer content"""
        try:
            search_query = f"%{query}%"
            results = self.database.execute_query("""
                SELECT * FROM medcards 
                WHERE question LIKE ? OR answer LIKE ?
                ORDER BY created_at DESC
            """, (search_query, search_query))
            
            return [MedCard.from_dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Failed to search cards: {e}")
            return []
    
    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily review statistics"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            # Get reviews for the day
            reviews = self.database.execute_query("""
                SELECT COUNT(*) as total, SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct
                FROM medcard_reviews 
                WHERE DATE(reviewed_at) = ?
            """, (date_str,))
            
            # Get due cards count
            due_cards = self.database.execute_query("""
                SELECT COUNT(*) as count
                FROM medcards 
                WHERE DATE(due_date) <= ?
            """, (date_str,))
            
            # Get new cards count
            new_cards = self.database.execute_query("""
                SELECT COUNT(*) as count
                FROM medcards 
                WHERE total_reviews = 0
            """)
            
            return {
                'date': date_str,
                'reviews_total': reviews[0]['total'] if reviews else 0,
                'reviews_correct': reviews[0]['correct'] if reviews else 0,
                'cards_due': due_cards[0]['count'] if due_cards else 0,
                'cards_new': new_cards[0]['count'] if new_cards else 0,
                'success_rate': (reviews[0]['correct'] / reviews[0]['total'] * 100) 
                               if reviews and reviews[0]['total'] > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get daily stats: {e}")
            return {}
    
    def get_specialty_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by medical specialty"""
        try:
            results = self.database.execute_query("""
                SELECT 
                    specialty,
                    COUNT(*) as total_cards,
                    SUM(CASE WHEN total_reviews = 0 THEN 1 ELSE 0 END) as new_cards,
                    SUM(CASE WHEN due_date <= datetime('now') THEN 1 ELSE 0 END) as due_cards,
                    AVG(CASE WHEN total_reviews > 0 THEN correct_reviews * 100.0 / total_reviews ELSE 0 END) as avg_success_rate
                FROM medcards 
                GROUP BY specialty
                ORDER BY total_cards DESC
            """)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to get specialty stats: {e}")
            return []
    
    def delete_card(self, card_id: str) -> bool:
        """Delete a card and its review history"""
        try:
            # Delete reviews first (foreign key constraint)
            self.database.execute_update(
                "DELETE FROM medcard_reviews WHERE card_id = ?",
                (card_id,)
            )
            
            # Delete card
            self.database.execute_update(
                "DELETE FROM medcards WHERE card_id = ?",
                (card_id,)
            )
            
            self.logger.info(f"Deleted card: {card_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete card {card_id}: {e}")
            return False
    
    def export_cards(self, specialty: str = None) -> List[Dict[str, Any]]:
        """Export cards for backup or sharing"""
        try:
            if specialty:
                results = self.database.execute_query(
                    "SELECT * FROM medcards WHERE specialty = ?",
                    (specialty,)
                )
            else:
                results = self.database.execute_query("SELECT * FROM medcards")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to export cards: {e}")
            return []
    
    def import_cards(self, cards_data: List[Dict[str, Any]]) -> int:
        """Import cards from external source"""
        imported_count = 0
        
        for card_data in cards_data:
            try:
                # Validate required fields
                required_fields = ['question', 'answer']
                if not all(field in card_data for field in required_fields):
                    continue
                
                # Create card
                card_id = self.create_card(
                    question=card_data['question'],
                    answer=card_data['answer'],
                    card_type=CardType(card_data.get('card_type', 'basic')),
                    specialty=card_data.get('specialty', 'general'),
                    tags=json.loads(card_data.get('tags', '[]')),
                    image_path=card_data.get('image_path')
                )
                
                if card_id:
                    imported_count += 1
                    
            except Exception as e:
                self.logger.warning(f"Failed to import card: {e}")
                continue
        
        self.logger.info(f"Imported {imported_count} cards")
        return imported_count

# Export main classes
__all__ = ['MedCardsSystem', 'MedCard', 'CardType', 'CardDifficulty', 'ReviewResult']