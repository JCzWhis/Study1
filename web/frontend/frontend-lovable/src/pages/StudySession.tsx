import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { 
  ArrowLeft,
  Play,
  Pause,
  Clock,
  Brain,
  CheckCircle,
  BookOpen,
  FileText,
  MessageCircle,
  Lightbulb,
  Timer,
  Target
} from "lucide-react";

interface StudyContent {
  title: string;
  content: string;
  keyPoints: string[];
  activeRecallQuestions: string[];
  clinicalCases: string[];
}

interface StudyTopic {
  id: string;
  title: string;
  description: string;
  estimatedMinutes: number;
  difficulty: string;
  subtopics: string[];
  keyPoints: string[];
}

const StudySession = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const planId = searchParams.get('plan');

  // Función para generar contenido dinámico basado en el tema
  const generateContentForTopic = (topic: StudyTopic, originalData: any): StudyContent => {
    const mainTopic = originalData?.mainTopic || "Tema Médico";
    const specialty = originalData?.specialty || "Medicina General";
    
    console.log("🔬 Generando contenido para:", topic.title);
    console.log("🎯 Tema principal:", mainTopic);
    
    return {
      title: topic.title,
      content: `
# ${topic.title}

## Introducción Clínica
${topic.description}

Este tema es fundamental para el entendimiento de ${mainTopic} en el contexto de ${specialty}. 

## Contenido Teórico Principal sobre ${mainTopic}

### Conceptos Fundamentales de ${mainTopic}
En el estudio específico de ${mainTopic}, es crucial comprender los mecanismos subyacentes que caracterizan esta condición médica. Este tema (${topic.title}) forma parte integral del entendimiento completo de ${mainTopic}.

### Fisiopatología de ${mainTopic}
Los procesos fisiopatológicos específicos involucrados en ${mainTopic} incluyen múltiples vías moleculares y celulares que convergen en las manifestaciones clínicas características que observamos en la práctica médica.

### Manifestaciones Clínicas de ${mainTopic}
Las presentaciones típicas de ${mainTopic} varían según múltiples factores:
- Edad del paciente y género
- Estadio o severidad de ${mainTopic}
- Factores de riesgo específicos para ${mainTopic}
- Comorbilidades asociadas con ${mainTopic}

### Diagnóstico Específico de ${mainTopic}
El abordaje diagnóstico especializado para ${mainTopic} requiere:
- Historia clínica enfocada en ${mainTopic}
- Examen físico específico para ${mainTopic}
- Estudios complementarios dirigidos para ${mainTopic}
- Criterios diagnósticos específicos para ${mainTopic}

### Tratamiento Dirigido para ${mainTopic}
Las opciones terapéuticas específicas para ${mainTopic} incluyen:
- Medidas no farmacológicas específicas para ${mainTopic}
- Tratamiento farmacológico dirigido para ${mainTopic}
- Manejo específico de complicaciones de ${mainTopic}
- Seguimiento especializado a largo plazo

### Pronóstico y Complicaciones
El pronóstico de ${mainTopic} depende de:
- Diagnóstico temprano
- Adherencia al tratamiento
- Factores pronósticos específicos
- Manejo integral del paciente

## Aspectos Específicos en ${specialty}
En el contexto de ${specialty}, ${mainTopic} presenta características particulares que requieren consideración especializada.

## Casos Clínicos Relevantes
La aplicación práctica de este conocimiento se evidencia en la evaluación y manejo de pacientes con ${mainTopic}.

## Implicaciones para la Práctica Clínica
Este conocimiento es fundamental para el manejo efectivo de pacientes con ${mainTopic} en la práctica clínica diaria.
      `,
      keyPoints: topic.keyPoints,
      activeRecallQuestions: [
        `¿Cuáles son los mecanismos fisiopatológicos principales de ${mainTopic}?`,
        `¿Cómo se presenta clínicamente ${mainTopic} y cuáles son los signos más característicos?`,
        `¿Cuál es el abordaje diagnóstico sistemático para ${mainTopic}?`,
        `¿Cuáles son las opciones terapéuticas disponibles para ${mainTopic} y cuándo está indicada cada una?`,
        `¿Qué complicaciones pueden presentarse en ${mainTopic} y cómo se previenen?`,
        `¿Cuáles son los factores pronósticos más importantes en ${mainTopic}?`,
        `¿Cómo se relaciona ${topic.title} con el manejo integral de ${mainTopic}?`,
        `¿Qué consideraciones especiales tiene ${mainTopic} en el contexto de ${specialty}?`
      ],
      clinicalCases: [
        `Paciente con manifestaciones típicas de ${mainTopic}. ¿Cuál sería el abordaje diagnóstico inicial?`,
        `Caso clínico de ${mainTopic} con complicaciones. ¿Cómo modificaría el tratamiento?`
      ]
    };
  };

  const [topic, setTopic] = useState<StudyTopic | null>(null);
  const [content, setContent] = useState<StudyContent | null>(null);
  const [currentPhase, setCurrentPhase] = useState<'reading' | 'active_recall' | 'confidence' | 'completed'>('reading');
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [confidence, setConfidence] = useState([7]);
  const [notes, setNotes] = useState("");
  const [answers, setAnswers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Cargar datos del tema
    const loadTopic = async () => {
      setLoading(true);
      
      try {
        // Intentar cargar datos del plan guardado
        if (planId) {
          const savedPlan = localStorage.getItem(`plan_${planId}`);
          if (savedPlan) {
            const planData = JSON.parse(savedPlan);
            console.log("📚 Plan cargado:", planData);
            
            // Buscar el tema específico en el plan
            const topicFromPlan = planData.topics?.find((t: any) => t.id === topicId);
            if (topicFromPlan) {
              console.log("✅ Tema encontrado en plan:", topicFromPlan);
              setTopic(topicFromPlan);
              
              // Generar contenido basado en el tema del plan
              const dynamicContent = generateContentForTopic(topicFromPlan, planData.originalData);
              setContent(dynamicContent);
              setLoading(false);
              return;
            }
          }
        }
        
        // Fallback: datos simulados
        console.log("⚠️ Usando datos simulados para topicId:", topicId);
      } catch (error) {
        console.error("❌ Error cargando tema:", error);
      }
      
      // Simulación de datos - fallback
      const mockTopic: StudyTopic = {
        id: topicId!,
        title: "Patogenia y Fisiopatología de Artritis Reumatoide",
        description: "Mecanismos inmunológicos y cascada inflamatoria en AR",
        estimatedMinutes: 45,
        difficulty: "medio",
        subtopics: ["Autoinmunidad", "Citocinas proinflamatorias", "Activación de linfocitos T"],
        keyPoints: ["TNF-α como mediador clave", "Papel de IL-1 e IL-6", "Destrucción articular"]
      };

      const mockContent: StudyContent = {
        title: mockTopic.title,
        content: `
# Patogenia y Fisiopatología de Artritis Reumatoide

## Introducción Clínica
La artritis reumatoide (AR) es una enfermedad autoinmune sistémica crónica que afecta principalmente las articulaciones sinoviales, caracterizada por inflamación persistente que lleva a destrucción articular progresiva. Afecta aproximadamente al 0.5-1% de la población mundial, con una relación mujer:hombre de 3:1. La edad de presentación típica es entre 30-50 años, aunque puede presentarse a cualquier edad.

La importancia clínica radica en que sin tratamiento adecuado, la AR causa discapacidad funcional significativa, deterioro de la calidad de vida y reducción de la expectativa de vida. El diagnóstico temprano y el inicio precoz del tratamiento son cruciales para prevenir el daño articular irreversible.

## Mecanismos Inmunológicos Fundamentales

### 1. Fase de Iniciación: Ruptura de la Tolerancia Inmunológica

**Factores Genéticos:**
- **HLA-DRB1**: Los alelos que contienen el "epítope compartido" (secuencia QKRAA o QRRAA en posiciones 70-74) confieren susceptibilidad
- **Genes no-HLA**: PTPN22, STAT4, TRAF1-C5, TNFAIP3, que regulan la activación de linfocitos T y la apoptosis
- **Factor de riesgo genético total**: Aproximadamente 50-60% de la susceptibilidad

**Factores Ambientales Desencadenantes:**
- **Infecciones**: Porphyromonas gingivalis (periodontitis), virus de Epstein-Barr, citomegalovirus
- **Tabaquismo**: Aumenta el riesgo 2-3 veces, especialmente en portadores de HLA-DR4
- **Microbiota intestinal**: Disbiosis que altera la tolerancia inmunológica
- **Estrés y trauma**: Pueden actuar como factores desencadenantes

**Modificaciones Post-traduccionales:**
- **Citrulinación de proteínas**: La enzima peptidil-arginina deiminasa (PAD) convierte arginina en citrulina
- **Proteínas citrulinadas comunes**: Vimentina, fibrinógeno, colágeno tipo II, histonas
- **Pérdida de tolerancia**: El sistema inmune reconoce estas proteínas modificadas como antígenos extraños

### 2. Activación del Sistema Inmune Adaptativo

**Presentación Antigénica:**
- **Células dendríticas**: Capturan antígenos citrulinados en articulaciones y los presentan en ganglios linfáticos
- **Macrófagos sinoviales**: Actúan como células presentadoras de antígenos locales
- **Presentación por HLA-DR**: Los péptidos citrulinados se unen preferentemente a moléculas HLA-DR con epítope compartido

**Activación de Linfocitos T:**
- **Diferenciación Th1**: Producen IFN-γ que activa macrófagos y aumenta la presentación de HLA-DR
- **Diferenciación Th17**: Producen IL-17A, IL-17F, IL-22 que inducen inflamación local
- **Th2 y Tfh**: Ayudan en la activación de linfocitos B y producción de anticuerpos
- **Treg deficientes**: Reducción en número y función de linfocitos T reguladores

**Activación de Linfocitos B:**
- **Activación T-dependiente**: Los Th foliculares ayudan en centros germinales
- **Activación T-independiente**: Por complejos inmunes y PAMPs
- **Cambio de isotipo**: De IgM a IgG, mediado por citocinas como IL-21
- **Maduración de afinidad**: Mejora la especificidad contra antígenos citrulinados

### 3. Cascada de Citocinas y Mediadores Inflamatorios

**TNF-α: El Mediador Central**
- **Fuentes principales**: Macrófagos activados, linfocitos T, fibroblastos sinoviales
- **Efectos sistémicos**: Fiebre, pérdida de peso, fatiga, proteínas de fase aguda
- **Efectos locales**: 
  - Activación de células endoteliales → expresión de moléculas de adhesión
  - Inducción de quimiocinas → reclutamiento de células inflamatorias
  - Estimulación de angiogénesis → formación de nuevos vasos
  - Activación de fibroblastos → proliferación sinovial

**Interleucina-1β (IL-1β):**
- **Activación del inflamasoma**: NLRP3 activa caspasa-1 que procesa pro-IL-1β
- **Efectos en cartílago**: Induce condrocitos a producir MMP-1, MMP-3, MMP-13
- **Inhibición de síntesis**: Reduce producción de colágeno tipo II y proteoglicanos
- **Efectos sistémicos**: Fiebre, somnolencia, anorexia

**Interleucina-6 (IL-6):**
- **Producción**: Macrófagos, fibroblastos, células endoteliales
- **Efectos hepáticos**: Induce proteínas de fase aguda (PCR, SAA, fibrinógeno)
- **Efectos en hueso**: Activa osteoclastos vía RANKL, inhibe osteoblastos
- **Efectos sistémicos**: Anemia de enfermedad crónica, trombocitosis

**Interleucina-17 (IL-17A/F):**
- **Fuentes**: Células Th17, células γδ T, células NK
- **Inducción de quimiocinas**: CXCL1, CXCL5, CXCL8 que reclutan neutrófilos
- **Activación de fibroblastos**: Producción de MMP-1, MMP-3, VEGF
- **Sinergia con TNF-α**: Potencia los efectos inflamatorios

### 4. Formación del Pannus: Tejido Sinovial Patológico

**Hiperplasia Sinovial:**
- **Proliferación de sinoviocitos**: Tipo A (macrófagos) y tipo B (fibroblastos)
- **Resistencia a apoptosis**: Expresión aumentada de Bcl-2, p53 mutante
- **Comportamiento "cuasi-tumoral": Invasión y migración anómalas

**Angiogénesis Patológica:**
- **VEGF (factor de crecimiento endotelial vascular)**: Inducido por hipoxia e inflamación
- **Angiopoyetinas**: Regulan maduración vascular
- **Nuevos vasos**: Facilitan entrada de células inflamatorias y nutrientes

**Infiltración Celular:**
- **Macrófagos**: M1 proinflamatorios dominan sobre M2 antiinflamatorios
- **Linfocitos T**: Principalmente memoria efectora, reducción de Treg
- **Linfocitos B**: Formación de centros germinales ectópicos
- **Células plasmáticas**: Producen anticuerpos localmente

### 5. Mecanismos de Destrucción Articular

**Destrucción del Cartílago:**
- **Metaloproteinasas de matriz (MMPs)**:
  - MMP-1 (colagenasa-1): Degrada colágeno tipo I y III
  - MMP-3 (estromelisina-1): Degrada proteoglicanos y colágeno tipo IV
  - MMP-13 (colagenasa-3): Específica para colágeno tipo II
- **Agrecanasas (ADAMTS)**: ADAMTS-4 y ADAMTS-5 degradan agrecano
- **Inhibición de síntesis**: Reducción de colágeno tipo II y proteoglicanos

**Erosión Ósea:**
- **Sistema RANK/RANKL/OPG**:
  - RANKL: Expresado por osteoblastos, fibroblastos sinoviales, linfocitos T activados
  - RANK: Receptor en precursores de osteoclastos
  - OPG: Receptor señuelo que inhibe RANKL
- **Diferenciación de osteoclastos**: M-CSF + RANKL → osteoclastos multinucleados
- **Activación**: TNF-α, IL-1β, IL-17 aumentan expresión de RANKL
- **Resorción ósea**: Acidificación y liberación de proteasas (catepsina K)

**Inhibición de Formación Ósea:**
- **Vía Wnt/β-catenina**: Inhibida por DKK-1 y esclerostina
- **Factores inflamatorios**: TNF-α e IL-1β inhiben diferenciación de osteoblastos
- **Resultado neto**: Desbalance hacia resorción ósea

### 6. Autoanticuerpos y Complejos Inmunes

**Factor Reumatoide (FR):**
- **Naturaleza**: Anticuerpos IgM, IgG, IgA contra porción Fc de IgG
- **Prevalencia**: 70-80% de pacientes con AR
- **Producción local**: En tejido sinovial por células plasmáticas
- **Efectos patogénicos**: Formación de complejos inmunes, activación de complemento

**Anticuerpos Anti-Péptidos Citrulinados (ACPA):**
- **Especificidad**: >95% específicos para AR
- **Sensibilidad**: 60-70% de pacientes con AR
- **Valor pronóstico**: Asociados con mayor destrucción articular
- **Producción**: Puede preceder síntomas clínicos por años

**Otros Autoanticuerpos:**
- **Anti-CarP**: Contra proteínas carbamiladas
- **Anti-PAD4**: Contra la enzima peptidil-arginina deiminasa
- **Anti-vimentina mutada**: Marcador temprano

### 7. Perpetuación de la Inflamación

**Retroalimentación Positiva:**
- **Hipoxia sinovial**: Induce HIF-1α → VEGF y factores pro-angiogénicos
- **Estrés oxidativo**: Radicales libres dañan tejidos y activan NFκB
- **Complejos inmunes**: Activan complemento y células vía receptores Fc
- **DAMPs**: Proteínas del shock térmico, fragmentos de matriz extracelular

**Escape de Regulación:**
- **Reducción de IL-10**: Citocina antiinflamatoria
- **Disfunción de Treg**: Menor capacidad supresora
- **Resistencia a apoptosis**: En sinoviocitos y células inflamatorias
- **Epigenética**: Metilación del DNA altera expresión génica

## Implicaciones Terapéuticas Basadas en Patogenia

### Terapias Dirigidas Actuales:

**Inhibidores de TNF-α:**
- **Mecanismo**: Bloquean TNF-α soluble y/o transmembranal
- **Fármacos**: Adalimumab, etanercept, infliximab, golimumab, certolizumab
- **Eficacia**: Mejoran síntomas y retrasan progresión radiológica
- **Limitaciones**: 30-40% de pacientes no responden, riesgo de infecciones

**Inhibidores de IL-6:**
- **Tocilizumab**: Anticuerpo anti-receptor de IL-6
- **Sarilumab**: Anticuerpo anti-receptor de IL-6
- **Efectos**: Mejoran síntomas sistémicos, normalizan PCR

**Depleción de Linfocitos B:**
- **Rituximab**: Anticuerpo anti-CD20
- **Efectos**: Reduce producción de autoanticuerpos y células plasmáticas

**Inhibidores de JAK:**
- **Tofacitinib, baricitinib, upadacitinib**: Inhiben vías JAK/STAT
- **Ventaja**: Vía oral, múltiples citocinas inhibidas

### Futuras Direcciones Terapéuticas:

**Terapias Celulares:**
- **Células madre mesenquimales**: Propiedades inmunomoduladoras
- **Treg expandidos**: Restaurar tolerancia inmunológica

**Modulación del Microbioma:**
- **Probióticos específicos**: Restaurar equilibrio inmunológico
- **Metabolitos bacterianos**: Ácidos grasos de cadena corta

**Medicina Personalizada:**
- **Biomarcadores**: Predecir respuesta terapéutica
- **Farmacogenómica**: Optimizar dosis según genética

Este conocimiento patogénico profundo permite un manejo más racional y efectivo de la AR, con terapias dirigidas específicamente a los mecanismos fisiopatológicos subyacentes.
        `,
        keyPoints: mockTopic.keyPoints,
        activeRecallQuestions: [
          "¿Cuál es el papel del 'epítope compartido' en HLA-DRB1 en la susceptibilidad a AR? ¿Cómo interactúa con factores ambientales como el tabaquismo?",
          "Explica detalladamente el proceso de citrulinación de proteínas y por qué lleva a la pérdida de tolerancia inmunológica en AR",
          "Describe la cascada de citocinas en AR: ¿Cómo TNF-α, IL-1β, IL-6 e IL-17 interactúan para perpetuar la inflamación?",
          "¿Qué diferencias existen entre las células Th1, Th17 y Treg en la patogenia de AR? ¿Cómo se relacionan con la severidad de la enfermedad?",
          "Explica el sistema RANK/RANKL/OPG en la destrucción ósea. ¿Cómo las citocinas inflamatorias alteran este equilibrio?",
          "¿Qué son los anticuerpos anti-CCP y por qué son más específicos que el factor reumatoide? ¿Cuál es su valor pronóstico?",
          "Describe la formación del pannus: ¿Qué tipos celulares lo componen y qué características 'cuasi-tumorales' presenta?",
          "¿Cómo las metaloproteinasas (MMP-1, MMP-3, MMP-13) contribuyen a la destrucción del cartílago? ¿Qué las regula?",
          "Explica las bases moleculares de las terapias anti-TNF: ¿Por qué son efectivas y cuáles son sus limitaciones?",
          "¿Qué papel juega la angiogénesis patológica en la perpetuación de la AR? ¿Cómo VEGF y la hipoxia contribuyen?"
        ],
        clinicalCases: [
          "Mujer de 35 años con rigidez matinal > 1 hora, artritis simétrica en manos. FR+, anti-CCP+. ¿Qué citocinas estarían elevadas?",
          "Paciente con AR de 5 años de evolución presenta erosiones en rayos X. ¿Qué mecanismos patogénicos explican este hallazgo?"
        ]
      };

      setTopic(mockTopic);
      setContent(mockContent);
      setLoading(false);
    };

    loadTopic();
  }, [topicId]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startTimer = () => setIsTimerRunning(true);
  const pauseTimer = () => setIsTimerRunning(false);

  const handlePhaseComplete = () => {
    if (currentPhase === 'reading') {
      setCurrentPhase('active_recall');
      setCurrentQuestionIndex(0);
    } else if (currentPhase === 'active_recall') {
      setCurrentPhase('confidence');
    } else if (currentPhase === 'confidence') {
      setCurrentPhase('completed');
      completeStudySession();
    }
  };

  const handleNextQuestion = () => {
    if (content && currentQuestionIndex < content.activeRecallQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handlePhaseComplete();
    }
  };

  const completeStudySession = () => {
    // Aquí enviarías los datos al backend
    console.log({
      topicId,
      timeElapsed,
      confidence: confidence[0],
      notes,
      answers,
      completed: true
    });
  };

  const handleBackToPlan = () => {
    if (planId) {
      navigate(`/plan/${planId}`);
    } else {
      navigate('/plans');
    }
  };

  if (loading || !topic || !content) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button variant="outline" onClick={handleBackToPlan}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver al Plan
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{topic.title}</h1>
          <p className="text-gray-600">{topic.description}</p>
        </div>
      </div>

      {/* Timer y Progreso */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-medical-blue-600" />
                <span className="text-2xl font-bold">{formatTime(timeElapsed)}</span>
                <span className="text-sm text-gray-600">/ {topic.estimatedMinutes} min</span>
              </div>
              
              <Button
                onClick={isTimerRunning ? pauseTimer : startTimer}
                size="sm"
                className="bg-medical-blue-600 hover:bg-medical-blue-700"
              >
                {isTimerRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium">
                  {currentPhase === 'reading' ? 'Lectura' :
                   currentPhase === 'active_recall' ? 'Active Recall' :
                   currentPhase === 'confidence' ? 'Evaluación' : 'Completado'}
                </span>
              </div>
              
              <Progress 
                value={
                  currentPhase === 'reading' ? 25 :
                  currentPhase === 'active_recall' ? 60 :
                  currentPhase === 'confidence' ? 85 : 100
                } 
                className="w-32 h-2" 
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contenido según la fase */}
      {currentPhase === 'reading' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5" />
              <span>Contenido de Estudio</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none">
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {content.content}
            </div>
            
            <div className="mt-6 pt-6 border-t">
              <h4 className="font-semibold mb-3 flex items-center space-x-2">
                <Target className="w-4 h-4" />
                <span>Puntos Clave para Recordar</span>
              </h4>
              <ul className="space-y-2">
                {content.keyPoints.map((point, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-6 pt-6 border-t">
              <Button 
                onClick={handlePhaseComplete}
                className="w-full bg-medical-blue-600 hover:bg-medical-blue-700"
              >
                Continuar a Active Recall
                <Brain className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {currentPhase === 'active_recall' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" />
              <span>Active Recall - Pregunta {currentQuestionIndex + 1} de {content.activeRecallQuestions.length}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2 flex items-center space-x-2">
                <Lightbulb className="w-4 h-4 text-blue-600" />
                <span>Pregunta</span>
              </h3>
              <p className="text-gray-700">{content.activeRecallQuestions[currentQuestionIndex]}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tu respuesta:
              </label>
              <Textarea
                value={answers[currentQuestionIndex] || ""}
                onChange={(e) => {
                  const newAnswers = [...answers];
                  newAnswers[currentQuestionIndex] = e.target.value;
                  setAnswers(newAnswers);
                }}
                placeholder="Explica tu respuesta con el mayor detalle posible..."
                rows={5}
                className="w-full"
              />
            </div>

            <div className="flex space-x-3">
              <Button
                onClick={handleNextQuestion}
                className="flex-1 bg-medical-blue-600 hover:bg-medical-blue-700"
              >
                {currentQuestionIndex < content.activeRecallQuestions.length - 1 ? 'Siguiente Pregunta' : 'Evaluar Confianza'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {currentPhase === 'confidence' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="w-5 h-5" />
              <span>Evaluación de Confianza</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">
                ¿Qué tan confiado te sientes con este tema?
              </h3>
              <p className="text-gray-600 mb-6">
                Esta evaluación ayuda al algoritmo de repetición espaciada
              </p>
            </div>

            <div className="space-y-4">
              <div className="text-center">
                <span className="text-3xl font-bold text-medical-blue-600">
                  {confidence[0]}/10
                </span>
              </div>
              
              <Slider
                value={confidence}
                onValueChange={setConfidence}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>Muy inseguro</span>
                <span>Completamente seguro</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notas adicionales (opcional):
              </label>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Aspectos que necesitas reforzar, dudas, comentarios..."
                rows={3}
              />
            </div>

            <Button 
              onClick={handlePhaseComplete}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Completar Sesión de Estudio
            </Button>
          </CardContent>
        </Card>
      )}

      {currentPhase === 'completed' && (
        <Card className="text-center">
          <CardContent className="p-8">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              ¡Sesión Completada!
            </h2>
            <p className="text-gray-600 mb-6">
              Has completado el estudio de "{topic.title}"
            </p>
            
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{formatTime(timeElapsed)}</div>
                <div className="text-sm text-gray-600">Tiempo estudiado</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{confidence[0]}/10</div>
                <div className="text-sm text-gray-600">Confianza</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{content.activeRecallQuestions.length}</div>
                <div className="text-sm text-gray-600">Preguntas respondidas</div>
              </div>
            </div>

            <Button 
              onClick={handleBackToPlan}
              className="bg-medical-blue-600 hover:bg-medical-blue-700"
            >
              Volver al Plan de Estudio
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default StudySession;