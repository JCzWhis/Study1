import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { motion } from 'framer-motion';
import { Plus, Calendar, BookOpen, Target, MoreVertical, Upload } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const Plans = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPdfUpload, setShowPdfUpload] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  const { data: plans, isLoading } = useQuery('plans',
    () => fetch('/api/plans').then(res => res.json())
  );

  const createPlanMutation = useMutation(
    (newPlan) => axios.post('/api/plans', newPlan),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('plans');
        setShowCreateModal(false);
        toast.success('Plan creado exitosamente');
      },
      onError: () => {
        toast.error('Error al crear el plan');
      }
    }
  );

  const uploadPdfMutation = useMutation(
    ({ file, specialty }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('specialty', specialty);
      return axios.post('/api/rag/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    {
      onSuccess: (response) => {
        toast.success('PDF cargado exitosamente al sistema RAG');
        setShowPdfUpload(false);
      },
      onError: (error) => {
        toast.error('Error al cargar el PDF');
        console.error('PDF upload error:', error);
      }
    }
  );

  if (isLoading) {
    return <PlansListSkeleton />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Planes</h1>
          <p className="text-gray-600 mt-1">Organiza y gestiona tus planes de estudio médico</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowPdfUpload(true)}
            className="btn-medical-outline flex items-center gap-2"
          >
            <Upload className="h-5 w-5" />
            Subir PDF a RAG
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-medical-primary flex items-center gap-2"
          >
            <Plus className="h-5 w-5" />
            Nuevo Plan
          </button>
        </div>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <QuickStat
          icon={Calendar}
          label="Planes Activos"
          value={plans?.length || 0}
          color="blue"
        />
        <QuickStat
          icon={BookOpen}
          label="Total Temas"
          value={plans?.reduce((acc, plan) => acc + (plan.topics?.length || 0), 0) || 0}
          color="green"
        />
        <QuickStat
          icon={Target}
          label="Pendientes Hoy"
          value="12"
          color="orange"
        />
        <QuickStat
          icon={Calendar}
          label="Próximo Examen"
          value="15 días"
          color="purple"
        />
      </div>

      {/* Lista de planes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {plans?.map((plan, index) => (
          <PlanCard key={plan.id} plan={plan} index={index} />
        ))}
        
        {!plans?.length && (
          <div className="col-span-full text-center py-12">
            <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay planes creados</h3>
            <p className="text-gray-500 mb-4">Comienza creando tu primer plan de estudio</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-medical-primary"
            >
              Crear Primer Plan
            </button>
          </div>
        )}
      </div>

      {/* Modal crear plan */}
      {showCreateModal && (
        <CreatePlanModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={(data) => createPlanMutation.mutate(data)}
          isLoading={createPlanMutation.isLoading}
        />
      )}

      {/* Modal subir PDF */}
      {showPdfUpload && (
        <PdfUploadModal
          onClose={() => setShowPdfUpload(false)}
          onSubmit={(data) => uploadPdfMutation.mutate(data)}
          isLoading={uploadPdfMutation.isLoading}
        />
      )}
    </div>
  );
};

const QuickStat = ({ icon: Icon, label, value, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    orange: 'text-orange-600 bg-orange-50',
    purple: 'text-purple-600 bg-purple-50'
  };

  return (
    <div className="medical-card p-6">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${colorClasses[color]} mr-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{label}</p>
        </div>
      </div>
    </div>
  );
};

const PlanCard = ({ plan, index }) => {
  const navigate = useNavigate();
  const specialtyColors = {
    cardiologia: 'bg-red-50 text-red-700 border-red-200',
    reumatologia: 'bg-blue-50 text-blue-700 border-blue-200',
    medicina_interna: 'bg-green-50 text-green-700 border-green-200'
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
      className="medical-card-hover p-6"
    >
      {/* Header del plan */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{plan.title}</h3>
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded border ${specialtyColors[plan.specialty] || specialtyColors.medicina_interna}`}>
            {plan.specialty.replace('_', ' ')}
          </span>
        </div>
        <button className="p-1 text-gray-400 hover:text-gray-600">
          <MoreVertical className="h-5 w-5" />
        </button>
      </div>

      {/* Estadísticas del plan */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-600">{plan.topics?.length || 0}</p>
          <p className="text-xs text-gray-500">Temas</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">68%</p>
          <p className="text-xs text-gray-500">Progreso</p>
        </div>
      </div>

      {/* Progreso visual */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progreso general</span>
          <span>68%</span>
        </div>
        <div className="progress-bar-bg">
          <div className="progress-bar-fill bg-blue-500" style={{ width: '68%' }} />
        </div>
      </div>

      {/* Fechas */}
      <div className="text-sm text-gray-500 mb-4">
        <p>📅 Creado: {formatDate(plan.created_at)}</p>
        {plan.target_date && (
          <p>🎯 Meta: {formatDate(plan.target_date)}</p>
        )}
      </div>

      {/* Acciones */}
      <div className="flex gap-2">
        <button 
          onClick={() => navigate('/study', { state: { planId: plan.id } })}
          className="flex-1 btn-medical-primary text-sm"
        >
          Estudiar
        </button>
        <button className="flex-1 btn-medical-outline text-sm">
          Ver Detalles
        </button>
      </div>
    </motion.div>
  );
};

const CreatePlanModal = ({ onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    title: '',
    specialty: 'medicina_interna',
    topics: '',
    target_date: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const topicsArray = formData.topics
      .split('\n')
      .map(topic => topic.trim())
      .filter(topic => topic.length > 0);

    onSubmit({
      title: formData.title,
      specialty: formData.specialty,
      topics: topicsArray,
      target_date: formData.target_date ? new Date(formData.target_date).toISOString() : null
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Crear Nuevo Plan</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Título */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Título del Plan
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="ej. Preparación Examen Cardiología"
                required
              />
            </div>

            {/* Especialidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Especialidad
              </label>
              <select
                value={formData.specialty}
                onChange={(e) => setFormData(prev => ({ ...prev, specialty: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="medicina_interna">Medicina Interna</option>
                <option value="cardiologia">Cardiología</option>
                <option value="reumatologia">Reumatología</option>
                <option value="endocrinologia">Endocrinología</option>
                <option value="neurologia">Neurología</option>
                <option value="gastroenterologia">Gastroenterología</option>
              </select>
            </div>

            {/* Temas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temas (uno por línea)
              </label>
              <textarea
                value={formData.topics}
                onChange={(e) => setFormData(prev => ({ ...prev, topics: e.target.value }))}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Insuficiencia Cardíaca
Arritmias Cardíacas
Síndrome Coronario Agudo"
                required
              />
            </div>

            {/* Fecha objetivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha Objetivo (opcional)
              </label>
              <input
                type="date"
                value={formData.target_date}
                onChange={(e) => setFormData(prev => ({ ...prev, target_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Botones */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 btn-medical-primary disabled:opacity-50"
              >
                {isLoading ? 'Creando...' : 'Crear Plan'}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

const PdfUploadModal = ({ onClose, onSubmit, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [specialty, setSpecialty] = useState('medicina_interna');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error('Por favor selecciona un archivo PDF');
      return;
    }
    
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Solo se permiten archivos PDF');
      return;
    }

    onSubmit({ file: selectedFile, specialty });
  };

  const specialties = [
    { value: 'medicina_interna', label: 'Medicina Interna' },
    { value: 'cardiologia', label: 'Cardiología' },
    { value: 'reumatologia', label: 'Reumatología' },
    { value: 'endocrinologia', label: 'Endocrinología' },
    { value: 'neurologia', label: 'Neurología' },
    { value: 'gastroenterologia', label: 'Gastroenterología' },
    { value: 'general', label: 'General' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-xl max-w-md w-full"
      >
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Subir PDF al Sistema RAG</h2>
          <p className="text-sm text-gray-600 mb-6">
            Sube contenido médico específico para enriquecer el conocimiento del sistema
          </p>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Especialidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Especialidad
              </label>
              <select
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {specialties.map(spec => (
                  <option key={spec.value} value={spec.value}>
                    {spec.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Archivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Archivo PDF
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              {selectedFile && (
                <p className="text-sm text-gray-600 mt-1">
                  Archivo seleccionado: {selectedFile.name}
                </p>
              )}
            </div>

            {/* Info adicional */}
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm text-blue-800">
                📚 El PDF será procesado y dividido en fragmentos para mejorar la generación de planes de estudio.
              </p>
            </div>

            {/* Botones */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 btn-medical-primary disabled:opacity-50"
              >
                {isLoading ? 'Subiendo...' : 'Subir PDF'}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

const PlansListSkeleton = () => (
  <div className="space-y-8">
    <div className="flex justify-between items-center">
      <div>
        <div className="skeleton-title mb-2" />
        <div className="skeleton-text w-64" />
      </div>
      <div className="skeleton w-24 h-10" />
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton h-16" />
        </div>
      ))}
    </div>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton-title mb-4" />
          <div className="skeleton h-24 mb-4" />
          <div className="skeleton-text" />
        </div>
      ))}
    </div>
  </div>
);

export default Plans;
