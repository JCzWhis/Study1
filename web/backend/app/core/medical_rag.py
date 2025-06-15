"""
Medical RAG (Retrieval Augmented Generation) System
Integrates medical knowledge from Hugging Face datasets
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import logging
import PyPDF2
import io
import re

logger = logging.getLogger(__name__)


class MedicalKnowledgeRAG:
    """RAG system for medical knowledge retrieval and enhancement."""
    
    def __init__(self, data_dir: str = "./data/medical_rag"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model (multilingual, good for Spanish)
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=str(self.data_dir / "chroma_db"))
        
        # Collection for medical knowledge
        self.collection = self.chroma_client.get_or_create_collection(
            name="medical_knowledge",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
        )
        
        self.is_initialized = False
    
    async def initialize_knowledge_base(self):
        """Initialize the medical knowledge base from Hugging Face datasets."""
        if self.is_initialized:
            return
        
        try:
            logger.info("Initializing medical knowledge base...")
            
            # Check if we already have data
            if self.collection.count() > 0:
                logger.info(f"Knowledge base already exists with {self.collection.count()} documents")
                self.is_initialized = True
                return
            
            # Load medical datasets
            await self._load_medical_datasets()
            
            # Load curated medical knowledge
            await self._load_curated_knowledge()
            
            self.is_initialized = True
            logger.info("Medical knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            # Continue with basic knowledge if datasets fail
            await self._load_fallback_knowledge()
            self.is_initialized = True
    
    async def _load_medical_datasets(self):
        """Load medical datasets from Hugging Face."""
        try:
            # Try to load Spanish medical diagnostic dataset
            logger.info("Loading Spanish medical dataset...")
            dataset = load_dataset("somosnlp/Sam_Diagnostic", split="train[:1000]")  # Limit for demo
            
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(dataset):
                # Extract relevant fields (adjust based on actual dataset structure)
                text_content = self._extract_text_from_dataset_item(item)
                if text_content:
                    documents.append(text_content)
                    metadatas.append({
                        "source": "somosnlp/Sam_Diagnostic",
                        "type": "diagnostic",
                        "language": "spanish",
                        "index": i
                    })
                    ids.append(f"sam_diag_{i}")
            
            if documents:
                # Add to ChromaDB in batches
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]
                    
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
                
                logger.info(f"Added {len(documents)} documents from Spanish medical dataset")
            
        except Exception as e:
            logger.warning(f"Could not load Hugging Face datasets: {e}")
            # Continue with fallback knowledge
    
    def _extract_text_from_dataset_item(self, item: Dict) -> str:
        """Extract meaningful text from dataset item."""
        # Adapt this based on the actual structure of the datasets
        text_parts = []
        
        # Common fields in medical datasets
        for field in ['text', 'question', 'answer', 'explanation', 'content', 'description']:
            if field in item and item[field]:
                text_parts.append(str(item[field]))
        
        # If no standard fields, try to concatenate all string values
        if not text_parts:
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 10:  # Meaningful text
                    text_parts.append(f"{key}: {value}")
        
        return " ".join(text_parts)
    
    async def _load_curated_knowledge(self):
        """Load curated medical knowledge by specialty."""
        medical_knowledge = {
            "cardiologia": [
                {
                    "title": "Insuficiencia Cardíaca - Fisiopatología",
                    "content": """La insuficiencia cardíaca es un síndrome clínico caracterizado por la incapacidad del corazón para bombear sangre de manera eficiente. Se clasifica según la fracción de eyección: HFrEF (≤40%), HFmrEF (41-49%), y HFpEF (≥50%). Los síntomas incluyen disnea, edema, fatigue. El tratamiento incluye inhibidores de la ECA, betabloqueadores, diuréticos, y en casos avanzados, dispositivos como marcapasos o trasplante.""",
                    "keywords": ["insuficiencia cardiaca", "fraccion eyeccion", "HFrEF", "HFpEF", "disnea", "edema"],
                    "level": "intermedio"
                },
                {
                    "title": "Síndrome Coronario Agudo - Diagnóstico",
                    "content": """El síndrome coronario agudo incluye angina inestable, IAMEST e IAMSEST. El diagnóstico se basa en síntomas (dolor torácico), ECG (elevación ST, ondas Q, inversión T), y biomarcadores (troponina, CK-MB). El manejo urgente incluye antiagregación (aspirina, clopidogrel), anticoagulación (heparina), y revascularización (angioplastia primaria o trombolisis).""",
                    "keywords": ["sindrome coronario agudo", "IAMEST", "IAMSEST", "troponina", "angioplastia", "trombolisis"],
                    "level": "avanzado"
                }
            ],
            "medicina_interna": [
                {
                    "title": "Diabetes Mellitus Tipo 2 - Manejo",
                    "content": """La diabetes tipo 2 se caracteriza por resistencia a la insulina y deficiencia relativa de insulina. Criterios diagnósticos: glucemia en ayunas ≥126 mg/dL, HbA1c ≥6.5%, o glucemia al azar ≥200 mg/dL con síntomas. El tratamiento escalonado incluye metformina como primera línea, seguido de sulfonilureas, inhibidores DPP-4, análogos GLP-1, o insulina según objetivos glucémicos individualizados.""",
                    "keywords": ["diabetes tipo 2", "metformina", "HbA1c", "glucemia", "resistencia insulina"],
                    "level": "basico"
                },
                {
                    "title": "Hipertensión Arterial - Tratamiento",
                    "content": """La hipertensión se define como PAS ≥140 mmHg o PAD ≥90 mmHg. El tratamiento incluye modificaciones del estilo de vida y farmacoterapia. Primera línea: inhibidores ECA/ARA II, diuréticos tiazídicos, bloqueadores de canales de calcio. Objetivos: <140/90 mmHg en general, <130/80 mmHg en diabéticos o enfermedad cardiovascular.""",
                    "keywords": ["hipertension arterial", "inhibidores ECA", "ARA II", "diureticos", "presion arterial"],
                    "level": "basico"
                }
            ],
            "neurologia": [
                {
                    "title": "Accidente Cerebrovascular - Manejo Agudo",
                    "content": """El ACV requiere evaluación urgente con TC/RM cerebral. ACV isquémico: trombolisis IV con rt-PA en <4.5h o trombectomía mecánica en <6h para grandes vasos. ACV hemorrágico: control de presión arterial, reversión anticoagulación, evaluación neuroquirúrgica. Escalas: NIH Stroke Scale para severidad, escala FAST para detección prehospitalaria.""",
                    "keywords": ["accidente cerebrovascular", "ACV", "trombolisis", "rt-PA", "trombectomia", "NIH stroke scale"],
                    "level": "avanzado"
                }
            ]
        }
        
        documents = []
        metadatas = []
        ids = []
        
        for specialty, topics in medical_knowledge.items():
            for i, topic in enumerate(topics):
                full_text = f"{topic['title']}\n\n{topic['content']}\n\nPalabras clave: {', '.join(topic['keywords'])}"
                
                documents.append(full_text)
                metadatas.append({
                    "source": "curated_knowledge",
                    "specialty": specialty,
                    "title": topic['title'],
                    "level": topic['level'],
                    "keywords": ", ".join(topic['keywords']),  # Convert list to string
                    "language": "spanish"
                })
                ids.append(f"curated_{specialty}_{i}")
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} curated medical documents")
    
    async def _load_fallback_knowledge(self):
        """Load basic fallback knowledge if other sources fail."""
        fallback_docs = [
            {
                "content": "La medicina basada en evidencia integra la experiencia clínica con la mejor evidencia científica disponible y las preferencias del paciente.",
                "metadata": {"source": "fallback", "type": "general", "language": "spanish"}
            }
        ]
        
        for i, doc in enumerate(fallback_docs):
            self.collection.add(
                documents=[doc["content"]],
                metadatas=[doc["metadata"]],
                ids=[f"fallback_{i}"]
            )
    
    async def retrieve_relevant_knowledge(
        self, 
        query: str, 
        specialty: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Retrieve relevant medical knowledge for a query."""
        if not self.is_initialized:
            await self.initialize_knowledge_base()
        
        try:
            # Build where clause for filtering
            where_clause = {}
            if specialty:
                where_clause["specialty"] = specialty
            
            # Query the knowledge base
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "relevance_score": 1.0 - distance,  # Convert distance to similarity
                        "source": metadata.get("source", "unknown")
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return []
    
    async def enhance_plan_generation_prompt(
        self, 
        specialty: str, 
        level: str, 
        topics: List[str]
    ) -> str:
        """Enhance the plan generation prompt with relevant medical knowledge."""
        
        # Retrieve relevant knowledge for each topic
        all_knowledge = []
        for topic in topics:
            knowledge = await self.retrieve_relevant_knowledge(
                f"{specialty} {topic} {level}",
                specialty=specialty,
                n_results=2
            )
            all_knowledge.extend(knowledge)
        
        # Also get general knowledge about the specialty
        specialty_knowledge = await self.retrieve_relevant_knowledge(
            f"{specialty} estudio planificación {level}",
            specialty=specialty,
            n_results=3
        )
        all_knowledge.extend(specialty_knowledge)
        
        # Build enhanced context
        if all_knowledge:
            context_parts = []
            for item in all_knowledge[:8]:  # Limit to avoid token limits
                if item['relevance_score'] > 0.7:  # Only high-relevance items
                    context_parts.append(f"- {item['content'][:500]}...")  # Truncate long content
            
            if context_parts:
                enhanced_context = f"""
CONTEXTO MÉDICO ESPECÍFICO:
{chr(10).join(context_parts)}

Utiliza este contexto médico específico para crear un plan de estudio detallado y clínicamente relevante.
"""
                return enhanced_context
        
        return ""
    
    async def add_pdf_content(self, pdf_content: bytes, filename: str, specialty: str = "general") -> bool:
        """Add PDF content to the knowledge base."""
        try:
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text_content = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text_content += f"\n--- Página {page_num + 1} ---\n"
                text_content += page.extract_text()
            
            if not text_content.strip():
                logger.warning(f"No text extracted from PDF: {filename}")
                return False
            
            # Split content into chunks
            chunks = self._split_text_into_chunks(text_content, max_chunk_size=1000)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Only meaningful chunks
                    documents.append(chunk)
                    metadatas.append({
                        "source": "user_pdf",
                        "filename": filename,
                        "specialty": specialty,
                        "chunk": i,
                        "language": "spanish",
                        "type": "pdf_content"
                    })
                    ids.append(f"pdf_{filename}_{i}")
            
            if documents:
                # Add to ChromaDB in batches
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]
                    
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
                
                logger.info(f"Added {len(documents)} chunks from PDF: {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            return False
    
    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks."""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size, start new chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def add_markdown_content(self, markdown_content: str, filename: str, specialty: str = "general") -> bool:
        """Add markdown content to the knowledge base."""
        try:
            if not markdown_content.strip():
                logger.warning(f"Empty markdown content for file: {filename}")
                return False
            
            # Extract title from filename or content
            title = self._extract_title_from_filename(filename)
            
            # Clean and process markdown content
            cleaned_content = self._clean_markdown_content(markdown_content)
            
            # Split content into chunks
            chunks = self._split_text_into_chunks(cleaned_content, max_chunk_size=1000)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Only meaningful chunks
                    documents.append(chunk)
                    metadatas.append({
                        "source": "medical_markdown",
                        "filename": filename,
                        "title": title,
                        "specialty": specialty,
                        "chunk": i,
                        "language": "spanish",
                        "type": "markdown_content"
                    })
                    ids.append(f"md_{filename.replace(' ', '_').replace('.md', '')}_{i}")
            
            if documents:
                # Add to ChromaDB in batches
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]
                    
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
                
                logger.info(f"Added {len(documents)} chunks from markdown: {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing markdown {filename}: {e}")
            return False
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract clean title from filename."""
        # Remove the UUID at the end and .md extension
        title = filename.replace('.md', '')
        # Split by space and remove last part if it looks like a UUID
        parts = title.split(' ')
        if len(parts) > 1 and len(parts[-1]) == 32 and parts[-1].isalnum():
            title = ' '.join(parts[:-1])
        return title
    
    def _clean_markdown_content(self, content: str) -> str:
        """Clean and normalize markdown content."""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Convert markdown headers to clean text
        content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)
        
        # Remove markdown formatting but keep structure
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
        content = re.sub(r'`(.*?)`', r'\1', content)        # Code
        
        # Clean up bullet points
        content = re.sub(r'^[\-\*\+]\s+', '• ', content, flags=re.MULTILINE)
        
        return content.strip()
    
    async def bulk_load_markdown_directory(self, directory_path: str) -> Dict[str, int]:
        """Bulk load all markdown files from a directory."""
        directory = Path(directory_path)
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return {"error": "Directory not found", "loaded": 0}
        
        # Initialize knowledge base first
        if not self.is_initialized:
            await self.initialize_knowledge_base()
        
        results = {"loaded": 0, "failed": 0, "skipped": 0}
        markdown_files = list(directory.glob("*.md"))
        
        logger.info(f"Found {len(markdown_files)} markdown files to process")
        
        for md_file in markdown_files:
            try:
                # Skip README files
                if md_file.name.lower() == 'readme.md':
                    results["skipped"] += 1
                    continue
                
                # Determine specialty from filename or content
                specialty = self._determine_specialty_from_filename(md_file.name)
                
                # Read file content
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Add to RAG system
                success = await self.add_markdown_content(content, md_file.name, specialty)
                
                if success:
                    results["loaded"] += 1
                    logger.info(f"✅ Loaded: {md_file.name}")
                else:
                    results["failed"] += 1
                    logger.warning(f"❌ Failed: {md_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing file {md_file.name}: {e}")
                results["failed"] += 1
        
        logger.info(f"Bulk loading completed: {results}")
        return results
    
    def _determine_specialty_from_filename(self, filename: str) -> str:
        """Determine medical specialty from filename."""
        filename_lower = filename.lower()
        
        # Specialty mappings
        specialty_keywords = {
            "reumatologia": ["artritis", "lupus", "vasculitis", "articular", "reumat", "espondiloartritis", 
                           "polimialgia", "miopat", "miositis", "cristales", "osteoporosis", "biologico",
                           "dolor", "inflamatorio"],
            "cardiologia": ["cardiaca", "cardiolog", "coronario", "arritmia", "fibrilacion", "hipertension",
                          "aortic", "valvular", "infarto", "angina"],
            "endocrinologia": ["diabetes", "tiroides", "suprarrenal", "acromegalia", "hipoglicemia",
                             "hiperglicemia", "insulina", "endocrin"],
            "nefrologia": ["renal", "nefr", "dialisis", "glomerulo", "proteinuria", "hiponatremia",
                          "hipokalemia", "hiperkalemia", "riñon"],
            "hematologia": ["anemia", "leucemia", "linfoma", "trombocit", "hemolisis", "coagulacion",
                          "hematolog", "mieloma", "hemograma", "ferritina"],
            "infectologia": ["antibiot", "antimicrobiano", "infeccion", "vih", "tuberculosis", "microbio",
                           "resistencia", "gram", "fungic"],
            "neurologia": ["neurologico", "acv", "encef", "mening", "neuropat", "convulsion", "cefalea"],
            "gastroenterologia": ["hepat", "cirrosis", "gastro", "esofag", "nutric", "disfagia"],
            "medicina_interna": ["hospitalizado", "intensivo", "shock", "medicina interna", "general"]
        }
        
        for specialty, keywords in specialty_keywords.items():
            if any(keyword in filename_lower for keyword in keywords):
                return specialty
        
        return "medicina_general"


# Global RAG instance
medical_rag = MedicalKnowledgeRAG()