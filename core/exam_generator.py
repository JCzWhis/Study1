"""
MedStudy Pro - Exam Generator System
Adaptive 45-question medical exams based on study plans and RAG content
"""

import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import requests
import uuid

class QuestionType(Enum):
    """Types of medical exam questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    CASE_STUDY = "case_study"
    IMAGE_BASED = "image_based"
    TRUE_FALSE = "true_false"
    MATCHING = "matching"
    FILL_BLANK = "fill_blank"

class QuestionDifficulty(Enum):
    """Question difficulty levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class ExamQuestion:
    """Individual exam question"""
    question_id: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    specialty: str
    topic: str
    question_text: str
    options: List[str]  # For multiple choice
    correct_answer: str
    explanation: str
    image_path: Optional[str] = None
    time_limit_seconds: int = 120
    points: int = 1

    def __post_init__(self):
        if isinstance(self.question_type, str):
            self.question_type = QuestionType(self.question_type)
        if isinstance(self.difficulty, str):
            self.difficulty = QuestionDifficulty(self.difficulty)

@dataclass
class ExamResult:
    """Result of a completed exam"""
    exam_id: str
    student_answers: Dict[str, str]
    correct_answers: Dict[str, str]
    score_percentage: float
    time_taken_seconds: int
    questions_by_difficulty: Dict[str, int]
    performance_by_topic: Dict[str, Dict[str, Any]]

class MedicalExamGenerator:
    """Generates adaptive medical exams based on RAG content and study plans"""
    
    def __init__(self, config, database, rag_engine):
        self.config = config
        self.database = database
        self.rag_engine = rag_engine
        self.logger = logging.getLogger('MedStudy.ExamGenerator')
        
        # Initialize Ollama for question generation
        self._initialize_ollama()
        
        # Question templates and patterns
        self._initialize_question_templates()
        
        self.logger.info("Medical Exam Generator initialized")
    
    def _initialize_ollama(self):
        """Initialize Ollama client for question generation"""
        try:
            ollama_config = self.config.get_ollama_config()
            self.ollama_host = ollama_config['host']
            self.ollama_model = ollama_config['model']
            self.ollama_timeout = ollama_config['timeout']
            
            # Test connection
            response = requests.get(self.ollama_host, timeout=5)
            if response.status_code == 200:
                self.logger.info(f"Ollama connected for exam generation")
            else:
                self.logger.warning(f"Ollama connection issue for exams")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama for exams: {e}")
            self.ollama_host = None
    
    def _initialize_question_templates(self):
        """Initialize question generation templates"""
        self.question_templates = {
            QuestionType.MULTIPLE_CHOICE: {
                "basic": "Basándote en el siguiente contenido médico, crea una pregunta de opción múltiple BÁSICA sobre {topic}:\n\nCONTENIDO:\n{content}\n\nFormato requerido:\nPregunta: [pregunta clara y directa]\nA) [opción]\nB) [opción]\nC) [opción]\nD) [opción]\nRespuesta correcta: [letra]\nExplicación: [explicación breve]",
                
                "intermediate": "Crea una pregunta de opción múltiple de nivel INTERMEDIO sobre {topic} que requiera análisis clínico:\n\nCONTENIDO:\n{content}\n\nLa pregunta debe evaluar comprensión y aplicación clínica. Incluye un escenario breve si es apropiado.\n\nFormato requerido:\nPregunta: [pregunta con escenario clínico]\nA) [opción]\nB) [opción]\nC) [opción]\nD) [opción]\nRespuesta correcta: [letra]\nExplicación: [explicación detallada con razonamiento clínico]",
                
                "advanced": "Desarrolla una pregunta AVANZADA de opción múltiple sobre {topic} que evalúe razonamiento clínico complejo:\n\nCONTENIDO:\n{content}\n\nLa pregunta debe incluir un caso clínico complejo que requiera diagnóstico diferencial o manejo avanzado.\n\nFormato requerido:\nPregunta: [caso clínico complejo con pregunta específica]\nA) [opción]\nB) [opción]\nC) [opción]\nD) [opción]\nRespuesta correcta: [letra]\nExplicación: [explicación exhaustiva con diagnóstico diferencial]"
            },
            
            QuestionType.CASE_STUDY: {
                "basic": "Crea un caso clínico BÁSICO sobre {topic} con pregunta directa:\n\nCONTENIDO:\n{content}\n\nFormato:\nCaso: [presentación simple del paciente]\nPregunta: [pregunta directa sobre diagnóstico o manejo]\nA) [opción]\nB) [opción]\nC) [opción]\nD) [opción]\nRespuesta correcta: [letra]\nExplicación: [razonamiento clínico]",
                
                "intermediate": "Desarrolla un caso clínico de complejidad INTERMEDIA sobre {topic}:\n\nCONTENIDO:\n{content}\n\nEl caso debe incluir historia clínica, examen físico y algunos estudios. La pregunta debe evaluar razonamiento diagnóstico.\n\nFormato:\nCaso: [historia completa con examen físico]\nPregunta: [pregunta sobre diagnóstico más probable o próximo paso]\nA) [opción]\nB) [opción]\nC) [opción]\nD) [opción]\nRespuesta correcta: [letra]\nExplicación: [análisis del caso con diagnóstico diferencial]",
                
                "advanced": "Construye un caso clínico AVANZADO sobre {topic} que simule una situación real compleja:\n\nCONTENIDO:\n{content}\n\nIncluye historia detallada, examen físico completo, estudios de laboratorio e imagen. La pregunta debe evaluar manejo avanzado o complicaciones.\n\nFormato:\nCaso: [presentación completa del caso con evolución]\nPregunta: [pregunta sobre manejo complejo o complicaciones]\nA) [opción]\nB) [opción]\nC) [opción]\nD) [opción]\nRespuesta correcta: [letra]\nExplicación: [análisis exhaustivo con referencias a guías clínicas]"
            }
        }
    
    def generate_exam(self, plan_id: str = None, specialty: str = "general", 
                     questions_count: int = 45, difficulty_distribution: Dict[str, float] = None) -> Dict[str, Any]:
        """Generate a complete medical exam"""
        
        if not self.ollama_host:
            raise RuntimeError("Ollama not available for exam generation")
        
        # Default difficulty distribution for medical exams
        if difficulty_distribution is None:
            difficulty_distribution = {
                "basic": 0.3,        # 30% basic questions
                "intermediate": 0.5, # 50% intermediate questions  
                "advanced": 0.2      # 20% advanced questions
            }
        
        self.logger.info(f"Generating exam: {questions_count} questions, specialty: {specialty}")
        
        # Get topics for exam
        topics = self._get_exam_topics(plan_id, specialty)
        
        if not topics:
            raise ValueError(f"No topics found for specialty: {specialty}")
        
        # Generate questions
        exam_id = f"exam_{uuid.uuid4().hex[:12]}"
        questions = []
        
        # Calculate question distribution
        question_distribution = self._calculate_question_distribution(
            questions_count, difficulty_distribution, len(topics)
        )
        
        # Generate questions for each difficulty level
        for difficulty, count in question_distribution.items():
            difficulty_questions = self._generate_questions_for_difficulty(
                topics, difficulty, count, specialty
            )
            questions.extend(difficulty_questions)
        
        # Shuffle questions
        random.shuffle(questions)
        
        # Create exam metadata
        exam_data = {
            'exam_id': exam_id,
            'plan_id': plan_id,
            'specialty': specialty,
            'questions_total': len(questions),
            'questions': [q.__dict__ for q in questions],
            'difficulty_distribution': difficulty_distribution,
            'topics_covered': topics,
            'estimated_duration_minutes': len(questions) * 2,  # 2 minutes per question
            'created_at': datetime.now().isoformat(),
            'exam_type': 'adaptive'
        }
        
        # Store exam in database
        self._store_exam_metadata(exam_data)
        
        self.logger.info(f"Generated exam {exam_id}: {len(questions)} questions across {len(topics)} topics")
        
        return exam_data
    
    def _get_exam_topics(self, plan_id: str = None, specialty: str = "general") -> List[str]:
        """Get topics for exam based on study plan or specialty"""
        
        if plan_id:
            # Get topics from specific study plan
            try:
                result = self.database.execute_query(
                    "SELECT topics FROM study_plans WHERE plan_id = ?",
                    (plan_id,)
                )
                
                if result:
                    topics = json.loads(result[0]['topics'])
                    return topics[:10]  # Limit to 10 topics max
                    
            except Exception as e:
                self.logger.warning(f"Failed to get topics from plan {plan_id}: {e}")
        
        # Get topics from processed documents by specialty
        try:
            # Get recent study sessions topics
            recent_topics = self.database.execute_query("""
                SELECT DISTINCT topic FROM study_sessions 
                WHERE started_at >= datetime('now', '-30 days')
                ORDER BY started_at DESC 
                LIMIT 8
            """)
            
            if recent_topics:
                return [t['topic'] for t in recent_topics]
            
        except Exception as e:
            self.logger.warning(f"Failed to get recent topics: {e}")
        
        # Fallback to default medical topics by specialty
        default_topics = self._get_default_topics_by_specialty(specialty)
        return default_topics
    
    def _get_default_topics_by_specialty(self, specialty: str) -> List[str]:
        """Get default topics for medical specialties"""
        
        specialty_topics = {
            "internal_medicine": [
                "Hipertensión arterial", "Diabetes mellitus", "Insuficiencia cardíaca",
                "Neumonía", "Asma bronquial", "EPOC", "Infarto de miocardio",
                "Arritmias cardíacas", "Insuficiencia renal", "Hepatitis"
            ],
            
            "rheumatology": [
                "Artritis reumatoide", "Lupus eritematoso sistémico", "Espondilitis anquilosante",
                "Fibromialgia", "Osteoartritis", "Gota", "Artritis psoriásica",
                "Síndrome de Sjögren", "Esclerosis sistémica", "Vasculitis"
            ],
            
            "cardiology": [
                "Síndrome coronario agudo", "Insuficiencia cardíaca", "Arritmias",
                "Valvulopatías", "Hipertensión pulmonar", "Pericarditis",
                "Miocardiopatías", "Endocarditis", "Aterosclerosis", "Shock cardiogénico"
            ],
            
            "general": [
                "Diagnóstico diferencial", "Manejo del dolor", "Infecciones comunes",
                "Medicina preventiva", "Farmacología clínica", "Emergencias médicas",
                "Interpretación de laboratorios", "Ética médica", "Comunicación médica"
            ]
        }
        
        return specialty_topics.get(specialty, specialty_topics["general"])
    
    def _calculate_question_distribution(self, total_questions: int, 
                                       difficulty_dist: Dict[str, float], 
                                       topic_count: int) -> Dict[str, int]:
        """Calculate how many questions of each difficulty to generate"""
        
        distribution = {}
        remaining = total_questions
        
        for difficulty, percentage in difficulty_dist.items():
            count = int(total_questions * percentage)
            distribution[difficulty] = count
            remaining -= count
        
        # Add remaining questions to intermediate
        if remaining > 0:
            distribution["intermediate"] = distribution.get("intermediate", 0) + remaining
        
        return distribution
    
    def _generate_questions_for_difficulty(self, topics: List[str], difficulty: str, 
                                         count: int, specialty: str) -> List[ExamQuestion]:
        """Generate questions for a specific difficulty level"""
        
        questions = []
        questions_per_topic = max(1, count // len(topics))
        
        for i, topic in enumerate(topics):
            if len(questions) >= count:
                break
                
            # Get relevant content for this topic
            relevant_content = self._get_content_for_topic(topic, specialty)
            
            if not relevant_content:
                continue
            
            # Generate questions for this topic
            topic_questions = self._generate_topic_questions(
                topic, relevant_content, difficulty, questions_per_topic, specialty
            )
            
            questions.extend(topic_questions)
        
        # Ensure we have the right number of questions
        return questions[:count]
    
    def _get_content_for_topic(self, topic: str, specialty: str) -> str:
        """Get relevant content for a topic from RAG system"""
        
        try:
            # Search for relevant content
            search_results = self.rag_engine.search_documents(
                query=f"{topic} {specialty}",
                top_k=3
            )
            
            if search_results:
                # Combine top results
                content_pieces = [result['text'] for result in search_results]
                return "\n\n".join(content_pieces)
            
        except Exception as e:
            self.logger.warning(f"Failed to get content for topic {topic}: {e}")
        
        # Fallback content
        return f"Contenido médico relacionado con {topic} en el contexto de {specialty}."
    
    def _generate_topic_questions(self, topic: str, content: str, difficulty: str,
                                count: int, specialty: str) -> List[ExamQuestion]:
        """Generate questions for a specific topic"""
        
        questions = []
        
        for i in range(count):
            try:
                # Determine question type (favor multiple choice and case studies)
                question_types = [QuestionType.MULTIPLE_CHOICE, QuestionType.CASE_STUDY]
                if difficulty == "advanced":
                    question_types.append(QuestionType.CASE_STUDY)  # More case studies for advanced
                
                question_type = random.choice(question_types)
                
                # Generate question using Ollama
                question_data = self._call_ollama_for_question(
                    topic, content, difficulty, question_type, specialty
                )
                
                if question_data:
                    question = ExamQuestion(
                        question_id=f"q_{uuid.uuid4().hex[:8]}",
                        question_type=question_type,
                        difficulty=QuestionDifficulty(difficulty),
                        specialty=specialty,
                        topic=topic,
                        question_text=question_data['question'],
                        options=question_data.get('options', []),
                        correct_answer=question_data['correct_answer'],
                        explanation=question_data['explanation'],
                        time_limit_seconds=self._get_time_limit(difficulty),
                        points=self._get_points(difficulty)
                    )
                    
                    questions.append(question)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate question for {topic}: {e}")
                continue
        
        return questions
    
    def _call_ollama_for_question(self, topic: str, content: str, difficulty: str,
                                question_type: QuestionType, specialty: str) -> Dict[str, Any]:
        """Call Ollama to generate a specific question"""
        
        # Get template for this question type and difficulty
        template = self.question_templates.get(question_type, {}).get(difficulty)
        
        if not template:
            template = self.question_templates[QuestionType.MULTIPLE_CHOICE]["intermediate"]
        
        # Format prompt
        prompt = template.format(topic=topic, content=content[:1500])  # Limit content length
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # Higher creativity for question generation
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=self.ollama_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                
                # Parse the generated question
                return self._parse_generated_question(generated_text, question_type)
            
        except Exception as e:
            self.logger.error(f"Ollama question generation failed: {e}")
        
        return None
    
    def _parse_generated_question(self, generated_text: str, 
                                question_type: QuestionType) -> Dict[str, Any]:
        """Parse the generated question text into structured data"""
        
        try:
            lines = [line.strip() for line in generated_text.split('\n') if line.strip()]
            
            question_data = {
                'question': '',
                'options': [],
                'correct_answer': '',
                'explanation': ''
            }
            
            current_section = None
            
            for line in lines:
                if line.startswith('Pregunta:') or line.startswith('Caso:'):
                    question_data['question'] = line.split(':', 1)[1].strip()
                    current_section = 'question'
                    
                elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                    option = line[2:].strip()
                    question_data['options'].append(option)
                    
                elif line.startswith('Respuesta correcta:'):
                    answer = line.split(':', 1)[1].strip()
                    question_data['correct_answer'] = answer.upper()
                    
                elif line.startswith('Explicación:'):
                    explanation = line.split(':', 1)[1].strip()
                    question_data['explanation'] = explanation
                    current_section = 'explanation'
                    
                elif current_section == 'explanation' and line:
                    question_data['explanation'] += ' ' + line
                    
                elif current_section == 'question' and line and not line.startswith(('A)', 'B)', 'C)', 'D)')):
                    question_data['question'] += ' ' + line
            
            # Validate question data
            if (question_data['question'] and 
                len(question_data['options']) >= 3 and 
                question_data['correct_answer'] and 
                question_data['explanation']):
                
                return question_data
            
        except Exception as e:
            self.logger.warning(f"Failed to parse generated question: {e}")
        
        return None
    
    def _get_time_limit(self, difficulty: str) -> int:
        """Get time limit in seconds based on difficulty"""
        time_limits = {
            "basic": 90,        # 1.5 minutes
            "intermediate": 120, # 2 minutes
            "advanced": 180     # 3 minutes
        }
        return time_limits.get(difficulty, 120)
    
    def _get_points(self, difficulty: str) -> int:
        """Get points based on difficulty"""
        points = {
            "basic": 1,
            "intermediate": 2,
            "advanced": 3
        }
        return points.get(difficulty, 1)
    
    def _store_exam_metadata(self, exam_data: Dict[str, Any]):
        """Store exam metadata in database"""
        try:
            # Prepare questions for JSON serialization
            questions_to_serialize = []
            for q_dict in exam_data['questions']:
                serializable_q = q_dict.copy() # Start with a copy
                if isinstance(serializable_q.get('question_type'), Enum):
                    serializable_q['question_type'] = serializable_q['question_type'].value
                if isinstance(serializable_q.get('difficulty'), Enum):
                    serializable_q['difficulty'] = serializable_q['difficulty'].value
                questions_to_serialize.append(serializable_q)
            
            questions_json = json.dumps(questions_to_serialize)

            self.database.execute_update("""
                INSERT INTO exam_results 
                (exam_id, plan_id, exam_type, questions_total, started_at, questions_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                exam_data['exam_id'],
                exam_data.get('plan_id'),
                exam_data['exam_type'],
                exam_data['questions_total'],
                exam_data['created_at'],
                questions_json
            ))
            
            self.logger.info(f"Stored exam metadata: {exam_data['exam_id']}")
            
        except Exception as e:
            self.logger.error(f"Failed to store exam metadata: {e}")
            # It might be useful to re-raise or handle more specifically if tests need it
            raise # Re-raise to ensure test failures are clear if this path is taken
    
    def evaluate_exam(self, exam_id: str, student_answers: Dict[str, str], 
                     time_taken_seconds: int) -> ExamResult:
        """Evaluate completed exam and return results"""
        
        # Get exam questions
        exam_data = self._get_exam_by_id(exam_id)
        if not exam_data:
            raise ValueError(f"Exam not found: {exam_id}")
        
        questions = [ExamQuestion(**q) for q in exam_data['questions']]
        
        # Calculate results
        correct_answers = {}
        total_points = 0
        earned_points = 0
        
        questions_by_difficulty = {"basic": 0, "intermediate": 0, "advanced": 0}
        performance_by_topic = {}
        
        for question in questions:
            correct_answers[question.question_id] = question.correct_answer
            total_points += question.points
            
            # Count by difficulty
            questions_by_difficulty[question.difficulty.value] += 1
            
            # Track by topic
            if question.topic not in performance_by_topic:
                performance_by_topic[question.topic] = {
                    'total': 0, 'correct': 0, 'percentage': 0
                }
            performance_by_topic[question.topic]['total'] += 1
            
            # Check if answer is correct
            student_answer = student_answers.get(question.question_id, '')
            if student_answer.upper() == question.correct_answer.upper():
                earned_points += question.points
                performance_by_topic[question.topic]['correct'] += 1
        
        # Calculate percentages
        score_percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
        
        for topic_data in performance_by_topic.values():
            if topic_data['total'] > 0:
                topic_data['percentage'] = (topic_data['correct'] / topic_data['total']) * 100
        
        # Create result object
        result = ExamResult(
            exam_id=exam_id,
            student_answers=student_answers,
            correct_answers=correct_answers,
            score_percentage=score_percentage,
            time_taken_seconds=time_taken_seconds,
            questions_by_difficulty=questions_by_difficulty,
            performance_by_topic=performance_by_topic
        )
        
        # Store results
        self._store_exam_results(result)
        
        self.logger.info(f"Evaluated exam {exam_id}: {score_percentage:.1f}% score")
        
        return result
    
    def _get_exam_by_id(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """Get exam data by ID from the exam_results table."""
        try:
            query = """
                SELECT exam_id, plan_id, exam_type, questions_total, started_at, questions_data
                FROM exam_results
                WHERE exam_id = ?
            """
            result = self.database.execute_query(query, (exam_id,))
            
            if result:
                db_row = result[0]
                
                # Parse questions_data JSON string
                questions = []
                if db_row['questions_data']:
                    try:
                        questions = json.loads(db_row['questions_data'])
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Error decoding questions_data JSON for exam {exam_id}: {e}")
                        # Depending on requirements, either return None or exam_data without questions
                        return None 
                
                # Reconstruct exam_data. Note: 'specialty' is not in exam_results.
                # 'difficulty_distribution' and 'topics_covered' are also not stored directly.
                # This reconstructed exam_data will be partial compared to the one in generate_exam.
                exam_data = {
                    'exam_id': db_row['exam_id'],
                    'plan_id': db_row['plan_id'],
                    'exam_type': db_row['exam_type'],
                    'questions_total': db_row['questions_total'],
                    'created_at': db_row['started_at'], # DB stores it as started_at
                    'questions': questions,
                    # 'specialty': db_row['specialty'], # Not available in exam_results
                }
                return exam_data
            else:
                self.logger.warning(f"Exam with ID {exam_id} not found in exam_results.")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching exam {exam_id} from database: {e}")
            return None
    
    def _store_exam_results(self, result: ExamResult):
        """Store exam results in database"""
        try:
            self.database.execute_update("""
                UPDATE exam_results 
                SET questions_correct = ?, score_percentage = ?, 
                    time_taken_seconds = ?, detailed_results = ?, completed_at = ?
                WHERE exam_id = ?
            """, (
                sum(1 for topic in result.performance_by_topic.values() 
                    if topic['correct'] > 0),
                result.score_percentage,
                result.time_taken_seconds,
                json.dumps({
                    'performance_by_topic': result.performance_by_topic,
                    'questions_by_difficulty': result.questions_by_difficulty
                }),
                datetime.now().isoformat(),
                result.exam_id
            ))
         
        except Exception as e:
            self.logger.error(f"Failed to store exam results: {e}")
    
    def get_exam_statistics(self, specialty: str = None) -> Dict[str, Any]:
        """Get exam performance statistics"""
        try:
            where_clause = "WHERE exam_type = 'adaptive'"
            params = []
            
            if specialty:
                # This would need a specialty field in exam_results table
                pass
            
            results = self.database.execute_query(f"""
                SELECT 
                    COUNT(*) as total_exams,
                    AVG(score_percentage) as avg_score,
                    AVG(time_taken_seconds) as avg_time,
                    MAX(score_percentage) as best_score,
                    MIN(score_percentage) as worst_score
                FROM exam_results 
                {where_clause}
                AND completed_at IS NOT NULL
            """, tuple(params))
            
            if results:
                return results[0]
                
        except Exception as e:
            self.logger.error(f"Failed to get exam statistics: {e}")
        
        return {}

# Export main classes
__all__ = ['MedicalExamGenerator', 'ExamQuestion', 'ExamResult', 'QuestionType', 'QuestionDifficulty']