# 🚀 MedStudy Pro - Guía de Instalación Rápida

## 📋 Requisitos del Sistema

- **Python 3.8+** (Recomendado: Python 3.11+)
- **4GB RAM** mínimo (8GB+ recomendado)
- **5GB espacio libre** en disco
- **Windows 10+, macOS 10.14+, o Linux Ubuntu 18.04+**

## ⚡ Instalación Automática (Recomendada)

### Opción 1: Asistente de Lanzamiento
```bash
# 1. Descargar/clonar el proyecto
git clone https://github.com/tu-usuario/medstudy-pro.git
cd medstudy-pro

# 2. Ejecutar asistente automático
python launch_assistant.py
```

El asistente te guiará paso a paso y configurará todo automáticamente.

### Opción 2: Setup Tradicional
```bash
# 1. Instalar dependencias
python setup.py

# 2. Ejecutar diagnóstico
python main.py --diagnostic

# 3. Lanzar aplicación
python main.py
```

## 🛠️ Instalación Manual

### Paso 1: Instalar Python
- **Windows/Mac**: Descargar desde [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3 python3-pip`

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Instalar Ollama (IA Local)
- **Windows/Mac**: Descargar desde [ollama.ai](https://ollama.ai)
- **Linux**: `curl https://ollama.ai/install.sh | sh`

### Paso 4: Configurar Ollama
```bash
# Iniciar servicio (mantener terminal abierto)
ollama serve

# En otra terminal: descargar modelo
ollama pull phi3:mini
```

### Paso 5: Lanzar MedStudy Pro
```bash
python main.py
```

## 🔧 Solución de Problemas

### Error: "Ollama no encontrado"
1. Verificar instalación: `ollama --version`
2. Si no está instalado: visitar [ollama.ai](https://ollama.ai)
3. Reiniciar terminal después de instalar

### Error: "Modelo no encontrado"
```bash
ollama pull phi3:mini
```

### Error: "Dependencias faltantes"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "No se puede conectar a Ollama"
1. Verificar que el servicio esté corriendo: `ollama serve`
2. Verificar en otra terminal: `ollama list`

## 🚀 Métodos de Lanzamiento

| Comando | Descripción |
|---------|-------------|
| `python main.py` | Lanzar aplicación desktop |
| `python main.py --diagnostic` | Ejecutar diagnóstico del sistema |
| `python main.py --web` | Lanzar interfaz web (Gradio) |
| `python gradio_launcher.py` | Lanzar solo interfaz web |
| `python launch_assistant.py` | Ejecutar asistente de configuración |
| `python test_system.py` | Ejecutar tests completos |

## 📊 Verificación de Instalación

Ejecutar test completo:
```bash
python test_system.py
```

Verificar componentes críticos:
```bash
python -c "from core import DatabaseManager; print('✅ Core funcional')"
python -c "from app.config import config; print('✅ Config funcional')"
python -c "import customtkinter; print('✅ UI funcional')"
```

## 🎯 Primeros Pasos

1. **Lanzar aplicación**: `python main.py`
2. **Verificar estado**: Revisar indicadores en la interfaz
3. **Chat con IA**: Usar el panel lateral de chat
4. **Subir documentos**: Tab "Documentos" para agregar material de estudio
5. **Crear sesiones**: Tab "Sesiones" para estudio estructurado

## 💡 Consejos de Rendimiento

- **RAM**: 8GB+ para mejor rendimiento con IA
- **SSD**: Mejora velocidad de carga de documentos
- **GPU**: Ollama puede usar GPU si está disponible
- **Internet**: Solo necesario para instalación inicial

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/medstudy-pro/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/medstudy-pro/wiki)
- **Tests**: `python test_system.py`

---