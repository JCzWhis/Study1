"""
MedStudy Pro - Core System Components
Contains the core functionality including database, utilities,
RAG engine, MedCards system, exam generator, study planner,
and NEW medical AI components.
"""

from .database import DatabaseManager, initialize_database
from .utils import (
    SystemChecker, FileUtils, TimeUtils, DataUtils, 
    PerformanceUtils, MedicalUtils, run_system_diagnostic
)
from .rag_engine import MedicalRAGEngine
from .medcards_system import MedCardsSystem, MedCard, CardType, CardDifficulty
from .exam_generator import MedicalExamGenerator, ExamQuestion, ExamResult
from .study_planner import RetrospectiveStudyPlanner, ConfidenceLevel, StudyPriority

# 🆕 NEW MEDICAL AI COMPONENTS
from .llm_manager import LLMManager
from .study_session_manager import (
    StudySessionManager, SessionStatus, SessionType, 
    ActiveRecallPrompt, StudySegment
)
from .medical_knowledge_analyzer import (
    MedicalKnowledgeAnalyzer, KnowledgeLevel, ConceptType, 
    KnowledgeGap, ConceptMastery
)

__all__ = [
    # Original components
    'DatabaseManager', 'initialize_database',
    'SystemChecker', 'FileUtils', 'TimeUtils', 'DataUtils',
    'PerformanceUtils', 'MedicalUtils', 'run_system_diagnostic',
    'MedicalRAGEngine', 'MedCardsSystem', 'MedCard', 'CardType', 'CardDifficulty',
    'MedicalExamGenerator', 'ExamQuestion', 'ExamResult',
    'RetrospectiveStudyPlanner', 'ConfidenceLevel', 'StudyPriority',
    
    # 🆕 NEW MEDICAL AI COMPONENTS
    'LLMManager',
    'StudySessionManager', 'SessionStatus', 'SessionType', 
    'ActiveRecallPrompt', 'StudySegment',
    'MedicalKnowledgeAnalyzer', 'KnowledgeLevel', 'ConceptType', 
    'KnowledgeGap', 'ConceptMastery'
]