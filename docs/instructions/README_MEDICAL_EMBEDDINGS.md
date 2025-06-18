# Medical Embeddings System - GTX 1080Ti Optimized

## Overview

Premium medical embeddings system specifically optimized for GTX 1080Ti (11GB VRAM) with 32GB RAM. Generates high-quality embeddings from medical documents using state-of-the-art models with maximum performance.

## Hardware Requirements

- **GPU**: GTX 1080Ti (11GB VRAM) + CUDA 12.2
- **RAM**: 32GB DDR4 (minimum 16GB)
- **Storage**: 10GB free space (for models and output)
- **OS**: Windows/Linux with CUDA support

## Models Used

- **Text**: `intfloat/multilingual-e5-large` (2.24GB VRAM)
- **Images**: `openai/clip-vit-large-patch14` (1.7GB VRAM)
- **Total VRAM usage**: ~9.9GB (90% of 11GB)

## Performance Targets

- ⏱️ **Processing time**: <15 minutes for 250MB documents
- 🎮 **GPU utilization**: >85%
- 🧠 **RAM usage**: <20GB of 32GB
- ✅ **Similarity score**: >0.95
- ⚡ **Search speed**: <50ms per query

## Features

### Advanced Processing
- **Medical-specific chunking**: Intelligent segmentation by pathologies/systems
- **Batch processing**: 2000+ simultaneous chunks
- **Multilingual support**: Spanish/English medical texts
- **Format support**: PDF, MD, DOCX, HTML, CSV, TXT

### GPU Optimization
- **CUDA acceleration**: Full GPU utilization
- **Memory management**: Optimized for 11GB VRAM
- **Mixed precision**: FP16 for memory efficiency
- **Batch optimization**: Dynamic batch sizing

### Quality Features
- **Medical taxonomy detection**: Automatic pathology classification
- **Contextual embeddings**: Preserve medical relationships
- **Validation testing**: Quality assurance with similarity scores
- **Checkpoint system**: Resume processing after interruption

## Quick Start

### 1. Installation

```bash
# Install system
python install_medical_embeddings.py

# Or manual installation
pip install -r requirements_medical_embeddings.txt
```

### 2. Prepare Documents

Place your medical documents in the `Material para embeddings/` folder:

```
Material para embeddings/
├── medical_document1.pdf
├── clinical_notes.md
├── research_paper.docx
└── pathology_guide.html
```

Supported formats: `.pdf`, `.md`, `.docx`, `.html`, `.csv`, `.txt`

### 3. Generate Embeddings

```bash
# Easy launcher (recommended)
python launch_medical_embeddings.py

# Or direct execution
python medical_embeddings_system.py
```

### 4. Results

The system creates a complete knowledge base:

```
medical_knowledge_base/
├── embeddings/
│   ├── text_e5_large.h5          # High-quality text embeddings
│   ├── images_clip_large.h5      # Image embeddings
│   ├── faiss_gpu_index.bin       # GPU-optimized search index
│   ├── metadata.parquet          # Rich metadata with medical categories
│   └── config.json               # System configuration
├── processed/
│   ├── chunks/                   # Segmented text chunks
│   └── images/                   # Extracted images
└── logs/
    ├── gpu_performance.log       # GPU utilization metrics
    └── processing_stats.json     # Complete statistics
```

## Advanced Usage

### Custom Configuration

Create `medical_embeddings_config.json`:

```json
{
  "hardware": {
    "max_batch_size": 2048,
    "target_vram_usage": 0.90
  },
  "processing": {
    "chunk_size": 1200,
    "chunk_overlap": 200,
    "max_workers": 8
  },
  "models": {
    "text_model": "intfloat/multilingual-e5-large",
    "image_model": "openai/clip-vit-large-patch14"
  }
}
```

### Programmatic Usage

```python
from medical_embeddings_system import MedicalEmbeddingsSystem

# Initialize system
system = MedicalEmbeddingsSystem(
    input_dir="my_documents",
    output_dir="my_knowledge_base"
)

# Run processing
results = system.run()

# Check results
if results['success']:
    print(f"Generated {results['embeddings_generated']} embeddings")
    print(f"Similarity score: {results['validation_results']['similarity_score']:.3f}")
```

### Search Example

```python
import faiss
import h5py
import numpy as np
from sentence_transformers import SentenceTransformer

# Load index and embeddings
index = faiss.read_index("medical_knowledge_base/embeddings/faiss_gpu_index.bin")
model = SentenceTransformer("intfloat/multilingual-e5-large")

# Search query
query = "síndrome de lupus eritematoso sistémico"
query_embedding = model.encode([f"passage: {query}"])

# Search
scores, indices = index.search(query_embedding.astype(np.float32), k=10)

print(f"Top results for '{query}':")
for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
    print(f"{i+1}. Score: {score:.3f}, Index: {idx}")
```

## Medical Categories Detected

The system automatically detects and categorizes:

- **Pathologies**: Diseases, syndromes, conditions
- **Anatomy**: Organs, systems, body parts  
- **Symptoms**: Clinical presentations
- **Medications**: Drugs, treatments, dosages
- **Procedures**: Diagnostic and therapeutic procedures

## Performance Monitoring

### GPU Utilization
- Real-time VRAM monitoring
- Temperature tracking
- Utilization percentage
- Memory allocation patterns

### Processing Statistics
- Documents per minute
- Chunks per second
- Embeddings generation rate
- Error tracking and recovery

## Troubleshooting

### Common Issues

1. **CUDA not detected**
   ```bash
   # Check CUDA installation
   nvidia-smi
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Out of memory**
   - Reduce batch size in config
   - Close other GPU applications
   - Check available VRAM

3. **Slow processing**
   - Verify GPU acceleration
   - Check disk I/O speed
   - Monitor RAM usage

### Performance Optimization

1. **For smaller GPU memory**:
   ```json
   {
     "hardware": {
       "max_batch_size": 1024,
       "target_vram_usage": 0.80
     }
   }
   ```

2. **For faster processing**:
   ```json
   {
     "processing": {
       "max_workers": 16,
       "batch_size": 4096
     }
   }
   ```

## System Architecture

### Processing Pipeline
1. **Document Discovery**: Scan input directory
2. **Content Extraction**: Text and images from multiple formats
3. **Medical Chunking**: Intelligent segmentation by medical context
4. **Embedding Generation**: Batch processing with GPU acceleration
5. **Index Creation**: FAISS GPU-optimized vector database
6. **Validation**: Quality assurance and similarity testing
7. **Output Generation**: Structured knowledge base

### Memory Management
- **GPU Memory**: Optimized for 11GB VRAM with headroom
- **System Memory**: Efficient use of 32GB RAM
- **Disk Caching**: Smart caching for large datasets
- **Checkpointing**: Automatic progress saving

## API Reference

### Main Classes

- `MedicalEmbeddingsSystem`: Main system orchestrator
- `PremiumEmbeddingEngine`: E5-large + CLIP-large models
- `MedicalTextChunker`: Medical-aware text segmentation
- `DocumentProcessor`: Multi-format document handling
- `FAISSIndexManager`: GPU-optimized vector indexing
- `GPUMonitor`: Real-time performance monitoring

### Key Methods

- `system.run()`: Execute complete pipeline
- `system.process_documents()`: Document processing only
- `system.generate_embeddings()`: Embedding generation only
- `system.create_faiss_index()`: Index creation only

## License

This system is designed for medical research and educational purposes. Ensure compliance with medical data regulations (HIPAA, GDPR) when processing sensitive documents.

## Support

For issues or optimization requests:
1. Check logs in `medical_knowledge_base/logs/`
2. Verify hardware requirements
3. Review GPU driver compatibility
4. Monitor system resources during processing

---

**Built for GTX 1080Ti Excellence** - Maximum quality medical embeddings with optimized performance.