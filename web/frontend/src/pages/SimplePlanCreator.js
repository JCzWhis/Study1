import React, { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';

const SimplePlanCreator = () => {
  const [formData, setFormData] = useState({
    specialty: '',
    topic: '',
    level: 'residente',
    weeks: 4,
    hours_per_week: 10,
    specific_topics: '',
    materials: ''
  });

  const queryClient = useQueryClient();

  // Create plan mutation
  const createPlanMutation = useMutation(
    (planData) => 
      fetch('/api/plans/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          specialty: planData.specialty,
          level: planData.level,
          target_date: new Date(Date.now() + planData.weeks * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          specific_topics: planData.topic ? [planData.topic] : [],
          hours_per_week: planData.hours_per_week,
          current_knowledge: {},
          additional_topics: planData.specific_topics,
          materials: planData.materials
        })
      }).then(res => res.json()),
    {
      onSuccess: (data) => {
        if (data.success) {
          toast.success('¡Plan de estudio creado exitosamente!');
          queryClient.invalidateQueries('plans');
          // Reset form
          setFormData({
            specialty: '',
            topic: '',
            level: 'residente',
            weeks: 4,
            hours_per_week: 10,
            specific_topics: '',
            materials: ''
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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.specialty || !formData.topic) {
      toast.error('Por favor completa especialidad y tema principal');
      return;
    }
    createPlanMutation.mutate(formData);
  };

  const levels = [
    { value: 'estudiante', label: 'Estudiante de Medicina' },
    { value: 'residente', label: 'Residente' },
    { value: 'especialista', label: 'Especialista' },
    { value: 'fellow', label: 'Fellow' }
  ];

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

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-medical p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-text mb-2">
            🎓 Creador de Planes Simplificado
          </h1>
          <p className="text-medical-text-secondary">
            Crea planes de estudio médicos con IA - Interfaz simple y directa
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Especialidad y Nivel */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-medical-text mb-2">
                Especialidad Médica *
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
                Nivel de Complejidad *
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
          </div>

          {/* Tema Principal */}
          <div>
            <label className="block text-sm font-medium text-medical-text mb-2">
              Tema Principal *
            </label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => handleInputChange('topic', e.target.value)}
              placeholder="Ej: Insuficiencia Cardíaca, Diabetes Tipo 2, Accidente Cerebrovascular"
              className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
            />
            <p className="mt-1 text-sm text-medical-text-tertiary">
              El tema principal que quieres estudiar en profundidad
            </p>
          </div>

          {/* Tiempo y Dedicación */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-medical-text mb-2">
                Duración (semanas)
              </label>
              <input
                type="number"
                min="1"
                max="52"
                value={formData.weeks}
                onChange={(e) => handleInputChange('weeks', parseInt(e.target.value))}
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

          {/* Temas Específicos Adicionales */}
          <div>
            <label className="block text-sm font-medium text-medical-text mb-2">
              Temas Específicos Adicionales
            </label>
            <textarea
              value={formData.specific_topics}
              onChange={(e) => handleInputChange('specific_topics', e.target.value)}
              placeholder="Ej: Farmacología cardiovascular, Electrocardiografía, Ecocardiografía (separados por comas)"
              rows="3"
              className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p className="mt-1 text-sm text-medical-text-tertiary">
              Temas adicionales que quieres incluir en el plan (opcional)
            </p>
          </div>

          {/* Material Específico */}
          <div>
            <label className="block text-sm font-medium text-medical-text mb-2">
              Material de Estudio Específico
            </label>
            <textarea
              value={formData.materials}
              onChange={(e) => handleInputChange('materials', e.target.value)}
              placeholder="Ej: Harrison's Principles of Internal Medicine, Guías ESC 2023, Casos clínicos del Hospital X"
              rows="3"
              className="w-full px-4 py-3 border border-medical-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p className="mt-1 text-sm text-medical-text-tertiary">
              Libros, artículos, guías o recursos específicos que quieres usar (opcional)
            </p>
          </div>

          {/* Resumen del Plan */}
          {formData.specialty && formData.topic && (
            <div className="bg-accent-50 p-4 rounded-lg border border-accent-200">
              <h3 className="font-medium text-accent-800 mb-2">📋 Resumen del Plan:</h3>
              <ul className="text-sm text-accent-700 space-y-1">
                <li>• <strong>Especialidad:</strong> {specialties.find(s => s.value === formData.specialty)?.label}</li>
                <li>• <strong>Nivel:</strong> {levels.find(l => l.value === formData.level)?.label}</li>
                <li>• <strong>Tema principal:</strong> {formData.topic}</li>
                <li>• <strong>Duración:</strong> {formData.weeks} semanas</li>
                <li>• <strong>Dedicación:</strong> {formData.hours_per_week} horas/semana</li>
                <li>• <strong>Total de horas:</strong> {formData.weeks * formData.hours_per_week} horas</li>
              </ul>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={createPlanMutation.isLoading}
              className="px-8 py-4 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {createPlanMutation.isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Creando plan con IA...</span>
                </div>
              ) : (
                '🧠 Crear Plan con IA'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SimplePlanCreator;