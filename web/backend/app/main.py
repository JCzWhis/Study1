"""
MedStudy Web - FastAPI Main Application
Sistema de Planificación Retrospectiva para Medicina
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime, timedelta
import uuid
from app.core.llm_service import llm_service

# Configuración de la app
app = FastAPI(
    title="MedStudy Planner API",
    description="API REST para el Sistema de Planificación Retrospectiva Médica",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:8080",  # Posible puerto alternativo
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Modelos Pydantic
class StudyPlan(BaseModel):
    id: Optional[str] = None
    title: str
    specialty: str
    topics: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    confidence_levels: Optional[Dict[str, str]] = {}
    target_date: Optional[datetime] = None

class StudyTopic(BaseModel):
    id: Optional[str] = None
    plan_id: str
    name: str
    confidence_level: str  # red, orange, yellow, green, blue
    last_studied: Optional[datetime] = None
    next_review: Optional[datetime] = None
    study_count: int = 0
    estimated_hours: float = 2.0
    specialty: str = "general"

class ConfidenceUpdate(BaseModel):
    topic_id: str
    new_confidence: str
    session_duration: Optional[int] = 0  # minutos
    notes: Optional[str] = ""

class DashboardStats(BaseModel):
    active_plans: int
    total_topics: int
    study_hours: float
    efficiency_percentage: float
    confidence_distribution: Dict[str, int]
    weekly_progress: List[Dict[str, Any]]
    pending_today: int
    streak_days: int

class StudySession(BaseModel):
    id: Optional[str] = None
    topic_id: str
    duration_minutes: int
    confidence_before: str
    confidence_after: str
    notes: Optional[str] = ""
    created_at: Optional[datetime] = None

class PlanCreationRequest(BaseModel):
    specialty: str
    level: str  # "estudiante", "residente", "especialista"
    target_date: Optional[str] = None
    current_knowledge: Optional[Dict[str, str]] = {}
    specific_topics: Optional[List[str]] = None
    hours_per_week: Optional[int] = 10

# Configuration and database setup
def get_sample_data() -> Dict:
    """Generate sample data for development.
    
    Returns:
        Dict: Sample database structure
    """
    return {
        "plans": [
            {
                "id": "plan_cardio_2024",
            "title": "Preparación Examen Cardiología",
            "specialty": "cardiologia",
            "topics": [
                "Insuficiencia Cardíaca", 
                "Arritmias Cardíacas", 
                "Síndrome Coronario Agudo",
                "Valvulopatías",
                "Hipertensión Arterial"
            ],
            "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "confidence_levels": {},
            "target_date": (datetime.now() + timedelta(days=30)).isoformat()
        },
        {
            "id": "plan_reuma_2024", 
            "title": "Reumatología - Fellow",
            "specialty": "reumatologia",
            "topics": [
                "Artritis Reumatoide", 
                "Lupus Eritematoso Sistémico", 
                "Espondilitis Anquilosante",
                "Síndrome de Sjögren",
                "Vasculitis Sistémicas"
            ],
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "confidence_levels": {},
            "target_date": (datetime.now() + timedelta(days=45)).isoformat()
        },
        {
            "id": "plan_internist_2024",
            "title": "Medicina Interna - Actualización",
            "specialty": "medicina_interna", 
            "topics": [
                "Diabetes Mellitus", 
                "Enfermedad Renal Crónica",
                "Neumonía Comunitaria",
                "Sepsis y Shock",
                "Trastornos Electrolíticos"
            ],
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "confidence_levels": {},
            "target_date": (datetime.now() + timedelta(days=60)).isoformat()
        }
        ],
        "topics": [
        {
            "id": "topic_ic_001",
            "plan_id": "plan_cardio_2024",
            "name": "Insuficiencia Cardíaca",
            "confidence_level": "red",
            "last_studied": None,
            "next_review": datetime.now().isoformat(),
            "study_count": 0,
            "estimated_hours": 4.0,
            "specialty": "cardiologia"
        },
        {
            "id": "topic_arr_001",
            "plan_id": "plan_cardio_2024", 
            "name": "Arritmias Cardíacas",
            "confidence_level": "orange",
            "last_studied": (datetime.now() - timedelta(days=2)).isoformat(),
            "next_review": (datetime.now() + timedelta(days=1)).isoformat(),
            "study_count": 2,
            "estimated_hours": 3.5,
            "specialty": "cardiologia"
        },
        {
            "id": "topic_ar_001",
            "plan_id": "plan_reuma_2024",
            "name": "Artritis Reumatoide",
            "confidence_level": "yellow",
            "last_studied": (datetime.now() - timedelta(days=5)).isoformat(),
            "next_review": (datetime.now() + timedelta(days=2)).isoformat(),
            "study_count": 4,
            "estimated_hours": 3.0,
            "specialty": "reumatologia"
        },
        {
            "id": "topic_lupus_001",
            "plan_id": "plan_reuma_2024",
            "name": "Lupus Eritematoso Sistémico",
            "confidence_level": "green",
            "last_studied": (datetime.now() - timedelta(days=10)).isoformat(),
            "next_review": (datetime.now() + timedelta(days=11)).isoformat(),
            "study_count": 8,
            "estimated_hours": 2.5,
            "specialty": "reumatologia"
        },
        {
            "id": "topic_dm_001",
            "plan_id": "plan_internist_2024",
            "name": "Diabetes Mellitus",
            "confidence_level": "blue",
            "last_studied": (datetime.now() - timedelta(days=30)).isoformat(),
            "next_review": (datetime.now() + timedelta(days=60)).isoformat(),
            "study_count": 15,
            "estimated_hours": 2.0,
            "specialty": "medicina_interna"
        }
        ],
        "sessions": []
    }

# Initialize database
fake_db = get_sample_data()

# Utility functions
def calculate_next_review(confidence_level: str, study_count: int = 0) -> datetime:
    """Calcula próxima revisión según algoritmo Ali Abdaal"""
    intervals = {
        "red": 1,      # 1 día
        "orange": 3,   # 3 días  
        "yellow": 7,   # 1 semana
        "green": 21,   # 3 semanas
        "blue": 90     # 3 meses
    }
    
    base_interval = intervals.get(confidence_level, 1)
    
    # Ajustar por número de estudios (máximo 2x el intervalo base)
    multiplier = min(1 + (study_count * 0.1), 2.0)
    final_interval = int(base_interval * multiplier)
    
    return datetime.now() + timedelta(days=final_interval)

# Endpoints principales
@app.get("/")
async def read_root():
    return {
        "message": "MedStudy Planner API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/api/docs",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "plans": "/api/plans", 
            "topics": "/api/topics",
            "study": "/api/study"
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "api_version": "1.0.0"
    }

@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    """Obtiene estadísticas completas para el dashboard"""
    
    # Calcular estadísticas reales
    plans = fake_db["plans"]
    topics = fake_db["topics"]
    
    # Distribución de confianza
    confidence_dist = {
        "red": len([t for t in topics if t["confidence_level"] == "red"]),
        "orange": len([t for t in topics if t["confidence_level"] == "orange"]),
        "yellow": len([t for t in topics if t["confidence_level"] == "yellow"]),
        "green": len([t for t in topics if t["confidence_level"] == "green"]),
        "blue": len([t for t in topics if t["confidence_level"] == "blue"])
    }
    
    # Progreso semanal (simulado)
    weekly_progress = [
        {"day": "Lun", "progress": 80, "hours": 3.2},
        {"day": "Mar", "progress": 95, "hours": 4.1},
        {"day": "Mié", "progress": 60, "hours": 2.8},
        {"day": "Jue", "progress": 100, "hours": 4.5},
        {"day": "Vie", "progress": 75, "hours": 3.0},
        {"day": "Sáb", "progress": 40, "hours": 1.8},
        {"day": "Dom", "progress": 85, "hours": 3.5}
    ]
    
    # Temas pendientes hoy
    now = datetime.now()
    pending_today = 0
    for topic in topics:
        if topic["next_review"]:
            try:
                next_review = datetime.fromisoformat(topic["next_review"].replace('Z', '+00:00'))
                if next_review.date() <= now.date():
                    pending_today += 1
            except:
                pass
    
    total_hours = sum([t["estimated_hours"] for t in topics])
    
    return DashboardStats(
        active_plans=len(plans),
        total_topics=len(topics),
        study_hours=total_hours,
        efficiency_percentage=87.3,
        confidence_distribution=confidence_dist,
        weekly_progress=weekly_progress,
        pending_today=pending_today,
        streak_days=12
    )

@app.get("/api/plans")
async def get_study_plans():
    """Obtiene todos los planes de estudio"""
    return fake_db["plans"]

@app.get("/api/plans/{plan_id}", response_model=StudyPlan)
async def get_study_plan(plan_id: str):
    """Obtiene un plan específico"""
    plan = next((p for p in fake_db["plans"] if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan

@app.post("/api/plans", response_model=StudyPlan)
async def create_study_plan(plan: StudyPlan):
    """Crea un nuevo plan de estudio"""
    plan.id = f"plan_{uuid.uuid4().hex[:8]}"
    plan.created_at = datetime.now()
    plan.updated_at = datetime.now()
    
    plan_dict = plan.dict()
    fake_db["plans"].append(plan_dict)
    
    # Crear temas asociados
    for topic_name in plan.topics:
        topic = {
            "id": f"topic_{uuid.uuid4().hex[:8]}",
            "plan_id": plan.id,
            "name": topic_name,
            "confidence_level": "red",
            "last_studied": None,
            "next_review": datetime.now().isoformat(),
            "study_count": 0,
            "estimated_hours": 2.0,
            "specialty": plan.specialty
        }
        fake_db["topics"].append(topic)
    
    return plan

@app.get("/api/plans/{plan_id}/topics", response_model=List[StudyTopic])
async def get_plan_topics(plan_id: str):
    """Obtiene temas de un plan específico"""
    topics = [t for t in fake_db["topics"] if t["plan_id"] == plan_id]
    return topics

@app.get("/api/topics/due")
async def get_due_topics():
    """Obtiene temas pendientes para hoy"""
    now = datetime.now()
    due_topics = []
    
    print(f"DEBUG: Total topics in database: {len(fake_db['topics'])}")
    
    # Si no hay temas, crear algunos de ejemplo automáticamente
    if len(fake_db["topics"]) == 0:
        print("DEBUG: No topics found, creating sample topics...")
        sample_topics = [
            {
                "id": "topic_sample_1",
                "plan_id": "plan_cardio_2024",
                "name": "Insuficiencia Cardíaca Aguda",
                "confidence_level": "red",
                "last_studied": None,
                "next_review": now.isoformat(),
                "study_count": 0,
                "estimated_hours": 2.0,
                "specialty": "cardiologia"
            },
            {
                "id": "topic_sample_2", 
                "plan_id": "plan_cardio_2024",
                "name": "Electrocardiografía Básica",
                "confidence_level": "orange",
                "last_studied": (now - timedelta(days=1)).isoformat(),
                "next_review": now.isoformat(),
                "study_count": 1,
                "estimated_hours": 1.5,
                "specialty": "cardiologia"
            },
            {
                "id": "topic_sample_3",
                "plan_id": "plan_reuma_2024", 
                "name": "Artritis Reumatoide - Diagnóstico",
                "confidence_level": "yellow",
                "last_studied": (now - timedelta(days=3)).isoformat(),
                "next_review": now.isoformat(),
                "study_count": 2,
                "estimated_hours": 3.0,
                "specialty": "reumatologia"
            }
        ]
        fake_db["topics"].extend(sample_topics)
        print(f"DEBUG: Added {len(sample_topics)} sample topics")
    
    for topic in fake_db["topics"]:
        print(f"DEBUG: Checking topic: {topic.get('name', 'No name')} - Next review: {topic.get('next_review', 'None')}")
        
        # Asegurar que todos los campos requeridos estén presentes
        if "id" not in topic:
            topic["id"] = f"topic_{uuid.uuid4().hex[:8]}"
        if "confidence_level" not in topic:
            topic["confidence_level"] = "red"
        if "study_count" not in topic:
            topic["study_count"] = 0
        if "estimated_hours" not in topic:
            topic["estimated_hours"] = 2.0
            
        # Determinar si está pendiente
        is_due = False
        
        if topic.get("next_review"):
            try:
                next_review = datetime.fromisoformat(topic["next_review"].replace('Z', '+00:00'))
                if next_review.date() <= now.date():
                    is_due = True
            except Exception as e:
                print(f"DEBUG: Error parsing date: {e}")
                is_due = True  # Si hay error, considerarlo pendiente
        else:
            # Si no tiene next_review, está pendiente
            topic["next_review"] = now.isoformat()
            is_due = True
            
        if is_due:
            due_topics.append(topic)
            print(f"DEBUG: Added due topic: {topic.get('name', 'No name')}")
    
    # Ordenar por prioridad (rojo primero)
    priority_order = {"red": 0, "orange": 1, "yellow": 2, "green": 3, "blue": 4}
    due_topics.sort(key=lambda x: priority_order.get(x.get("confidence_level", "red"), 5))
    
    print(f"DEBUG: Returning {len(due_topics)} due topics")
    return due_topics

@app.post("/api/topics/{topic_id}/study")
async def study_topic(topic_id: str, update: ConfidenceUpdate):
    """Marca un tema como estudiado y actualiza confianza"""
    
    # Buscar el tema
    topic = None
    for t in fake_db["topics"]:
        if t["id"] == topic_id:
            topic = t
            break
    
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    
    old_confidence = topic["confidence_level"]
    
    # Actualizar datos del tema
    topic["confidence_level"] = update.new_confidence
    topic["last_studied"] = datetime.now().isoformat()
    topic["study_count"] += 1
    
    # Calcular próxima revisión
    next_review = calculate_next_review(update.new_confidence, topic["study_count"])
    topic["next_review"] = next_review.isoformat()
    
    # Registrar sesión de estudio
    session = {
        "id": f"session_{uuid.uuid4().hex[:8]}",
        "topic_id": topic_id,
        "topic_name": topic.get("name", "Unknown Topic"),
        "duration_minutes": update.session_duration or 30,
        "confidence_before": old_confidence,
        "confidence_after": update.new_confidence,
        "notes": update.notes or "",
        "created_at": datetime.now().isoformat(),
        "specialty": topic.get("specialty", "general")
    }
    
    # Ensure sessions list exists
    if "sessions" not in fake_db:
        fake_db["sessions"] = []
    
    fake_db["sessions"].append(session)
    
    return {
        "message": f"Tema actualizado: {old_confidence} → {update.new_confidence}",
        "next_review": next_review.isoformat(),
        "session_id": session["id"]
    }

@app.get("/api/sessions")
async def get_sessions():
    """Obtiene todas las sesiones de estudio"""
    sessions = fake_db.get("sessions", [])
    # Sort by creation date, newest first
    return sorted(sessions, key=lambda x: x["created_at"], reverse=True)

@app.get("/api/analytics/confidence-trends")
async def get_confidence_trends():
    """Obtiene tendencias de confianza a lo largo del tiempo"""
    # Datos simulados para gráficos
    return {
        "dates": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-02-15"],
        "data": [
            {"date": "2024-01-01", "red": 20, "orange": 15, "yellow": 10, "green": 5, "blue": 0},
            {"date": "2024-01-15", "red": 18, "orange": 14, "yellow": 12, "green": 6, "blue": 0},
            {"date": "2024-02-01", "red": 15, "orange": 12, "yellow": 14, "green": 8, "blue": 1},
            {"date": "2024-02-15", "red": 12, "orange": 10, "yellow": 15, "green": 10, "blue": 3}
        ]
    }

@app.get("/api/analytics/specialty-distribution")
async def get_specialty_distribution():
    """Distribución de tiempo por especialidad"""
    specialty_data = {}
    for topic in fake_db["topics"]:
        specialty = topic.get("specialty", "general")
        if specialty not in specialty_data:
            specialty_data[specialty] = {"topics": 0, "hours": 0}
        specialty_data[specialty]["topics"] += 1
        specialty_data[specialty]["hours"] += topic.get("estimated_hours", 0)
    
    return specialty_data

# ============ PLAN CREATION ENDPOINTS ============

@app.post("/api/plans/create")
async def create_study_plan(request: PlanCreationRequest):
    """Create a new study plan using AI with enhanced RAG"""
    try:
        # Initialize RAG system first
        from app.core.medical_rag import medical_rag
        if not medical_rag.is_initialized:
            await medical_rag.initialize_knowledge_base()
        
        # Check if Ollama is available
        is_available = await llm_service.ollama.check_model_availability()
        
        if is_available:
            # Generate plan using AI with RAG enhancement
            plan_data = await llm_service.generate_study_plan(
                specialty=request.specialty,
                level=request.level,
                target_date=request.target_date or (datetime.now() + timedelta(days=30)).isoformat(),
                current_knowledge=request.current_knowledge or {},
                specific_topics=request.specific_topics
            )
        else:
            # Fallback: Generate enhanced plan without Ollama but with RAG
            plan_data = await _create_enhanced_fallback_plan(
                request.specialty,
                request.level,
                request.target_date or (datetime.now() + timedelta(days=30)).isoformat(),
                request.specific_topics or []
            )
        
        # Add to fake database
        fake_db["plans"].append(plan_data)
        
        # Create detailed topics with enhanced content
        await _create_enhanced_topics(plan_data, request.specialty)
        
        return {
            "success": True,
            "plan": plan_data,
            "message": "Plan de estudio creado exitosamente con contenido médico especializado"
        }
        
    except Exception as e:
        print(f"Error creating plan: {e}")
        # Even if there's an error, provide a basic plan
        fallback_plan = await _create_basic_fallback_plan(request)
        fake_db["plans"].append(fallback_plan)
        await _create_enhanced_topics(fallback_plan, request.specialty)
        
        return {
            "success": True,
            "plan": fallback_plan,
            "message": "Plan de estudio creado con contenido básico (modo sin IA)"
        }

@app.get("/api/plans/topics/suggestions")
async def get_topic_suggestions(specialty: str, level: str = "estudiante"):
    """Get AI-generated topic suggestions for a specialty"""
    try:
        is_available = await llm_service.ollama.check_model_availability()
        if not is_available:
            # Return default suggestions if AI not available
            default_topics = {
                "cardiologia": ["Insuficiencia Cardíaca", "Arritmias", "Síndrome Coronario Agudo"],
                "medicina_interna": ["Diabetes", "Hipertensión", "Neumonía"],
                "neurologia": ["ACV", "Epilepsia", "Cefaleas"]
            }
            return {"topics": default_topics.get(specialty.lower(), ["Tema 1", "Tema 2", "Tema 3"])}
        
        topics = await llm_service.generate_topic_suggestions(specialty, level)
        return {"topics": topics}
        
    except Exception as e:
        print(f"Error getting topic suggestions: {e}")
        return {"topics": ["Error al obtener sugerencias"]}

@app.get("/api/llm/status")
async def check_llm_status():
    """Check if LLM service is available"""
    try:
        from app.config import settings
        is_available = await llm_service.ollama.check_model_availability()
        return {
            "available": is_available,
            "model": llm_service.ollama.model,
            "model_config": llm_service.ollama.model_config,
            "service": "ollama",
            "base_url": llm_service.ollama.base_url
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "model": "gemma2:2b",
            "service": "ollama"
        }

@app.get("/api/llm/models")
async def get_available_models():
    """Get list of available LLM models"""
    try:
        from app.config import settings
        return {
            "current_model": settings.OLLAMA_MODEL,
            "available_models": settings.get_available_models_list()
        }
    except Exception as e:
        return {
            "error": str(e),
            "current_model": "gemma2:2b",
            "available_models": []
        }

@app.post("/api/llm/switch-model")
async def switch_llm_model(model_name: str):
    """Switch to a different LLM model"""
    try:
        from app.config import settings
        
        if not settings.is_model_available(model_name):
            raise HTTPException(status_code=400, detail=f"Model {model_name} not supported")
        
        # Update the global LLM service
        global llm_service
        llm_service.ollama = OllamaService(model=model_name)
        llm_service.model_config = settings.get_model_config(model_name)
        
        # Update system prompt for new model
        if settings.get_model_config(model_name).get("system_prompt_language") == "spanish":
            llm_service.system_prompt = """Eres un experto en educación médica y planificación de estudios..."""
        else:
            llm_service.system_prompt = """You are an expert in medical education and study planning..."""
        
        return {
            "success": True,
            "message": f"Switched to model: {model_name}",
            "current_model": model_name,
            "model_config": settings.get_model_config(model_name)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching model: {str(e)}")

@app.get("/api/rag/test")
async def test_rag_query(query: str = "insuficiencia cardiaca", specialty: str = "cardiologia"):
    """Test RAG query directly"""
    try:
        from app.core.medical_rag import medical_rag
        
        # Initialize if needed
        if not medical_rag.is_initialized:
            await medical_rag.initialize_knowledge_base()
        
        # Test retrieval
        results = await medical_rag.retrieve_relevant_knowledge(
            query=query,
            specialty=specialty,
            n_results=3
        )
        
        return {
            "query": query,
            "specialty": specialty,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "specialty": specialty
        }

@app.get("/api/rag/status")
async def check_rag_status():
    """Check RAG system status"""
    try:
        from app.core.medical_rag import medical_rag
        
        # Initialize if needed
        if not medical_rag.is_initialized:
            await medical_rag.initialize_knowledge_base()
        
        # Test query
        test_results = await medical_rag.retrieve_relevant_knowledge(
            "cardiologia test", n_results=1
        )
        
        return {
            "rag_available": True,
            "knowledge_base_initialized": medical_rag.is_initialized,
            "document_count": medical_rag.collection.count(),
            "test_query_results": len(test_results)
        }
    except Exception as e:
        return {
            "rag_available": False,
            "error": str(e),
            "knowledge_base_initialized": False
        }

@app.post("/api/rag/upload-pdf")
async def upload_pdf_to_rag(
    file: UploadFile = File(...),
    specialty: str = "general"
):
    """Upload a PDF file to enhance the RAG knowledge base"""
    try:
        from app.core.medical_rag import medical_rag
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        content = await file.read()
        
        # Add to RAG
        success = await medical_rag.add_pdf_content(
            pdf_content=content,
            filename=file.filename,
            specialty=specialty
        )
        
        if success:
            return {
                "success": True,
                "message": f"PDF '{file.filename}' uploaded and processed successfully",
                "filename": file.filename,
                "specialty": specialty,
                "document_count": medical_rag.collection.count()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to process PDF content")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

@app.post("/api/rag/bulk-load-embeddings")
async def bulk_load_medical_embeddings():
    """Bulk load all markdown files from 'Material para embeddings' directory"""
    try:
        from app.core.medical_rag import medical_rag
        from pathlib import Path
        
        # Path to the embeddings directory
        embeddings_dir = Path(__file__).parent.parent.parent.parent / "Material para embeddings"
        
        if not embeddings_dir.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Embeddings directory not found: {embeddings_dir}"
            )
        
        # Initialize RAG system
        if not medical_rag.is_initialized:
            await medical_rag.initialize_knowledge_base()
        
        # Get current document count
        initial_count = medical_rag.collection.count()
        
        # Bulk load all markdown files
        results = await medical_rag.bulk_load_markdown_directory(str(embeddings_dir))
        
        # Get final document count
        final_count = medical_rag.collection.count()
        new_documents = final_count - initial_count
        
        return {
            "success": True,
            "message": "Bulk loading completed successfully",
            "results": results,
            "document_count": {
                "initial": initial_count,
                "final": final_count,
                "new_documents": new_documents
            },
            "embeddings_directory": str(embeddings_dir)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during bulk loading: {str(e)}")

@app.get("/api/rag/collection-stats")
async def get_rag_collection_stats():
    """Get detailed statistics about the RAG collection"""
    try:
        from app.core.medical_rag import medical_rag
        
        if not medical_rag.is_initialized:
            await medical_rag.initialize_knowledge_base()
        
        # Get collection info
        collection = medical_rag.collection
        total_docs = collection.count()
        
        # Get sample documents to analyze
        if total_docs > 0:
            sample_results = collection.query(
                query_texts=["medicina"],
                n_results=min(100, total_docs)
            )
            
            # Analyze metadata
            specialty_counts = {}
            source_counts = {}
            language_counts = {}
            
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas'][0]:
                    specialty = metadata.get('specialty', 'unknown')
                    source = metadata.get('source', 'unknown')
                    language = metadata.get('language', 'unknown')
                    
                    specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
                    source_counts[source] = source_counts.get(source, 0) + 1
                    language_counts[language] = language_counts.get(language, 0) + 1
        else:
            specialty_counts = {}
            source_counts = {}
            language_counts = {}
        
        return {
            "total_documents": total_docs,
            "is_initialized": medical_rag.is_initialized,
            "collection_name": collection.name,
            "specialty_distribution": specialty_counts,
            "source_distribution": source_counts,
            "language_distribution": language_counts,
            "sample_analyzed": min(100, total_docs)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_documents": 0,
            "is_initialized": False
        }

# ============ HELPER FUNCTIONS ============

async def _create_enhanced_fallback_plan(specialty: str, level: str, target_date: str, topics: List[str]) -> Dict:
    """Create enhanced plan with RAG content even without Ollama"""
    from app.core.medical_rag import medical_rag
    
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    
    # Get RAG-enhanced topics if possible
    enhanced_topics = []
    if topics:
        for topic in topics:
            # Try to get RAG context for this topic
            rag_content = await medical_rag.retrieve_relevant_knowledge(
                f"{specialty} {topic} {level}",
                specialty=specialty,
                n_results=2
            )
            
            if rag_content:
                description = f"Basado en conocimiento médico especializado: {rag_content[0]['content'][:200]}..."
            else:
                description = f"Tema de {specialty} nivel {level}"
                
            enhanced_topics.append({
                "name": topic,
                "description": description,
                "estimated_hours": 2.5,
                "priority": "high",
                "rag_enhanced": bool(rag_content)
            })
    else:
        # Default topics based on specialty
        default_topics = {
            "cardiologia": [
                "Insuficiencia Cardíaca", "Arritmias Cardíacas", "Síndrome Coronario Agudo",
                "Hipertensión Arterial", "Valvulopatías", "Electrocardiografía"
            ],
            "medicina_interna": [
                "Diabetes Mellitus", "Hipertensión Arterial", "Neumonía",
                "Enfermedad Renal Crónica", "Sepsis", "Trastornos Electrolíticos"
            ],
            "reumatologia": [
                "Artritis Reumatoide", "Lupus Eritematoso Sistémico", "Espondilitis Anquilosante",
                "Osteoartritis", "Gota", "Vasculitis"
            ]
        }
        
        topic_list = default_topics.get(specialty, ["Tema 1", "Tema 2", "Tema 3"])
        for topic in topic_list[:6]:  # Limit to 6 topics
            enhanced_topics.append({
                "name": topic,
                "description": f"Estudio especializado de {topic} para {level}",
                "estimated_hours": 2.0,
                "priority": "medium",
                "rag_enhanced": False
            })
    
    return {
        "plan_id": plan_id,
        "title": f"Plan de {specialty.title()} - {level.title()}",
        "specialty": specialty,
        "level": level,
        "topics": enhanced_topics,
        "created_at": datetime.now().isoformat(),
        "target_date": target_date,
        "total_hours": sum(t["estimated_hours"] for t in enhanced_topics),
        "description": f"Plan de estudio personalizado para {specialty} nivel {level} con metodología de repetición espaciada",
        "methodology": "Active Recall + Spaced Repetition + RAG-enhanced content"
    }

async def _create_basic_fallback_plan(request: PlanCreationRequest) -> Dict:
    """Create most basic plan when everything else fails"""
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    
    basic_topics = [
        {
            "name": f"Fundamentos de {request.specialty}",
            "description": "Conceptos básicos y fundamentales",
            "estimated_hours": 3.0,
            "priority": "high"
        },
        {
            "name": f"Casos Clínicos en {request.specialty}",
            "description": "Aplicación práctica de conocimientos",
            "estimated_hours": 4.0,
            "priority": "high"
        },
        {
            "name": f"Actualización en {request.specialty}",
            "description": "Conocimientos actualizados y guidelines",
            "estimated_hours": 2.0,
            "priority": "medium"
        }
    ]
    
    return {
        "plan_id": plan_id,
        "title": f"Plan Básico - {request.specialty.title()}",
        "specialty": request.specialty,
        "level": request.level,
        "topics": basic_topics,
        "created_at": datetime.now().isoformat(),
        "target_date": request.target_date or (datetime.now() + timedelta(days=30)).isoformat(),
        "total_hours": sum(t["estimated_hours"] for t in basic_topics),
        "description": f"Plan básico de {request.specialty} con metodología científica",
        "methodology": "Repetición espaciada básica"
    }

async def _create_enhanced_topics(plan_data: Dict, specialty: str):
    """Create detailed topic entries with RAG enhancement"""
    from app.core.medical_rag import medical_rag
    
    for i, topic_info in enumerate(plan_data.get("topics", [])):
        # Get enhanced content from RAG
        topic_name = topic_info.get("name", f"Topic {i+1}")
        
        rag_content = await medical_rag.retrieve_relevant_knowledge(
            f"{specialty} {topic_name} estudio",
            specialty=specialty,
            n_results=1
        )
        
        # Create detailed study content
        study_content = ""
        if rag_content:
            study_content = f"""
CONTENIDO ESPECIALIZADO:
{rag_content[0]['content'][:1000]}

OBJETIVOS DE APRENDIZAJE:
• Dominar los conceptos fundamentales
• Aplicar conocimientos en casos clínicos
• Integrar con otros temas de {specialty}

METODOLOGÍA DE ESTUDIO:
• Active Recall cada 10 minutos
• Casos clínicos prácticos
• Repetición espaciada personalizada
"""
        else:
            study_content = f"""
TEMA: {topic_name}

ENFOQUE DE ESTUDIO:
• Revisar conceptos fundamentales
• Practicar con casos clínicos
• Aplicar metodología de repetición espaciada

TIEMPO ESTIMADO: {topic_info.get('estimated_hours', 2)} horas
NIVEL: {plan_data.get('level', 'general')}
"""
        
        topic_entry = {
            "id": f"topic_{uuid.uuid4().hex[:8]}",
            "plan_id": plan_data["plan_id"],
            "name": topic_name,
            "confidence_level": "red",  # Start with lowest confidence
            "last_studied": None,
            "next_review": datetime.now().isoformat(),
            "study_count": 0,
            "estimated_hours": topic_info.get("estimated_hours", 2.0),
            "specialty": specialty,
            "description": topic_info.get("description", ""),
            "study_content": study_content,
            "rag_enhanced": bool(rag_content),
            "priority": topic_info.get("priority", "medium")
        }
        
        fake_db["topics"].append(topic_entry)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
