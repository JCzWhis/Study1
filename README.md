# 🧠 MedStudy Pro

> **Asistente de Estudio Médico con IA Local**

Sistema completo de estudio médico que combina tarjetas Anki inteligentes, chat médico con IA y gestión de documentos usando tecnologías modernas.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-phi3%3Amini-green.svg)
![Gradio](https://img.shields.io/badge/Interface-Gradio-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características Principales

### 🤖 Chat Médico Inteligente
- Respuestas contextualizadas usando RAG (Retrieval-Augmented Generation)
- Búsqueda semántica en documentos médicos
- Compatible con Ollama (phi3:mini) - **100% local y gratuito**
- Preparado para Gemini y Claude

### 🎴 Sistema Anki Avanzado
- Algoritmo de repetición espaciada (SRS) fiel a Anki
- Generación automática de tarjetas con IA
- Estadísticas detalladas de progreso
- Importación/exportación compatible

### 📚 Gestión de Documentos
- Procesamiento automático de PDFs y textos
- Sistema RAG con embeddings locales
- Base de conocimientos médicos personalizada
- Búsqueda semántica inteligente

### 📊 Dashboard de Progreso
- Estadísticas visuales de estudio
- Análisis de rendimiento por tema
- Seguimiento de rachas de estudio
- Métricas de retención de información

## 🚀 Instalación Rápida

### Prerrequisitos
1. **Python 3.11+**
2. **Ollama** desde [ollama.ai](https://ollama.ai)
3. **Modelo phi3:mini**: `ollama pull phi3:mini`

### Setup en 3 pasos
```bash
# 1. Clonar repositorio
git clone https://github.com/JCzWhis/Study1.git
cd Study1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python main.py
```

## 🎯 Uso

### Interfaz Web Moderna
```bash
python main.py --interface gradio
# 🌐 Abre http://localhost:7860
```

### Interfaz Desktop (Alternativa)
```bash
python main.py --interface tkinter
```

### Diagnóstico del Sistema
```bash
python utils/diagnostics.py
# Verifica Ollama y dependencias
```

## 📁 Estructura del Proyecto

```
Study1/
├── 🚀 main.py                    # Launcher principal
├── 📋 requirements.txt           # Dependencias
├── ⚙️ config_template.ini        # Configuración
│
├── 🌐 interfaces/                # Interfaces de usuario
│   ├── gradio_app.py             # Web moderna (Gradio)
│   └── tkinter_app.py            # Desktop (CustomTkinter)
│
├── 🧠 core/                      # Sistema principal
│   ├── llm_manager.py            # Gestión de LLMs
│   ├── anki_system.py            # Tarjetas inteligentes
│   └── rag_engine.py             # Motor de documentos
│
├── 💾 data/                      # Persistencia
│   ├── database.py               # SQLite + modelos
│   └── migrations/               # Actualizaciones BD
│
├── 🔧 utils/                     # Utilidades
│   ├── config.py                 # Configuración
│   ├── logging.py                # Sistema de logs
│   └── diagnostics.py            # Herramientas debug
│
└── 🧪 tests/                     # Tests automatizados
```

## ⚙️ Configuración

### Configuración Básica (Automática)
El sistema se configura solo al primer uso.

### Configuración Avanzada
```bash
cp config_template.ini config.ini
# Editar según necesidades
```

## 🔮 Roadmap

### 🎯 Versión Actual (v1.0)
- ✅ Chat médico con Ollama
- ✅ Sistema Anki completo
- ✅ Gestión de documentos
- ✅ Interfaz Gradio moderna

### 🚀 Próximas Versiones
- [ ] 🌐 Integración con Gemini (Google)
- [ ] 🤖 Soporte para Claude (Anthropic)
- [ ] 📱 App móvil
- [ ] 🔊 Síntesis de voz
- [ ] ☁️ Sincronización en la nube

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Especialmente de la comunidad médica.

### Áreas que Necesitan Ayuda:
- 🏥 **Contenido médico**: Casos clínicos, protocolos
- 🧠 **Prompts**: Optimización para especialidades
- 🎨 **UI/UX**: Mejorar experiencia de usuario
- 🧪 **Testing**: Casos de prueba
- 📖 **Documentación**: Guías y tutoriales

## 📄 Licencia

MIT License - Uso libre para educación médica.

## 👨‍⚕️ Créditos

Desarrollado **por médicos para médicos** usando:
- **Ollama + phi3:mini**: IA local gratuita
- **Gradio**: Interfaz web moderna
- **SQLite**: Base de datos ligera
- **Python**: Ecosistema robusto

---

<div align="center">

**[⭐ Star este proyecto](https://github.com/JCzWhis/Study1)** •
**[🐛 Reportar Issues](https://github.com/JCzWhis/Study1/issues)** •
**[💬 Discusiones](https://github.com/JCzWhis/Study1/discussions)**
</div>
