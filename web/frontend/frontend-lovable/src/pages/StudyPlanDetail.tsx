import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ArrowLeft,
  Play,
  Clock,
  CheckCircle,
  Circle,
  Calendar,
  Target,
  BookOpen,
  Brain,
  FileText,
  TrendingUp,
  Settings,
  BarChart3
} from "lucide-react";

interface StudyTopic {
  id: string;
  title: string;
  description: string;
  day: number;
  session: number;
  estimatedMinutes: number;
  difficulty: 'facil' | 'medio' | 'dificil';
  completed: boolean;
  confidence?: number;
  subtopics: string[];
  keyPoints: string[];
  studiedAt?: string;
}

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
  currentDay: number;
  status: 'active' | 'completed' | 'paused';
  topics: StudyTopic[];
}

const StudyPlanDetail = () => {
  const { planId } = useParams<{ planId: string }>();
  const navigate = useNavigate();
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [selectedDay, setSelectedDay] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Cargar datos del plan desde localStorage o API
    const loadPlan = async () => {
      setLoading(true);
      
      try {
        // Intentar cargar desde localStorage primero (planes recién creados)
        const savedPlan = localStorage.getItem(`plan_${planId}`);
        let planData: StudyPlan;
        
        if (savedPlan) {
          const parsed = JSON.parse(savedPlan);
          planData = {
            ...parsed,
            topics: generateTopicsFromUserData(parsed.originalData || {})
          };
        } else {
          // Plan existente - usar datos mock
          planData = {
            id: planId!,
            title: "Artritis Reumatoide - Manejo Integral",
            specialty: "Reumatología", 
            level: "becado",
            duration: 30,
            sessionsPerDay: 2,
            totalSessions: 60,
            completedSessions: 18,
            progress: 30,
            description: "Estudio comprehensivo desde patogenia hasta tratamientos biológicos",
            createdAt: "2024-06-01",
            currentDay: 10,
            status: 'active',
            topics: generateMockTopics()
          };
        }

        setPlan(planData);
        setSelectedDay(planData.currentDay);
      } catch (error) {
        console.error("Error loading plan:", error);
      } finally {
        setLoading(false);
      }
    };

    loadPlan();
  }, [planId]);

  const generateTopicsFromUserData = (userData: any): StudyTopic[] => {
    const topics: StudyTopic[] = [];
    const {
      mainTopic = "Tema Médico",
      specialty = "Medicina General",
      level = "interno",
      duration = 30,
      sessionsPerDay = 2,
      subtopics = [],
      description = ""
    } = userData;

    // USAR EL TEMA PRINCIPAL DEL USUARIO COMO BASE
    console.log("🎯 Generando temas para TEMA PRINCIPAL:", mainTopic);
    console.log("📚 Con especialidad:", specialty);
    console.log("🔍 Subtemas del usuario:", subtopics);
    
    let topicsToUse = [...subtopics]; // Comenzar con subtemas del usuario
    
    // Si el usuario agregó pocos subtemas, complementar con temas basados en EL TEMA PRINCIPAL
    if (topicsToUse.length < 5) {
      const defaultTopics = generateDefaultSubtopicsForMainTopic(mainTopic, specialty);
      const additionalTopics = defaultTopics.filter(topic => !topicsToUse.includes(topic));
      topicsToUse = [...topicsToUse, ...additionalTopics];
    }
    
    console.log("📚 Temas a usar:", topicsToUse);
    
    // Agregar temas complementarios según el nivel
    if (level === "especialista") {
      topicsToUse = [...topicsToUse, "Casos Complejos", "Investigación Actual", "Manejo Avanzado"];
    } else if (level === "becado") {
      topicsToUse = [...topicsToUse, "Casos Clínicos", "Diagnóstico Diferencial", "Protocolos"];
    } else {
      topicsToUse = [...topicsToUse, "Fundamentos", "Conceptos Básicos", "Examen Físico"];
    }

    // Distribuir los temas a lo largo de la duración del plan
    const totalSessions = duration * sessionsPerDay;
    const topicsPerSession = Math.max(1, Math.ceil(topicsToUse.length / totalSessions));
    
    let topicIndex = 0;
    for (let day = 1; day <= duration; day++) {
      for (let session = 1; session <= sessionsPerDay; session++) {
        if (topicIndex >= topicsToUse.length) {
          // Si se acabaron los subtemas, reciclar con enfoque diferente
          const recycledTopic = topicsToUse[topicIndex % topicsToUse.length];
          const focusType = session === 1 ? "Teoría" : session === 2 ? "Casos Clínicos" : "Revisión";
          
          topics.push({
            id: `${day}-${session}`,
            title: `${recycledTopic} - ${focusType}`,
            description: `Estudio ${session === 1 ? 'teórico' : session === 2 ? 'práctico con casos' : 'de revisión'} de ${recycledTopic}`,
            day,
            session,
            estimatedMinutes: session === 1 ? 45 : 30,
            difficulty: getDifficultyForLevel(level, topicIndex),
            completed: false,
            subtopics: generateSubtopicsForTopic(recycledTopic, mainTopic),
            keyPoints: generateKeyPointsForTopic(recycledTopic, mainTopic),
          });
        } else {
          const currentTopic = topicsToUse[topicIndex];
          
          topics.push({
            id: `${day}-${session}`,
            title: `${mainTopic}: ${currentTopic}`,
            description: `${session === 1 ? 'Estudio teórico' : 'Aplicación práctica'} de ${currentTopic} en el contexto de ${mainTopic}`,
            day,
            session,
            estimatedMinutes: session === 1 ? 45 : 30,
            difficulty: getDifficultyForLevel(level, topicIndex),
            completed: false,
            subtopics: generateSubtopicsForTopic(currentTopic, mainTopic),
            keyPoints: generateKeyPointsForTopic(currentTopic, mainTopic),
          });
        }
        
        topicIndex++;
      }
    }

    return topics;
  };

  const generateDefaultSubtopicsForMainTopic = (mainTopic: string, specialty: string): string[] => {
    // Generar subtemas específicos basados en EL TEMA PRINCIPAL del usuario
    console.log("🔍 Generando subtemas para tema principal:", mainTopic);
    
    const topicLower = mainTopic.toLowerCase();
    
    // Casos específicos basados en el tema principal
    if (topicLower.includes("artritis")) {
      return ["Patogenia", "Criterios Diagnósticos", "DMARDs", "Biológicos", "Manifestaciones Extraarticulares"];
    } else if (topicLower.includes("diabetes")) {
      return ["Fisiopatología", "Diagnóstico", "Tratamiento Farmacológico", "Complicaciones", "Manejo Nutricional"];
    } else if (topicLower.includes("hipertensión") || topicLower.includes("hipertension")) {
      return ["Fisiopatología", "Clasificación", "Tratamiento No Farmacológico", "Antihipertensivos", "Complicaciones"];
    } else if (topicLower.includes("insuficiencia cardíaca") || topicLower.includes("insuficiencia cardiaca")) {
      return ["Fisiopatología", "Clasificación NYHA", "Diagnóstico", "Tratamiento Farmacológico", "Dispositivos"];
    } else if (topicLower.includes("asma")) {
      return ["Fisiopatología", "Clasificación", "Diagnóstico", "Tratamiento Escalonado", "Crisis Asmática"];
    } else if (topicLower.includes("epoc") || topicLower.includes("enfermedad pulmonar")) {
      return ["Fisiopatología", "Diagnóstico", "Tratamiento", "Oxigenoterapia", "Exacerbaciones"];
    } else if (topicLower.includes("cáncer") || topicLower.includes("cancer") || topicLower.includes("oncología")) {
      return ["Patogenia", "Diagnóstico", "Estadificación", "Tratamiento", "Cuidados Paliativos"];
    } else if (topicLower.includes("ictus") || topicLower.includes("accidente cerebrovascular")) {
      return ["Fisiopatología", "Diagnóstico", "Tratamiento Agudo", "Rehabilitación", "Prevención Secundaria"];
    } else if (topicLower.includes("neumonía") || topicLower.includes("neumonia")) {
      return ["Etiología", "Diagnóstico", "Tratamiento Antibiótico", "Complicaciones", "Prevención"];
    } else if (topicLower.includes("covid") || topicLower.includes("coronavirus")) {
      return ["Fisiopatología", "Diagnóstico", "Tratamiento", "Complicaciones", "Vacunación"];
    } else {
      // Temas genéricos basados en el tema principal proporcionado
      return [
        `Fisiopatología de ${mainTopic}`,
        `Diagnóstico de ${mainTopic}`,
        `Tratamiento de ${mainTopic}`,
        `Complicaciones de ${mainTopic}`,
        `Manejo Integral de ${mainTopic}`
      ];
    }
  };

  const getDifficultyForLevel = (level: string, index: number): 'facil' | 'medio' | 'dificil' => {
    if (level === "interno") {
      return index < 3 ? 'facil' : index < 6 ? 'medio' : 'dificil';
    } else if (level === "becado") {
      return index < 2 ? 'facil' : index < 5 ? 'medio' : 'dificil';
    } else { // especialista
      return index < 1 ? 'medio' : 'dificil';
    }
  };

  const generateSubtopicsForTopic = (topic: string, mainTopic: string): string[] => {
    // Generar subtemas específicos para cada tema en el contexto del tema principal
    const baseSubtopics = [
      `Conceptos fundamentales de ${topic} en ${mainTopic}`,
      `Mecanismos específicos de ${topic}`, 
      `Manifestaciones de ${topic} en ${mainTopic}`,
      `Diagnóstico específico de ${topic}`,
      `Terapéutica dirigida para ${topic}`
    ];
    return baseSubtopics.slice(0, 3); // Limitar a 3 subtemas por sesión
  };

  const generateKeyPointsForTopic = (topic: string, mainTopic: string): string[] => {
    // Generar puntos clave específicos para el tema en el contexto del tema principal
    return [
      `Concepto clave de ${topic} en ${mainTopic}`,
      `Relación entre ${topic} y ${mainTopic}`,
      `Aplicación clínica específica`,
      `Consideraciones diagnósticas y terapéuticas`
    ];
  };

  const generateMockTopics = (): StudyTopic[] => {
    const topics: StudyTopic[] = [];
    const baseTopics = [
      {
        title: "Patogenia y Fisiopatología",
        description: "Mecanismos inmunológicos y cascada inflamatoria en AR",
        subtopics: ["Autoinmunidad", "Citocinas proinflamatorias", "Activación de linfocitos T"],
        keyPoints: ["TNF-α como mediador clave", "Papel de IL-1 e IL-6", "Destrucción articular"]
      },
      {
        title: "Criterios Diagnósticos",
        description: "Aplicación de criterios ACR/EULAR 2010 en la práctica",
        subtopics: ["Rigidez matinal", "Artritis simétrica", "Factor reumatoide"],
        keyPoints: ["Score ≥6 puntos", "Articulaciones afectadas", "Reactantes de fase aguda"]
      },
      {
        title: "Manifestaciones Clínicas",
        description: "Signos y síntomas articulares y extraarticulares",
        subtopics: ["Artritis periférica", "Nódulos reumatoides", "Manifestaciones oculares"],
        keyPoints: ["Patrón simétrico", "Rigidez > 1 hora", "Deformidades tardías"]
      },
      {
        title: "Estudios de Laboratorio",
        description: "Interpretación de biomarcadores y auto-anticuerpos",
        subtopics: ["Factor reumatoide", "Anti-CCP", "PCR y VSG"],
        keyPoints: ["Anti-CCP más específico", "PCR como marcador de actividad", "Utilidad pronóstica"]
      },
      {
        title: "Imagenología",
        description: "Radiografía, ultrasonido y RM en el diagnóstico",
        subtopics: ["Erosiones articulares", "Estrechamiento del espacio", "Ultrasonido doppler"],
        keyPoints: ["Erosiones tempranas", "Score de Sharp", "Actividad inflamatoria"]
      },
      {
        title: "DMARDs Convencionales",
        description: "Metotrexato como piedra angular del tratamiento",
        subtopics: ["Mecanismo de acción", "Dosis y vía de administración", "Efectos adversos"],
        keyPoints: ["Dosis 15-25mg semanal", "Ácido fólico suplementario", "Monitoreo hepático"]
      },
      {
        title: "Terapia Biológica",
        description: "Anti-TNF y otras terapias dirigidas",
        subtopics: ["Adalimumab", "Etanercept", "Rituximab"],
        keyPoints: ["Criterios de inicio", "Screening infecciones", "Monitoreo seguridad"]
      },
      {
        title: "Tratamiento No Farmacológico",
        description: "Fisioterapia y medidas de soporte",
        subtopics: ["Ejercicio terapéutico", "Protección articular", "Educación del paciente"],
        keyPoints: ["Ejercicio aeróbico", "Fortalecimiento muscular", "Adherencia al tratamiento"]
      }
    ];

    let topicIndex = 0;
    for (let day = 1; day <= 30; day++) {
      for (let session = 1; session <= 2; session++) {
        const baseTopic = baseTopics[topicIndex % baseTopics.length];
        
        topics.push({
          id: `${day}-${session}`,
          title: `${baseTopic.title} ${session === 2 ? '- Casos Clínicos' : ''}`,
          description: baseTopic.description,
          day,
          session,
          estimatedMinutes: session === 1 ? 45 : 30,
          difficulty: topicIndex < 3 ? 'facil' : topicIndex < 6 ? 'medio' : 'dificil',
          completed: day < 10 || (day === 10 && session === 1),
          confidence: day < 10 ? Math.floor(Math.random() * 3) + 7 : undefined,
          subtopics: baseTopic.subtopics,
          keyPoints: baseTopic.keyPoints,
          studiedAt: day < 10 ? `2024-06-${String(day).padStart(2, '0')}` : undefined
        });
        
        topicIndex++;
      }
    }

    return topics;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'facil': return 'bg-green-100 text-green-800';
      case 'medio': return 'bg-blue-100 text-blue-800';
      case 'dificil': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'facil': return 'Fácil';
      case 'medio': return 'Medio';
      case 'dificil': return 'Difícil';
      default: return difficulty;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 8) return 'text-green-600';
    if (confidence >= 6) return 'text-blue-600';
    if (confidence >= 4) return 'text-gray-600';
    return 'text-red-600';
  };

  const handleStudyTopic = (topicId: string) => {
    navigate(`/study/${topicId}?plan=${planId}`);
  };

  const getDayTopics = (day: number) => {
    return plan?.topics.filter(topic => topic.day === day) || [];
  };

  const getWeekDays = (week: number) => {
    const startDay = (week - 1) * 7 + 1;
    const endDay = Math.min(startDay + 6, plan?.duration || 30);
    return Array.from({ length: endDay - startDay + 1 }, (_, i) => startDay + i);
  };

  if (loading || !plan) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="grid grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const totalWeeks = Math.ceil(plan.duration / 7);
  const currentWeek = Math.ceil(selectedDay / 7);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button variant="outline" onClick={() => navigate('/plans')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a Planes
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">{plan.title}</h1>
          <div className="flex items-center space-x-4 mt-2">
            <Badge variant="secondary">{plan.specialty}</Badge>
            <Badge className="bg-blue-100 text-blue-800">
              {plan.level === 'interno' ? 'Interno' : plan.level === 'becado' ? 'Becado' : 'Especialista'}
            </Badge>
            <span className="text-sm text-gray-600">
              Día {plan.currentDay} de {plan.duration}
            </span>
          </div>
        </div>
      </div>

      {/* Progreso general */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-medical-blue-600" />
                <span className="text-sm font-medium">Progreso General</span>
              </div>
              <div className="text-2xl font-bold">{plan.progress}%</div>
              <Progress value={plan.progress} className="h-2" />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium">Sesiones Completadas</span>
              </div>
              <div className="text-2xl font-bold">{plan.completedSessions}/{plan.totalSessions}</div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium">Tiempo Estudiado</span>
              </div>
              <div className="text-2xl font-bold">{Math.round(plan.completedSessions * 0.75)}h</div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-turquoise-600" />
                <span className="text-sm font-medium">Días Restantes</span>
              </div>
              <div className="text-2xl font-bold">{plan.duration - plan.currentDay}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="calendar" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calendar">Calendario</TabsTrigger>
          <TabsTrigger value="topics">Todos los Temas</TabsTrigger>
          <TabsTrigger value="analytics">Analíticas</TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="space-y-6">
          {/* Selector de semana */}
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {Array.from({ length: totalWeeks }, (_, i) => i + 1).map(week => (
              <Button
                key={week}
                variant={currentWeek === week ? "default" : "outline"}
                onClick={() => setSelectedDay(getWeekDays(week)[0])}
                className="whitespace-nowrap"
              >
                Semana {week}
              </Button>
            ))}
          </div>

          {/* Días de la semana seleccionada */}
          <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
            {getWeekDays(currentWeek).map(day => {
              const dayTopics = getDayTopics(day);
              const completedCount = dayTopics.filter(t => t.completed).length;
              
              return (
                <Card 
                  key={day}
                  className={`cursor-pointer transition-all ${
                    selectedDay === day ? 'ring-2 ring-medical-blue-500' : ''
                  } ${day === plan.currentDay ? 'bg-blue-50' : ''}`}
                  onClick={() => setSelectedDay(day)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-sm">Día {day}</CardTitle>
                      {day === plan.currentDay && (
                        <Badge variant="secondary" className="text-xs">Hoy</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      <div className="text-xs text-gray-600">
                        {completedCount}/{dayTopics.length} completadas
                      </div>
                      <Progress 
                        value={(completedCount / dayTopics.length) * 100} 
                        className="h-1"
                      />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Temas del día seleccionado */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="w-5 h-5" />
                <span>Día {selectedDay} - Sesiones de Estudio</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {getDayTopics(selectedDay).map(topic => (
                  <Card key={topic.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            {topic.completed ? (
                              <CheckCircle className="w-5 h-5 text-green-600" />
                            ) : (
                              <Circle className="w-5 h-5 text-gray-400" />
                            )}
                            <h3 className="font-semibold">{topic.title}</h3>
                            <Badge className={getDifficultyColor(topic.difficulty)}>
                              {getDifficultyLabel(topic.difficulty)}
                            </Badge>
                            {topic.completed && topic.confidence && (
                              <Badge variant="outline" className={getConfidenceColor(topic.confidence)}>
                                Confianza: {topic.confidence}/10
                              </Badge>
                            )}
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-3">{topic.description}</p>
                          
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                            <span className="flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{topic.estimatedMinutes} min</span>
                            </span>
                            <span>Sesión {topic.session}</span>
                            {topic.studiedAt && (
                              <span>Estudiado: {topic.studiedAt}</span>
                            )}
                          </div>

                          <div className="space-y-2">
                            <div>
                              <span className="text-xs font-medium text-gray-700">Subtemas:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {topic.subtopics.map((subtopic, idx) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {subtopic}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            
                            <div>
                              <span className="text-xs font-medium text-gray-700">Puntos clave:</span>
                              <ul className="text-xs text-gray-600 mt-1 ml-4">
                                {topic.keyPoints.map((point, idx) => (
                                  <li key={idx} className="list-disc">{point}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>

                        <div className="ml-4">
                          <Button
                            onClick={() => handleStudyTopic(topic.id)}
                            className={topic.completed ? 
                              "bg-green-600 hover:bg-green-700" : 
                              "bg-medical-blue-600 hover:bg-medical-blue-700"
                            }
                          >
                            {topic.completed ? (
                              <>
                                <BookOpen className="w-4 h-4 mr-2" />
                                Revisar
                              </>
                            ) : (
                              <>
                                <Play className="w-4 h-4 mr-2" />
                                Estudiar
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topics">
          <Card>
            <CardHeader>
              <CardTitle>Todos los Temas del Plan</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {plan.topics.map(topic => (
                  <div 
                    key={topic.id}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleStudyTopic(topic.id)}
                  >
                    <div className="flex items-center space-x-3">
                      {topic.completed ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-400" />
                      )}
                      <div>
                        <div className="font-medium">{topic.title}</div>
                        <div className="text-sm text-gray-600">
                          Día {topic.day}, Sesión {topic.session} • {topic.estimatedMinutes} min
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getDifficultyColor(topic.difficulty)}>
                        {getDifficultyLabel(topic.difficulty)}
                      </Badge>
                      {topic.completed && topic.confidence && (
                        <Badge variant="outline" className={getConfidenceColor(topic.confidence)}>
                          {topic.confidence}/10
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Progreso por Semana</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.from({ length: totalWeeks }, (_, i) => {
                    const week = i + 1;
                    const weekDays = getWeekDays(week);
                    const weekTopics = plan.topics.filter(t => weekDays.includes(t.day));
                    const completedWeekTopics = weekTopics.filter(t => t.completed);
                    const weekProgress = weekTopics.length > 0 ? (completedWeekTopics.length / weekTopics.length) * 100 : 0;
                    
                    return (
                      <div key={week} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Semana {week}</span>
                          <span>{completedWeekTopics.length}/{weekTopics.length}</span>
                        </div>
                        <Progress value={weekProgress} className="h-2" />
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-5 h-5" />
                  <span>Nivel de Confianza</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['Alto (8-10)', 'Medio (6-7)', 'Bajo (4-5)', 'Muy Bajo (1-3)'].map((level, idx) => {
                    const range = idx === 0 ? [8, 10] : idx === 1 ? [6, 7] : idx === 2 ? [4, 5] : [1, 3];
                    const count = plan.topics.filter(t => 
                      t.confidence && t.confidence >= range[0] && t.confidence <= range[1]
                    ).length;
                    const total = plan.topics.filter(t => t.confidence).length;
                    const percentage = total > 0 ? (count / total) * 100 : 0;
                    
                    return (
                      <div key={level} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>{level}</span>
                          <span>{count} temas</span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default StudyPlanDetail;