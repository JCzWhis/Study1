
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { 
  Brain,
  Clock, 
  BookOpen, 
  TrendingUp,
  Flame,
  Plus,
  Upload,
  BarChart3,
  Settings
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import StatCard from "@/components/StatCard";
import StudyPlanCard from "@/components/StudyPlanCard";
import QuickActionButton from "@/components/QuickActionButton";
import { apiService } from "@/services/api";

const Dashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [analytics, setAnalytics] = useState({
    totalStudyTime: 127,
    activePlans: 5,
    averageConfidence: 8.2,
    currentStreak: 12
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const data = await apiService.getAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error('Error loading analytics:', error);
        // Keep default demo data on error
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return "¡Bienvenido de vuelta, Dr.!";
    if (hour < 18) return "¡Buenas tardes, Dr.!";
    return "¡Buenas noches, Dr.!";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-800 to-blue-600 rounded-xl p-8 text-white mb-8">
        <h2 className="text-3xl font-bold mb-2 text-white">{getGreeting()}</h2>
        <p className="text-blue-100 mb-6">Continúa tu aprendizaje médico basado en evidencia</p>
        <div className="flex space-x-4">
          <Button 
            onClick={() => navigate('/estudio')}
            className="bg-white text-blue-800 px-6 py-3 hover:bg-blue-50 font-semibold"
          >
            🚀 Iniciar Estudio
          </Button>
          <Button 
            onClick={() => navigate('/plans')}
            variant="outline"
            className="border-white text-white px-6 py-3 hover:bg-white hover:text-blue-800"
          >
            📋 Crear Plan
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Tiempo Total"
          value={isLoading ? "..." : `${analytics.totalStudyTime} hrs`}
          icon={Clock}
          color="blue"
        />
        <StatCard
          title="Planes Activos"
          value={isLoading ? "..." : analytics.activePlans.toString()}
          icon={BookOpen}
          color="green"
        />
        <StatCard
          title="Confianza Promedio"
          value={isLoading ? "..." : `${analytics.averageConfidence}/10`}
          icon={TrendingUp}
          color="turquoise"
        />
        <StatCard
          title="Streak Actual"
          value={isLoading ? "..." : `${analytics.currentStreak} días`}
          icon={Flame}
          color="purple"
        />
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <h3 className="text-xl font-semibold mb-4">📚 Planes de Estudio Recientes</h3>
          <div className="space-y-4">
            <StudyPlanCard
              title="Artritis Reumatoide - Actualización 2024"
              progress={65}
              timeLeft="2h 30min"
              specialty="Reumatología"
            />
            <StudyPlanCard
              title="Cardiología Intervencionista"
              progress={40}
              timeLeft="4h 15min"
              specialty="Cardiología"
            />
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold mb-4">⚡ Acciones Rápidas</h3>
          <div className="space-y-3">
            <QuickActionButton 
              icon={Plus} 
              text="Crear Plan con IA" 
              onClick={() => navigate('/planes')}
            />
            <QuickActionButton 
              icon={Upload} 
              text="Subir Material PDF" 
            />
            <QuickActionButton 
              icon={BarChart3} 
              text="Ver Analíticas" 
              onClick={() => navigate('/analiticas')}
            />
            <QuickActionButton 
              icon={Settings} 
              text="Configuración" 
              onClick={() => navigate('/configuracion')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
