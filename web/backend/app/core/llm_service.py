"""
LLM Service for MedStudy - Ollama + Phi3 Integration with Medical RAG
"""

import asyncio
import json
from typing import Dict, List, Optional
import httpx
from datetime import datetime, timedelta
from .medical_rag import medical_rag


class OllamaService:
    """Service for interacting with Ollama and Phi3 model."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "phi3:mini"):
        # Alternative models: "llama3.2:1b", "gemma2:2b"
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from Phi3 model."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error: No se pudo generar respuesta del modelo."
    
    async def check_model_availability(self) -> bool:
        """Check if Phi3 model is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            models = response.json().get("models", [])
            return any(model.get("name", "").startswith(self.model) for model in models)
        except:
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class MedStudyPlanGenerator:
    """Medical study plan generator using Phi3."""
    
    def __init__(self):
        self.ollama = OllamaService()
        self.system_prompt = """Eres un experto en educación médica y planificación de estudios. 
Tu tarea es crear planes de estudio personalizados para estudiantes de medicina usando el método de repetición espaciada.

IMPORTANTE: Responde SIEMPRE en formato JSON válido, sin texto adicional.

Principios del plan:
- Basado en el método Ali Abdaal de repetición espaciada
- Priorizar temas según dificultad y importancia clínica
- Incluir tiempo estimado realista por tema
- Considerar el nivel del estudiante y fecha objetivo
- Organizar por sistemas/especialidades médicas"""
    
    async def generate_study_plan(
        self,
        specialty: str,
        level: str,
        target_date: str,
        current_knowledge: Dict[str, str],
        specific_topics: List[str] = None
    ) -> Dict:
        """Generate a complete medical study plan with RAG enhancement."""
        
        # Get enhanced context from RAG
        rag_context = ""
        try:
            if specific_topics:
                rag_context = await medical_rag.enhance_plan_generation_prompt(
                    specialty, level, specific_topics
                )
            else:
                # Get general context for the specialty
                rag_context = await medical_rag.enhance_plan_generation_prompt(
                    specialty, level, [specialty]
                )
        except Exception as e:
            print(f"Warning: Could not retrieve RAG context: {e}")
        
        prompt = f"""
{rag_context}

Crea un plan de estudio médico DETALLADO para:
- Especialidad: {specialty}
- Nivel: {level}
- Fecha objetivo: {target_date}
- Conocimiento actual: {json.dumps(current_knowledge, indent=2)}
- Temas específicos: {specific_topics or 'No especificados'}

IMPORTANTE: Utiliza el contexto médico específico proporcionado arriba para crear contenido detallado y clínicamente relevante.

Responde con este formato JSON EXACTO:
{{
    "plan_title": "Título del plan",
    "specialty": "{specialty}",
    "level": "{level}",
    "target_date": "{target_date}",
    "estimated_total_hours": 0,
    "topics": [
        {{
            "name": "Nombre del tema",
            "priority": "high|medium|low",
            "estimated_hours": 0.0,
            "confidence_level": "red",
            "description": "Descripción breve",
            "key_concepts": ["concepto1", "concepto2"],
            "clinical_relevance": "Alta|Media|Baja",
            "difficulty": "Básico|Intermedio|Avanzado"
        }}
    ],
    "study_schedule": {{
        "total_weeks": 0,
        "hours_per_week": 0,
        "sessions_per_week": 0
    }},
    "learning_objectives": ["objetivo1", "objetivo2"],
    "resources": ["recurso1", "recurso2"]
}}
"""
        
        response = await self.ollama.generate_response(prompt, self.system_prompt)
        
        try:
            # Clean and parse JSON response
            cleaned_response = self._clean_json_response(response)
            plan_data = json.loads(cleaned_response)
            
            # Validate and enhance the plan
            return self._validate_and_enhance_plan(plan_data)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response}")
            # Return fallback plan with RAG
            return await self._create_fallback_plan(specialty, level, target_date, specific_topics)
    
    async def generate_topic_suggestions(self, specialty: str, level: str) -> List[str]:
        """Generate topic suggestions for a specialty."""
        
        prompt = f"""
Lista los 15 temas más importantes para estudiar en {specialty} a nivel {level}.
Responde SOLO con un array JSON de strings:
["tema1", "tema2", "tema3", ...]
"""
        
        response = await self.ollama.generate_response(prompt, self.system_prompt)
        
        try:
            cleaned_response = self._clean_json_response(response)
            topics = json.loads(cleaned_response)
            return topics if isinstance(topics, list) else []
        except:
            return self._get_default_topics(specialty)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean response to extract valid JSON."""
        # Remove markdown code blocks
        response = response.replace("```json", "").replace("```", "")
        
        # Find JSON object boundaries
        start = response.find("{")
        end = response.rfind("}") + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        # Try array format
        start = response.find("[")
        end = response.rfind("]") + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        return response.strip()
    
    def _validate_and_enhance_plan(self, plan_data: Dict) -> Dict:
        """Validate and enhance the generated plan."""
        
        # Ensure required fields
        plan_data.setdefault("plan_id", f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        plan_data.setdefault("created_at", datetime.now().isoformat())
        plan_data.setdefault("updated_at", datetime.now().isoformat())
        
        # Validate topics
        topics = plan_data.get("topics", [])
        for topic in topics:
            topic.setdefault("id", f"topic_{len(topic.get('name', '').replace(' ', '_'))}")
            topic.setdefault("confidence_level", "red")
            topic.setdefault("last_studied", None)
            topic.setdefault("next_review", datetime.now().isoformat())
            topic.setdefault("study_count", 0)
        
        return plan_data
    
    async def _create_fallback_plan(self, specialty: str, level: str, target_date: str, topics: List[str] = None) -> Dict:
        """Create a fallback plan when AI generation fails, enhanced with RAG."""
        
        # Try to get RAG content for fallback plan
        print(f"DEBUG: Creating fallback plan for {specialty}, topics: {topics}")
        rag_topics = []
        if topics:
            from .medical_rag import medical_rag
            try:
                for topic in topics:
                    knowledge = await medical_rag.retrieve_relevant_knowledge(
                        f"{specialty} {topic} {level}",
                        specialty=specialty,
                        n_results=1
                    )
                    if knowledge and len(knowledge) > 0:  # Remove score threshold for now
                        content = knowledge[0]['content']
                        print(f"DEBUG: Found RAG content for {topic}: {content[:100]}...")
                        # Extract meaningful info from RAG content
                        rag_topics.append({
                            "id": f"topic_{topic.lower().replace(' ', '_')}",
                            "name": topic,
                            "priority": "high",
                            "estimated_hours": 6.0,
                            "confidence_level": "red", 
                            "description": content[:200] + "..." if len(content) > 200 else content,
                            "key_concepts": self._extract_key_concepts(content)[:3],  # Limit to 3
                            "clinical_relevance": "Alta",
                            "difficulty": "Intermedio",
                            "last_studied": None,
                            "next_review": datetime.now().isoformat(),
                            "study_count": 0
                        })
            except Exception as e:
                print(f"Error getting RAG content for fallback: {e}")
        
        # If no RAG topics, use basic topic
        if not rag_topics:
            rag_topics = [{
                "id": "topic_intro",
                "name": "Introducción y Conceptos Básicos",
                "priority": "high",
                "estimated_hours": 8.0,
                "confidence_level": "red",
                "description": "Fundamentos básicos de la especialidad",
                "key_concepts": ["Conceptos básicos", "Terminología", "Anatomía relevante"],
                "clinical_relevance": "Alta",
                "difficulty": "Básico",
                "last_studied": None,
                "next_review": datetime.now().isoformat(),
                "study_count": 0
            }]
        
        return {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "plan_title": f"Plan de Estudio - {specialty.title()}",
            "specialty": specialty,
            "level": level,
            "target_date": target_date,
            "estimated_total_hours": 40,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "topics": rag_topics,
            "study_schedule": {
                "total_weeks": 8,
                "hours_per_week": 5,
                "sessions_per_week": 3
            },
            "learning_objectives": [
                "Dominar conceptos fundamentales",
                "Aplicar conocimientos en casos clínicos"
            ],
            "resources": [
                "Libros de texto especializados",
                "Casos clínicos",
                "Artículos de revisión"
            ]
        }
    
    def _get_default_topics(self, specialty: str) -> List[str]:
        """Get default topics for common specialties."""
        
        default_topics = {
            "cardiologia": [
                "Insuficiencia Cardíaca",
                "Síndrome Coronario Agudo",
                "Arritmias",
                "Valvulopatías",
                "Hipertensión Arterial"
            ],
            "medicina_interna": [
                "Diabetes Mellitus",
                "Enfermedad Renal Crónica",
                "Neumonía",
                "Sepsis",
                "Trastornos Electrolíticos"
            ],
            "neurologia": [
                "Accidente Cerebrovascular",
                "Epilepsia",
                "Cefaleas",
                "Enfermedad de Parkinson",
                "Esclerosis Múltiple"
            ]
        }
        
        return default_topics.get(specialty.lower(), [
            "Tema 1", "Tema 2", "Tema 3", "Tema 4", "Tema 5"
        ])
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from RAG content."""
        # Simple extraction of medical terms (can be improved with NLP)
        concepts = []
        key_phrases = content.split(". ")[:3]  # First 3 sentences
        for phrase in key_phrases:
            if len(phrase) > 10 and len(phrase) < 60:  # Reasonable length
                concepts.append(phrase.strip())
        return concepts if concepts else ["Conceptos fundamentales", "Aplicación clínica"]


# Global instance
llm_service = MedStudyPlanGenerator()