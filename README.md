# 🏥 MedStudy Pro - Sistema de Estudio Médico con IA

## 🎯 **Descripción**

MedStudy Pro es un sistema avanzado de educación médica que utiliza inteligencia artificial (Django + LangChain + Ollama) para crear planes de estudio personalizados, generar evaluaciones adaptativas y proporcionar análisis de progreso con repetición espaciada.

![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Gemma2-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 **Inicio Rápido**

### **Instalación en 1 Comando**
```bash
cd quickstart
./START_MEDSTUDY.bat  # Windows
./start_medstudy.sh   # Linux/Mac
```

### **Acceso a Interfaces**
- **Django Admin:** http://localhost:8000/admin/
- **API REST:** http://localhost:8000/api/v1/
- **Frontend:** http://localhost:3000/
- **Health Check:** http://localhost:8000/health/

### **🔧 Para Desarrolladores**
```bash
# 1. Sistema Django
cd medstudy_app
python setup_django_medstudy.py
source venv_django/bin/activate  # Linux/Mac
venv_django\Scripts\activate     # Windows
python manage.py runserver 8000

# 2. Frontend React
cd frontend
npm install && npm start

# 3. Ollama (IA local)
ollama serve
ollama pull gemma2:2b
```

## ✨ Características Principales

### 🧠 **Metodología Científica de Aprendizaje**
- **Active Recall**: Preguntas integradas cada 10 minutos durante el estudio
- **Repetición Espaciada**: Algoritmo SRS personalizado para medicina
- **Interleaving**: Mezcla inteligente de temas para mejor retención
- **Técnica Feynman**: Simplificación forzada para verificar comprensión

### 📖 **Sesiones de Estudio Estructuradas**
- **45 minutos** de contenido generado por IA desde tu propio RAG
- **Timer Pomodoro** integrado con seguimiento de progreso
- **Interfaz web responsiva** optimizada para estudio médico
- **Quiz interactivo** con evaluación de confianza por tema
- **Contenido médico especializado** con RAG personalizable

### 📋 **Planificador Retrospectivo**
- Sistema basado en **Ali Abdaal's Spaced Repetition Spreadsheet**
- **No predicción del futuro**: Te enfocas en lo que NO sabes
- **Color-coding** por nivel de comprensión
- **Seguimiento automático** de intervalos de repetición

### 🧪 **Exámenes Personalizados**
- **45 preguntas** por plan de estudio completo
- **Casos clínicos** generados desde tu RAG
- **Adaptativo** según tu rendimiento histórico
- **Feedback explicativo** inmediato

### 🎴 **Sistema "MedCards" (inspirado en Anki)**
- **Generación automática** de tarjetas desde sesiones
- **Algoritmo SRS** optimizado para medicina
- **Integración visual** con imágenes médicas
- **Sincronización** con progreso de estudio

## 🎯 **Público Objetivo**

- **Estudiantes de Medicina** (pregrado y postgrado)
- **Residentes** preparando rotaciones
- **Especialistas** actualizando conocimientos
- **Médicos** preparando certificaciones

## 🖥️ **App Desktop Híbrida (Mejor de ambos mundos)**

### **¿Por qué Desktop + Web UI?**
- ✅ **100% Privado**: Todo corre en tu PC, sin enviar datos afuera
- ✅ **Sin internet**: Funciona completamente offline una vez instalado
- ✅ **UI moderna**: Interfaz web bonita que se abre en tu navegador
- ✅ **Fácil instalación**: Un solo .exe/.dmg que incluye todo
- ✅ **Como Discord/Slack**: App desktop con interfaz web local

### **Experiencia de Usuario**
```
1️⃣ Doble clic en MedStudy.exe
         ↓
2️⃣ Se inicia automáticamente:
   ├── 🔧 Backend FastAPI (puerto 8000)  
   ├── 🌐 Frontend React (puerto 3000)
   └── 🌍 Se abre navegador en localhost:3000
         ↓
3️⃣ Interfaz web moderna en tu navegador local:

┌──────────────────────────────────────────────────────────┐
│ 🧠 MedStudy Pro - localhost:3000 (OFFLINE) 🔒           │
├─────────────────────────────────────────────────────────┤
│ 📊 Dashboard │ 📋 Planes │ 📖 Estudio │ 📈 Analytics    │
├─────────────────────────────────────────────────────────┤
│ 📖 SESIÓN DE ESTUDIO ACTIVA                             │
│ ┌─────────────────────┐ ┌─────────────────────────────┐ │
│ │ ⏱️ 23:45 / 45:00     │ │ 🎯 Artritis Reumatoide     │ │
│ │ ████████░░░ 52%     │ │ Confianza: 🟡 Medio        │ │
│ └─────────────────────┘ └─────────────────────────────┘ │
│ 📚 Contenido generado por IA local (Ollama):            │
│ • Patogenia: autoinmune, citocinas TNF-α               │
│ • Criterios ACR/EULAR 2010 para diagnóstico            │  
│ • DMARDs primera línea: MTX + ácido fólico             │
│ 🧠 Active Recall en 7 min                              │
│ [⏸️ Pausar] [📝 Notas] [✅ Completar] [🔄 Quiz Final]  │
└─────────────────────────────────────────────────────────┘
```

## 📋 **Comandos Disponibles**

### **Desarrollo Local**
```bash
# Backend FastAPI
cd web/backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend React
cd web/frontend
npm start

# Verificar APIs
curl http://localhost:8000/api/health
curl http://localhost:8000/api/docs  # Swagger docs
```

### **Producción**
```bash
# Build frontend para producción
cd web/frontend
npm run build

# Deploy backend
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Con Docker (opcional)
docker-compose up -d
```

### **Testing y Debug**
```bash
# Test backend
cd web/backend
python -m pytest tests/

# Test RAG system
curl http://localhost:8000/api/rag/test

# Verificar Ollama
ollama list
ollama ps
```

## 🔧 **Solución de Problemas**

### **Error: Ollama no encontrado**
```bash
# 1. Instalar Ollama
# Windows/Mac: https://ollama.ai
# Linux: curl https://ollama.ai/install.sh | sh

# 2. Iniciar servicio
ollama serve

# 3. Descargar modelo
ollama pull phi3:mini
```

### **Error: Dependencias faltantes**
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O usar setup automático
python setup.py
```

### **Error: No se puede conectar a Ollama**
```bash
# Verificar que Ollama esté corriendo
ollama list

# Si no está corriendo:
ollama serve

# En otra terminal:
python main.py --diagnostic
```

### **Error: Modelo gemma2:2b no encontrado**
```bash
# Descargar modelo específico
ollama pull gemma2:2b

# Verificar modelos instalados
ollama list
```

## 📁 **Estructura del Proyecto**

```
Study1/ (MedStudy Pro - Web App)
├── 📋 README.md                  # Documentación principal
├── ⚙️ .env.example               # Variables de entorno ejemplo
│
├── 🌐 web/                       # Aplicación web completa
│   ├── 🚀 backend/               # API FastAPI + IA
│   │   ├── app/
│   │   │   ├── main.py           # FastAPI app principal ✅
│   │   │   ├── core/
│   │   │   │   ├── llm_service.py        # Gestión Ollama/Gemma 3-2B ✅
│   │   │   │   └── medical_rag.py        # RAG con embeddings ✅
│   │   │   ├── database/         # Modelos SQLite (futuro)
│   │   │   ├── models/           # Pydantic schemas ✅
│   │   │   └── routers/          # Endpoints organizados
│   │   ├── requirements.txt      # Dependencias Python ✅
│   │   └── .env                  # Config local (NO incluir en git)
│   │
│   └── 💻 frontend/              # React SPA moderna
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Dashboard.js          # Panel principal ✅
│       │   │   ├── Plans.js              # Gestión de planes ✅
│       │   │   ├── SimplePlanCreator.js  # Creador IA ✅
│       │   │   ├── Study.js              # Sesiones de estudio ✅
│       │   │   └── Analytics.js          # Métricas y progreso ✅
│       │   ├── components/       # Componentes reutilizables
│       │   └── App.js           # Router principal ✅
│       ├── package.json         # Dependencias Node.js ✅
│       └── public/              # Assets estáticos
│
├── 🗂️ Legacy Desktop/            # Versión desktop original
│   ├── main.py                  # Launcher CustomTkinter
│   ├── app/ui/                  # Interfaces desktop
│   └── core/                    # Lógica compartida
│
├── 💾 data/                     # Datos locales (auto-creado)
├── 📊 logs/                     # Logs del sistema (auto-creado)
└── 🧪 tests/                    # Tests automatizados
```

## 🎨 **Paleta de Colores**

- **Azul Primario**: `#1E3A8A` (professional medical)
- **Verde Médico**: `#10B981` (success, progress)
- **Turquesa**: `#06B6D4` (info, accents)
- **Fondo Estudio**: `#FEFCF9` (concentración)
- **Texto**: `#1F2937` (legibilidad óptima)

## 🔬 **Basado en Evidencia Científica**

### **Referencias Implementadas:**
- **Active Recall**: Karpicke & Roediger (2008)
- **Spaced Repetition**: Ebbinghaus, Pimsleur
- **Interleaving**: Rohrer & Taylor (2010)
- **Testing Effect**: McDaniel & Einstein (2007)
- **Ali Abdaal**: Spreadsheet retrospectivo para medicina

### **Optimizado para Medicina:**
- **Casos clínicos** como contexto principal
- **Imágenes diagnósticas** integradas
- **Terminología médica** en embeddings
- **Estructura diagnóstica**: síntomas → diagnóstico → tratamiento

## 🔮 **Roadmap**

### **v1.0 - MVP Web (Actual)**
- [x] ✅ FastAPI backend con endpoints completos
- [x] ✅ React frontend con navegación funcional  
- [x] ✅ Configuración Ollama + Gemma 3-2B integrada
- [x] ✅ RAG médico con ChromaDB y PDFs completamente funcional
- [x] ✅ Creador de planes con IA funcional
- [x] ✅ Sistema de estudio con timer y confianza
- [x] ✅ Upload de PDFs para enriquecer RAG
- [x] ✅ Dashboard con métricas de progreso
- [x] ✅ Embeddings médicos cargados masivamente
- [x] ✅ Script completo para interfaz Lovable generado

### **v1.1 - Funcionalidades Avanzadas**
- [ ] 🧪 Generador de exámenes adaptativos 
- [ ] 🎴 Sistema MedCards SRS integrado
- [ ] 📊 Analytics avanzados con gráficos
- [ ] 🔍 Búsqueda inteligente en RAG
- [ ] 💾 Base de datos PostgreSQL

### **v1.2 - Empaquetado Desktop**
- [ ] 📦 PyInstaller/Electron para .exe/.dmg/.appimage
- [ ] 🚀 Auto-launcher que inicia backend+frontend+browser
- [ ] 💾 Instalador con Ollama + Gemma 3-2B incluido
- [ ] 🔧 Auto-updater integrado
- [ ] 🎯 Testing beta con médicos reales

### **v2.0 - Futuro**
- [ ] 🖼️ OCR avanzado para imágenes médicas
- [ ] 🤖 Modelos médicos especializados
- [ ] 📱 App móvil complementaria
- [ ] 🌐 Comunidad médica integrada

## 🤝 **Contribuir**

**¡Buscamos médicos y desarrolladores!**

### **Áreas Prioritarias:**
- 🏥 **Validación médica**: Casos clínicos, protocolos
- 🧠 **Optimización de prompts**: Especialidades específicas
- 🎨 **UX médico**: Workflow optimizado para estudio
- 🔬 **Testing**: Validación con estudiantes reales

### **Cómo Contribuir:**
1. Fork del repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 **Licencia**

**MIT License** - Uso libre para educación médica

```
Copyright (c) 2024 Dr. Cruz Migueles

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 👨‍⚕️ **Desarrollado por Médicos**

**Dr. Cruz Migueles** - Internista y Reumatólogo  
*"Aplicando neurociencia cognitiva al estudio médico"*

**Especialización:**
- 🏥 Medicina Interna 
- 🦴 Reumatología (Fellow)
- 💻 Programación en Python
- 🧠 Neurociencia del aprendizaje

## 📞 **Soporte y Contacto**

- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/Study1/issues)
- 💬 **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/Study1/discussions)
- 📧 **Email**: tu-email@example.com
- 🐦 **Twitter**: @tu-usuario

## 🙏 **Agradecimientos**

- **Ali Abdaal** por su metodología de repetición espaciada
- **Ollama Team** por la IA local accessible
- **CustomTkinter** por la interfaz moderna
- **Anki** por inspirar el sistema SRS
- **Comunidad médica** por feedback y validación

---

<div align="center">

**[⭐ Star este proyecto](https://github.com/tu-usuario/Study1)** •
**[🐛 Reportar Issues](https://github.com/tu-usuario/Study1/issues)** •
**[💬 Discusiones médicas](https://github.com/tu-usuario/Study1/discussions)** •
**[📖 Documentación](https://github.com/tu-usuario/Study1/wiki)**

### 🎉 **¡Haz que el estudio médico sea más efectivo!**

</div>