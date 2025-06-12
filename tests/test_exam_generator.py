import unittest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from core.exam_generator import (
    MedicalExamGenerator,
    ExamQuestion,
    QuestionType,
    QuestionDifficulty,
    ExamResult
)

# Helper to create ExamQuestion instances easily if needed, or we can use dicts
def create_sample_question(q_id, topic, difficulty: QuestionDifficulty, text, options, correct_answer, explanation, points=1, q_type: QuestionType = QuestionType.MULTIPLE_CHOICE, specialty="general"):
    # Returns a dictionary, similar to what q.__dict__ would do, but with Enums as string values
    return {
        'question_id': q_id,
        'question_type': q_type.value, # Use .value
        'difficulty': difficulty.value, # Use .value
        'specialty': specialty,
        'topic': topic,
        'question_text': text,
        'options': options,
        'correct_answer': correct_answer,
        'explanation': explanation,
        'image_path': None,
        'time_limit_seconds': 120, # Default
        'points': points
    }

class TestMedicalExamGenerator(unittest.TestCase):

    def setUp(self):
        # Mock DatabaseManager
        self.mock_db = MagicMock()
        self.mock_db.execute_update_calls = [] # To store calls to execute_update

        def mock_execute_update(query, params=None):
            self.mock_db.execute_update_calls.append({'query': query, 'params': params})
            return 1 # Simulate 1 row affected
        
        self.mock_db.execute_update = mock_execute_update
        self.mock_db.execute_query.return_value = [] # Default return

        # Mock RAGEngine
        self.mock_rag_engine = MagicMock()

        # Mock Config
        # Provide enough config to prevent errors in __init__ or _initialize_ollama
        self.mock_config = MagicMock()
        self.mock_config.get_ollama_config.return_value = {
            'host': 'http://mock-ollama-host:11434', # Mock host
            'model': 'mock_model',
            'timeout': 5
        }
        
        # Patch requests.get to prevent actual HTTP calls in _initialize_ollama
        self.patcher = patch('requests.get')
        self.mock_requests_get = self.patcher.start()
        self.mock_requests_get.return_value.status_code = 200 # Simulate Ollama is up

        # Instantiate MedicalExamGenerator
        self.exam_generator = MedicalExamGenerator(
            config=self.mock_config,
            database=self.mock_db,
            rag_engine=self.mock_rag_engine
        )
        
        # Ensure _initialize_ollama doesn't break things if it makes network calls
        # It's called in __init__, so self.patcher handles it.

    def tearDown(self):
        self.patcher.stop() # Stop the requests.get patcher

    def test_store_and_get_exam(self):
        sample_dt = datetime.now()
        sample_questions_list = [
            create_sample_question( # This now returns a dict with stringified enums
                q_id="q001", topic="Hypertension", difficulty=QuestionDifficulty.BASIC,
                text="What is hypertension?", options=["High BP", "Low BP"],
                correct_answer="A", explanation="High blood pressure", points=1
            ),
            create_sample_question( # This now returns a dict with stringified enums
                q_id="q002", topic="Diabetes", difficulty=QuestionDifficulty.INTERMEDIATE,
                text="What is Type 2 Diabetes?", options=["Insulin resistance", "Insulin overproduction"],
                correct_answer="A", explanation="Often due to insulin resistance.", points=2
            )
        ]

        sample_exam_data = {
            'exam_id': "test_exam_001",
            'plan_id': "test_plan_001",
            'specialty': "cardiology", # This field is in exam_data but not exam_results table
            'questions_total': len(sample_questions_list),
            'questions': sample_questions_list,
            'created_at': sample_dt.isoformat(),
            'exam_type': "adaptive"
        }

        # 1. Test _store_exam_metadata
        self.exam_generator._store_exam_metadata(sample_exam_data)
        
        # Check if execute_update was called correctly
        self.assertEqual(len(self.mock_db.execute_update_calls), 1)
        call_args = self.mock_db.execute_update_calls[0]
        self.assertIn("INSERT INTO exam_results", call_args['query'])
        self.assertIn("questions_data", call_args['query']) # Ensure new column is in query
        
        # Params: (exam_id, plan_id, exam_type, questions_total, started_at, questions_data_json)
        expected_params = (
            sample_exam_data['exam_id'],
            sample_exam_data['plan_id'],
            sample_exam_data['exam_type'],
            sample_exam_data['questions_total'],
            sample_exam_data['created_at'],
            json.dumps(sample_exam_data['questions'])
        )
        self.assertEqual(call_args['params'], expected_params)

        # 2. Test _get_exam_by_id
        # Configure mock_db.execute_query to return the stored data
        # This simulates the DB row that _get_exam_by_id would query
        mock_db_row = {
            'exam_id': sample_exam_data['exam_id'],
            'plan_id': sample_exam_data['plan_id'],
            'exam_type': sample_exam_data['exam_type'],
            'questions_total': sample_exam_data['questions_total'],
            'started_at': sample_exam_data['created_at'],
            'questions_data': json.dumps(sample_exam_data['questions']) # Stored as JSON
        }
        self.mock_db.execute_query.return_value = [mock_db_row]

        retrieved_exam_data = self.exam_generator._get_exam_by_id("test_exam_001")

        self.assertIsNotNone(retrieved_exam_data)
        self.assertEqual(retrieved_exam_data['exam_id'], sample_exam_data['exam_id'])
        self.assertEqual(retrieved_exam_data['plan_id'], sample_exam_data['plan_id'])
        self.assertEqual(retrieved_exam_data['exam_type'], sample_exam_data['exam_type'])
        self.assertEqual(retrieved_exam_data['questions_total'], sample_exam_data['questions_total'])
        self.assertEqual(retrieved_exam_data['created_at'], sample_exam_data['created_at'])
        
        # Compare questions. They should be dicts.
        self.assertEqual(len(retrieved_exam_data['questions']), len(sample_questions_list))
        for i in range(len(sample_questions_list)):
            # Converting ExamQuestion objects to dicts for comparison if they were objects
            # In this setup, sample_questions_list already contains dicts.
            self.assertDictEqual(retrieved_exam_data['questions'][i], sample_questions_list[i])

    def test_evaluate_exam_flow(self):
        eval_exam_id = "test_eval_exam_001"
        sample_dt = datetime.now()

        # Simplified questions for evaluation clarity
        # create_sample_question now returns dicts with stringified enums
        question1_dict = create_sample_question(
            q_id="q1", topic="TopicA", difficulty=QuestionDifficulty.BASIC,
            text="Q1 Text", options=["A", "B"], correct_answer="A", explanation="Expl A", points=1
        )
        question2_dict = create_sample_question(
            q_id="q2", topic="TopicB", difficulty=QuestionDifficulty.INTERMEDIATE,
            text="Q2 Text", options=["A", "B", "C"], correct_answer="B", explanation="Expl B", points=2
        )

        eval_exam_questions = [question1_dict, question2_dict]

        eval_exam_data = {
            'exam_id': eval_exam_id,
            'plan_id': "eval_plan_001",
            'exam_type': "adaptive",
            'questions_total': len(eval_exam_questions),
            'created_at': sample_dt.isoformat(),
            'questions': eval_exam_questions,
            # 'specialty': 'general' # Not strictly needed for _get_exam_by_id reconstruction
        }

        # Mock _get_exam_by_id to return our specific exam data for evaluation
        # This is more direct than setting up execute_query for this specific test case
        with patch.object(self.exam_generator, '_get_exam_by_id', return_value=eval_exam_data) as mock_get_method:
            student_answers = {"q1": "A", "q2": "C"} # q1 correct, q2 incorrect
            time_taken = 300

            # Reset execute_update_calls before this action
            self.mock_db.execute_update_calls = []

            result = self.exam_generator.evaluate_exam(eval_exam_id, student_answers, time_taken)

            mock_get_method.assert_called_once_with(eval_exam_id)

            # Assertions for ExamResult
            self.assertIsInstance(result, ExamResult)
            self.assertEqual(result.exam_id, eval_exam_id)
            self.assertEqual(result.student_answers, student_answers)
            
            expected_correct_answers = {"q1": "A", "q2": "B"}
            self.assertEqual(result.correct_answers, expected_correct_answers)

            # Score calculation: q1 is 1 point (correct), q2 is 2 points (incorrect). Total points = 1+2=3. Earned = 1.
            # Score = (1/3) * 100
            self.assertAlmostEqual(result.score_percentage, (1.0/3.0) * 100.0, places=2)
            self.assertEqual(result.time_taken_seconds, time_taken)

            # Check performance_by_topic (assuming questions have topics)
            self.assertIn("TopicA", result.performance_by_topic)
            self.assertEqual(result.performance_by_topic["TopicA"]['correct'], 1)
            self.assertEqual(result.performance_by_topic["TopicA"]['total'], 1)
            self.assertIn("TopicB", result.performance_by_topic)
            self.assertEqual(result.performance_by_topic["TopicB"]['correct'], 0)
            self.assertEqual(result.performance_by_topic["TopicB"]['total'], 1)

            # Check questions_by_difficulty
            self.assertEqual(result.questions_by_difficulty[QuestionDifficulty.BASIC.value], 1)
            self.assertEqual(result.questions_by_difficulty[QuestionDifficulty.INTERMEDIATE.value], 1)


            # Check that _store_exam_results called database.execute_update
            self.assertEqual(len(self.mock_db.execute_update_calls), 1)
            store_results_call = self.mock_db.execute_update_calls[0]
            # Make assertion for SQL query more robust
            self.assertTrue("UPDATE exam_results" in store_results_call['query'])
            self.assertTrue("SET" in store_results_call['query'])
            self.assertTrue("questions_correct = ?" in store_results_call['query'])
            self.assertTrue("score_percentage = ?" in store_results_call['query'])
            self.assertTrue("time_taken_seconds = ?" in store_results_call['query'])
            self.assertTrue("detailed_results = ?" in store_results_call['query'])
            self.assertTrue("completed_at = ?" in store_results_call['query'])
            self.assertTrue("WHERE exam_id = ?" in store_results_call['query'])
            
            # Params for UPDATE: (questions_correct, score_percentage, time_taken_seconds, detailed_results_json, completed_at, exam_id)
            # questions_correct here is count of questions with at least one correct, which is a bit ambiguous from problem desc.
            # sum(1 for topic in result.performance_by_topic.values() if topic['correct'] > 0)
            # For this case, TopicA has 1 correct, TopicB has 0. So 1.
            num_correct_questions = 1 
            
            detailed_results_json = json.dumps({
                'performance_by_topic': result.performance_by_topic,
                'questions_by_difficulty': result.questions_by_difficulty
            })

            # We don't know the exact completed_at timestamp, so we check for its existence.
            self.assertEqual(store_results_call['params'][0], num_correct_questions)
            self.assertAlmostEqual(store_results_call['params'][1], result.score_percentage, places=2)
            self.assertEqual(store_results_call['params'][2], time_taken)
            self.assertEqual(store_results_call['params'][3], detailed_results_json)
            self.assertIsNotNone(store_results_call['params'][4]) # completed_at
            self.assertEqual(store_results_call['params'][5], eval_exam_id)


if __name__ == '__main__':
    unittest.main()
