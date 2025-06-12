import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, RotateCcw, CheckCircle, Clock, Brain } from 'lucide-react';
import { useQuery } from 'react-query';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const Study = () => {
  const [currentTopic, setCurrentTopic] = useState(null);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [sessionPhase, setSessionPhase] = useState('ready'); // ready, studying, quiz, completed
  
  const location = useLocation();
  const planId = location.state?.planId; // Get planId from navigation state

  const { data: dueTopics } = useQuery('due-topics',
    () => axios.get('/api/topics/due').then(res => res.data)
  );

  // Filter topics by plan if planId is provided
  const filteredTopics = planId && dueTopics 
    ? dueTopics.filter(topic => topic.plan_id === planId)
    : dueTopics;

  // Timer effect
  useEffect(() => {
    let interval = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimerSeconds(seconds => seconds + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startStudySession = (topic) => {
    setCurrentTopic(topic);
    setSessionPhase('studying');
    setTimerSeconds(0);
    setIsTimerRunning(true);
  };

  const pauseTimer = () => {
    setIsTimerRunning(!isTimerRunning);
  };

  const resetSession = () => {
    setIsTimerRunning(false);
    setTimerSeconds(0);
    setSessionPhase('ready');
    setCurrentTopic(null);
  };

  const completeSession = () => {
    setIsTimerRunning(false);
    setSessionPhase('quiz');
  };

  if (sessionPhase === 'studying' && currentTopic) {
    return <StudySession 
      topic={currentTopic}
      timerSeconds={timerSeconds}
      isTimerRunning={isTimerRunning}
      onPause={pauseTimer}
      onComplete={completeSession}
      onReset={resetSession}
    />;
  }

  if (sessionPhase === 'quiz' && currentTopic) {
    return <QuizSession 
      topic={currentTopic}
      sessionDuration={timerSeconds}
      onComplete={resetSession}
    />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sesiones de Estudio</h1>
        <p className="text-gray-600">Estudia con metodología científica y seguimiento de progreso</p>
      </div>

      {/* Estadísticas de estudio */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StudyStatCard
          icon={Clock}
          title="Tiempo Hoy"
          value="2h 45m"
          subtitle="Meta: 4h"
          color="blue"
        />
        <StudyStatCard
          icon={Brain}
          title="Temas Estudiados"
          value="8"
          subtitle="Esta semana"
          color="green"
        />
        <StudyStatCard
          icon={CheckCircle}
          title="Sesiones Completadas"
          value="23"
          subtitle="Este mes"
          color="purple"
        />
        <StudyStatCard
          icon={Play}
          title="Racha"
          value="12 días"
          subtitle="¡Excelente!"
          color="orange"
        />
      </div>

      {/* Temas pendientes para estudiar */}
      <div className="medical-card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          🎯 {planId ? 'Temas del Plan Seleccionado' : 'Temas Pendientes para Hoy'} ({filteredTopics?.length || 0})
        </h2>
        
        {filteredTopics && filteredTopics.length > 0 ? (
          <div className="grid gap-4">
            {filteredTopics.map((topic, index) => (
              <TopicStudyCard 
                key={topic.id} 
                topic={topic} 
                index={index}
                onStart={() => startStudySession(topic)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ¡Todos los temas al día!
            </h3>
            <p className="text-gray-500">
              No hay temas pendientes para hoy. ¡Excelente trabajo!
            </p>
          </div>
        )}
      </div>

      {/* Metodología */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MethodologyCard
          icon="⏱️"
          title="Pomodoro Médico"
          description="Sesiones de 45 minutos optimizadas para contenido médico complejo"
        />
        <MethodologyCard
          icon="🎓"
          title="Active Recall"
          description="Preguntas automáticas cada 10 minutos para verificar comprensión"
        />
        <MethodologyCard
          icon="🔄"
          title="Repetición Espaciada"
          description="Algoritmo Ali Abdaal con intervalos adaptativos por confianza"
        />
      </div>
    </div>
  );
};

const StudyStatCard = ({ icon: Icon, title, value, subtitle, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    orange: 'text-orange-600 bg-orange-50'
  };

  return (
    <div className="medical-card p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]} mr-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
      </div>
    </div>
  );
};

const TopicStudyCard = ({ topic, index, onStart }) => {
  const confidenceColors = {
    red: 'bg-red-500',
    orange: 'bg-orange-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500'
  };

  const priorityLabels = {
    red: 'Urgente',
    orange: 'Alto',
    yellow: 'Medio',
    green: 'Bajo',
    blue: 'Mantenimiento'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <div className="flex items-center space-x-4">
        <div className={`w-4 h-4 rounded-full ${confidenceColors[topic.confidence_level]}`} />
        <div>
          <h3 className="font-medium text-gray-900">{topic.name}</h3>
          <p className="text-sm text-gray-500">
            📚 {topic.specialty} • Prioridad: {priorityLabels[topic.confidence_level]}
          </p>
          <p className="text-xs text-gray-400">
            Estudiado {topic.study_count} veces • ~{topic.estimated_hours}h estimadas
          </p>
        </div>
      </div>
      <button
        onClick={onStart}
        className="btn-medical-primary flex items-center gap-2"
      >
        <Play className="h-4 w-4" />
        Estudiar
      </button>
    </motion.div>
  );
};

const MethodologyCard = ({ icon, title, description }) => (
  <div className="medical-card p-6 text-center">
    <div className="text-3xl mb-4">{icon}</div>
    <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </div>
);

const StudySession = ({ topic, timerSeconds, isTimerRunning, onPause, onComplete, onReset }) => {
  const progress = Math.min((timerSeconds / (45 * 60)) * 100, 100);
  
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header de sesión */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Estudiando: {topic.name}</h1>
        <p className="text-gray-600">📚 {topic.specialty}</p>
      </div>

      {/* Timer principal */}
      <div className="medical-card p-8 text-center">
        <div className="mb-6">
          <div className={`text-6xl font-bold mb-4 ${timerSeconds > 45 * 60 ? 'text-green-600' : 'text-blue-600'}`}>
            {Math.floor(timerSeconds / 60)}:{(timerSeconds % 60).toString().padStart(2, '0')}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600">
            Meta: 45 minutos • Progreso: {Math.round(progress)}%
          </p>
        </div>

        <div className="flex justify-center gap-4">
          <button
            onClick={onPause}
            className={`btn-medical-primary flex items-center gap-2 ${!isTimerRunning ? 'bg-green-600 hover:bg-green-700' : ''}`}
          >
            {isTimerRunning ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            {isTimerRunning ? 'Pausar' : 'Continuar'}
          </button>
          <button
            onClick={onComplete}
            className="btn-medical-secondary flex items-center gap-2"
          >
            <CheckCircle className="h-5 w-5" />
            Completar
          </button>
          <button
            onClick={onReset}
            className="btn-medical-outline flex items-center gap-2"
          >
            <RotateCcw className="h-5 w-5" />
            Reiniciar
          </button>
        </div>
      </div>

      {/* Contenido de estudio */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Área principal de estudio */}
        <div className="lg:col-span-2 medical-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📖 Área de Estudio</h3>
          <div className="prose max-w-none">
            <p className="text-gray-600 mb-4">
              Aquí estudiarás el tema <strong>{topic.name}</strong>. Puedes usar cualquier recurso:
            </p>
            <ul className="text-sm text-gray-600 space-y-2">
              <li>• Libros de texto médicos</li>
              <li>• Videos educativos</li>
              <li>• Casos clínicos</li>
              <li>• Artículos de investigación</li>
              <li>• Simuladores médicos</li>
            </ul>
            <div className="bg-blue-50 p-4 rounded-lg mt-6">
              <p className="text-sm text-blue-800">
                💡 <strong>Tip:</strong> Cada 10 minutos aparecerá una pregunta de Active Recall para verificar tu comprensión.
              </p>
            </div>
          </div>
        </div>

        {/* Panel lateral */}
        <div className="space-y-4">
          {/* Notas rápidas */}
          <div className="medical-card p-4">
            <h4 className="font-medium text-gray-900 mb-3">📝 Notas Rápidas</h4>
            <textarea
              placeholder="Anota conceptos clave, dudas, ideas importantes..."
              className="w-full h-32 text-sm border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Objetivos de la sesión */}
          <div className="medical-card p-4">
            <h4 className="font-medium text-gray-900 mb-3">🎯 Objetivos</h4>
            <div className="space-y-2 text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Entender conceptos básicos
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Revisar casos clínicos
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Memorizar puntos clave
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const QuizSession = ({ topic, sessionDuration, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [newConfidence, setNewConfidence] = useState(topic.confidence_level);

  const questions = [
    {
      question: `¿Cuáles son los puntos más importantes sobre ${topic.name}?`,
      type: 'text'
    },
    {
      question: `¿Qué aspectos de ${topic.name} te resultan más difíciles?`,
      type: 'text'
    },
    {
      question: `¿Cómo calificarías tu confianza actual en este tema?`,
      type: 'confidence'
    }
  ];

  const handleSubmit = async () => {
    try {
      // Send study session data to backend
      const response = await axios.post(`/api/topics/${topic.id}/study`, {
        topic_id: topic.id,
        new_confidence: newConfidence,
        session_duration: Math.floor(sessionDuration / 60), // Convert to minutes
        notes: selectedAnswer
      });
      
      console.log('Study session completed:', response.data);
      onComplete();
    } catch (error) {
      console.error('Error completing study session:', error);
      onComplete(); // Still complete the session even if API call fails
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Quiz Post-Estudio</h1>
        <p className="text-gray-600">Evalúa tu comprensión de {topic.name}</p>
        <p className="text-sm text-gray-500">Tiempo estudiado: {Math.floor(sessionDuration / 60)} minutos</p>
      </div>

      <div className="medical-card p-6">
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm text-gray-500">Pregunta {currentQuestion + 1} de {questions.length}</span>
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>
          
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {questions[currentQuestion].question}
          </h3>

          {questions[currentQuestion].type === 'text' ? (
            <textarea
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              className="w-full h-32 border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Escribe tu respuesta aquí..."
            />
          ) : (
            <div className="space-y-3">
              {['red', 'orange', 'yellow', 'green', 'blue'].map((level) => (
                <button
                  key={level}
                  onClick={() => setNewConfidence(level)}
                  className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
                    newConfidence === level 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center">
                    <div className={`w-4 h-4 rounded-full mr-3 ${
                      level === 'red' ? 'bg-red-500' :
                      level === 'orange' ? 'bg-orange-500' :
                      level === 'yellow' ? 'bg-yellow-500' :
                      level === 'green' ? 'bg-green-500' : 'bg-blue-500'
                    }`} />
                    <div>
                      <p className="font-medium">
                        {level === 'red' ? '🔴 No sé nada' :
                         level === 'orange' ? '🟠 Sé muy poco' :
                         level === 'yellow' ? '🟡 Sé algo' :
                         level === 'green' ? '🟢 Sé bastante' : '🔵 Lo domino'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {level === 'red' ? 'Estudiar hoy' :
                         level === 'orange' ? 'Cada 3 días' :
                         level === 'yellow' ? 'Semanal' :
                         level === 'green' ? 'Cada 3 semanas' : 'Cada 3 meses'}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex gap-3">
          {currentQuestion > 0 && (
            <button
              onClick={() => setCurrentQuestion(currentQuestion - 1)}
              className="btn-medical-outline"
            >
              Anterior
            </button>
          )}
          
          {currentQuestion < questions.length - 1 ? (
            <button
              onClick={() => setCurrentQuestion(currentQuestion + 1)}
              className="btn-medical-primary ml-auto"
            >
              Siguiente
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="btn-medical-primary ml-auto"
            >
              Completar Sesión
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Study;
