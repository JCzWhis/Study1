# 🧠 MedStudy Pro

> **Sistema de Estudio Médico Basado en Neurociencia Cognitiva con IA Local**

Aplicación desktop que implementa las mejores prácticas de aprendizaje (Active Recall, Repetición Espaciada, Interleaving) para crear un asistente de estudio médico personalizado usando IA 100% local.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-phi3%3Amini-green.svg)
![CustomTkinter](https://img.shields.io/badge/Interface-CustomTkinter-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características Principales

### 🧠 **Metodología Científica de Aprendizaje**
- **Active Recall**: Preguntas integradas cada 10 minutos durante el estudio
- **Repetición Espaciada**: Algoritmo SRS personalizado para medicina
- **Interleaving**: Mezcla inteligente de temas para mejor retención
- **Técnica Feynman**: Simplificación forzada para verificar comprensión

### 📖 **Sesiones de Estudio Estructuradas**
- **45 minutos** de contenido generado por IA desde tu propio RAG
- **Timer Pomodoro** integrado con modo concentración
- **Chat tutor lateral** para dudas inmediatas (phi3:mini)
- **Quiz final** de 10 preguntas por sesión
- **Imágenes médicas** y esquemas integrados

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

## 🖥️ **Aplicación Desktop Local**

### **¿Por qué Desktop?**
- ✅ **100% Privado**: Tus datos médicos nunca salen de tu PC
- ✅ **Sin internet**: Funciona completamente offline
- ✅ **Rendimiento**: Sin latencia de conexión
- ✅ **Vendible**: Instalador .exe profesional
- ✅ **Datos seguros**: Base de datos local encriptada

### **Interfaz de Sesión**
```
┌─────────────────────────────────────────────────────────┐
│ ⏰ 23:45  📚 Cardiología: Insuficiencia Cardíaca  [🔧] │
├─────────────────────────────────┬───────────────────────┤
│ 📖 CONTENIDO PRINCIPAL          │ 💬 Tutor IA          │
│                                 │ ───────────────────   │
│ # Insuficiencia Cardíaca        │ 👋 ¿Dudas sobre      │
│                                 │ este tema?            │
│ [🖼️ Imagen: Eco normal vs IC]   │                       │
│                                 │ [Minimizar chat] ➖   │
│ 🧠 Active Recall cada 10min     │                       │
│ ─────────────────────────────   │                       │
│ Progreso: ████████░░ 80%        │                       │
│ [⏸️] [📝] [Quiz Final ▶️]        │                       │
└─────────────────────────────────┴───────────────────────┘
```

## 🚀 Instalación

### **Prerrequisitos**
1. **Windows 10/11** (próximamente Mac/Linux)
2. **Python 3.11+**
3. **Ollama** + modelo **phi3:mini**

### **Instalación Rápida**
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/Study1.git
cd Study1

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar Ollama
ollama pull phi3:mini
ollama serve

# 5. Ejecutar aplicación
python main.py
```

### **Instalación para Usuarios Finales** (Próximamente)
- **MedStudy-Pro-Setup.exe** - Instalador automático
- **MedStudy-Pro-Portable.zip** - Versión portable

## 📁 Arquitectura del Proyecto

```
Study1/ (MedStudy Pro)
├── 🚀 main.py                    # Launcher principal
├── 📋 requirements.txt           # Dependencias completas
├── ⚙️ config_template.ini        # Configuración
│
├── 📱 app/                       # Aplicación desktop
│   ├── ui/                       # Interfaces CustomTkinter
│   │   ├── main_window.py        # Ventana principal
│   │   ├── dashboard.py          # Dashboard de progreso
│   │   ├── session.py            # Sesión de estudio
│   │   └── components/           # Componentes reutilizables
│   │       ├── chat_tutor.py     # Chat lateral IA
│   │       ├── timer.py          # Timer Pomodoro
│   │       └── quiz_widget.py    # Sistema de preguntas
│   └── config.py                 # Configuración app
│
├── 🧠 core/                      # Motor del sistema
│   ├── rag_engine.py             # RAG con embeddings locales
│   ├── llm_manager.py            # Gestión Ollama/phi3
│   ├── study_planner.py          # Planificador retrospectivo
│   ├── spaced_repetition.py      # Algoritmo SRS médico
│   └── database.py               # SQLite + modelos
│
├── 💾 data/                      # Datos locales
│   ├── documents/                # PDFs subidos por usuario
│   ├── images/                   # Imágenes médicas extraídas
│   ├── embeddings/               # Vectores para RAG
│   └── user_progress/            # Progreso y estadísticas
│
└── 🧪 tests/                     # Tests automatizados
```

## 🎨 Paleta de Colores

- **Azul Primario**: `#1E3A8A` (professional medical)
- **Verde Médico**: `#10B981` (success, progress)
- **Turquesa**: `#06B6D4` (info, accents)
- **Fondo Estudio**: `#FEFCF9` (concentración)
- **Texto**: `#1F2937` (legibilidad óptima)

## 🔬 Basado en Evidencia Científica

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

## 🔮 Roadmap

### **v1.0 - MVP (Actual)**
- [x] ✅ Estructura base del proyecto
- [x] ✅ Configuración Ollama + phi3:mini
- [ ] 🚧 Interfaz desktop CustomTkinter
- [ ] 🚧 RAG básico con PDFs
- [ ] 🚧 Sesiones de estudio funcionales

### **v1.1 - Beta**
- [ ] 📋 Planificador retrospectivo completo
- [ ] 🧪 Exámenes de 45 preguntas
- [ ] 🎴 Sistema MedCards SRS
- [ ] 📊 Dashboard de progreso

### **v1.2 - Release**
- [ ] 📦 Empaquetado .exe
- [ ] 🔧 Instalador automático
- [ ] 📖 Documentación completa
- [ ] 🎯 Testing beta con médicos

### **v2.0 - Futuro**
- [ ] 🖼️ OCR avanzado para imágenes médicas
- [ ] 🤖 Modelos médicos especializados
- [ ] 📱 Sincronización móvil
- [ ] 🌐 Comunidad médica integrada

## 🤝 Contribuir

**¡Buscamos médicos y desarrolladores!**

### **Áreas Prioritarias:**
- 🏥 **Validación médica**: Casos clínicos, protocolos
- 🧠 **Optimización de prompts**: Especialidades específicas
- 🎨 **UX médico**: Workflow optimizado para estudio
- 🔬 **Testing**: Validación con estudiantes reales

## 📄 Licencia

**MIT License** - Uso libre para educación médica

## 👨‍⚕️ Desarrollado por Médicos

**Dr. Cruz Migueles** - Internista y Reumatólogo  
*"Aplicando neurociencia cognitiva al estudio médico"*

---

<div align="center">

**[⭐ Star este proyecto](https://github.com/tu-usuario/Study1)** •
**[🐛 Reportar Issues](https://github.com/tu-usuario/Study1/issues)** •
**[💬 Discusiones médicas](https://github.com/tu-usuario/Study1/discussions)**

</div>