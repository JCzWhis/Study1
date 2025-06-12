
"""
MedStudy Pro - Core System Components
Contains the core functionality including database, utilities,
RAG engine, MedCards system, exam generator, study planner,
and medical AI components.
"""

print("🔄 Loading MedStudy Pro core components...")

# Importaciones básicas que siempre deben funcionar
try:
    from .database import DatabaseManager, initialize_database
    print("   ✅ Database components loaded")
except ImportError as e:
    print(f"   ❌ Database components failed: {e}")
    DatabaseManager = None
    initialize_database = None

try:
    from .utils import (
        SystemChecker, FileUtils, TimeUtils, DataUtils, 
        PerformanceUtils, MedicalUtils, run_system_diagnostic
    )
    print("   ✅ Core utilities loaded")
except ImportError as e:
    print(f"   ❌ Core utilities failed: {e}")
    SystemChecker = None
    FileUtils = None
    TimeUtils = None
    DataUtils = None
    PerformanceUtils = None
    MedicalUtils = None
    run_system_diagnostic = None

# Función para importaciones avanzadas de manera segura
def safe_import_advanced():
    """Importa componentes avanzados de manera segura"""
    components = {}
    
    # LLM Manager
    try:
        from .llm_manager import LLMManager
        components['LLMManager'] = LLMManager
        print("   ✅ LLM Manager loaded")
    except ImportError as e:
        print(f"   ⚠️ LLM Manager not available: {e}")
        components['LLMManager'] = None
    except Exception as e:
        print(f"   ⚠️ LLM Manager error: {e}")
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
        print("   ✅ Study Session components loaded")
    except ImportError as e:
        print(f"   ⚠️ Study Session components not available: {e}")
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
        print("   ✅ Medical Knowledge Analyzer loaded")
    except ImportError as e:
        print(f"   ⚠️ Medical Knowledge Analyzer not available: {e}")
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
        print("   ✅ RAG Engine loaded")
    except ImportError as e:
        print(f"   ⚠️ RAG Engine not available: {e}")
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
        print("   ✅ MedCards System loaded")
    except ImportError as e:
        print(f"   ⚠️ MedCards System not available: {e}")
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
        print("   ✅ Exam Generator loaded")
    except ImportError as e:
        print(f"   ⚠️ Exam Generator not available: {e}")
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
        print("   ✅ Study Planner loaded")
    except ImportError as e:
        print(f"   ⚠️ Study Planner not available: {e}")
        components.update({
            'RetrospectiveStudyPlanner': None,
            'ConfidenceLevel': None,
            'StudyPriority': None
        })
    
    return components

# Ejecutar importaciones avanzadas
_advanced_components = safe_import_advanced()

# Hacer disponibles las importaciones en el namespace
globals().update(_advanced_components)

# Crear lista de exports
_always_available = []
if DatabaseManager:
    _always_available.extend(['DatabaseManager', 'initialize_database'])
if SystemChecker:
    _always_available.extend([
        'SystemChecker', 'FileUtils', 'TimeUtils', 'DataUtils',
        'PerformanceUtils', 'MedicalUtils', 'run_system_diagnostic'
    ])

_optional_available = [k for k, v in _advanced_components.items() if v is not None]

__all__ = _always_available + _optional_available

available_count = len([x for x in globals().values() if x is not None and callable(x)])
print(f"✅ Core module loaded. {available_count} components available.")
