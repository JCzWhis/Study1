#!/usr/bin/env python3
"""
MedStudy Web App Creator - Organized Structure

This script creates a complete organized web application structure for MedStudy.
Run from Study1 directory: python create_organized_web_app.py

Features:
- FastAPI backend with modern structure
- React frontend with TypeScript support
- Proper separation of concerns
- Configuration management
- Documentation generation
"""

import os
import json
from pathlib import Path
import shutil
from typing import Dict, List, Optional
from datetime import datetime

def create_organized_web_app() -> bool:
    """Create organized MedStudy web application structure.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("🚀 MedStudy Web App - Organized Structure")
    print("=" * 60)
    
    # Base directory (Study1)
    base_dir = Path.cwd()
    print(f"📁 Base repository: {base_dir}")
    
    # Verify we're in Study1
    if not (base_dir / "venv").exists():
        print("❌ Error: Run from Study1 directory (where venv exists)")
        return False
    
    # Crear estructura organizada
    print("\n📂 Organizando estructura del repo...")
    
    # 1. Crear directorios principales
    main_dirs = ["web", "shared", "docs"]
    for directory in main_dirs:
        dir_path = base_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    # 2. Crear estructura de la web app
    web_dirs = [
        "web/backend/app/models",
        "web/backend/app/routers", 
        "web/backend/app/core",
        "web/backend/app/database",
        "web/frontend/src/components/ui",
        "web/frontend/src/components/layout",
        "web/frontend/src/components/charts",
        "web/frontend/src/pages",
        "web/frontend/src/hooks",
        "web/frontend/src/utils", 
        "web/frontend/src/styles",
        "web/frontend/public",
        "web/data",
        "web/logs"
    ]
    
    print("\n🌐 Creando estructura web app...")
    for directory in web_dirs:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    # 3. Crear archivos del backend
    create_backend_files(base_dir / "web")
    
    # 4. Crear archivos del frontend
    create_frontend_files(base_dir / "web")
    
    # 5. Crear archivos de configuración
    create_config_files(base_dir)
    
    # 6. Crear README principal actualizado
    create_main_readme(base_dir)
    
    print(f"\n🎉 Web App created successfully!")
    print(f"📁 Organized structure in: {base_dir}")
    
    print("\n🚀 To run:")
    print("1. Backend FastAPI:")
    print("   cd web/backend")
    print("   ../../venv/Scripts/activate  # Windows")
    print("   pip install -r requirements.txt")
    print("   uvicorn app.main:app --reload")
    print("")
    print("2. Frontend React (new terminal):")
    print("   cd web/frontend")
    print("   npm install")
    print("   npm start")
    print("")
    print("3. Open browser: http://localhost:3000")
    
    return True

def create_backend_files(web_dir: Path) -> None:
    """Create FastAPI backend files with modern structure.
    
    Args:
        web_dir: Path to the web directory
    """
    print("\nCreating FastAPI backend...")
    
    # Create requirements.txt with organized dependencies
    requirements = """# MedStudy Web Backend - FastAPI
# Core FastAPI dependencies
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
python-dotenv>=1.0.0

# Database and ORM
sqlalchemy>=2.0.23
alembic>=1.13.0

# Authentication and security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Data processing
pandas>=2.1.0
numpy>=1.24.0

# HTTP client
httpx>=0.25.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
"""
    
    (web_dir / "backend/requirements.txt").write_text(requirements, encoding='utf-8')
    print("  ✅ requirements.txt")
    
    # main.py con CORS y estructura mejorada
    main_py = '''"""
MedStudy Web - FastAPI Main Application
Sistema de Planificación Retrospectiva para Medicina
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime, timedelta
import uuid

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
    weekly_progress: List[Dict[str, any]]
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

@app.get("/api/plans", response_model=List[StudyPlan])
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
    
    for topic in fake_db["topics"]:
        if topic["next_review"]:
            try:
                next_review = datetime.fromisoformat(topic["next_review"].replace('Z', '+00:00'))
                if next_review.date() <= now.date():
                    due_topics.append(topic)
            except:
                pass
    
    # Ordenar por prioridad (rojo primero)
    priority_order = {"red": 0, "orange": 1, "yellow": 2, "green": 3, "blue": 4}
    due_topics.sort(key=lambda x: priority_order.get(x["confidence_level"], 5))
    
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
        "duration_minutes": update.session_duration,
        "confidence_before": old_confidence,
        "confidence_after": update.new_confidence,
        "notes": update.notes,
        "created_at": datetime.now().isoformat()
    }
    fake_db["sessions"].append(session)
    
    return {
        "message": f"Tema actualizado: {old_confidence} → {update.new_confidence}",
        "next_review": next_review.isoformat(),
        "session_id": session["id"]
    }

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
        specialty = topic["specialty"]
        if specialty not in specialty_data:
            specialty_data[specialty] = {"topics": 0, "hours": 0}
        specialty_data[specialty]["topics"] += 1
        specialty_data[specialty]["hours"] += topic["estimated_hours"]
    
    return specialty_data

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''
    
    (web_dir / "backend/app/main.py").write_text(main_py, encoding='utf-8')
    print("  ✅ main.py (backend completo)")
    
    # __init__.py files
    init_files = [
        "backend/app/__init__.py",
        "backend/app/models/__init__.py",
        "backend/app/routers/__init__.py",
        "backend/app/core/__init__.py",
        "backend/app/database/__init__.py"
    ]
    
    for init_file in init_files:
        (web_dir / init_file).write_text('"""MedStudy Backend Module"""', encoding='utf-8')
    
    print("  ✅ __init__.py files")
    
    # Archivo de configuración de entorno
    env_file = """# MedStudy Web - Environment Variables
DATABASE_URL=sqlite:///./data/medstudy.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEBUG=True
API_PREFIX=/api
"""
    (web_dir / "backend/.env").write_text(env_file, encoding='utf-8')
    print("  ✅ .env")

def create_frontend_files(web_dir):
    """Crea archivos del frontend React"""
    print("\n⚛️ Creando frontend React...")
    
    # package.json actualizado
    package_json = {
        "name": "medstudy-web-frontend",
        "version": "1.0.0", 
        "description": "MedStudy Planner - Frontend React Profesional",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0", 
            "react-scripts": "5.0.1",
            "react-router-dom": "^6.8.0",
            "axios": "^1.6.0",
            "tailwindcss": "^3.3.0",
            "autoprefixer": "^10.4.16",
            "postcss": "^8.4.32",
            "@tailwindcss/forms": "^0.5.7",
            "lucide-react": "^0.294.0",
            "recharts": "^2.8.0",
            "framer-motion": "^10.16.0",
            "clsx": "^2.0.0",
            "react-hot-toast": "^2.4.1",
            "date-fns": "^2.30.0",
            "@headlessui/react": "^1.7.17",
            "react-query": "^3.39.3"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test", 
            "eject": "react-scripts eject"
        },
        "eslintConfig": {
            "extends": [
                "react-app",
                "react-app/jest"
            ]
        },
        "browserslist": {
            "production": [
                ">0.2%",
                "not dead",
                "not op_mini all"
            ],
            "development": [
                "last 1 chrome version",
                "last 1 firefox version", 
                "last 1 safari version"
            ]
        },
        "proxy": "http://localhost:8000"
    }
    
    (web_dir / "frontend/package.json").write_text(json.dumps(package_json, indent=2), encoding='utf-8')
    print("  ✅ package.json")
    
    # public/index.html
    index_html = '''<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎓</text></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#1E3A8A" />
    <meta
      name="description"
      content="MedStudy Planner - Sistema de Planificación Retrospectiva para Medicina con metodología Ali Abdaal"
    />
    <meta name="keywords" content="medicina, estudio, planificación, ali abdaal, active recall, reumatología" />
    <meta name="author" content="Dr. Cruz Migueles" />
    <title>MedStudy Planner - Planificación Retrospectiva Médica</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <noscript>Necesitas habilitar JavaScript para ejecutar MedStudy Planner.</noscript>
    <div id="root"></div>
  </body>
</html>
'''
    
    (web_dir / "frontend/public/index.html").write_text(index_html, encoding='utf-8')
    print("  ✅ index.html")
    
    # src/index.js
    index_js = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
    
    (web_dir / "frontend/src/index.js").write_text(index_js, encoding='utf-8')
    print("  ✅ index.js")
    
    # Crear componentes React
    create_react_components(web_dir)
    create_react_pages(web_dir)

def create_react_components(web_dir: Path) -> None:
    """Create main React components with modern patterns.
    
    Args:
        web_dir: Path to the web directory
    """
    print("  🏗️ Creating React components...")
    
    # src/App.js principal con React Query
    app_js = '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Plans from './pages/Plans';
import Study from './pages/Study'; 
import Analytics from './pages/Analytics';
import './styles/index.css';

// Configurar React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutos
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App min-h-screen bg-medical-bg">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/plans" element={<Plans />} />
              <Route path="/study" element={<Study />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </Layout>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1F2937',
                color: '#F9FAFB',
                fontFamily: 'Inter, sans-serif',
              },
              success: {
                iconTheme: {
                  primary: '#10B981',
                  secondary: '#FFFFFF',
                },
              },
              error: {
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#FFFFFF',
                },
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
'''
    
    (web_dir / "frontend/src/App.js").write_text(app_js, encoding='utf-8')
    print("  ✅ App.js")
    
    # CSS principal con tema médico completo
    index_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

/* Fuentes Google */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Variables CSS para tema médico profesional */
:root {
  /* Colores principales */
  --primary-50: #EBF4FF;
  --primary-100: #DBEAFE;
  --primary-500: #3B82F6;
  --primary-600: #2563EB;
  --primary-700: #1D4ED8;
  --primary-800: #1E40AF;
  --primary-900: #1E3A8A;
  
  /* Colores secundarios */
  --secondary-50: #D1FAE5;
  --secondary-100: #A7F3D0;
  --secondary-500: #10B981;
  --secondary-600: #059669;
  --secondary-700: #047857;
  
  /* Colores de acento */
  --accent-50: #CFFAFE;
  --accent-500: #06B6D4;
  --accent-600: #0891B2;
  
  /* Colores de estado */
  --warning-500: #F59E0B;
  --error-500: #EF4444;
  --success-500: #10B981;
  
  /* Grises médicos */
  --gray-50: #F8FAFC;
  --gray-100: #F1F5F9;
  --gray-200: #E2E8F0;
  --gray-300: #CBD5E1;
  --gray-400: #94A3B8;
  --gray-500: #64748B;
  --gray-600: #475569;
  --gray-700: #334155;
  --gray-800: #1E293B;
  --gray-900: #0F172A;
  
  /* Fondo y superficies */
  --bg-primary: #F8FAFC;
  --bg-secondary: #FFFFFF;
  --surface: #FFFFFF;
  --surface-hover: #F8FAFC;
  
  /* Texto */
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-tertiary: #64748B;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* Transiciones */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reset y base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 400;
}

/* Componentes médicos personalizados */
@layer components {
  /* Cards médicas */
  .medical-card {
    @apply bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100;
  }
  
  .medical-card-hover {
    @apply medical-card hover:-translate-y-1 hover:shadow-2xl;
  }
  
  /* Botones médicos */
  .btn-medical-primary {
    @apply bg-primary-900 hover:bg-primary-800 text-white font-medium px-6 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg;
  }
  
  .btn-medical-secondary {
    @apply bg-secondary-500 hover:bg-secondary-600 text-white font-medium px-6 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg;
  }
  
  .btn-medical-outline {
    @apply border-2 border-primary-900 text-primary-900 hover:bg-primary-900 hover:text-white font-medium px-6 py-3 rounded-lg transition-all duration-200;
  }
  
  /* Badges de confianza */
  .confidence-red {
    @apply bg-red-50 text-red-700 ring-1 ring-red-200;
  }
  
  .confidence-orange {
    @apply bg-orange-50 text-orange-700 ring-1 ring-orange-200;
  }
  
  .confidence-yellow {
    @apply bg-yellow-50 text-yellow-700 ring-1 ring-yellow-200;
  }
  
  .confidence-green {
    @apply bg-green-50 text-green-700 ring-1 ring-green-200;
  }
  
  .confidence-blue {
    @apply bg-blue-50 text-blue-700 ring-1 ring-blue-200;
  }
  
  /* Headers médicos */
  .medical-header {
    @apply text-gray-900 font-bold tracking-tight;
  }
  
  .medical-subheader {
    @apply text-gray-600 font-medium;
  }
  
  /* Progress bars médicos */
  .progress-bar-bg {
    @apply w-full bg-gray-200 rounded-full h-2;
  }
  
  .progress-bar-fill {
    @apply h-2 rounded-full transition-all duration-500;
  }
  
  /* Layouts médicos */
  .medical-sidebar {
    @apply bg-white border-r border-gray-200 shadow-sm;
  }
  
  .medical-main {
    @apply bg-gray-50 min-h-screen;
  }
  
  /* Stats cards */
  .stat-card {
    @apply medical-card p-6;
  }
  
  .stat-value {
    @apply text-3xl font-bold text-gray-900;
  }
  
  .stat-label {
    @apply text-sm font-medium text-gray-500 uppercase tracking-wide;
  }
  
  .stat-change {
    @apply text-sm font-medium;
  }
  
  .stat-change-positive {
    @apply stat-change text-green-600;
  }
  
  .stat-change-negative {
    @apply stat-change text-red-600;
  }
}

/* Animaciones personalizadas */
@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

@keyframes slideIn {
  from { 
    opacity: 0; 
    transform: translateX(-20px); 
  }
  to { 
    opacity: 1; 
    transform: translateX(0); 
  }
}

@keyframes scaleIn {
  from { 
    opacity: 0; 
    transform: scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: scale(1); 
  }
}

@keyframes pulse {
  0%, 100% { 
    opacity: 1; 
  }
  50% { 
    opacity: 0.5; 
  }
}

/* Utilidades de animación */
.animate-fadeIn {
  animation: fadeIn 0.6s ease-out;
}

.animate-slideIn {
  animation: slideIn 0.4s ease-out;
}

.animate-scaleIn {
  animation: scaleIn 0.3s ease-out;
}

.animate-pulse-custom {
  animation: pulse 2s infinite;
}

/* Estados de loading */
.skeleton {
  @apply animate-pulse bg-gray-200 rounded;
}

.skeleton-text {
  @apply skeleton h-4 w-full;
}

.skeleton-title {
  @apply skeleton h-6 w-3/4;
}

.skeleton-avatar {
  @apply skeleton h-10 w-10 rounded-full;
}

/* Focus states médicos */
.focus-medical {
  @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
}

/* Scrollbars personalizados */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--gray-400) var(--gray-100);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: var(--gray-100);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--gray-400);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--gray-500);
}

/* Responsive utilities */
@media (max-width: 640px) {
  .mobile-p-4 {
    @apply p-4;
  }
  
  .mobile-text-sm {
    @apply text-sm;
  }
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  .print-only {
    display: block !important;
  }
}

/* Dark mode support (preparado para futuro) */
@media (prefers-color-scheme: dark) {
  .dark-mode-ready {
    /* Variables para dark mode */
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .medical-card {
    @apply border-2 border-gray-800;
  }
}
'''
    
    (web_dir / "frontend/src/styles/index.css").write_text(index_css, encoding='utf-8')
    print("  ✅ index.css (tema médico completo)")
    
    # Componente Layout
    layout_component = '''import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Brain, 
  BarChart3, 
  BookOpen, 
  Calendar,
  Settings,
  User,
  Bell,
  Search
} from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3, current: location.pathname === '/dashboard' || location.pathname === '/' },
    { name: 'Planes', href: '/plans', icon: Calendar, current: location.pathname === '/plans' },
    { name: 'Estudiar', href: '/study', icon: BookOpen, current: location.pathname === '/study' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, current: location.pathname === '/analytics' },
  ];

  return (
    <div className="min-h-screen bg-medical-bg">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 medical-sidebar">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center px-6 border-b border-gray-200">
            <Brain className="h-8 w-8 text-primary-900" />
            <span className="ml-3 text-xl font-bold text-gray-900">MedStudy</span>
          </div>
          
          {/* Navigation */}
          <nav className="flex flex-1 flex-col p-4">
            <ul role="list" className="flex flex-1 flex-col gap-y-2">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`group flex gap-x-3 rounded-lg p-3 text-sm font-medium transition-all duration-200 ${
                      item.current
                        ? 'bg-primary-50 text-primary-900 shadow-sm'
                        : 'text-gray-600 hover:text-primary-900 hover:bg-gray-50'
                    }`}
                  >
                    <item.icon
                      className={`h-5 w-5 shrink-0 ${
                        item.current ? 'text-primary-900' : 'text-gray-400 group-hover:text-primary-900'
                      }`}
                    />
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
            
            {/* User section */}
            <div className="mt-auto">
              <div className="flex items-center gap-x-4 px-3 py-3 text-sm font-medium text-gray-900 hover:bg-gray-50 rounded-lg transition-colors duration-200">
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <User className="h-4 w-4 text-primary-900" />
                </div>
                <span className="sr-only">Tu perfil</span>
                <span className="truncate">Dr. Cruz Migueles</span>
              </div>
            </div>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Top header */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="relative flex flex-1 items-center">
              <Search className="pointer-events-none absolute left-3 h-5 w-5 text-gray-400" />
              <input
                type="search"
                placeholder="Buscar temas, planes..."
                className="block h-full w-full border-0 py-0 pl-10 pr-0 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm bg-transparent"
              />
            </div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 transition-colors duration-200"
              >
                <span className="sr-only">Ver notificaciones</span>
                <Bell className="h-6 w-6" />
              </button>
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 transition-colors duration-200"
              >
                <span className="sr-only">Configuración</span>
                <Settings className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-8">
          <div className="px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
'''
    
    (web_dir / "frontend/src/components/layout/Layout.js").write_text(layout_component, encoding='utf-8')
    print("  ✅ Layout.js")

def create_react_pages(web_dir: Path) -> None:
    """Create React page components.
    
    Args:
        web_dir: Path to the web directory
    """
    """Crea las páginas principales de React"""
    print("  📄 Creando páginas React...")
    
    # Dashboard page
    dashboard_page = '''import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Clock, 
  Target, 
  BookOpen,
  Calendar,
  Brain,
  Award
} from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  // Obtener datos del dashboard
  const { data: stats, isLoading } = useQuery('dashboard-stats', 
    () => axios.get('/api/dashboard').then(res => res.data)
  );

  const { data: dueTopics } = useQuery('due-topics',
    () => axios.get('/api/topics/due').then(res => res.data)
  );

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  const confidenceColors = {
    red: 'bg-red-500',
    orange: 'bg-orange-500', 
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500'
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Vista general de tu progreso en estudios médicos</p>
        </div>
        <div className="text-sm text-gray-500">
          📅 {new Date().toLocaleDateString('es-ES', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Planes Activos"
          value={stats?.active_plans || 0}
          subtitle="+1 esta semana"
          icon={Calendar}
          color="blue"
          trend="up"
        />
        <MetricCard
          title="Total Temas"
          value={stats?.total_topics || 0}
          subtitle="+8 este mes"
          icon={BookOpen}
          color="green"
          trend="up"
        />
        <MetricCard
          title="Horas Estudio"
          value={`${stats?.study_hours || 0}h`}
          subtitle="3.2h promedio/día"
          icon={Clock}
          color="orange"
          trend="neutral"
        />
        <MetricCard
          title="Eficiencia"
          value={`${stats?.efficiency_percentage || 0}%`}
          subtitle="+5% vs mes anterior"
          icon={Target}
          color="purple"
          trend="up"
        />
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribución de confianza */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎯 Distribución de Confianza
          </h3>
          <div className="space-y-4">
            {stats?.confidence_distribution && Object.entries(stats.confidence_distribution).map(([level, count]) => (
              <div key={level} className="flex items-center">
                <div className="flex items-center w-32">
                  <div className={`w-3 h-3 rounded-full ${confidenceColors[level]} mr-2`} />
                  <span className="text-sm capitalize">{level}</span>
                </div>
                <div className="flex-1 mx-4">
                  <div className="progress-bar-bg">
                    <div 
                      className={`progress-bar-fill ${confidenceColors[level]}`}
                      style={{ width: `${(count / stats.total_topics) * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm font-medium w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Progreso semanal */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📈 Progreso Esta Semana
          </h3>
          <div className="flex justify-between items-end h-32">
            {stats?.weekly_progress?.map((day, index) => (
              <div key={day.day} className="flex flex-col items-center">
                <div 
                  className="w-8 bg-primary-500 rounded-t"
                  style={{ height: `${day.progress}%` }}
                />
                <span className="text-xs text-gray-500 mt-2">{day.day}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 text-sm text-gray-600 text-center">
            Promedio: 25.5h esta semana • Meta: 30h
          </div>
        </motion.div>
      </div>

      {/* Temas pendientes */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="medical-card p-6"
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            🎯 Temas Pendientes para Hoy ({stats?.pending_today || 0})
          </h3>
          <button className="btn-medical-primary text-sm">
            Ver Todos →
          </button>
        </div>
        
        <div className="space-y-3">
          {dueTopics?.slice(0, 5).map((topic) => (
            <PendingTopicCard key={topic.id} topic={topic} />
          ))}
          
          {!dueTopics?.length && (
            <div className="text-center py-8 text-gray-500">
              🎉 ¡No hay temas pendientes para hoy! Excelente trabajo.
            </div>
          )}
        </div>
      </motion.div>

      {/* Estadísticas adicionales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={Brain}
          title="Racha de Estudio"
          value={`${stats?.streak_days || 0} días`}
          description="¡Sigue así!"
          color="green"
        />
        <StatCard
          icon={Award}
          title="Nivel de Confianza"
          value="Intermedio"
          description="68% de temas en verde/azul"
          color="blue"
        />
        <StatCard
          icon={TrendingUp}
          title="Tendencia"
          value="+12%"
          description="Mejora vs mes anterior"
          color="purple"
        />
      </div>
    </div>
  );
};

// Componentes auxiliares
const MetricCard = ({ title, value, subtitle, icon: Icon, color, trend }) => {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    purple: 'text-purple-600'
  };

  const trendIcons = {
    up: '↗️',
    down: '↘️', 
    neutral: '➡️'
  };

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      className="medical-card-hover p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</p>
          <p className="text-xs text-gray-500">
            {trendIcons[trend]} {subtitle}
          </p>
        </div>
        <div className={`p-3 rounded-lg bg-${color}-50`}>
          <Icon className={`h-6 w-6 ${colorClasses[color]}`} />
        </div>
      </div>
    </motion.div>
  );
};

const PendingTopicCard = ({ topic }) => {
  const confidenceStyles = {
    red: 'bg-red-50 text-red-700 border-red-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200'
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="flex items-center space-x-4">
        <div className={`px-2 py-1 rounded text-xs font-medium border ${confidenceStyles[topic.confidence_level]}`}>
          {topic.confidence_level}
        </div>
        <div>
          <h4 className="font-medium text-gray-900">{topic.name}</h4>
          <p className="text-sm text-gray-500">📚 {topic.specialty}</p>
        </div>
      </div>
      <button className="btn-medical-primary text-sm">
        Estudiar
      </button>
    </div>
  );
};

const StatCard = ({ icon: Icon, title, value, description, color }) => {
  const colorClasses = {
    green: 'text-green-600 bg-green-50',
    blue: 'text-blue-600 bg-blue-50',
    purple: 'text-purple-600 bg-purple-50'
  };

  return (
    <div className="medical-card p-6 text-center">
      <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} mb-4`}>
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className="text-xl font-bold text-gray-900 my-1">{value}</p>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
  );
};

const DashboardSkeleton = () => (
  <div className="space-y-8">
    <div className="flex justify-between items-center">
      <div>
        <div className="skeleton-title mb-2" />
        <div className="skeleton-text w-64" />
      </div>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton-text mb-2" />
          <div className="skeleton-title mb-1" />
          <div className="skeleton-text w-20" />
        </div>
      ))}
    </div>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {[...Array(2)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton-title mb-4" />
          <div className="skeleton h-32" />
        </div>
      ))}
    </div>
  </div>
);

export default Dashboard;
'''
    
    (web_dir / "frontend/src/pages/Dashboard.js").write_text(dashboard_page, encoding='utf-8')
    print("  ✅ Dashboard.js")
    
    # Plans page
    plans_page = '''import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { motion } from 'framer-motion';
import { Plus, Calendar, BookOpen, Target, MoreVertical } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const Plans = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const queryClient = useQueryClient();
  
  const { data: plans, isLoading } = useQuery('study-plans',
    () => axios.get('/api/plans').then(res => res.data)
  );

  const createPlanMutation = useMutation(
    (newPlan) => axios.post('/api/plans', newPlan),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('study-plans');
        setShowCreateModal(false);
        toast.success('Plan creado exitosamente');
      },
      onError: () => {
        toast.error('Error al crear el plan');
      }
    }
  );

  if (isLoading) {
    return <PlansListSkeleton />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Planes</h1>
          <p className="text-gray-600 mt-1">Organiza y gestiona tus planes de estudio médico</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-medical-primary flex items-center gap-2"
        >
          <Plus className="h-5 w-5" />
          Nuevo Plan
        </button>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <QuickStat
          icon={Calendar}
          label="Planes Activos"
          value={plans?.length || 0}
          color="blue"
        />
        <QuickStat
          icon={BookOpen}
          label="Total Temas"
          value={plans?.reduce((acc, plan) => acc + (plan.topics?.length || 0), 0) || 0}
          color="green"
        />
        <QuickStat
          icon={Target}
          label="Pendientes Hoy"
          value="12"
          color="orange"
        />
        <QuickStat
          icon={Calendar}
          label="Próximo Examen"
          value="15 días"
          color="purple"
        />
      </div>

      {/* Lista de planes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {plans?.map((plan, index) => (
          <PlanCard key={plan.id} plan={plan} index={index} />
        ))}
        
        {!plans?.length && (
          <div className="col-span-full text-center py-12">
            <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay planes creados</h3>
            <p className="text-gray-500 mb-4">Comienza creando tu primer plan de estudio</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-medical-primary"
            >
              Crear Primer Plan
            </button>
          </div>
        )}
      </div>

      {/* Modal crear plan */}
      {showCreateModal && (
        <CreatePlanModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={(data) => createPlanMutation.mutate(data)}
          isLoading={createPlanMutation.isLoading}
        />
      )}
    </div>
  );
};

const QuickStat = ({ icon: Icon, label, value, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    orange: 'text-orange-600 bg-orange-50',
    purple: 'text-purple-600 bg-purple-50'
  };

  return (
    <div className="medical-card p-6">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${colorClasses[color]} mr-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{label}</p>
        </div>
      </div>
    </div>
  );
};

const PlanCard = ({ plan, index }) => {
  const specialtyColors = {
    cardiologia: 'bg-red-50 text-red-700 border-red-200',
    reumatologia: 'bg-blue-50 text-blue-700 border-blue-200',
    medicina_interna: 'bg-green-50 text-green-700 border-green-200'
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
      className="medical-card-hover p-6"
    >
      {/* Header del plan */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{plan.title}</h3>
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded border ${specialtyColors[plan.specialty] || specialtyColors.medicina_interna}`}>
            {plan.specialty.replace('_', ' ')}
          </span>
        </div>
        <button className="p-1 text-gray-400 hover:text-gray-600">
          <MoreVertical className="h-5 w-5" />
        </button>
      </div>

      {/* Estadísticas del plan */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-600">{plan.topics?.length || 0}</p>
          <p className="text-xs text-gray-500">Temas</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">68%</p>
          <p className="text-xs text-gray-500">Progreso</p>
        </div>
      </div>

      {/* Progreso visual */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progreso general</span>
          <span>68%</span>
        </div>
        <div className="progress-bar-bg">
          <div className="progress-bar-fill bg-blue-500" style={{ width: '68%' }} />
        </div>
      </div>

      {/* Fechas */}
      <div className="text-sm text-gray-500 mb-4">
        <p>📅 Creado: {formatDate(plan.created_at)}</p>
        {plan.target_date && (
          <p>🎯 Meta: {formatDate(plan.target_date)}</p>
        )}
      </div>

      {/* Acciones */}
      <div className="flex gap-2">
        <button className="flex-1 btn-medical-primary text-sm">
          Estudiar
        </button>
        <button className="flex-1 btn-medical-outline text-sm">
          Ver Detalles
        </button>
      </div>
    </motion.div>
  );
};

const CreatePlanModal = ({ onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    title: '',
    specialty: 'medicina_interna',
    topics: '',
    target_date: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const topicsArray = formData.topics
      .split('\\n')
      .map(topic => topic.trim())
      .filter(topic => topic.length > 0);

    onSubmit({
      title: formData.title,
      specialty: formData.specialty,
      topics: topicsArray,
      target_date: formData.target_date ? new Date(formData.target_date).toISOString() : null
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Crear Nuevo Plan</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Título */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Título del Plan
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="ej. Preparación Examen Cardiología"
                required
              />
            </div>

            {/* Especialidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Especialidad
              </label>
              <select
                value={formData.specialty}
                onChange={(e) => setFormData(prev => ({ ...prev, specialty: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="medicina_interna">Medicina Interna</option>
                <option value="cardiologia">Cardiología</option>
                <option value="reumatologia">Reumatología</option>
                <option value="endocrinologia">Endocrinología</option>
                <option value="neurologia">Neurología</option>
                <option value="gastroenterologia">Gastroenterología</option>
              </select>
            </div>

            {/* Temas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temas (uno por línea)
              </label>
              <textarea
                value={formData.topics}
                onChange={(e) => setFormData(prev => ({ ...prev, topics: e.target.value }))}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Insuficiencia Cardíaca
Arritmias Cardíacas
Síndrome Coronario Agudo"
                required
              />
            </div>

            {/* Fecha objetivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Objetivo (opcional)
              </label>
              <input
                type="date"
                value={formData.target_date}
                onChange={(e) => setFormData(prev => ({ ...prev, target_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Botones */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 btn-medical-primary disabled:opacity-50"
              >
                {isLoading ? 'Creando...' : 'Crear Plan'}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

const PlansListSkeleton = () => (
  <div className="space-y-8">
    <div className="flex justify-between items-center">
      <div>
        <div className="skeleton-title mb-2" />
        <div className="skeleton-text w-64" />
      </div>
      <div className="skeleton w-24 h-10" />
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton h-16" />
        </div>
      ))}
    </div>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton-title mb-4" />
          <div className="skeleton h-24 mb-4" />
          <div className="skeleton-text" />
        </div>
      ))}
    </div>
  </div>
);

export default Plans;
'''
    (web_dir / "frontend/src/pages/Plans.js").write_text(plans_page, encoding='utf-8')
    print("  ✅ Plans.js")
    
    # Study page
    study_page = '''import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, RotateCcw, CheckCircle, Clock, Brain } from 'lucide-react';
import { useQuery } from 'react-query';
import axios from 'axios';

const Study = () => {
  const [currentTopic, setCurrentTopic] = useState(null);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [sessionPhase, setSessionPhase] = useState('ready'); // ready, studying, quiz, completed

  const { data: dueTopics } = useQuery('due-topics',
    () => axios.get('/api/topics/due').then(res => res.data)
  );

  // Timer effect
  useEffect(() => {
    let interval = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimerSeconds(seconds => seconds + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startStudySession = (topic) => {
    setCurrentTopic(topic);
    setSessionPhase('studying');
    setTimerSeconds(0);
    setIsTimerRunning(true);
  };

  const pauseTimer = () => {
    setIsTimerRunning(!isTimerRunning);
  };

  const resetSession = () => {
    setIsTimerRunning(false);
    setTimerSeconds(0);
    setSessionPhase('ready');
    setCurrentTopic(null);
  };

  const completeSession = () => {
    setIsTimerRunning(false);
    setSessionPhase('quiz');
  };

  if (sessionPhase === 'studying' && currentTopic) {
    return <StudySession 
      topic={currentTopic}
      timerSeconds={timerSeconds}
      isTimerRunning={isTimerRunning}
      onPause={pauseTimer}
      onComplete={completeSession}
      onReset={resetSession}
    />;
  }

  if (sessionPhase === 'quiz' && currentTopic) {
    return <QuizSession 
      topic={currentTopic}
      sessionDuration={timerSeconds}
      onComplete={resetSession}
    />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sesiones de Estudio</h1>
        <p className="text-gray-600">Estudia con metodología científica y seguimiento de progreso</p>
      </div>

      {/* Estadísticas de estudio */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StudyStatCard
          icon={Clock}
          title="Tiempo Hoy"
          value="2h 45m"
          subtitle="Meta: 4h"
          color="blue"
        />
        <StudyStatCard
          icon={Brain}
          title="Temas Estudiados"
          value="8"
          subtitle="Esta semana"
          color="green"
        />
        <StudyStatCard
          icon={CheckCircle}
          title="Sesiones Completadas"
          value="23"
          subtitle="Este mes"
          color="purple"
        />
        <StudyStatCard
          icon={Play}
          title="Racha"
          value="12 días"
          subtitle="¡Excelente!"
          color="orange"
        />
      </div>

      {/* Temas pendientes para estudiar */}
      <div className="medical-card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          🎯 Temas Pendientes para Hoy ({dueTopics?.length || 0})
        </h2>
        
        {dueTopics && dueTopics.length > 0 ? (
          <div className="grid gap-4">
            {dueTopics.map((topic, index) => (
              <TopicStudyCard 
                key={topic.id} 
                topic={topic} 
                index={index}
                onStart={() => startStudySession(topic)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ¡Todos los temas al día!
            </h3>
            <p className="text-gray-500">
              No hay temas pendientes para hoy. ¡Excelente trabajo!
            </p>
          </div>
        )}
      </div>

      {/* Metodología */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MethodologyCard
          icon="⏱️"
          title="Pomodoro Médico"
          description="Sesiones de 45 minutos optimizadas para contenido médico complejo"
        />
        <MethodologyCard
          icon="🎓"
          title="Active Recall"
          description="Preguntas automáticas cada 10 minutos para verificar comprensión"
        />
        <MethodologyCard
          icon="🔄"
          title="Repetición Espaciada"
          description="Algoritmo Ali Abdaal con intervalos adaptativos por confianza"
        />
      </div>
    </div>
  );
};

const StudyStatCard = ({ icon: Icon, title, value, subtitle, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    orange: 'text-orange-600 bg-orange-50'
  };

  return (
    <div className="medical-card p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]} mr-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
      </div>
    </div>
  );
};

const TopicStudyCard = ({ topic, index, onStart }) => {
  const confidenceColors = {
    red: 'bg-red-500',
    orange: 'bg-orange-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500'
  };

  const priorityLabels = {
    red: 'Urgente',
    orange: 'Alto',
    yellow: 'Medio',
    green: 'Bajo',
    blue: 'Mantenimiento'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <div className="flex items-center space-x-4">
        <div className={`w-4 h-4 rounded-full ${confidenceColors[topic.confidence_level]}`} />
        <div>
          <h3 className="font-medium text-gray-900">{topic.name}</h3>
          <p className="text-sm text-gray-500">
            📚 {topic.specialty} • Prioridad: {priorityLabels[topic.confidence_level]}
          </p>
          <p className="text-xs text-gray-400">
            Estudiado {topic.study_count} veces • ~{topic.estimated_hours}h estimadas
          </p>
        </div>
      </div>
      <button
        onClick={onStart}
        className="btn-medical-primary flex items-center gap-2"
      >
        <Play className="h-4 w-4" />
        Estudiar
      </button>
    </motion.div>
  );
};

const MethodologyCard = ({ icon, title, description }) => (
  <div className="medical-card p-6 text-center">
    <div className="text-3xl mb-4">{icon}</div>
    <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </div>
);

const StudySession = ({ topic, timerSeconds, isTimerRunning, onPause, onComplete, onReset }) => {
  const progress = Math.min((timerSeconds / (45 * 60)) * 100, 100);
  
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header de sesión */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Estudiando: {topic.name}</h1>
        <p className="text-gray-600">📚 {topic.specialty}</p>
      </div>

      {/* Timer principal */}
      <div className="medical-card p-8 text-center">
        <div className="mb-6">
          <div className={`text-6xl font-bold mb-4 ${timerSeconds > 45 * 60 ? 'text-green-600' : 'text-blue-600'}`}>
            {Math.floor(timerSeconds / 60)}:{(timerSeconds % 60).toString().padStart(2, '0')}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600">
            Meta: 45 minutos • Progreso: {Math.round(progress)}%
          </p>
        </div>

        <div className="flex justify-center gap-4">
          <button
            onClick={onPause}
            className={`btn-medical-primary flex items-center gap-2 ${!isTimerRunning ? 'bg-green-600 hover:bg-green-700' : ''}`}
          >
            {isTimerRunning ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            {isTimerRunning ? 'Pausar' : 'Continuar'}
          </button>
          <button
            onClick={onComplete}
            className="btn-medical-secondary flex items-center gap-2"
          >
            <CheckCircle className="h-5 w-5" />
            Completar
          </button>
          <button
            onClick={onReset}
            className="btn-medical-outline flex items-center gap-2"
          >
            <RotateCcw className="h-5 w-5" />
            Reiniciar
          </button>
        </div>
      </div>

      {/* Contenido de estudio */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Área principal de estudio */}
        <div className="lg:col-span-2 medical-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📖 Área de Estudio</h3>
          <div className="prose max-w-none">
            <p className="text-gray-600 mb-4">
              Aquí estudiarás el tema <strong>{topic.name}</strong>. Puedes usar cualquier recurso:
            </p>
            <ul className="text-sm text-gray-600 space-y-2">
              <li>• Libros de texto médicos</li>
              <li>• Videos educativos</li>
              <li>• Casos clínicos</li>
              <li>• Artículos de investigación</li>
              <li>• Simuladores médicos</li>
            </ul>
            <div className="bg-blue-50 p-4 rounded-lg mt-6">
              <p className="text-sm text-blue-800">
                💡 <strong>Tip:</strong> Cada 10 minutos aparecerá una pregunta de Active Recall para verificar tu comprensión.
              </p>
            </div>
          </div>
        </div>

        {/* Panel lateral */}
        <div className="space-y-4">
          {/* Notas rápidas */}
          <div className="medical-card p-4">
            <h4 className="font-medium text-gray-900 mb-3">📝 Notas Rápidas</h4>
            <textarea
              placeholder="Anota conceptos clave, dudas, ideas importantes..."
              className="w-full h-32 text-sm border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Objetivos de la sesión */}
          <div className="medical-card p-4">
            <h4 className="font-medium text-gray-900 mb-3">🎯 Objetivos</h4>
            <div className="space-y-2 text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Entender conceptos básicos
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Revisar casos clínicos
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Memorizar puntos clave
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const QuizSession = ({ topic, sessionDuration, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [newConfidence, setNewConfidence] = useState(topic.confidence_level);

  const questions = [
    {
      question: `¿Cuáles son los puntos más importantes sobre ${topic.name}?`,
      type: 'text'
    },
    {
      question: `¿Qué aspectos de ${topic.name} te resultan más difíciles?`,
      type: 'text'
    },
    {
      question: `¿Cómo calificarías tu confianza actual en este tema?`,
      type: 'confidence'
    }
  ];

  const handleSubmit = () => {
    // Aquí enviarías los datos al backend
    console.log('Enviando resultados de la sesión:', {
      topic_id: topic.id,
      duration: sessionDuration,
      new_confidence: newConfidence,
      answers: selectedAnswer
    });
    onComplete();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Quiz Post-Estudio</h1>
        <p className="text-gray-600">Evalúa tu comprensión de {topic.name}</p>
        <p className="text-sm text-gray-500">Tiempo estudiado: {Math.floor(sessionDuration / 60)} minutos</p>
      </div>

      <div className="medical-card p-6">
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm text-gray-500">Pregunta {currentQuestion + 1} de {questions.length}</span>
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>
          
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {questions[currentQuestion].question}
          </h3>

          {questions[currentQuestion].type === 'text' ? (
            <textarea
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              className="w-full h-32 border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Escribe tu respuesta aquí..."
            />
          ) : (
            <div className="space-y-3">
              {['red', 'orange', 'yellow', 'green', 'blue'].map((level) => (
                <button
                  key={level}
                  onClick={() => setNewConfidence(level)}
                  className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
                    newConfidence === level 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center">
                    <div className={`w-4 h-4 rounded-full mr-3 ${
                      level === 'red' ? 'bg-red-500' :
                      level === 'orange' ? 'bg-orange-500' :
                      level === 'yellow' ? 'bg-yellow-500' :
                      level === 'green' ? 'bg-green-500' : 'bg-blue-500'
                    }`} />
                    <div>
                      <p className="font-medium">
                        {level === 'red' ? '🔴 No sé nada' :
                         level === 'orange' ? '🟠 Sé muy poco' :
                         level === 'yellow' ? '🟡 Sé algo' :
                         level === 'green' ? '🟢 Sé bastante' : '🔵 Lo domino'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {level === 'red' ? 'Estudiar hoy' :
                         level === 'orange' ? 'Cada 3 días' :
                         level === 'yellow' ? 'Semanal' :
                         level === 'green' ? 'Cada 3 semanas' : 'Cada 3 meses'}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex gap-3">
          {currentQuestion > 0 && (
            <button
              onClick={() => setCurrentQuestion(currentQuestion - 1)}
              className="btn-medical-outline"
            >
              Anterior
            </button>
          )}
          
          {currentQuestion < questions.length - 1 ? (
            <button
              onClick={() => setCurrentQuestion(currentQuestion + 1)}
              className="btn-medical-primary ml-auto"
            >
              Siguiente
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="btn-medical-primary ml-auto"
            >
              Completar Sesión
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Study;
'''
    
    (web_dir / "frontend/src/pages/Study.js").write_text(study_page, encoding='utf-8')
    print("  ✅ Study.js")
    
    # Analytics page
    analytics_page = '''import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { TrendingUp, Calendar, Clock, Target } from 'lucide-react';
import axios from 'axios';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('month');
  
  const { data: confidenceTrends } = useQuery('confidence-trends',
    () => axios.get('/api/analytics/confidence-trends').then(res => res.data)
  );
  
  const { data: specialtyDistribution } = useQuery('specialty-distribution',
    () => axios.get('/api/analytics/specialty-distribution').then(res => res.data)
  );

  // Datos simulados para gráficos adicionales
  const studyTimeData = [
    { day: 'Lun', hours: 3.2, sessions: 4 },
    { day: 'Mar', hours: 4.1, sessions: 5 },
    { day: 'Mié', hours: 2.8, sessions: 3 },
    { day: 'Jue', hours: 4.5, sessions: 6 },
    { day: 'Vie', hours: 3.0, sessions: 4 },
    { day: 'Sáb', hours: 1.8, sessions: 2 },
    { day: 'Dom', hours: 3.5, sessions: 4 }
  ];

  const confidenceColors = ['#EF4444', '#F97316', '#EAB308', '#22C55E', '#3B82F6'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Análisis detallado de tu progreso en estudios médicos</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="week">Última semana</option>
          <option value="month">Último mes</option>
          <option value="quarter">Últimos 3 meses</option>
          <option value="year">Último año</option>
        </select>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <AnalyticsCard
          icon={Clock}
          title="Tiempo Total"
          value="127.5h"
          change="+12%"
          trend="up"
          color="blue"
        />
        <AnalyticsCard
          icon={Target}
          title="Eficiencia"
          value="87.3%"
          change="+5%"
          trend="up"
          color="green"
        />
        <AnalyticsCard
          icon={Calendar}
          title="Sesiones"
          value="48"
          change="+8"
          trend="up"
          color="purple"
        />
        <AnalyticsCard
          icon={TrendingUp}
          title="Mejora Promedio"
          value="+2.1"
          change="niveles/tema"
          trend="up"
          color="orange"
        />
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tiempo de estudio semanal */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📊 Tiempo de Estudio Semanal
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={studyTimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="day" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#F9FAFB', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="hours" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Evolución de confianza */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📈 Evolución de Confianza
          </h3>
          {confidenceTrends && (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={confidenceTrends.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#F9FAFB', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px'
                  }}
                />
                <Line type="monotone" dataKey="red" stroke="#EF4444" strokeWidth={2} />
                <Line type="monotone" dataKey="orange" stroke="#F97316" strokeWidth={2} />
                <Line type="monotone" dataKey="yellow" stroke="#EAB308" strokeWidth={2} />
                <Line type="monotone" dataKey="green" stroke="#22C55E" strokeWidth={2} />
                <Line type="monotone" dataKey="blue" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </motion.div>
      </div>

      {/* Distribución por especialidad */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📚 Distribución por Especialidad
          </h3>
          {specialtyDistribution && (
            <div className="space-y-4">
              {Object.entries(specialtyDistribution).map(([specialty, data]) => (
                <div key={specialty} className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-900 capitalize">
                      {specialty.replace('_', ' ')}
                    </p>
                    <p className="text-sm text-gray-500">{data.topics} temas</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-600">{data.hours}h</p>
                    <p className="text-xs text-gray-500">
                      {Math.round((data.hours / 20) * 100)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Estadísticas de rendimiento */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎯 Rendimiento
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Sesiones completadas</span>
              <span className="font-bold text-green-600">94%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Tiempo promedio/sesión</span>
              <span className="font-bold text-blue-600">42min</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Mejora de confianza</span>
              <span className="font-bold text-purple-600">+1.8</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Retención estimada</span>
              <span className="font-bold text-orange-600">89%</span>
            </div>
          </div>
        </motion.div>

        {/* Metas y objetivos */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎖️ Metas del Mes
          </h3>
          <div className="space-y-4">
            <GoalProgress
              title="Horas de estudio"
              current={87}
              target={120}
              unit="h"
            />
            <GoalProgress
              title="Temas completados"
              current={23}
              target={30}
              unit="temas"
            />
            <GoalProgress
              title="Confianza promedio"
              current={3.2}
              target={4.0}
              unit="nivel"
            />
          </div>
        </motion.div>
      </div>

      {/* Insights y recomendaciones */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="medical-card p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          💡 Insights y Recomendaciones
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <InsightCard
            type="success"
            title="Excelente consistencia"
            description="Has mantenido una racha de 12 días estudiando. ¡Sigue así!"
          />
          <InsightCard
            type="warning"
            title="Enfócate en Cardiología"
            description="Tienes 8 temas rojos en esta especialidad. Considera dedicar más tiempo."
          />
          <InsightCard
            type="info"
            title="Patrón optimal"
            description="Tus mejores sesiones son entre 2-4 PM. Programa estudios importantes en ese horario."
          />
        </div>
      </motion.div>
    </div>
  );
};

// Componentes auxiliares
const AnalyticsCard = ({ icon: Icon, title, value, change, trend, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    orange: 'text-orange-600 bg-orange-50'
  };

  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';

  return (
    <div className="medical-card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className={`text-sm ${trendColor}`}>
            {trend === 'up' ? '↗️' : '↘️'} {change}
          </p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
};

const GoalProgress = ({ title, current, target, unit }) => {
  const percentage = Math.min((current / target) * 100, 100);
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{title}</span>
        <span className="font-medium">{current}/{target} {unit}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">{Math.round(percentage)}% completado</p>
    </div>
  );
};

const InsightCard = ({ type, title, description }) => {
  const typeStyles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-orange-50 border-orange-200 text-orange-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const icons = {
    success: '✅',
    warning: '⚠️',
    info: 'ℹ️'
  };

  return (
    <div className={`p-4 rounded-lg border ${typeStyles[type]}`}>
      <div className="flex items-start">
        <span className="text-lg mr-2">{icons[type]}</span>
        <div>
          <h4 className="font-medium mb-1">{title}</h4>
          <p className="text-sm opacity-90">{description}</p>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
'''
    
    (web_dir / "frontend/src/pages/Analytics.js").write_text(analytics_page, encoding='utf-8')
    print("  ✅ Analytics.js")

def create_config_files(base_dir: Path) -> None:
    """Create project configuration files.
    
    Args:
        base_dir: Path to the base directory
    """
    print("\n⚙️ Creating configuration files...")
    
    # tailwind.config.js mejorado
    tailwind_config = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EBF4FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        secondary: {
          50: '#D1FAE5',
          100: '#A7F3D0',
          200: '#6EE7B7',
          300: '#34D399',
          400: '#10B981',
          500: '#059669',
          600: '#047857',
          700: '#065F46',
          800: '#064E3B',
          900: '#022C22',
        },
        accent: {
          50: '#CFFAFE',
          100: '#A5F3FC',
          200: '#67E8F9',
          300: '#22D3EE',
          400: '#06B6D4',
          500: '#0891B2',
          600: '#0E7490',
          700: '#155E75',
          800: '#164E63',
          900: '#083344',
        },
        medical: {
          bg: '#F8FAFC',
          card: '#FFFFFF',
          surface: '#F1F5F9',
          border: '#E2E8F0',
          text: '#0F172A',
          'text-secondary': '#475569',
          'text-tertiary': '#64748B',
        },
        confidence: {
          red: {
            50: '#FEF2F2',
            500: '#EF4444',
            600: '#DC2626',
          },
          orange: {
            50: '#FFF7ED', 
            500: '#F97316',
            600: '#EA580C',
          },
          yellow: {
            50: '#FEFCE8',
            500: '#EAB308',
            600: '#CA8A04',
          },
          green: {
            50: '#F0FDF4',
            500: '#22C55E',
            600: '#16A34A',
          },
          blue: {
            50: '#EFF6FF',
            500: '#3B82F6',
            600: '#2563EB',
          },
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fadeIn': 'fadeIn 0.6s ease-out',
        'slideIn': 'slideIn 0.4s ease-out',
        'scaleIn': 'scaleIn 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      boxShadow: {
        'medical': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'medical-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'medical-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
'''
    
    (base_dir / "web/frontend/tailwind.config.js").write_text(tailwind_config, encoding='utf-8')
    print("  ✅ tailwind.config.js")
    
    # postcss.config.js
    postcss_config = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
    
    (base_dir / "web/frontend/postcss.config.js").write_text(postcss_config, encoding='utf-8')
    print("  ✅ postcss.config.js")
    
    # .gitignore para web
    gitignore_web = '''# Dependencies
node_modules/
*/node_modules/

# Production builds
build/
dist/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Local data
web/data/
web/logs/
'''
    
    (base_dir / "web/.gitignore").write_text(gitignore_web, encoding='utf-8')
    print("  ✅ .gitignore")

def create_main_readme(base_dir: Path) -> None:
    """Create main README with updated documentation.
    
    Args:
        base_dir: Path to the base directory
    """
    """Crea README principal actualizado"""
    print("\n📖 Creando README principal...")
    
    readme = '''# MedStudy Pro - Complete Ecosystem

> **Sistema Integral de Estudio Médico** con metodología científica basada en neurociencia cognitiva

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Medical](https://img.shields.io/badge/medical-education-red.svg)

## 🎯 **Ecosistema Completo**

Este repositorio contiene **tres aplicaciones integradas** para el estudio médico:

### 📱 **1. Desktop App** (`/desktop`)
- **Tecnología**: Python + CustomTkinter
- **Uso**: Aplicación nativa offline
- **Características**: RAG local, MedCards, sesiones estructuradas

### 🖥️ **2. Planner App** (`/MedStudy_Planner`)  
- **Tecnología**: Python + CustomTkinter
- **Uso**: Planificador retrospectivo independiente
- **Metodología**: Sistema Ali Abdaal con color-coding

### 🌐 **3. Web App** (`/web`) - **NUEVA**
- **Tecnología**: FastAPI + React + Tailwind CSS
- **Uso**: Interfaz web moderna y profesional
- **Características**: Dashboard interactivo, API REST, responsive design

## 🚀 **Inicio Rápido - Web App**

### **Backend FastAPI**
```bash
cd web/backend
../../venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload```'''

def main() -> None:
    """Main entry point for the script."""
    try:
        success = create_organized_web_app()
        if not success:
            print("\n❌ Failed to create web app structure")
            exit(1)
        print("\n✓ Script completed successfully")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()