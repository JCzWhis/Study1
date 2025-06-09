"""
MedStudy Pro - Retrospective Study Planner
Based on Ali Abdaal's Spaced Repetition Spreadsheet methodology
Focus on what you DON'T know rather than predicting the future
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class ConfidenceLevel(Enum):
    """Confidence levels for topics (color-coded like Ali's system)"""
    RED = "red"           # Don't know at all
    ORANGE = "orange"     # Know a little bit
    YELLOW = "yellow"     # Know somewhat
    GREEN = "green"       # Know well
    BLUE = "blue"         # Know very well

class StudyPriority(Enum):
    """Study priority based on confidence and time since last study"""
    URGENT = "urgent"       # Red topics, or topics not studied in too long
    HIGH = "high"          # Orange topics, or overdue yellow topics
    MEDIUM = "medium"      # Yellow topics on schedule
    LOW = "low"           # Green topics
    OPTIONAL = "optional"  # Blue topics

@dataclass
class StudyTopic:
    """Individual study topic with retrospective tracking"""
    topic_id: str
    name: str
    specialty: str
    confidence_level: ConfidenceLevel
    last_studied: Optional[datetime]
    study_count: int
    time_spent_minutes: int
    notes: str
    created_at: datetime
    updated_at: datetime

@dataclass
class StudySession:
    """Record of a study session for retrospective analysis"""
    session_id: str
    topic_id: str
    duration_minutes: int
    confidence_before: ConfidenceLevel
    confidence_after: ConfidenceLevel
    notes: str
    session_date: datetime

class RetrospectiveStudyPlanner:
    """
    Study planner based on Ali Abdaal's retrospective methodology
    
    Core principles:
    1. Don't predict the future - focus on what you don't know NOW
    2. Color-code topics by confidence level
    3. Study topics with lowest confidence first
    4. Track actual study sessions, not planned ones
    5. Adjust priorities based on real data, not predictions
    """
    
    def __init__(self, database):
        self.database = database
        self.logger = logging.getLogger('MedStudy.StudyPlanner')
        
        # Initialize database tables if needed
        self._ensure_tables()
        
        self.logger.info("Retrospective Study Planner initialized")
    
    def _ensure_tables(self):
        """Ensure study planner tables exist"""
        try:
            # Study topics table (enhanced from basic schema)
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS study_topics (
                    topic_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    specialty TEXT DEFAULT 'general',
                    confidence_level TEXT DEFAULT 'red',
                    last_studied TEXT,
                    study_count INTEGER DEFAULT 0,
                    time_spent_minutes INTEGER DEFAULT 0,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (plan_id) REFERENCES study_plans (plan_id)
                )
            """)
            
            # Study session logs
            self.database.execute_update("""
                CREATE TABLE IF NOT EXISTS study_session_logs (
                    session_id TEXT PRIMARY KEY,
                    topic_id TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    confidence_before TEXT NOT NULL,
                    confidence_after TEXT NOT NULL,
                    session_notes TEXT DEFAULT '',
                    session_date TEXT NOT NULL,
                    FOREIGN KEY (topic_id) REFERENCES study_topics (topic_id)
                )
            """)
            
            # Create indexes for better performance
            self.database.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_study_topics_confidence ON study_topics (confidence_level)
            """)
            
            self.database.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_study_topics_last_studied ON study_topics (last_studied)
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to ensure study planner tables: {e}")
    
    def create_study_plan(self, title: str, specialty: str, 
                         topics: List[str]) -> str:
        """Create a new study plan with initial topics"""
        
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        
        try:
            # Create study plan
            self.database.execute_update("""
                INSERT INTO study_plans 
                (plan_id, title, specialty, topics, confidence_levels, last_studied, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id,
                title,
                specialty,
                json.dumps(topics),
                json.dumps({}),  # Will be populated as topics are studied
                json.dumps({}),  # Will be populated as topics are studied
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Create individual topic entries (all start as RED - unknown)
            for topic_name in topics:
                self.add_topic_to_plan(plan_id, topic_name, specialty)
            
            self.logger.info(f"Created study plan {plan_id}: {title} with {len(topics)} topics")
            return plan_id
            
        except Exception as e:
            self.logger.error(f"Failed to create study plan: {e}")
            raise
    
    def add_topic_to_plan(self, plan_id: str, topic_name: str, 
                         specialty: str = "general") -> str:
        """Add a new topic to an existing study plan"""
        
        topic_id = f"topic_{uuid.uuid4().hex[:8]}"
        
        try:
            self.database.execute_update("""
                INSERT INTO study_topics 
                (topic_id, plan_id, name, specialty, confidence_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                topic_id,
                plan_id,
                topic_name,
                specialty,
                ConfidenceLevel.RED.value,  # Always start as RED (don't know)
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            self.logger.info(f"Added topic {topic_name} to plan {plan_id}")
            return topic_id
            
        except Exception as e:
            self.logger.error(f"Failed to add topic: {e}")
            raise
    
    def get_study_priorities_today(self, plan_id: str = None) -> List[Dict[str, Any]]:
        """
        Get today's study priorities based on Ali Abdaal's methodology
        
        Priority logic:
        1. RED topics (don't know at all) - URGENT
        2. Topics not studied in 7+ days - HIGH
        3. ORANGE topics (know a little) - HIGH  
        4. YELLOW topics not studied in 3+ days - MEDIUM
        5. GREEN topics not studied in 7+ days - LOW
        6. BLUE topics - OPTIONAL
        """
        
        try:
            # Base query for topics
            where_clause = "WHERE 1=1"
            params = []
            
            if plan_id:
                where_clause += " AND plan_id = ?"
                params.append(plan_id)
            
            topics = self.database.execute_query(f"""
                SELECT * FROM study_topics {where_clause}
                ORDER BY confidence_level, last_studied ASC
            """, tuple(params))
            
            # Calculate priorities for each topic
            prioritized_topics = []
            today = datetime.now()
            
            for topic in topics:
                priority_info = self._calculate_topic_priority(topic, today)
                
                topic_data = {
                    'topic_id': topic['topic_id'],
                    'name': topic['name'],
                    'specialty': topic['specialty'],
                    'confidence_level': topic['confidence_level'],
                    'last_studied': topic['last_studied'],
                    'study_count': topic['study_count'],
                    'time_spent_minutes': topic['time_spent_minutes'],
                    'priority': priority_info['priority'],
                    'priority_reason': priority_info['reason'],
                    'days_since_study': priority_info['days_since_study'],
                    'recommended_duration': priority_info['recommended_duration']
                }
                
                prioritized_topics.append(topic_data)
            
            # Sort by priority (URGENT first, then HIGH, etc.)
            priority_order = {
                StudyPriority.URGENT.value: 0,
                StudyPriority.HIGH.value: 1,
                StudyPriority.MEDIUM.value: 2,
                StudyPriority.LOW.value: 3,
                StudyPriority.OPTIONAL.value: 4
            }
            
            prioritized_topics.sort(key=lambda x: priority_order.get(x['priority'], 5))
            
            self.logger.info(f"Generated study priorities: {len(prioritized_topics)} topics")
            return prioritized_topics
            
        except Exception as e:
            self.logger.error(f"Failed to get study priorities: {e}")
            return []
    
    def _calculate_topic_priority(self, topic: Dict[str, Any], 
                                today: datetime) -> Dict[str, Any]:
        """Calculate priority for a single topic based on Ali's methodology"""
        
        confidence = ConfidenceLevel(topic['confidence_level'])
        last_studied_str = topic['last_studied']
        
        # Calculate days since last study
        if last_studied_str:
            last_studied = datetime.fromisoformat(last_studied_str)
            days_since_study = (today - last_studied).days
        else:
            days_since_study = 999  # Never studied
        
        # Ali Abdaal's priority logic
        if confidence == ConfidenceLevel.RED:
            # RED topics are always URGENT
            priority = StudyPriority.URGENT
            reason = "No conoces este tema - prioridad máxima"
            duration = 60  # 1 hour for unknown topics
            
        elif days_since_study >= 7:
            # Any topic not studied in a week becomes HIGH priority
            priority = StudyPriority.HIGH
            reason = f"No estudiado en {days_since_study} días"
            duration = 45
            
        elif confidence == ConfidenceLevel.ORANGE:
            # ORANGE topics are HIGH priority (know a little)
            priority = StudyPriority.HIGH
            reason = "Conocimiento básico - necesita refuerzo"
            duration = 45
            
        elif confidence == ConfidenceLevel.YELLOW and days_since_study >= 3:
            # YELLOW topics become MEDIUM priority after 3 days
            priority = StudyPriority.MEDIUM
            reason = f"Conocimiento intermedio - repasar cada 3 días"
            duration = 30
            
        elif confidence == ConfidenceLevel.GREEN and days_since_study >= 7:
            # GREEN topics become LOW priority after a week
            priority = StudyPriority.LOW
            reason = "Buen conocimiento - repaso semanal"
            duration = 20
            
        elif confidence == ConfidenceLevel.BLUE:
            # BLUE topics are OPTIONAL (know very well)
            priority = StudyPriority.OPTIONAL
            reason = "Excelente conocimiento - repaso opcional"
            duration = 15
            
        else:
            # Default case
            priority = StudyPriority.MEDIUM
            reason = "Repaso de rutina"
            duration = 30
        
        return {
            'priority': priority.value,
            'reason': reason,
            'days_since_study': days_since_study,
            'recommended_duration': duration
        }
    
    def get_study_plan_overview(self, plan_id: str) -> Dict[str, Any]:
        """Get overview of study plan progress (Ali's spreadsheet view)"""
        
        try:
            # Get plan basic info
            plan = self.database.execute_query(
                "SELECT * FROM study_plans WHERE plan_id = ?",
                (plan_id,)
            )
            
            if not plan:
                return {}
            
            plan = plan[0]
            
            # For now, return basic info
            return {
                'plan_id': plan_id,
                'title': plan['title'],
                'specialty': plan['specialty'],
                'created_at': plan['created_at'],
                'updated_at': plan['updated_at']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get study plan overview: {e}")
            return {}

# Export main classes
__all__ = ['RetrospectiveStudyPlanner', 'StudyTopic', 'StudySession', 'ConfidenceLevel', 'StudyPriority']