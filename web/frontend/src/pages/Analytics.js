import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { TrendingUp, Calendar, Clock, Target } from 'lucide-react';
import axios from 'axios';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('month');
  
  const { data: confidenceTrends } = useQuery('confidence-trends',
    () => axios.get('/api/analytics/confidence-trends').then(res => res.data)
  );
  
  const { data: specialtyDistribution } = useQuery('specialty-distribution',
    () => axios.get('/api/analytics/specialty-distribution').then(res => res.data)
  );

  // Datos simulados para gráficos adicionales
  const studyTimeData = [
    { day: 'Lun', hours: 3.2, sessions: 4 },
    { day: 'Mar', hours: 4.1, sessions: 5 },
    { day: 'Mié', hours: 2.8, sessions: 3 },
    { day: 'Jue', hours: 4.5, sessions: 6 },
    { day: 'Vie', hours: 3.0, sessions: 4 },
    { day: 'Sáb', hours: 1.8, sessions: 2 },
    { day: 'Dom', hours: 3.5, sessions: 4 }
  ];

  const confidenceColors = ['#EF4444', '#F97316', '#EAB308', '#22C55E', '#3B82F6'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Análisis detallado de tu progreso en estudios médicos</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="week">Última semana</option>
          <option value="month">Último mes</option>
          <option value="quarter">Últimos 3 meses</option>
          <option value="year">Último año</option>
        </select>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <AnalyticsCard
          icon={Clock}
          title="Tiempo Total"
          value="127.5h"
          change="+12%"
          trend="up"
          color="blue"
        />
        <AnalyticsCard
          icon={Target}
          title="Eficiencia"
          value="87.3%"
          change="+5%"
          trend="up"
          color="green"
        />
        <AnalyticsCard
          icon={Calendar}
          title="Sesiones"
          value="48"
          change="+8"
          trend="up"
          color="purple"
        />
        <AnalyticsCard
          icon={TrendingUp}
          title="Mejora Promedio"
          value="+2.1"
          change="niveles/tema"
          trend="up"
          color="orange"
        />
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tiempo de estudio semanal */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📊 Tiempo de Estudio Semanal
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={studyTimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="day" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#F9FAFB', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="hours" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Evolución de confianza */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📈 Evolución de Confianza
          </h3>
          {confidenceTrends && (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={confidenceTrends.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#F9FAFB', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px'
                  }}
                />
                <Line type="monotone" dataKey="red" stroke="#EF4444" strokeWidth={2} />
                <Line type="monotone" dataKey="orange" stroke="#F97316" strokeWidth={2} />
                <Line type="monotone" dataKey="yellow" stroke="#EAB308" strokeWidth={2} />
                <Line type="monotone" dataKey="green" stroke="#22C55E" strokeWidth={2} />
                <Line type="monotone" dataKey="blue" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </motion.div>
      </div>

      {/* Distribución por especialidad */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📚 Distribución por Especialidad
          </h3>
          {specialtyDistribution && (
            <div className="space-y-4">
              {Object.entries(specialtyDistribution).map(([specialty, data]) => (
                <div key={specialty} className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-900 capitalize">
                      {specialty.replace('_', ' ')}
                    </p>
                    <p className="text-sm text-gray-500">{data.topics} temas</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-600">{data.hours}h</p>
                    <p className="text-xs text-gray-500">
                      {Math.round((data.hours / 20) * 100)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Estadísticas de rendimiento */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎯 Rendimiento
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Sesiones completadas</span>
              <span className="font-bold text-green-600">94%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Tiempo promedio/sesión</span>
              <span className="font-bold text-blue-600">42min</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Mejora de confianza</span>
              <span className="font-bold text-purple-600">+1.8</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Retención estimada</span>
              <span className="font-bold text-orange-600">89%</span>
            </div>
          </div>
        </motion.div>

        {/* Metas y objetivos */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎖️ Metas del Mes
          </h3>
          <div className="space-y-4">
            <GoalProgress
              title="Horas de estudio"
              current={87}
              target={120}
              unit="h"
            />
            <GoalProgress
              title="Temas completados"
              current={23}
              target={30}
              unit="temas"
            />
            <GoalProgress
              title="Confianza promedio"
              current={3.2}
              target={4.0}
              unit="nivel"
            />
          </div>
        </motion.div>
      </div>

      {/* Insights y recomendaciones */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="medical-card p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          💡 Insights y Recomendaciones
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <InsightCard
            type="success"
            title="Excelente consistencia"
            description="Has mantenido una racha de 12 días estudiando. ¡Sigue así!"
          />
          <InsightCard
            type="warning"
            title="Enfócate en Cardiología"
            description="Tienes 8 temas rojos en esta especialidad. Considera dedicar más tiempo."
          />
          <InsightCard
            type="info"
            title="Patrón optimal"
            description="Tus mejores sesiones son entre 2-4 PM. Programa estudios importantes en ese horario."
          />
        </div>
      </motion.div>
    </div>
  );
};

// Componentes auxiliares
const AnalyticsCard = ({ icon: Icon, title, value, change, trend, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    orange: 'text-orange-600 bg-orange-50'
  };

  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';

  return (
    <div className="medical-card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className={`text-sm ${trendColor}`}>
            {trend === 'up' ? '↗️' : '↘️'} {change}
          </p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
};

const GoalProgress = ({ title, current, target, unit }) => {
  const percentage = Math.min((current / target) * 100, 100);
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{title}</span>
        <span className="font-medium">{current}/{target} {unit}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">{Math.round(percentage)}% completado</p>
    </div>
  );
};

const InsightCard = ({ type, title, description }) => {
  const typeStyles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-orange-50 border-orange-200 text-orange-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const icons = {
    success: '✅',
    warning: '⚠️',
    info: 'ℹ️'
  };

  return (
    <div className={`p-4 rounded-lg border ${typeStyles[type]}`}>
      <div className="flex items-start">
        <span className="text-lg mr-2">{icons[type]}</span>
        <div>
          <h4 className="font-medium mb-1">{title}</h4>
          <p className="text-sm opacity-90">{description}</p>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
