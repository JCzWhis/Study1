# Sistema de Procesamiento de Embeddings para Knowledge Base

Sistema completo y robusto para convertir documentos médicos en embeddings optimizados para aplicaciones comerciales con LLM locales.

## 🎯 Características Principales

- **Procesamiento Robusto**: Maneja múltiples formatos sin fallar por archivos corruptos
- **Optimizado para Hardware Limitado**: Ryzen 5 3320G + 16GB RAM + GPU Vega
- **Multilingüe**: Español/Inglés con modelo multilingual-e5-base
- **Chunking Inteligente**: Preserva estructura de headers y contexto
- **Búsqueda Rápida**: Índices FAISS precomputados (<100ms)
- **Checkpoints**: Reanuda procesamiento si se interrumpe
- **Logging Detallado**: Seguimiento completo de éxitos/errores

## 📁 Estructura de Archivos

```
Study1/
├── embeddings_processor.py      # Sistema principal
├── setup_embeddings.py          # Instalación automática
├── requirements_embeddings.txt  # Dependencias
├── README_EMBEDDINGS.md        # Esta documentación
├── Material para embeddings/    # Carpeta de entrada (crear)
└── knowledge_base/              # Carpeta de salida (auto-creada)
    ├── embeddings/
    │   ├── text_multilingual_e5.h5
    │   ├── images_clip_vit32.h5
    │   ├── faiss_text_index.bin
    │   ├── metadata.parquet
    │   └── config.json
    ├── extracted/
    │   ├── chunks/
    │   └── images/
    └── logs/
        ├── processing.log
        ├── errors.log
        └── stats.json
```

## 🚀 Instalación Rápida

### 1. Instalación Automática (Recomendado)
```bash
python setup_embeddings.py
```

### 2. Instalación Manual
```bash
pip install -r requirements_embeddings.txt
```

## 📋 Requisitos del Sistema

- **Python**: 3.8+
- **RAM**: 8GB mínimo, 16GB recomendado
- **CPU**: 4+ cores (usará máximo 4 de 8 para mantener PC usable)
- **Almacenamiento**: ~1.2GB para embeddings de 250MB de documentos
- **GPU**: Opcional (Vega integrada soportada)

## 📄 Formatos Soportados

| Formato | Extensión | Características |
|---------|-----------|----------------|
| PDF | `.pdf` | Texto + imágenes extraídas |
| HTML | `.html`, `.htm` | Exports de Notion, estructura preservada |
| Markdown | `.md` | Chunking por headers |
| CSV | `.csv` | Cada fila como embedding individual |
| Word | `.docx` | Texto + tablas |
| Excel | `.xlsx`, `.xls` | Múltiples hojas |
| Texto | `.txt` | Auto-detección de encoding |

## 🎛️ Configuración

### Modelos Utilizados
- **Texto**: `intfloat/multilingual-e5-base` (560MB)
  - Optimizado para español/inglés técnico
  - Dimensión: 768
- **Imágenes**: `openai/clip-vit-base-patch32` (340MB)
  - Compatible con GPU Vega
  - Dimensión: 512

### Parámetros de Chunking
- **Tamaño**: 800 tokens
- **Overlap**: 120 tokens
- **Estrategia**: Preserva headers en Markdown, filas en CSV

### Limitaciones de Recursos
- **CPU**: Máximo 4 cores de 8 disponibles
- **RAM**: Máximo 8GB de 16GB disponibles
- **Batch Size**: 75 documentos
- **Timeout**: 120s por archivo
- **Tamaño Máximo**: 50MB por archivo

## 🏃‍♂️ Uso

### 1. Preparar Documentos
```bash
# Crear carpeta y colocar documentos
mkdir "Material para embeddings"
# Copiar tus PDFs, documentos, etc.
```

### 2. Ejecutar Procesamiento
```bash
python embeddings_processor.py
```

### 3. Seguimiento
- **Tiempo estimado**: 75-90 minutos para 1GB
- **Progreso**: Barra de progreso en consola
- **Logs**: `knowledge_base/logs/processing.log`
- **Checkpoints**: Cada 100 archivos procesados

## 📊 Ejemplo de Uso Completo

```python
# Después del procesamiento, usar los embeddings:
import numpy as np
import h5py
import faiss
import pandas as pd

# Cargar embeddings
with h5py.File('knowledge_base/embeddings/text_multilingual_e5.h5', 'r') as f:
    embeddings = f['embeddings'][:]

# Cargar índice FAISS
index = faiss.read_index('knowledge_base/embeddings/faiss_text_index.bin')

# Cargar metadata
metadata = pd.read_parquet('knowledge_base/embeddings/metadata.parquet')

# Buscar documentos similares
query_embedding = model.encode(["hipertensión arterial tratamiento"])
distances, indices = index.search(query_embedding, k=5)

# Obtener resultados
results = metadata.iloc[indices[0]]
```

## 🔧 Personalización

### Cambiar Modelos
```python
# En embeddings_processor.py, modificar ProcessingConfig:
@dataclass
class ProcessingConfig:
    text_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    image_model: str = "openai/clip-vit-large-patch14"
```

### Ajustar Recursos
```python
# Modificar limitaciones según tu hardware:
max_cpu_cores: int = 6  # Usar más cores
max_memory_gb: int = 12  # Usar más RAM
batch_size: int = 100   # Procesar más archivos simultáneamente
```

### Chunking Personalizado
```python
# Ajustar estrategia de chunking:
chunk_size: int = 1200  # Chunks más grandes
overlap_size: int = 200  # Mayor overlap
```

## 📈 Optimizaciones para LLM Pequeños

- **Chunks optimizados**: Para context window 4k-8k
- **Metadata estructurada**: Facilita retrieval preciso
- **Float16**: Reduce uso de memoria en 50%
- **Índice IVF**: Búsquedas sub-100ms para datasets grandes
- **Compatible con**: Llama 3.2 1B (128k context)

## 🐛 Solución de Problemas

### Error de Memoria
```bash
# Reducir batch size en embeddings_processor.py:
batch_size: int = 50
```

### Archivos Corruptos
- El sistema continúa automáticamente
- Revisa `knowledge_base/logs/errors.log`
- Archivos problemáticos se saltan sin afectar el resto

### Procesamiento Lento
```bash
# Verificar que no esté usando GPU cuando no debería:
export CUDA_VISIBLE_DEVICES=""
python embeddings_processor.py
```

### Modelos No Descargan
```python
# Forzar descarga manual:
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/multilingual-e5-base')
```

## 📊 Estadísticas Esperadas

Para **250MB de documentos médicos**:
- **Archivos procesados**: ~500-1000
- **Chunks generados**: ~15,000-25,000
- **Embeddings de texto**: ~600MB
- **Embeddings de imagen**: ~200MB
- **Índices FAISS**: ~300MB
- **Metadata**: ~50MB
- **Total final**: ~1.2GB

## 🔍 Casos de Uso

### 1. Knowledge Base Médico
```python
# Búsqueda semántica en literatura médica
query = "tratamiento diabetes tipo 2 metformina"
results = search_embeddings(query, top_k=10)
```

### 2. Generación de Contenido
```python
# Recuperar contexto para LLM
context = retrieve_context("insuficiencia cardíaca", max_tokens=2000)
response = llm.generate(f"Contexto: {context}\nPregunta: {query}")
```

### 3. Análisis de Documentos
```python
# Encontrar documentos similares
similar_docs = find_similar_documents(document_embedding, threshold=0.8)
```

## 🤝 Integración con Sistemas Existentes

### Con tu RAG Engine actual
```python
# Reemplazar ChromaDB con embeddings precomputados
# core/rag_engine.py - línea 234
embeddings = load_precomputed_embeddings()
faiss_index = load_faiss_index()
```

### Con la aplicación web
```python
# web/backend/app/core/medical_rag.py
# Usar embeddings locales en lugar de generar en tiempo real
```

## 📝 Logs y Monitoreo

### Logs Principales
- `processing.log`: Todo el procesamiento
- `errors.log`: Solo errores y advertencias
- `stats.json`: Estadísticas finales

### Métricas Clave
```json
{
  "total_files": 1250,
  "processed_files": 1240,
  "failed_files": 10,
  "total_chunks": 23450,
  "processing_time_minutes": 78.5,
  "success_rate": 0.992
}
```

## 🎓 Mejores Prácticas

1. **Organización de Material**:
   - Agrupa por especialidad médica
   - Usa nombres descriptivos
   - Evita archivos muy grandes (>50MB)

2. **Procesamiento**:
   - Ejecuta durante horas de bajo uso del PC
   - Monitorea logs en tiempo real
   - Permite que termine sin interrupciones

3. **Optimización**:
   - Ajusta batch_size según RAM disponible
   - Usa SSD para mejor rendimiento I/O
   - Considera procesamiento nocturno para datasets grandes

## 🚀 Siguientes Pasos

1. **Ejecutar instalación**: `python setup_embeddings.py`
2. **Colocar documentos**: En `Material para embeddings/`
3. **Procesar**: `python embeddings_processor.py`
4. **Integrar**: Con tu sistema RAG existente
5. **Optimizar**: Según resultados obtenidos

---

**Desarrollado para**: MedStudy Pro - Sistema de estudio médico inteligente  
**Optimizado para**: Hardware limitado y uso profesional  
**Soporte**: Consulta los logs para diagnóstico detallado