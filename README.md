# 🧠 MedStudy Pro

> **Sistema de Estudio Médico Basado en Neurociencia Cognitiva con IA Local**

Aplicación desktop que implementa las mejores prácticas de aprendizaje (Active Recall, Repetición Espaciada, Interleaving) para crear un asistente de estudio médico personalizado usando IA 100% local.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-phi3%3Amini-green.svg)
![CustomTkinter](https://img.shields.io/badge/Interface-CustomTkinter-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Instalación Rápida

### **Método Automático (Recomendado)**
```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/Study1.git
cd Study1

# 2. Ejecuta el setup automático
python setup.py

# 3. Inicia la aplicación
python main.py
```

### **Método Manual**
```bash
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Instalar Ollama
# Windows/Mac: Descargar desde https://ollama.ai
# Linux: curl https://ollama.ai/install.sh | sh

# 3. Iniciar Ollama y descargar modelo
ollama serve
ollama pull phi3:mini

# 4. Lanzar aplicación
python main.py
```

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

### **Interfaz Principal**
```
┌─────────────────────────────────────────────────────────┐
│ 🧠 MedStudy Pro - Medical Study Assistant              │
├─────────────────────────────────┬───────────────────────┤
│ 📊 Dashboard │ 📋 Plan │ 📖 Sesiones │ 🧪 Exámenes │ 📊 │
├─────────────────────────────────┼───────────────────────┤
│ 📖 ÁREA PRINCIPAL DE ESTUDIO    │ 💬 Chat Tutor IA     │
│                                 │ ───────────────────   │
│ # Tema: Artritis Reumatoide     │ 👋 ¿Dudas sobre      │
│                                 │ este tema?            │
│ [🖼️ Imagen: Articulaciones]     │                       │
│                                 │ [🔄] [📝] [📤]        │
│ 🧠 Active Recall en 8 min       │                       │
│ ─────────────────────────────   │ Escribe tu pregunta:  │
│ Progreso: ████████░░ 80%        │ [________________]    │
│ [⏸️] [📝] [Quiz Final ▶️]        │ [Enviar] [Parar]      │
└─────────────────────────────────┴───────────────────────┘
```

## 📋 **Comandos Disponibles**

### **Diagnóstico del Sistema**
```bash
python main.py --diagnostic    # Verificar estado completo
python main.py --config-info   # Mostrar configuración
python setup.py               # Setup automático
```

### **Modos de Lanzamiento**
```bash
python main.py                # Aplicación desktop (por defecto)
python main.py --web          # Interfaz web (Gradio)
python gradio_launcher.py     # Interfaz web directa
python main.py --force-launch # Forzar inicio sin diagnósticos
```

### **Desarrollo y Debug**
```bash
python main.py --debug        # Modo debug con logs verbosos
python quick_test.py          # Test rápido de componentes
python main.py --setup        # Ejecutar setup desde main
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

### **Error: Modelo phi3:mini no encontrado**
```bash
# Descargar modelo específico
ollama pull phi3:mini

# Verificar modelos instalados
ollama list
```

## 📁 **Estructura del Proyecto**

```
Study1/ (MedStudy Pro)
├── 🚀 main.py                    # Launcher principal MEJORADO
├── 🔧 setup.py                   # Setup automático NUEVO
├── 📋 requirements.txt           # Dependencias completas
├── ⚙️ config_template.ini        # Configuración plantilla
│
├── 📱 app/                       # Aplicación desktop
│   ├── ui/                       # Interfaces CustomTkinter
│   │   ├── main_window.py        # Ventana principal FUNCIONAL
│   │   └── components/           # Componentes reutilizables
│   │       └── chat_tutor_manager.py # Chat lateral IA FUNCIONAL
│   └── config.py                 # Configuración app
│
├── 🧠 core/                      # Motor del sistema COMPLETO
│   ├── llm_manager.py            # Gestión Ollama/phi3 ✅
│   ├── study_session_manager.py  # Sesiones de estudio ✅
│   ├── medical_knowledge_analyzer.py # Análisis IA ✅
│   ├── rag_engine.py             # RAG con embeddings ✅
│   ├── medcards_system.py        # Sistema SRS Anki-like ✅
│   ├── exam_generator.py         # Generador de exámenes ✅
│   ├── study_planner.py          # Planificador retrospectivo ✅
│   ├── database.py               # SQLite + modelos ✅
│   └── utils.py                  # Utilidades del sistema ✅
│
├── 🌐 gradio_launcher.py         # Interfaz web alternativa ✅
├── 🧪 quick_test.py              # Test rápido del sistema ✅
├── 💾 data/                      # Datos locales (auto-creado)
├── 📊 logs/                      # Logs del sistema (auto-creado)
└── 🧪 tests/                     # Tests automatizados
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

### **v1.0 - MVP (Actual)**
- [x] ✅ Estructura base del proyecto completa
- [x] ✅ Configuración Ollama + phi3:mini funcional
- [x] ✅ Interfaz desktop CustomTkinter integrada
- [x] ✅ Chat Tutor lateral con IA funcional
- [x] ✅ Sistema de diagnósticos automatizado
- [x] ✅ Setup automático completo
- [ ] 🚧 RAG básico con PDFs (70% completo)
- [ ] 🚧 Sesiones de estudio funcionales (80% completo)

### **v1.1 - Beta**
- [ ] 📋 Planificador retrospectivo UI completo
- [ ] 🧪 Exámenes de 45 preguntas
- [ ] 🎴 Sistema MedCards SRS UI
- [ ] 📊 Dashboard de progreso funcional

### **v1.2 - Release**
- [ ] 📦 Empaquetado .exe con PyInstaller
- [ ] 🔧 Instalador automático Windows/Mac
- [ ] 📖 Documentación completa
- [ ] 🎯 Testing beta con médicos

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