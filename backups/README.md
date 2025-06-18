# 💾 Backups - Sistemas Anteriores y Respaldos

## 🎯 **Propósito**

Esta carpeta contiene respaldos completos de todas las versiones anteriores del sistema MedStudy, permitiendo restaurar funcionalidades o migrar componentes específicos.

## 📁 **Estructura de Respaldos**

```
backups/
├── fastapi_system/           # Sistema FastAPI original completo
├── fastapi_system_legacy/    # Backup adicional FastAPI
├── gradio_system/           # Prototipos con interface Gradio
└── experimental/            # Sistemas de prueba y prototipos
```

## 🚀 **fastapi_system/**

### **Contenido**
- Backend FastAPI completo con Ollama
- Sistema RAG con ChromaDB
- APIs REST para planes de estudio
- Configuración de embeddings médicos

### **Cómo Restaurar**
```bash
cd backups/fastapi_system/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### **APIs Disponibles**
- `GET /health` - Health check
- `POST /api/study-plans/create` - Crear plan
- `POST /api/rag/query` - Consultar RAG
- `GET /docs` - Documentación Swagger

## 🧪 **experimental/**

### **Sistemas Incluidos**
- **MedStudy_Planner** - Planner desktop con tkinter
- **app/** - Primera versión de UI components
- **core/** - Lógica de negocio compartida
- **ui/** - Interfaces experimentales
- **data/** - Bases de datos de prueba
- **venv/** - Entornos virtuales legacy

### **Contenido Médico Legacy**
- Base de conocimiento médico original
- Embeddings procesados
- Logs de sistemas anteriores

## 📋 **Cuándo Usar Estos Respaldos**

### **FastAPI System**
- Si necesitas APIs más rápidas que Django
- Para desarrollo de microservicios
- Integración directa con Ollama sin LangChain

### **Experimental Systems**
- Recuperar funcionalidades específicas
- Análisis de evolución del código
- Debugging de problemas legacy

## 🔄 **Migración Desde Respaldos**

### **FastAPI → Django**
```bash
# Ya completada - ver MIGRATION_SUMMARY.md
cd docs/migration/
cat MIGRATION_SUMMARY.md
```

### **Restaurar Datos**
```bash
# Copiar base de conocimiento
cp -r backups/experimental/data/documents/ medical_knowledge/general/

# Restaurar embeddings
cp -r backups/experimental/medical_knowledge_base/ medstudy_app/data/
```

## ⚠️ **Importante**

### **NO Borrar Esta Carpeta**
- Contiene únicos respaldos de sistemas funcionales
- Histórico completo de desarrollo
- Funcionalidades que podrían ser necesarias en el futuro

### **Mantenimiento**
- Estos sistemas están "congelados"
- Solo para consulta y restauración
- NO actualizar código legacy

## 📞 **Soporte Legacy**

Para restaurar o migrar desde respaldos:
1. Consultar `/docs/migration/` para guías
2. Revisar READMEs específicos en cada carpeta
3. Usar scripts de restauración incluidos

---

**Respaldos seguros de toda la evolución de MedStudy 🔒**