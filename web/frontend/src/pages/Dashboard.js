import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Clock, 
  Target, 
  BookOpen,
  Calendar,
  Brain,
  Award
} from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  // Obtener datos del dashboard
  const { data: stats, isLoading } = useQuery('dashboard-stats', 
    () => axios.get('/api/dashboard').then(res => res.data)
  );

  const { data: dueTopics } = useQuery('due-topics',
    () => axios.get('/api/topics/due').then(res => res.data)
  );

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  const confidenceColors = {
    red: 'bg-red-500',
    orange: 'bg-orange-500', 
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500'
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Vista general de tu progreso en estudios médicos</p>
        </div>
        <div className="text-sm text-gray-500">
          📅 {new Date().toLocaleDateString('es-ES', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Planes Activos"
          value={stats?.active_plans || 0}
          subtitle="+1 esta semana"
          icon={Calendar}
          color="blue"
          trend="up"
        />
        <MetricCard
          title="Total Temas"
          value={stats?.total_topics || 0}
          subtitle="+8 este mes"
          icon={BookOpen}
          color="green"
          trend="up"
        />
        <MetricCard
          title="Horas Estudio"
          value={`${stats?.study_hours || 0}h`}
          subtitle="3.2h promedio/día"
          icon={Clock}
          color="orange"
          trend="neutral"
        />
        <MetricCard
          title="Eficiencia"
          value={`${stats?.efficiency_percentage || 0}%`}
          subtitle="+5% vs mes anterior"
          icon={Target}
          color="purple"
          trend="up"
        />
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribución de confianza */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎯 Distribución de Confianza
          </h3>
          <div className="space-y-4">
            {stats?.confidence_distribution && Object.entries(stats.confidence_distribution).map(([level, count]) => (
              <div key={level} className="flex items-center">
                <div className="flex items-center w-32">
                  <div className={`w-3 h-3 rounded-full ${confidenceColors[level]} mr-2`} />
                  <span className="text-sm capitalize">{level}</span>
                </div>
                <div className="flex-1 mx-4">
                  <div className="progress-bar-bg">
                    <div 
                      className={`progress-bar-fill ${confidenceColors[level]}`}
                      style={{ width: `${(count / stats.total_topics) * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm font-medium w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Progreso semanal */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="medical-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📈 Progreso Esta Semana
          </h3>
          <div className="flex justify-between items-end h-32">
            {stats?.weekly_progress?.map((day, index) => (
              <div key={day.day} className="flex flex-col items-center">
                <div 
                  className="w-8 bg-primary-500 rounded-t"
                  style={{ height: `${day.progress}%` }}
                />
                <span className="text-xs text-gray-500 mt-2">{day.day}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 text-sm text-gray-600 text-center">
            Promedio: 25.5h esta semana • Meta: 30h
          </div>
        </motion.div>
      </div>

      {/* Temas pendientes */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="medical-card p-6"
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            🎯 Temas Pendientes para Hoy ({stats?.pending_today || 0})
          </h3>
          <button className="btn-medical-primary text-sm">
            Ver Todos →
          </button>
        </div>
        
        <div className="space-y-3">
          {dueTopics?.slice(0, 5).map((topic) => (
            <PendingTopicCard key={topic.id} topic={topic} />
          ))}
          
          {!dueTopics?.length && (
            <div className="text-center py-8 text-gray-500">
              🎉 ¡No hay temas pendientes para hoy! Excelente trabajo.
            </div>
          )}
        </div>
      </motion.div>

      {/* Estadísticas adicionales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={Brain}
          title="Racha de Estudio"
          value={`${stats?.streak_days || 0} días`}
          description="¡Sigue así!"
          color="green"
        />
        <StatCard
          icon={Award}
          title="Nivel de Confianza"
          value="Intermedio"
          description="68% de temas en verde/azul"
          color="blue"
        />
        <StatCard
          icon={TrendingUp}
          title="Tendencia"
          value="+12%"
          description="Mejora vs mes anterior"
          color="purple"
        />
      </div>
    </div>
  );
};

// Componentes auxiliares
const MetricCard = ({ title, value, subtitle, icon: Icon, color, trend }) => {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    purple: 'text-purple-600'
  };

  const trendIcons = {
    up: '↗️',
    down: '↘️', 
    neutral: '➡️'
  };

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      className="medical-card-hover p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</p>
          <p className="text-xs text-gray-500">
            {trendIcons[trend]} {subtitle}
          </p>
        </div>
        <div className={`p-3 rounded-lg bg-${color}-50`}>
          <Icon className={`h-6 w-6 ${colorClasses[color]}`} />
        </div>
      </div>
    </motion.div>
  );
};

const PendingTopicCard = ({ topic }) => {
  const confidenceStyles = {
    red: 'bg-red-50 text-red-700 border-red-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200'
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="flex items-center space-x-4">
        <div className={`px-2 py-1 rounded text-xs font-medium border ${confidenceStyles[topic.confidence_level]}`}>
          {topic.confidence_level}
        </div>
        <div>
          <h4 className="font-medium text-gray-900">{topic.name}</h4>
          <p className="text-sm text-gray-500">📚 {topic.specialty}</p>
        </div>
      </div>
      <button className="btn-medical-primary text-sm">
        Estudiar
      </button>
    </div>
  );
};

const StatCard = ({ icon: Icon, title, value, description, color }) => {
  const colorClasses = {
    green: 'text-green-600 bg-green-50',
    blue: 'text-blue-600 bg-blue-50',
    purple: 'text-purple-600 bg-purple-50'
  };

  return (
    <div className="medical-card p-6 text-center">
      <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} mb-4`}>
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className="text-xl font-bold text-gray-900 my-1">{value}</p>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
  );
};

const DashboardSkeleton = () => (
  <div className="space-y-8">
    <div className="flex justify-between items-center">
      <div>
        <div className="skeleton-title mb-2" />
        <div className="skeleton-text w-64" />
      </div>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton-text mb-2" />
          <div className="skeleton-title mb-1" />
          <div className="skeleton-text w-20" />
        </div>
      ))}
    </div>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {[...Array(2)].map((_, i) => (
        <div key={i} className="medical-card p-6">
          <div className="skeleton-title mb-4" />
          <div className="skeleton h-32" />
        </div>
      ))}
    </div>
  </div>
);

export default Dashboard;
