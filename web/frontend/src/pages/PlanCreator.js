import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';

const PlanCreator = () => {
  const [formData, setFormData] = useState({
    specialty: '',
    level: 'estudiante',
    target_date: '',
    current_knowledge: {},
    specific_topics: [],
    hours_per_week: 10
  });
  const [currentTopicInput, setCurrentTopicInput] = useState('');
  const [knowledgeArea, setKnowledgeArea] = useState('');
  const [knowledgeLevel, setKnowledgeLevel] = useState('');

  const queryClient = useQueryClient();

  // Check LLM status
  const { data: llmStatus } = useQuery(
    'llm-status',
    () => fetch('/api/llm/status').then(res => res.json()),
    { refetchInterval: 30000 }
  );

  // Get topic suggestions
  const { data: suggestions, isLoading: loadingSuggestions } = useQuery(
    ['topic-suggestions', formData.specialty, formData.level],
    () => {
      if (!formData.specialty) return { topics: [] };
      return fetch(`/api/plans/topics/suggestions?specialty=${formData.specialty}&level=${formData.level}`)
        .then(res => res.json());
    },
    { enabled: !!formData.specialty }
  );

  // Create plan mutation
  const createPlanMutation = useMutation(
    (planData) => 
      fetch('/api/plans/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(planData)
      }).then(res => res.json()),
    {
      onSuccess: (data) => {
        if (data.success) {
          toast.success('¡Plan de estudio creado exitosamente!');
          queryClient.invalidateQueries('plans');
          // Reset form
          setFormData({
            specialty: '',
            level: 'estudiante',
            target_date: '',
            current_knowledge: {},
            specific_topics: [],
            hours_per_week: 10
          });
        } else {
          toast.error(data.message || 'Error al crear el plan');
        }
      },
      onError: (error) => {
        toast.error('Error al crear el plan de estudio');
        console.error('Error:', error);
      }
    }
  );

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const addTopic = (topic) => {
    if (topic && !formData.specific_topics.includes(topic)) {
      setFormData(prev => ({
        ...prev,
        specific_topics: [...prev.specific_topics, topic]
      }));
    }
    setCurrentTopicInput('');
  };

  const removeTopic = (topicToRemove) => {
    setFormData(prev => ({
      ...prev,
      specific_topics: prev.specific_topics.filter(topic => topic !== topicToRemove)
    }));
  };

  const addKnowledgeArea = () => {
    if (knowledgeArea && knowledgeLevel) {
      setFormData(prev => ({
        ...prev,
        current_knowledge: {
          ...prev.current_knowledge,
          [knowledgeArea]: knowledgeLevel
        }
      }));
      setKnowledgeArea('');
      setKnowledgeLevel('');
    }
  };

  const removeKnowledgeArea = (area) => {
    setFormData(prev => {
      const newKnowledge = { ...prev.current_knowledge };
      delete newKnowledge[area];
      return { ...prev, current_knowledge: newKnowledge };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.specialty || !formData.level) {
      toast.error('Por favor completa los campos obligatorios');
      return;
    }
    createPlanMutation.mutate(formData);
  };

  const specialties = [
    { value: 'cardiologia', label: 'Cardiología' },
    { value: 'medicina_interna', label: 'Medicina Interna' },
    { value: 'neurologia', label: 'Neurología' },
    { value: 'reumatologia', label: 'Reumatología' },
    { value: 'endocrinologia', label: 'Endocrinología' },
    { value: 'gastroenterologia', label: 'Gastroenterología' },
    { value: 'neumologia', label: 'Neumología' },
    { value: 'nefrologia', label: 'Nefrología' },
    { value: 'hematologia', label: 'Hematología' },
    { value: 'oncologia', label: 'Oncología' }
  ];

  const levels = [
    { value: 'estudiante', label: 'Estudiante de Medicina' },
    { value: 'residente', label: 'Residente' },
    { value: 'especialista', label: 'Especialista' },
    { value: 'fellow', label: 'Fellow' }
  ];

  const knowledgeLevels = [
    { value: 'basico', label: 'Básico' },
    { value: 'intermedio', label: 'Intermedio' },
    { value: 'avanzado', label: 'Avanzado' },
    { value: 'experto', label: 'Experto' }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-medical p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-text mb-2">
            🧠 Creador de Planes de Estudio
          </h1>
          <p className="text-medical-text-secondary">
            Crea planes de estudio personalizados con IA
          </p>
          
          {/* LLM Status Indicator */}
          <div className="mt-4 flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${llmStatus?.available ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-medical-text-tertiary">
              {llmStatus?.available ? 'IA disponible (Phi3)' : 'IA no disponible'}
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-medical-text mb-2">
                Especialidad *
              </label>
              <select
                value={formData.specialty}
                onChange={(e) => handleInputChange('specialty', e.target.value)}
                className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              >
                <option value="">Selecciona una especialidad</option>
                {specialties.map(spec => (
                  <option key={spec.value} value={spec.value}>
                    {spec.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-medical-text mb-2">
                Nivel Académico *
              </label>
              <select
                value={formData.level}
                onChange={(e) => handleInputChange('level', e.target.value)}
                className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              >
                {levels.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-medical-text mb-2">
                Fecha Objetivo
              </label>
              <input
                type="date"
                value={formData.target_date}
                onChange={(e) => handleInputChange('target_date', e.target.value)}
                className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-medical-text mb-2">
                Horas por Semana
              </label>
              <input
                type="number"
                min="1"
                max="80"
                value={formData.hours_per_week}
                onChange={(e) => handleInputChange('hours_per_week', parseInt(e.target.value))}
                className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          {/* Knowledge Assessment */}
          <div>
            <h3 className="text-lg font-semibold text-medical-text mb-4">
              Conocimiento Actual
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <input
                type="text"
                placeholder="Área de conocimiento"
                value={knowledgeArea}
                onChange={(e) => setKnowledgeArea(e.target.value)}
                className="px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <select
                value={knowledgeLevel}
                onChange={(e) => setKnowledgeLevel(e.target.value)}
                className="px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Nivel</option>
                {knowledgeLevels.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={addKnowledgeArea}
                className="px-4 py-3 bg-secondary-500 text-white rounded-lg hover:bg-secondary-600 transition-colors"
              >
                Agregar
              </button>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {Object.entries(formData.current_knowledge).map(([area, level]) => (
                <span
                  key={area}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-secondary-100 text-secondary-800"
                >
                  {area}: {level}
                  <button
                    type="button"
                    onClick={() => removeKnowledgeArea(area)}
                    className="ml-2 text-secondary-600 hover:text-secondary-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Topic Selection */}
          <div>
            <h3 className="text-lg font-semibold text-medical-text mb-4">
              Temas Específicos
            </h3>
            
            {/* Topic Input */}
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                placeholder="Agregar tema específico"
                value={currentTopicInput}
                onChange={(e) => setCurrentTopicInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTopic(currentTopicInput))}
                className="flex-1 px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <button
                type="button"
                onClick={() => addTopic(currentTopicInput)}
                className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                Agregar
              </button>
            </div>

            {/* AI Suggestions */}
            {formData.specialty && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-medical-text-secondary mb-2">
                  Sugerencias de IA:
                </h4>
                {loadingSuggestions ? (
                  <div className="text-sm text-medical-text-tertiary">Cargando sugerencias...</div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {suggestions?.topics?.map((topic, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => addTopic(topic)}
                        className="px-3 py-1 text-sm bg-accent-100 text-accent-800 rounded-full hover:bg-accent-200 transition-colors"
                      >
                        + {topic}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Selected Topics */}
            <div className="flex flex-wrap gap-2">
              {formData.specific_topics.map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800"
                >
                  {topic}
                  <button
                    type="button"
                    onClick={() => removeTopic(topic)}
                    className="ml-2 text-primary-600 hover:text-primary-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={createPlanMutation.isLoading || !llmStatus?.available}
              className="px-8 py-4 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {createPlanMutation.isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Creando plan...</span>
                </div>
              ) : (
                'Crear Plan de Estudio'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PlanCreator;