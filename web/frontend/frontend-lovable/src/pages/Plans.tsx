
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Search, Upload, BookOpen, Sparkles } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import CreatePlanDialog from "@/components/CreatePlanDialog";
import PlanCard from "@/components/PlanCard";
import StatCard from "@/components/StatCard";

const Plans = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSpecialty, setSelectedSpecialty] = useState("all");
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const plans = [
    {
      title: "Reumatología Avanzada",
      description: "Casos clínicos complejos y nuevos tratamientos",
      progress: 75,
      specialty: "Reumatología",
      studyTime: "3h 45min"
    },
    {
      title: "Cardiología Preventiva",
      description: "Factores de riesgo y estrategias preventivas",
      progress: 45,
      specialty: "Cardiología",
      studyTime: "2h 20min"
    },
    {
      title: "Neurología Clínica",
      description: "Diagnóstico diferencial en patologías neurológicas",
      progress: 60,
      specialty: "Neurología",
      studyTime: "4h 10min"
    },
    {
      title: "Endocrinología Práctica",
      description: "Manejo integral de diabetes y tiroides",
      progress: 30,
      specialty: "Endocrinología",
      studyTime: "2h 55min"
    }
  ];

  const specialties = [
    "Todos",
    "Cardiología",
    "Neurología", 
    "Reumatología",
    "Endocrinología",
    "Neumología",
    "Gastroenterología"
  ];

  const filteredPlans = plans.filter(plan => {
    const matchesSearch = plan.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plan.specialty.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSpecialty = selectedSpecialty === "all" || 
                            plan.specialty.toLowerCase() === selectedSpecialty.toLowerCase();
    return matchesSearch && matchesSpecialty;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-study-bg via-white to-medical-blue-50/30">
      <div className="p-8 max-w-7xl mx-auto">
        {/* Modern Header with gradient */}
        <div className="relative overflow-hidden bg-gradient-to-r from-medical-blue-800 via-medical-blue-700 to-medical-turquoise-600 rounded-2xl p-8 mb-8 shadow-lg">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
                  📋 Planes de Estudio
                  <Sparkles className="w-6 h-6 ml-3 text-medical-turquoise-300" />
                </h1>
                <p className="text-medical-blue-100 text-lg">
                  Organiza tu aprendizaje médico con planes personalizados
                </p>
              </div>
              <div className="flex space-x-3">
                <Button 
                  variant="outline"
                  className="bg-white/10 border-white/20 text-white hover:bg-white/20 backdrop-blur-sm"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Importar PDFs
                </Button>
                <Button 
                  onClick={() => setShowCreateDialog(true)}
                  className="bg-white text-medical-blue-800 hover:bg-medical-blue-50 shadow-lg"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Crear Nuevo Plan
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Modern Search and Filter Card */}
        <Card className="mb-8 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
          <CardContent className="p-8">
            <div className="flex flex-col sm:flex-row gap-6">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    placeholder="Buscar planes por título o especialidad..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-12 h-12 text-lg border-gray-200 focus:border-medical-turquoise-500 focus:ring-medical-turquoise-500/20"
                  />
                </div>
              </div>
              
              <div className="sm:w-64">
                <Select value={selectedSpecialty} onValueChange={setSelectedSpecialty}>
                  <SelectTrigger className="h-12 text-lg border-gray-200 focus:border-medical-turquoise-500">
                    <SelectValue placeholder="Especialidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las especialidades</SelectItem>
                    {specialties.slice(1).map((specialty) => (
                      <SelectItem key={specialty} value={specialty.toLowerCase()}>
                        {specialty}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
          <div className="transform hover:scale-105 transition-transform duration-200">
            <StatCard
              title="Planes Totales"
              value={plans.length.toString()}
              icon={BookOpen}
              color="blue"
            />
          </div>
          <div className="transform hover:scale-105 transition-transform duration-200">
            <StatCard
              title="Completados"
              value={plans.filter(p => p.progress > 80).length.toString()}
              icon={BookOpen}
              color="green"
            />
          </div>
          <div className="transform hover:scale-105 transition-transform duration-200">
            <StatCard
              title="En Progreso"
              value={plans.filter(p => p.progress > 0 && p.progress <= 80).length.toString()}
              icon={BookOpen}
              color="turquoise"
            />
          </div>
          <div className="transform hover:scale-105 transition-transform duration-200">
            <StatCard
              title="Progreso Promedio"
              value={`${Math.round(plans.reduce((acc, p) => acc + p.progress, 0) / plans.length)}%`}
              icon={BookOpen}
              color="blue"
            />
          </div>
        </div>

        {/* Modern Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredPlans.map((plan, index) => (
            <div 
              key={index} 
              className="transform hover:scale-105 transition-all duration-300 hover:shadow-xl"
            >
              <PlanCard
                title={plan.title}
                description={plan.description}
                progress={plan.progress}
                specialty={plan.specialty}
                studyTime={plan.studyTime}
              />
            </div>
          ))}
        </div>

        {/* Enhanced No results message */}
        {filteredPlans.length === 0 && (
          <Card className="shadow-xl border-0 bg-gradient-to-br from-white to-gray-50">
            <CardContent className="p-16 text-center">
              <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-medical-blue-100 to-medical-turquoise-100 rounded-full flex items-center justify-center">
                <BookOpen className="w-12 h-12 text-medical-blue-600" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-800 mb-3">No se encontraron planes</h3>
              <p className="text-gray-600 mb-8 text-lg max-w-md mx-auto">
                No hay planes que coincidan con tu búsqueda. Intenta con otros términos o crea un nuevo plan.
              </p>
              <Button 
                onClick={() => setShowCreateDialog(true)}
                className="bg-gradient-to-r from-medical-blue-700 to-medical-blue-800 hover:from-medical-blue-800 hover:to-medical-blue-900 text-white px-8 py-3 text-lg shadow-lg"
              >
                <Plus className="w-5 h-5 mr-2" />
                Crear Primer Plan
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Create Plan Dialog */}
        <CreatePlanDialog 
          open={showCreateDialog}
          onOpenChange={setShowCreateDialog}
        />
      </div>
    </div>
  );
};

export default Plans;
