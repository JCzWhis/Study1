"""
MedStudy Pro - Medical Knowledge Analyzer
Analizador de conocimiento médico con IA para evaluación de comprensión
Especializado en medicina interna y reumatología
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid

class KnowledgeLevel(Enum):
    """Niveles de conocimiento médico"""
    NOVICE = "novice"           # Estudiante de medicina
    INTERMEDIATE = "intermediate"  # Residente
    ADVANCED = "advanced"       # Fellow/Especialista
    EXPERT = "expert"          # Especialista experimentado

class ConceptType(Enum):
    """Tipos de conceptos médicos"""
    ANATOMY = "anatomy"
    PHYSIOLOGY = "physiology"
    PATHOLOGY = "pathology"
    PHARMACOLOGY = "pharmacology"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    PROCEDURE = "procedure"
    EMERGENCY = "emergency"

@dataclass
class KnowledgeGap:
    """Brecha de conocimiento identificada"""
    gap_id: str
    concept: str
    concept_type: ConceptType
    severity: str  # low, medium, high, critical
    description: str
    recommended_study_time: int  # minutes
    resources_needed: List[str]
    priority_score: float

@dataclass
class ConceptMastery:
    """Nivel de dominio de un concepto"""
    concept: str
    concept_type: ConceptType
    mastery_level: float  # 0.0 - 1.0
    confidence_score: float  # 0.0 - 1.0
    last_assessed: datetime
    times_reviewed: int
    improvement_trend: str  # improving, stable, declining

class MedicalKnowledgeAnalyzer:
    """Analizador de conocimiento médico con IA"""
    
    def __init__(self, config, database, llm_manager):
        self.config = config
        self.database = database
        self.llm_manager = llm_manager
        self.logger = logging.getLogger('MedStudy.KnowledgeAnalyzer')
        
        # Especialidades médicas y sus conceptos clave
        self._initialize_medical_taxonomy()
        
        # Algoritmos de análisis
        self._initialize_analysis_algorithms()
        
        self.logger.info("Medical Knowledge Analyzer initialized")
    
    def _initialize_medical_taxonomy(self):
        """Inicializa taxonomía médica especializada"""
        
        self.medical_taxonomy = {
            "medicina_interna": {
                "core_concepts": [
                    "Hipertensión arterial", "Diabetes mellitus", "Insuficiencia cardíaca",
                    "Infarto de miocardio", "Neumonía", "Sepsis", "Insuficiencia renal",
                    "Hepatitis", "Anemia", "Arritmias cardíacas"
                ],
                "subspecialties": {
                    "cardiologia": ["Ecocardiografía", "Electrocardiografía", "Cateterismo"],
                    "endocrinologia": ["Metabolismo", "Hormonas", "Diabetes"],
                    "nefrologia": ["Filtración glomerular", "Diálisis", "Trasplante"],
                    "gastroenterologia": ["Endoscopia", "Hepatología", "IBD"]
                }
            },
            
            "reumatologia": {
                "core_concepts": [
                    "Artritis reumatoide", "Lupus eritematoso sistémico", 
                    "Espondilitis anquilosante", "Osteoartritis", "Gota",
                    "Fibromialgia", "Vasculitis", "Síndrome de Sjögren"
                ],
                "diagnostic_tools": [
                    "Factor reumatoide", "Anti-CCP", "ANA", "Complemento",
                    "Radiografía", "Ultrasonido articular", "Resonancia magnética"
                ],
                "treatments": [
                    "DMARDs", "Biologicos", "Corticosteroides", "AINEs",
                    "Terapia física", "Infiltraciones", "Cirugía articular"
                ]
            }
        }
        
        # Criterios de evaluación por especialidad
        self.evaluation_criteria = {
            "medicina_interna": {
                "clinical_reasoning": 0.4,    # 40% razonamiento clínico
                "diagnostic_accuracy": 0.3,   # 30% precisión diagnóstica
                "treatment_knowledge": 0.2,   # 20% conocimiento terapéutico
                "emergency_management": 0.1   # 10% manejo de emergencias
            },
            
            "reumatologia": {
                "pattern_recognition": 0.3,   # 30% reconocimiento de patrones
                "differential_diagnosis": 0.25, # 25% diagnóstico diferencial
                "immunology_understanding": 0.2, # 20% comprensión inmunológica
                "treatment_selection": 0.15,  # 15% selección de tratamiento
                "monitoring_protocols": 0.1   # 10% protocolos de seguimiento
            }
        }
    
    def _initialize_analysis_algorithms(self):
        """Inicializa algoritmos de análisis"""
        
        self.analysis_prompts = {
            "concept_assessment": """Como especialista médico, evalúa la comprensión del estudiante sobre este concepto:

CONCEPTO: {concept}
RESPUESTA DEL ESTUDIANTE: {student_response}
CONTEXTO: {context}

EVALÚA:
1. Precisión médica (0-100)
2. Completitud de la respuesta (0-100)
3. Uso correcto de terminología (0-100)
4. Razonamiento clínico (0-100)
5. Identificación de brechas de conocimiento

FORMATO DE RESPUESTA:
Precisión: [0-100]
Completitud: [0-100]
Terminología: [0-100]
Razonamiento: [0-100]
Brechas identificadas: [lista de conceptos faltantes]
Recomendaciones: [sugerencias específicas de estudio]""",
            
            "case_analysis": """Analiza el razonamiento clínico del estudiante en este caso:

CASO CLÍNICO: {case_description}
RESPUESTA DEL ESTUDIANTE: {student_analysis}
DIAGNÓSTICO CORRECTO: {correct_diagnosis}

EVALÚA EL PROCESO DE RAZONAMIENTO:
1. Identificación de hallazgos clave
2. Formulación de diagnóstico diferencial
3. Selección de estudios apropiados
4. Llegada al diagnóstico correcto
5. Plan de tratamiento propuesto

Proporciona análisis detallado y puntuación (0-100) para cada área.""",
            
            "knowledge_gaps": """Basándote en el historial de desempeño del estudiante, identifica brechas de conocimiento:

HISTORIAL DE RESPUESTAS: {response_history}
ESPECIALIDAD: {specialty}
NIVEL ACTUAL: {current_level}

IDENTIFICA:
1. Conceptos con comprensión insuficiente
2. Áreas de conocimiento débiles
3. Patrones de errores recurrentes
4. Prioridades de estudio recomendadas

Para cada brecha, proporciona:
- Severidad (low/medium/high/critical)
- Tiempo de estudio recomendado
- Recursos específicos necesarios"""
        }
    
    def analyze_student_response(self, student_response: str, correct_answer: str,
                                concept: str, concept_type: ConceptType,
                                specialty: str = "medicina_interna") -> Dict[str, Any]:
        """Analiza respuesta del estudiante usando IA"""
        
        try:
            # Preparar prompt de análisis
            analysis_prompt = self.analysis_prompts["concept_assessment"].format(
                concept=concept,
                student_response=student_response,
                context=f"Especialidad: {specialty}, Tipo: {concept_type.value}"
            )
            
            # Obtener análisis de IA
            ai_analysis = self.llm_manager.chat(analysis_prompt, chat_type="teaching")
            
            # Parsear respuesta de IA
            parsed_analysis = self._parse_ai_analysis(ai_analysis)
            
            # Calcular scores y métricas
            analysis_result = {
                'concept': concept,
                'concept_type': concept_type.value,
                'specialty': specialty,
                'student_response': student_response,
                'correct_answer': correct_answer,
                'ai_analysis': parsed_analysis,
                'overall_score': self._calculate_overall_score(parsed_analysis),
                'mastery_level': self._determine_mastery_level(parsed_analysis),
                'knowledge_gaps': self._extract_knowledge_gaps(parsed_analysis, concept),
                'recommendations': self._generate_study_recommendations(parsed_analysis, concept),
                'analyzed_at': datetime.now().isoformat()
            }
            
            # Guardar análisis en base de datos
            self._save_analysis_result(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analizando respuesta: {e}")
            return self._fallback_analysis(student_response, correct_answer, concept)
    
    def analyze_case_reasoning(self, case_description: str, student_analysis: str,
                             correct_diagnosis: str, specialty: str) -> Dict[str, Any]:
        """Analiza razonamiento clínico en casos"""
        
        try:
            # Prompt específico para casos clínicos
            case_prompt = self.analysis_prompts["case_analysis"].format(
                case_description=case_description,
                student_analysis=student_analysis,
                correct_diagnosis=correct_diagnosis
            )
            
            ai_analysis = self.llm_manager.chat(case_prompt, chat_type="case_study")
            
            # Parsear análisis de caso clínico
            case_analysis = self._parse_case_analysis(ai_analysis)
            
            return {
                'case_id': f"case_{uuid.uuid4().hex[:8]}",
                'case_description': case_description,
                'student_analysis': student_analysis,
                'correct_diagnosis': correct_diagnosis,
                'specialty': specialty,
                'reasoning_scores': case_analysis['scores'],
                'clinical_thinking': case_analysis['clinical_thinking'],
                'diagnostic_accuracy': case_analysis['diagnostic_accuracy'],
                'improvement_areas': case_analysis['improvement_areas'],
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando caso clínico: {e}")
            return {}
    
    def identify_knowledge_gaps(self, student_id: str, specialty: str,
                               time_window_days: int = 30) -> List[KnowledgeGap]:
        """Identifica brechas de conocimiento basadas en historial"""
        
        try:
            # Obtener historial de respuestas
            response_history = self._get_student_history(student_id, time_window_days)
            
            if not response_history:
                return []
            
            # Preparar datos para análisis
            history_summary = self._summarize_response_history(response_history)
            
            gaps_prompt = self.analysis_prompts["knowledge_gaps"].format(
                response_history=json.dumps(history_summary, indent=2),
                specialty=specialty,
                current_level=self._estimate_current_level(response_history)
            )
            
            # Análisis de IA
            gaps_analysis = self.llm_manager.chat(gaps_prompt, chat_type="teaching")
            
            # Parsear y crear objetos KnowledgeGap
            knowledge_gaps = self._parse_knowledge_gaps(gaps_analysis, specialty)
            
            # Guardar gaps identificados
            for gap in knowledge_gaps:
                self._save_knowledge_gap(gap, student_id)
            
            return knowledge_gaps
            
        except Exception as e:
            self.logger.error(f"Error identificando brechas: {e}")
            return []
    
    def assess_concept_mastery(self, student_id: str, concept: str,
                             concept_type: ConceptType) -> ConceptMastery:
        """Evalúa dominio de un concepto específico"""
        
        try:
            # Obtener todas las interacciones con este concepto
            concept_history = self._get_concept_history(student_id, concept)
            
            if not concept_history:
                return self._create_initial_mastery(concept, concept_type)
            
            # Calcular métricas de dominio
            mastery_level = self._calculate_mastery_level(concept_history)
            confidence_score = self._calculate_confidence_score(concept_history)
            improvement_trend = self._analyze_improvement_trend(concept_history)
            
            mastery = ConceptMastery(
                concept=concept,
                concept_type=concept_type,
                mastery_level=mastery_level,
                confidence_score=confidence_score,
                last_assessed=datetime.now(),
                times_reviewed=len(concept_history),
                improvement_trend=improvement_trend
            )
            
            # Actualizar en base de datos
            self._update_concept_mastery(student_id, mastery)
            
            return mastery
            
        except Exception as e:
            self.logger.error(f"Error evaluando dominio: {e}")
            return self._create_initial_mastery(concept, concept_type)
    
    def generate_personalized_study_plan(self, student_id: str, specialty: str,
                                       target_hours: int = 20) -> Dict[str, Any]:
        """Genera plan de estudio personalizado"""
        
        try:
            # Identificar brechas de conocimiento
            knowledge_gaps = self.identify_knowledge_gaps(student_id, specialty)
            
            # Obtener dominio actual de conceptos
            current_mastery = self._get_current_mastery_levels(student_id, specialty)
            
            # Priorizar áreas de estudio
            study_priorities = self._prioritize_study_areas(knowledge_gaps, current_mastery)
            
            # Distribuir tiempo de estudio
            time_allocation = self._allocate_study_time(study_priorities, target_hours)
            
            # Crear plan estructurado
            study_plan = {
                'plan_id': f"plan_{uuid.uuid4().hex[:12]}",
                'student_id': student_id,
                'specialty': specialty,
                'target_hours': target_hours,
                'priority_areas': study_priorities,
                'time_allocation': time_allocation,
                'weekly_schedule': self._create_weekly_schedule(time_allocation),
                'recommended_resources': self._recommend_resources(study_priorities),
                'milestone_checkpoints': self._create_milestones(study_priorities),
                'created_at': datetime.now().isoformat(),
                'estimated_completion': self._estimate_completion_date(target_hours)
            }
            
            # Guardar plan
            self._save_study_plan(study_plan)
            
            return study_plan
            
        except Exception as e:
            self.logger.error(f"Error generando plan de estudio: {e}")
            return {}
    
    def track_learning_progress(self, student_id: str, specialty: str) -> Dict[str, Any]:
        """Rastrea progreso de aprendizaje"""
        
        try:
            # Obtener datos de progreso
            progress_data = {
                'student_id': student_id,
                'specialty': specialty,
                'current_level': self._assess_current_level(student_id, specialty),
                'mastery_distribution': self._get_mastery_distribution(student_id, specialty),
                'learning_velocity': self._calculate_learning_velocity(student_id),
                'consistency_score': self._calculate_consistency_score(student_id),
                'knowledge_gaps_count': len(self.identify_knowledge_gaps(student_id, specialty)),
                'recent_performance': self._get_recent_performance(student_id),
                'improvement_areas': self._identify_improvement_areas(student_id, specialty),
                'achievements': self._get_recent_achievements(student_id),
                'next_milestones': self._get_next_milestones(student_id),
                'updated_at': datetime.now().isoformat()
            }
            
            return progress_data
            
        except Exception as e:
            self.logger.error(f"Error rastreando progreso: {e}")
            return {}
    
    def _parse_ai_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Parsea respuesta de análisis de IA"""
        
        analysis = {
            'precision': 0,
            'completeness': 0,
            'terminology': 0,
            'reasoning': 0,
            'gaps': [],
            'recommendations': []
        }
        
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Precisión:'):
                try:
                    analysis['precision'] = int(re.search(r'\d+', line).group())
                except:
                    analysis['precision'] = 0
            
            elif line.startswith('Completitud:'):
                try:
                    analysis['completeness'] = int(re.search(r'\d+', line).group())
                except:
                    analysis['completeness'] = 0
            
            elif line.startswith('Terminología:'):
                try:
                    analysis['terminology'] = int(re.search(r'\d+', line).group())
                except:
                    analysis['terminology'] = 0
            
            elif line.startswith('Razonamiento:'):
                try:
                    analysis['reasoning'] = int(re.search(r'\d+', line).group())
                except:
                    analysis['reasoning'] = 0
            
            elif line.startswith('Brechas identificadas:'):
                gaps_text = line.replace('Brechas identificadas:', '').strip()
                if gaps_text:
                    analysis['gaps'] = [g.strip() for g in gaps_text.split(',')]
            
            elif line.startswith('Recomendaciones:'):
                rec_text = line.replace('Recomendaciones:', '').strip()
                if rec_text:
                    analysis['recommendations'] = [rec_text]
        
        return analysis
    
    def _parse_case_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Parsea análisis de caso clínico"""
        
        return {
            'scores': {'overall': 0, 'diagnostic': 0, 'reasoning': 0, 'treatment': 0},
            'clinical_thinking': 'developing',
            'diagnostic_accuracy': 0.0,
            'improvement_areas': []
        }
    
    def _parse_knowledge_gaps(self, gaps_response: str, specialty: str) -> List[KnowledgeGap]:
        """Parsea brechas de conocimiento identificadas"""
        
        gaps = []
        
        # Parsing básico - en implementación real sería más sofisticado
        lines = gaps_response.split('\n')
        current_gap = {}
        
        for line in lines:
            if 'Concepto:' in line:
                if current_gap:
                    gaps.append(self._create_knowledge_gap(current_gap, specialty))
                current_gap = {'concept': line.split('Concepto:')[1].strip()}
            
            elif 'Severidad:' in line:
                current_gap['severity'] = line.split('Severidad:')[1].strip().lower()
            
            elif 'Tiempo recomendado:' in line:
                try:
                    time_match = re.search(r'\d+', line)
                    current_gap['study_time'] = int(time_match.group()) if time_match else 30
                except:
                    current_gap['study_time'] = 30
        
        if current_gap:
            gaps.append(self._create_knowledge_gap(current_gap, specialty))
        
        return gaps
    
    def _create_knowledge_gap(self, gap_data: Dict, specialty: str) -> KnowledgeGap:
        """Crea objeto KnowledgeGap"""
        
        return KnowledgeGap(
            gap_id=f"gap_{uuid.uuid4().hex[:8]}",
            concept=gap_data.get('concept', 'Concepto desconocido'),
            concept_type=ConceptType.DIAGNOSIS,  # Default
            severity=gap_data.get('severity', 'medium'),
            description=f"Brecha identificada en {gap_data.get('concept')}",
            recommended_study_time=gap_data.get('study_time', 30),
            resources_needed=['Lectura dirigida', 'Casos clínicos'],
            priority_score=self._calculate_priority_score(gap_data.get('severity', 'medium'))
        )
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calcula score general"""
        
        scores = [
            analysis.get('precision', 0),
            analysis.get('completeness', 0),
            analysis.get('terminology', 0),
            analysis.get('reasoning', 0)
        ]
        
        return sum(scores) / len(scores) if scores else 0
    
    def _determine_mastery_level(self, analysis: Dict[str, Any]) -> str:
        """Determina nivel de dominio"""
        
        overall_score = self._calculate_overall_score(analysis)
        
        if overall_score >= 90:
            return "expert"
        elif overall_score >= 75:
            return "advanced"
        elif overall_score >= 60:
            return "intermediate"
        else:
            return "novice"
    
    def _extract_knowledge_gaps(self, analysis: Dict[str, Any], concept: str) -> List[str]:
        """Extrae brechas de conocimiento"""
        return analysis.get('gaps', [])
    
    def _generate_study_recommendations(self, analysis: Dict[str, Any], concept: str) -> List[str]:
        """Genera recomendaciones de estudio"""
        return analysis.get('recommendations', [])
    
    def _save_analysis_result(self, result: Dict[str, Any]):
        """Guarda resultado de análisis"""
        try:
            # Implementar guardado en BD
            pass
        except Exception as e:
            self.logger.error(f"Error guardando análisis: {e}")
    
    def _fallback_analysis(self, student_response: str, correct_answer: str, concept: str) -> Dict[str, Any]:
        """Análisis de respaldo sin IA"""
        
        # Análisis básico sin IA
        similarity = self._calculate_text_similarity(student_response, correct_answer)
        
        return {
            'concept': concept,
            'overall_score': similarity * 100,
            'mastery_level': 'intermediate' if similarity > 0.6 else 'novice',
            'fallback_analysis': True,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridad básica entre textos"""
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
    
    def _get_student_history(self, student_id: str, days: int) -> List[Dict]:
        """Obtiene historial del estudiante"""
        # Implementar consulta a BD
        return []
    
    def _summarize_response_history(self, history: List[Dict]) -> Dict:
        """Resume historial de respuestas"""
        return {'total_responses': len(history)}
    
    def _estimate_current_level(self, history: List[Dict]) -> str:
        """Estima nivel actual del estudiante"""
        return "intermediate"
    
    def _calculate_priority_score(self, severity: str) -> float:
        """Calcula score de prioridad"""
        priority_map = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        return priority_map.get(severity, 0.6)
    
    def _get_concept_history(self, student_id: str, concept: str) -> List[Dict]:
        """Obtiene historial de un concepto específico"""
        return []
    
    def _create_initial_mastery(self, concept: str, concept_type: ConceptType) -> ConceptMastery:
        """Crea dominio inicial para nuevo concepto"""
        
        return ConceptMastery(
            concept=concept,
            concept_type=concept_type,
            mastery_level=0.0,
            confidence_score=0.0,
            last_assessed=datetime.now(),
            times_reviewed=0,
            improvement_trend="new"
        )
    
    def _calculate_mastery_level(self, history: List[Dict]) -> float:
        """Calcula nivel de dominio basado en historial"""
        if not history:
            return 0.0
        
        # Análisis de tendencia y scores recientes
        recent_scores = [h.get('score', 0) for h in history[-5:]]
        return sum(recent_scores) / len(recent_scores) / 100 if recent_scores else 0.0
    
    def _calculate_confidence_score(self, history: List[Dict]) -> float:
        """Calcula score de confianza"""
        return 0.7  # Placeholder
    
    def _analyze_improvement_trend(self, history: List[Dict]) -> str:
        """Analiza tendencia de mejora"""
        if len(history) < 3:
            return "insufficient_data"
        
        recent_avg = sum(h.get('score', 0) for h in history[-3:]) / 3
        earlier_avg = sum(h.get('score', 0) for h in history[-6:-3]) / 3 if len(history) >= 6 else recent_avg
        
        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "declining"
        else:
            return "stable"
    
    def _update_concept_mastery(self, student_id: str, mastery: ConceptMastery):
        """Actualiza dominio de concepto en BD"""
        pass
    
    def _get_current_mastery_levels(self, student_id: str, specialty: str) -> Dict:
        """Obtiene niveles actuales de dominio"""
        return {}
    
    def _prioritize_study_areas(self, gaps: List[KnowledgeGap], mastery: Dict) -> List[Dict]:
        """Prioriza áreas de estudio"""
        return []
    
    def _allocate_study_time(self, priorities: List[Dict], total_hours: int) -> Dict:
        """Distribuye tiempo de estudio"""
        return {}
    
    def _create_weekly_schedule(self, allocation: Dict) -> Dict:
        """Crea horario semanal"""
        return {}
    
    def _recommend_resources(self, priorities: List[Dict]) -> Dict:
        """Recomienda recursos de estudio"""
        return {}
    
    def _create_milestones(self, priorities: List[Dict]) -> List[Dict]:
        """Crea hitos de progreso"""
        return []
    
    def _estimate_completion_date(self, hours: int) -> str:
        """Estima fecha de completación"""
        weeks = hours // 10  # Asume 10 horas por semana
        completion_date = datetime.now() + timedelta(weeks=weeks)
        return completion_date.isoformat()
    
    def _save_study_plan(self, plan: Dict):
        """Guarda plan de estudio"""
        pass
    
    def _save_knowledge_gap(self, gap: KnowledgeGap, student_id: str):
        """Guarda brecha de conocimiento"""
        pass
    
    def _assess_current_level(self, student_id: str, specialty: str) -> str:
        """Evalúa nivel actual del estudiante"""
        return "intermediate"
    
    def _get_mastery_distribution(self, student_id: str, specialty: str) -> Dict:
        """Obtiene distribución de dominio"""
        return {}
    
    def _calculate_learning_velocity(self, student_id: str) -> float:
        """Calcula velocidad de aprendizaje"""
        return 0.0
    
    def _calculate_consistency_score(self, student_id: str) -> float:
        """Calcula score de consistencia"""
        return 0.0
    
    def _get_recent_performance(self, student_id: str) -> Dict:
        """Obtiene rendimiento reciente"""
        return {}
    
    def _identify_improvement_areas(self, student_id: str, specialty: str) -> List[str]:
        """Identifica áreas de mejora"""
        return []
    
    def _get_recent_achievements(self, student_id: str) -> List[Dict]:
        """Obtiene logros recientes"""
        return []
    
    def _get_next_milestones(self, student_id: str) -> List[Dict]:
        """Obtiene próximos hitos"""
        return []

# Export main classes
__all__ = [
    'MedicalKnowledgeAnalyzer', 'KnowledgeLevel', 'ConceptType', 
    'KnowledgeGap', 'ConceptMastery'
]