"""
MedStudy Pro - Core System Components
Contains the core functionality including database, utilities,
RAG engine, MedCards system, exam generator, study planner,
and medical AI components.
"""

# Importaciones básicas que siempre funcionan
from .database import DatabaseManager, initialize_database
from .utils import (
    SystemChecker, FileUtils, TimeUtils, DataUtils, 
    PerformanceUtils, MedicalUtils, run_system_diagnostic
)

# Función para importaciones seguras
def safe_import_advanced_components():
    """Importa componentes avanzados de manera segura"""
    components = {}
    
    # LLM Manager
    try:
        from .llm_manager import LLMManager
        components['LLMManager'] = LLMManager
        print("✅ LLMManager imported successfully")
    except ImportError as e:
        print(f"⚠️ LLMManager not available: {e}")
        components['LLMManager'] = None
    
    # Study Session Manager
    try:
        from .study_session_manager import (
            StudySessionManager, SessionStatus, SessionType, 
            ActiveRecallPrompt, StudySegment
        )
        components.update({
            'StudySessionManager': StudySessionManager,
            'SessionStatus': SessionStatus,
            'SessionType': SessionType,
            'ActiveRecallPrompt': ActiveRecallPrompt,
            'StudySegment': StudySegment
        })
        print("✅ Study Session components imported successfully")
    except ImportError as e:
        print(f"⚠️ Study Session components not available: {e}")
        components.update({
            'StudySessionManager': None,
            'SessionStatus': None,
            'SessionType': None,
            'ActiveRecallPrompt': None,
            'StudySegment': None
        })
    
    # Medical Knowledge Analyzer
    try:
        from .medical_knowledge_analyzer import (
            MedicalKnowledgeAnalyzer, KnowledgeLevel, ConceptType, 
            KnowledgeGap, ConceptMastery
        )
        components.update({
            'MedicalKnowledgeAnalyzer': MedicalKnowledgeAnalyzer,
            'KnowledgeLevel': KnowledgeLevel,
            'ConceptType': ConceptType,
            'KnowledgeGap': KnowledgeGap,
            'ConceptMastery': ConceptMastery
        })
        print("✅ Medical Knowledge Analyzer imported successfully")
    except ImportError as e:
        print(f"⚠️ Medical Knowledge Analyzer not available: {e}")
        components.update({
            'MedicalKnowledgeAnalyzer': None,
            'KnowledgeLevel': None,
            'ConceptType': None,
            'KnowledgeGap': None,
            'ConceptMastery': None
        })
    
    # RAG Engine
    try:
        from .rag_engine import MedicalRAGEngine
        components['MedicalRAGEngine'] = MedicalRAGEngine
        print("✅ RAG Engine imported successfully")
    except ImportError as e:
        print(f"⚠️ RAG Engine not available: {e}")
        components['MedicalRAGEngine'] = None
    
    # MedCards System
    try:
        from .medcards_system import MedCardsSystem, MedCard, CardType, CardDifficulty
        components.update({
            'MedCardsSystem': MedCardsSystem,
            'MedCard': MedCard,
            'CardType': CardType,
            'CardDifficulty': CardDifficulty
        })
        print("✅ MedCards System imported successfully")
    except ImportError as e:
        print(f"⚠️ MedCards System not available: {e}")
        components.update({
            'MedCardsSystem': None,
            'MedCard': None,
            'CardType': None,
            'CardDifficulty': None
        })
    
    # Exam Generator
    try:
        from .exam_generator import MedicalExamGenerator, ExamQuestion, ExamResult
        components.update({
            'MedicalExamGenerator': MedicalExamGenerator,
            'ExamQuestion': ExamQuestion,
            'ExamResult': ExamResult
        })
        print("✅ Exam Generator imported successfully")
    except ImportError as e:
        print(f"⚠️ Exam Generator not available: {e}")
        components.update({
            'MedicalExamGenerator': None,
            'ExamQuestion': None,
            'ExamResult': None
        })
    
    # Study Planner
    try:
        from .study_planner import RetrospectiveStudyPlanner, ConfidenceLevel, StudyPriority
        components.update({
            'RetrospectiveStudyPlanner': RetrospectiveStudyPlanner,
            'ConfidenceLevel': ConfidenceLevel,
            'StudyPriority': StudyPriority
        })
        print("✅ Study Planner imported successfully")
    except ImportError as e:
        print(f"⚠️ Study Planner not available: {e}")
        components.update({
            'RetrospectiveStudyPlanner': None,
            'ConfidenceLevel': None,
            'StudyPriority': None
        })
    
    return components

# Ejecutar importaciones seguras
print("🔄 Loading MedStudy Pro core components...")
_advanced_components = safe_import_advanced_components()

# Hacer disponibles las importaciones en el namespace del módulo
globals().update(_advanced_components)

# Determinar qué está disponible para __all__
_available_components = [k for k, v in _advanced_components.items() if v is not None]

# Export main components
__all__ = [
    # Siempre disponibles
    'DatabaseManager', 'initialize_database',
    'SystemChecker', 'FileUtils', 'TimeUtils', 'DataUtils',
    'PerformanceUtils', 'MedicalUtils', 'run_system_diagnostic'
] + _available_components

print(f"✅ Core module loaded. Available components: {len(_available_components)}")
