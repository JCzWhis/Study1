
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Clock, 
  BookOpen, 
  Calendar, 
  Timer,
  TrendingUp,
  Award
} from "lucide-react";

const Analytics = () => {
  // Datos de ejemplo para las analíticas
  const weeklyData = [
    { day: "Lun", minutes: 120, sessions: 3 },
    { day: "Mar", minutes: 90, sessions: 2 },
    { day: "Mié", minutes: 150, sessions: 4 },
    { day: "Jue", minutes: 180, sessions: 3 },
    { day: "Vie", minutes: 60, sessions: 1 },
    { day: "Sáb", minutes: 200, sessions: 4 },
    { day: "Dom", minutes: 85, sessions: 2 }
  ];

  const topicProgress = [
    { topic: "Artritis Reumatoide", specialty: "Reumatología", confidence: 85, sessions: 12, progress: 90 },
    { topic: "Insuficiencia Cardíaca", specialty: "Cardiología", confidence: 70, sessions: 8, progress: 75 },
    { topic: "Diabetes Mellitus", specialty: "Endocrinología", confidence: 95, sessions: 15, progress: 95 },
    { topic: "Neumonía", specialty: "Neumología", confidence: 80, sessions: 10, progress: 85 },
    { topic: "ACV Isquémico", specialty: "Neurología", confidence: 60, sessions: 5, progress: 45 }
  ];

  const monthlyStats = {
    totalMinutes: 2850,
    totalSessions: 68,
    avgSessionLength: 42,
    streak: 12,
    completedPlans: 8,
    efficiency: 87
  };

  const upcomingReviews = [
    { topic: "Artritis Reumatoide", due: "En 2 horas", priority: "high" },
    { topic: "Diabetes Mellitus", due: "Mañana", priority: "medium" },
    { topic: "Neumonía", due: "En 3 días", priority: "low" },
    { topic: "Insuficiencia Cardíaca", due: "En 5 días", priority: "low" }
  ];

  const maxMinutes = Math.max(...weeklyData.map(d => d.minutes));

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-red-100 text-red-800 border-red-200";
      case "medium": return "bg-blue-100 text-blue-800 border-blue-200";
      case "low": return "bg-blue-100 text-blue-800 border-blue-200";
      default: return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-emerald-600";
    if (confidence >= 75) return "text-green-600";
    if (confidence >= 60) return "text-blue-600";
    if (confidence >= 45) return "text-gray-600";
    return "text-red-600";
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-study-text mb-2">📈 Analíticas de Estudio</h1>
        <p className="text-gray-600">
          Analiza tu progreso y optimiza tu aprendizaje médico
        </p>
      </div>

      {/* Estadísticas generales */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <Card className="bg-white study-shadow">
          <CardContent className="p-4 text-center">
            <Clock className="w-6 h-6 text-medical-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-medical-blue-800">
              {Math.round(monthlyStats.totalMinutes / 60)}h
            </div>
            <div className="text-xs text-gray-600">Tiempo Total</div>
          </CardContent>
        </Card>

        <Card className="bg-white study-shadow">
          <CardContent className="p-4 text-center">
            <BookOpen className="w-6 h-6 text-medical-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-medical-green-700">
              {monthlyStats.totalSessions}
            </div>
            <div className="text-xs text-gray-600">Sesiones</div>
          </CardContent>
        </Card>

        <Card className="bg-white study-shadow">
          <CardContent className="p-4 text-center">
            <Timer className="w-6 h-6 text-medical-turquoise-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-medical-turquoise-700">
              {monthlyStats.avgSessionLength}min
            </div>
            <div className="text-xs text-gray-600">Promedio</div>
          </CardContent>
        </Card>

        <Card className="bg-white study-shadow">
          <CardContent className="p-4 text-center">
            <Calendar className="w-6 h-6 text-medical-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-medical-blue-700">
              {monthlyStats.streak}
            </div>
            <div className="text-xs text-gray-600">Días Racha</div>
          </CardContent>
        </Card>

        <Card className="bg-white study-shadow">
          <CardContent className="p-4 text-center">
            <Award className="w-6 h-6 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-700">
              {monthlyStats.completedPlans}
            </div>
            <div className="text-xs text-gray-600">Completados</div>
          </CardContent>
        </Card>

        <Card className="bg-white study-shadow">
          <CardContent className="p-4 text-center">
            <TrendingUp className="w-6 h-6 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-700">
              {monthlyStats.efficiency}%
            </div>
            <div className="text-xs text-gray-600">Eficiencia</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Actividad semanal */}
        <div className="lg:col-span-2 space-y-8">
          <Card className="bg-white study-shadow">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="w-5 h-5 text-medical-blue-600" />
                <span>Actividad de la Semana</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weeklyData.map((day, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium w-12">{day.day}</span>
                      <span className="text-gray-600">{day.minutes} min</span>
                      <span className="text-gray-500">{day.sessions} sesiones</span>
                    </div>
                    <div className="relative">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-medical-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(day.minutes / maxMinutes) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Progreso por tema */}
          <Card className="bg-white study-shadow">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-medical-green-600" />
                <span>Progreso por Tema</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {topicProgress.map((topic, index) => (
                  <div key={index} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold text-study-text">{topic.topic}</h4>
                        <p className="text-sm text-gray-600">{topic.specialty} • {topic.sessions} sesiones</p>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${getConfidenceColor(topic.confidence)}`}>
                          {topic.confidence}%
                        </div>
                        <div className="text-xs text-gray-500">Confianza</div>
                      </div>
                    </div>
                    <Progress value={topic.progress} className="h-2" />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Progreso: {topic.progress}%</span>
                      <span>
                        {topic.progress >= 90 ? "🏆 Dominado" : 
                         topic.progress >= 75 ? "🎯 Avanzado" :
                         topic.progress >= 50 ? "📚 En progreso" : "🔄 Iniciando"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Panel lateral */}
        <div className="space-y-6">
          {/* Próximas revisiones */}
          <Card className="bg-white study-shadow">
            <CardHeader>
              <CardTitle className="text-lg flex items-center space-x-2">
                <Timer className="w-5 h-5 text-medical-turquoise-600" />
                <span>Próximas Revisiones</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {upcomingReviews.map((review, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm text-study-text">{review.topic}</p>
                    <p className="text-xs text-gray-600">{review.due}</p>
                  </div>
                  <Badge className={getPriorityColor(review.priority)}>
                    {review.priority === "high" ? "Alta" : 
                     review.priority === "medium" ? "Media" : "Baja"}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Métricas de rendimiento */}
          <Card className="bg-gradient-to-br from-medical-blue-50 to-medical-turquoise-50 border-medical-blue-200">
            <CardHeader>
              <CardTitle className="text-lg text-medical-blue-800">
                🎯 Métricas de Rendimiento
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Consistencia</span>
                  <span className="font-bold text-medical-blue-800">92%</span>
                </div>
                <Progress value={92} className="h-2" />
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Retención</span>
                  <span className="font-bold text-medical-green-700">87%</span>
                </div>
                <Progress value={87} className="h-2" />
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Velocidad</span>
                  <span className="font-bold text-medical-turquoise-700">78%</span>
                </div>
                <Progress value={78} className="h-2" />
              </div>
            </CardContent>
          </Card>

          {/* Logros recientes */}
          <Card className="bg-white study-shadow">
            <CardHeader>
              <CardTitle className="text-lg flex items-center space-x-2">
                <Award className="w-5 h-5 text-medical-blue-600" />
                <span>Logros Recientes</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center space-x-3 p-2 bg-blue-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  🏆
                </div>
                <div>
                  <p className="text-sm font-medium">Racha de 12 días</p>
                  <p className="text-xs text-gray-600">¡Excelente consistencia!</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-2 bg-green-50 rounded-lg">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  🎯
                </div>
                <div>
                  <p className="text-sm font-medium">Plan completado</p>
                  <p className="text-xs text-gray-600">Diabetes Mellitus</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-2 bg-blue-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  ⚡
                </div>
                <div>
                  <p className="text-sm font-medium">50 horas de estudio</p>
                  <p className="text-xs text-gray-600">Este mes</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
