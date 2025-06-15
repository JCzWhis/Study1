# 🧪 Guía de Testing - MedStudy Pro con Gemma 3-2B

## 🚀 **Pasos para Probar el Sistema**

### **📋 Paso 1: Preparar el Entorno**

```bash
# 1. Abrir terminal en el proyecto
cd /mnt/c/reumai_tts/MedStudyPro/Study1/web/backend

# 2. Verificar que tienes los archivos actualizados
ls -la app/core/llm_service.py
ls -la app/config.py
ls -la test_gemma_integration.py
ls -la migrate_to_gemma.py
```

### **📋 Paso 2: Instalar Dependencias**

```bash
# Instalar dependencias Python
pip install fastapi uvicorn httpx chromadb sentence-transformers datasets PyPDF2 python-multipart aiofiles

# O usar el requirements.txt
pip install -r requirements.txt
```

### **📋 Paso 3: Configurar Ollama**

```bash
# 3.1 Verificar si Ollama está instalado
ollama --version

# 3.2 Si no está instalado, instalarlo
# Windows: Descargar desde https://ollama.ai
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# 3.3 Iniciar Ollama (en terminal separada)
ollama serve

# 3.4 Descargar Gemma 3-2B
ollama pull gemma2:2b

# 3.5 Verificar que está disponible
ollama list
```

### **📋 Paso 4: Ejecutar Script de Migración**

```bash
# Ejecutar script automático de migración
python migrate_to_gemma.py

# Deberías ver:
# ✅ Ollama disponible
# ✅ Servicio funcionando  
# ✅ Modelo descargado
# ✅ Verificación exitosa
```

### **📋 Paso 5: Test de Integración**

```bash
# Ejecutar test completo del sistema
python test_gemma_integration.py

# Deberías ver:
# 🔧 Test 1: LLM Service Configuration ✅
# 🔍 Test 2: Model Availability Check ✅
# 💬 Test 3: Simple Response Generation ✅
# 📚 Test 4: Medical Study Plan Generation ✅
# 💡 Test 5: Topic Suggestions Generation ✅
# 🔍 Test 6: RAG Integration with Gemma ✅
# 🚀 Test 7: Enhanced Plan Generation ✅
```

### **📋 Paso 6: Cargar Embeddings Médicos**

```bash
# Test simple de procesamiento
python simple_test_embeddings.py

# Deberías ver:
# 📚 Found 468 markdown files
# ✅ Successfully processed: 5 files

# Una vez que funcione el backend, cargar todos:
# curl -X POST http://localhost:8000/api/rag/bulk-load-embeddings
```

### **📋 Paso 7: Iniciar el Backend**

```bash
# Terminal 1: Mantener Ollama corriendo
ollama serve

# Terminal 2: Iniciar FastAPI
python -m uvicorn app.main:app --reload --port 8000

# Deberías ver:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### **📋 Paso 8: Test de APIs**

```bash
# Terminal 3: Probar endpoints

# 8.1 Health check
curl http://localhost:8000/api/health

# 8.2 Estado del LLM
curl http://localhost:8000/api/llm/status

# 8.3 Modelos disponibles
curl http://localhost:8000/api/llm/models

# 8.4 Test RAG
curl "http://localhost:8000/api/rag/test?query=artritis%20reumatoide&specialty=reumatologia"

# 8.5 Estado del RAG
curl http://localhost:8000/api/rag/status

# 8.6 Cargar embeddings (toma unos minutos)
curl -X POST http://localhost:8000/api/rag/bulk-load-embeddings

# 8.7 Estadísticas de la colección
curl http://localhost:8000/api/rag/collection-stats
```

### **📋 Paso 9: Iniciar Frontend**

```bash
# Terminal 4: Frontend
cd ../frontend

# Instalar dependencias (si no están)
npm install

# Iniciar React
npm start

# Se abre automáticamente en http://localhost:3000
```

### **📋 Paso 10: Test Completo via Web**

1. **Dashboard**: Ver estadísticas
2. **Planes**: Crear nuevo plan con IA
3. **Estudio**: Probar sesión de estudio  
4. **Analytics**: Ver progreso

## 🔍 **Qué Verificar en Cada Paso**

### **✅ Test de Gemma 3-2B**
- [ ] Modelo descargado: `ollama list` muestra `gemma2:2b`
- [ ] Servicio respondiendo: `curl http://localhost:11434/api/tags`
- [ ] Configuración correcta: Model = `gemma2:2b` en test
- [ ] Respuestas coherentes: JSON válido en respuestas
- [ ] Velocidad mejorada: Respuestas más rápidas que Phi3

### **✅ Test de RAG con Embeddings**
- [ ] 468 archivos markdown detectados
- [ ] Procesamiento sin errores
- [ ] Clasificación por especialidades correcta
- [ ] Búsquedas devuelven contenido relevante
- [ ] Integración LLM + RAG funcionando

### **✅ Test de APIs**
- [ ] `/api/llm/status` → `"available": true`
- [ ] `/api/llm/models` → Lista 4 modelos
- [ ] `/api/rag/status` → RAG inicializado  
- [ ] `/api/rag/collection-stats` → 1000+ documentos
- [ ] `/api/plans/create` → Genera plan con Gemma

### **✅ Test de Frontend**
- [ ] Página carga sin errores
- [ ] Dashboard muestra datos
- [ ] Crear plan funciona
- [ ] Sesiones de estudio operativas
- [ ] RAG integrado en contenido

## 🚨 **Solución de Problemas**

### **Error: Ollama no encontrado**
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh
# O descargar desde https://ollama.ai
```

### **Error: Modelo no disponible**
```bash
ollama pull gemma2:2b
ollama list  # Verificar
```

### **Error: Dependencias faltantes**
```bash
pip install -r requirements.txt
```

### **Error: Puerto ocupado**
```bash
# Cambiar puerto del backend
python -m uvicorn app.main:app --reload --port 8001

# Cambiar puerto del frontend
PORT=3001 npm start
```

### **Error: ChromaDB**
```bash
# Limpiar base de datos
rm -rf data/medical_rag/chroma_db
# Reiniciar el backend
```

## 📊 **Resultados Esperados**

### **Performance con Gemma 3-2B**
- ⏱️ **Tiempo de respuesta**: 2-5 segundos
- 🎯 **Precisión médica**: >90% contenido relevante  
- 📋 **Formato JSON**: 100% respuestas válidas
- 🧠 **Coherencia**: Planes de estudio lógicos
- 🔍 **RAG Integration**: Contenido específico incluido

### **Métricas de Éxito**
- ✅ **Backend**: Inicia sin errores
- ✅ **LLM**: Responde a queries médicas
- ✅ **RAG**: 468 archivos cargados
- ✅ **Frontend**: Interfaz funcional
- ✅ **Integración**: Plan generation working

## 📞 **¿Qué Hacer Si Algo Falla?**

1. **Revisar logs** del backend
2. **Verificar Ollama** está corriendo
3. **Comprobar dependencias** instaladas
4. **Limpiar cache** de ChromaDB
5. **Reiniciar servicios** uno por uno

---

## 🎉 **¡Listos para Probar!**

Sigue estos pasos en orden y avísame en qué paso estás o si encuentras algún error. ¡Vamos a ver Gemma 3-2B en acción con los embeddings médicos!