import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Plus, 
  Search, 
  BookOpen, 
  Clock, 
  User,
  Target,
  Calendar,
  TrendingUp,
  Play,
  Trash2,
  Edit
} from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import CreateStudyPlanDialog from "@/components/CreateStudyPlanDialog";
import StatCard from "@/components/StatCard";

interface StudyPlan {
  id: string;
  title: string;
  specialty: string;
  level: string;
  duration: number;
  sessionsPerDay: number;
  totalSessions: number;
  completedSessions: number;
  progress: number;
  description?: string;
  createdAt: string;
  estimatedHours: number;
  currentDay: number;
  status: 'active' | 'completed' | 'paused';
}

const Plans = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSpecialty, setSelectedSpecialty] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  // Cargar planes desde localStorage o usar datos de ejemplo
  const [plans, setPlans] = useState<StudyPlan[]>(() => {
    try {
      const savedPlans = localStorage.getItem('allPlans');
      if (savedPlans) {
        return JSON.parse(savedPlans);
      }
    } catch (error) {
      console.error('Error loading plans from localStorage:', error);
    }
    
    // Datos de ejemplo por defecto
    return [
      {
        id: "example-1",
        title: "Artritis Reumatoide - Manejo Integral",
        specialty: "Reumatología",
        level: "becado",
        duration: 30,
        sessionsPerDay: 2,
        totalSessions: 60,
        completedSessions: 45,
        progress: 75,
        description: "Estudio comprehensivo desde patogenia hasta tratamientos biológicos",
        createdAt: "2024-06-01",
        estimatedHours: 45,
        currentDay: 23,
        status: 'active'
      },
      {
        id: "example-2", 
        title: "Insuficiencia Cardíaca - Casos Complejos",
        specialty: "Cardiología",
        level: "especialista",
        duration: 45,
        sessionsPerDay: 1,
        totalSessions: 45,
        completedSessions: 20,
        progress: 44,
        description: "Manejo avanzado de IC con fracción de eyección preservada y reducida",
        createdAt: "2024-05-15",
        estimatedHours: 34,
        currentDay: 20,
        status: 'active'
      }
    ];
  });

  const specialties = [
    "Todos",
    "Medicina Interna",
    "Cardiología",
    "Neurología", 
    "Gastroenterología",
    "Endocrinología",
    "Reumatología",
    "Neumología",
    "Nefrología"
  ];

  const filteredPlans = plans.filter(plan => {
    const matchesSearch = plan.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plan.specialty.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSpecialty = selectedSpecialty === "all" || plan.specialty === selectedSpecialty;
    const matchesStatus = selectedStatus === "all" || plan.status === selectedStatus;
    
    return matchesSearch && matchesSpecialty && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'paused': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'interno': return 'bg-emerald-100 text-emerald-800';
      case 'becado': return 'bg-blue-100 text-blue-800';
      case 'especialista': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLevelLabel = (level: string) => {
    switch (level) {
      case 'interno': return 'Interno';
      case 'becado': return 'Becado';
      case 'especialista': return 'Especialista';
      default: return level;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Activo';
      case 'completed': return 'Completado';
      case 'paused': return 'Pausado';
      default: return status;
    }
  };

  const handleCreatePlan = (planData: any) => {
    console.log("🎯 Creando plan con datos:", planData);
    
    const newPlan: StudyPlan = {
      id: Date.now().toString(), // Usar timestamp para ID único
      title: `${planData.mainTopic} - ${planData.specialty}`,
      specialty: planData.specialty,
      level: planData.level,
      duration: planData.duration,
      sessionsPerDay: planData.sessionsPerDay,
      totalSessions: planData.duration * planData.sessionsPerDay,
      completedSessions: 0,
      progress: 0,
      description: planData.description || `Plan de estudio de ${planData.mainTopic}`,
      createdAt: new Date().toISOString().split('T')[0],
      estimatedHours: Math.round(planData.duration * planData.sessionsPerDay * 0.75),
      currentDay: 1,
      status: 'active'
    };

    console.log("📋 Plan creado:", newPlan);

    try {
      // Guardar el plan individual
      localStorage.setItem(`plan_${newPlan.id}`, JSON.stringify({
        ...newPlan,
        originalData: planData
      }));
      console.log("💾 Plan guardado en localStorage");

      // Guardar la lista completa de planes
      const updatedPlans = [newPlan, ...plans];
      setPlans(updatedPlans);
      localStorage.setItem('allPlans', JSON.stringify(updatedPlans));
      console.log("📝 Lista de planes actualizada:", updatedPlans.length);
      
      // Mostrar alerta de éxito
      alert(`✅ Plan "${newPlan.title}" creado exitosamente!`);
      
    } catch (error) {
      console.error("❌ Error creando plan:", error);
      alert("Error al crear el plan. Intenta de nuevo.");
    }
  };

  const handleOpenPlan = (planId: string) => {
    navigate(`/plan/${planId}`);
  };

  // Estadísticas
  const totalPlans = plans.length;
  const activePlans = plans.filter(p => p.status === 'active').length;
  const completedPlans = plans.filter(p => p.status === 'completed').length;
  const totalStudyHours = plans.reduce((sum, plan) => sum + (plan.completedSessions * 0.75), 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Planes de Estudio</h1>
          <p className="text-gray-600">Gestiona tus planes de estudio personalizados con IA</p>
        </div>
        <Button 
          onClick={() => setShowCreateDialog(true)}
          className="bg-medical-blue-600 hover:bg-medical-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Plan de Estudio
        </Button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total de Planes"
          value={totalPlans.toString()}
          icon={BookOpen}
          color="blue"
        />
        <StatCard
          title="Planes Activos"
          value={activePlans.toString()}
          icon={Play}
          color="green"
        />
        <StatCard
          title="Completados"
          value={completedPlans.toString()}
          icon={Target}
          color="turquoise"
        />
        <StatCard
          title="Horas Estudiadas"
          value={`${Math.round(totalStudyHours)}h`}
          icon={Clock}
          color="purple"
        />
      </div>

      {/* Filtros */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar planes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
            
            <Select value={selectedSpecialty} onValueChange={setSelectedSpecialty}>
              <SelectTrigger>
                <SelectValue placeholder="Especialidad" />
              </SelectTrigger>
              <SelectContent>
                {specialties.map((specialty) => (
                  <SelectItem key={specialty} value={specialty === "Todos" ? "all" : specialty}>
                    {specialty}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="active">Activos</SelectItem>
                <SelectItem value="completed">Completados</SelectItem>
                <SelectItem value="paused">Pausados</SelectItem>
              </SelectContent>
            </Select>

            <div className="text-sm text-gray-600 flex items-center">
              {filteredPlans.length} de {totalPlans} planes
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Planes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredPlans.map((plan) => (
          <Card key={plan.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-lg mb-2">{plan.title}</CardTitle>
                  <div className="flex flex-wrap gap-2 mb-2">
                    <Badge variant="secondary">{plan.specialty}</Badge>
                    <Badge className={getLevelColor(plan.level)}>
                      {getLevelLabel(plan.level)}
                    </Badge>
                    <Badge className={getStatusColor(plan.status)}>
                      {getStatusLabel(plan.status)}
                    </Badge>
                  </div>
                </div>
              </div>
              
              {plan.description && (
                <p className="text-sm text-gray-600 mt-2">{plan.description}</p>
              )}
            </CardHeader>

            <CardContent className="pt-0">
              <div className="space-y-4">
                {/* Progreso */}
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Progreso</span>
                    <span>{plan.completedSessions}/{plan.totalSessions} sesiones</span>
                  </div>
                  <Progress value={plan.progress} className="h-2" />
                </div>

                {/* Información del plan */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span>{plan.duration} días</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span>{plan.sessionsPerDay}/día</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Target className="w-4 h-4 text-gray-400" />
                    <span>Día {plan.currentDay}/{plan.duration}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-gray-400" />
                    <span>{plan.estimatedHours}h estimadas</span>
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="flex space-x-2 pt-2">
                  <Button 
                    onClick={() => handleOpenPlan(plan.id)}
                    className="flex-1 bg-medical-blue-600 hover:bg-medical-blue-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    {plan.progress === 0 ? 'Comenzar' : 'Continuar'}
                  </Button>
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Estado vacío */}
      {filteredPlans.length === 0 && (
        <Card className="text-center py-12">
          <CardContent>
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No se encontraron planes
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || selectedSpecialty !== "all" || selectedStatus !== "all" 
                ? "Intenta ajustar los filtros de búsqueda"
                : "Crea tu primer plan de estudio personalizado"
              }
            </p>
            {(!searchTerm && selectedSpecialty === "all" && selectedStatus === "all") && (
              <Button 
                onClick={() => setShowCreateDialog(true)}
                className="bg-medical-blue-600 hover:bg-medical-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Crear Primer Plan
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Diálogo de creación */}
      <CreateStudyPlanDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onCreatePlan={handleCreatePlan}
      />
    </div>
  );
};

export default Plans;