
import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { 
  Brain,
  Play, 
  Pause, 
  Square,
  BookOpen,
  Clock,
  CheckCircle,
  FileText,
  RotateCcw
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/services/api";

const Study = () => {
  const { toast } = useToast();
  const [isStudying, setIsStudying] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(23 * 60 + 45); // 23:45
  const [totalTime] = useState(45 * 60); // 45 minutos en segundos
  const [confidence] = useState(7);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isStudying) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    
    return () => clearInterval(interval);
  }, [isStudying]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return (timeElapsed / totalTime) * 100;
  };

  const handleStartPause = () => {
    setIsStudying(!isStudying);
    toast({
      title: isStudying ? "Sesión pausada" : "Sesión reanudada",
      description: isStudying ? "Tu progreso ha sido guardado" : "¡Continúa con el aprendizaje!",
    });
  };

  const handleEndSession = () => {
    setIsStudying(false);
    toast({
      title: "🎉 ¡Sesión completada!",
      description: `Has estudiado ${formatTime(timeElapsed)}. Excelente trabajo.`,
    });
  };

  return (
    <div className="min-h-screen bg-study-bg">
      {/* Study Header */}
      <div className="bg-white shadow-sm p-6 border-b">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">📖 Sesión de Estudio Activa</h2>
            <p className="text-gray-600">Artritis Reumatoide - Módulo 3</p>
          </div>
          <div className="flex space-x-4">
            <Button 
              variant="outline"
              onClick={handleStartPause}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              {isStudying ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  ⏸️ Pausar
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  ▶️ Continuar
                </>
              )}
            </Button>
            <Button 
              onClick={handleEndSession}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <Square className="w-4 h-4 mr-2" />
              ⏹️ Terminar
            </Button>
          </div>
        </div>
      </div>

      {/* Study Interface */}
      <div className="flex h-screen">
        {/* Main Content Area */}
        <div className="flex-1 p-8">
          {/* Progress and Timer */}
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-medical-blue-600" />
                  ⏱️ Tiempo
                </h3>
                <span className="text-2xl font-bold text-medical-blue-800">
                  {formatTime(timeElapsed)}
                </span>
              </div>
              <Progress value={getProgressPercentage()} className="mb-2" />
              <p className="text-sm text-gray-600">
                {formatTime(timeElapsed)} / {formatTime(totalTime)}
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">🎯 Tema Actual</h3>
                <span className="px-3 py-1 bg-medical-turquoise-100 text-medical-turquoise-800 rounded-full text-sm">
                  Medio
                </span>
              </div>
              <p className="text-lg font-medium">Artritis Reumatoide</p>
              <p className="text-sm text-gray-600">Confianza: {confidence}/10</p>
            </div>
          </div>

          {/* Study Content */}
          <div className="bg-white rounded-xl p-8 shadow-sm mb-6">
            <h3 className="text-xl font-semibold mb-6">📚 Contenido Generado por IA</h3>
            <div className="prose max-w-none">
              <h4 className="text-lg font-medium text-medical-blue-800 mb-3">
                Patogenia de la Artritis Reumatoide
              </h4>
              <ul className="space-y-2 mb-6">
                <li>• <strong>Autoinmune:</strong> Activación anómala del sistema inmune</li>
                <li>• <strong>Citocinas TNF-α:</strong> Factor clave en la inflamación</li>
                <li>• <strong>Pannus sinovial:</strong> Tejido inflamatorio destructivo</li>
              </ul>

              <h4 className="text-lg font-medium text-medical-blue-800 mb-3">
                Criterios Diagnósticos ACR/EULAR 2010
              </h4>
              <ul className="space-y-2 mb-6">
                <li>• <strong>Articulaciones afectadas:</strong> Pequeñas articulaciones (0-5 puntos)</li>
                <li>• <strong>Serología:</strong> Factor reumatoide y anti-CCP</li>
                <li>• <strong>Duración:</strong> Síntomas &gt; 6 semanas</li>
              </ul>
            </div>

            {/* Active Recall Prompt */}
            <div className="bg-medical-blue-50 border border-medical-blue-200 rounded-lg p-4 mt-6">
              <div className="flex items-center mb-2">
                <Brain className="w-5 h-5 text-medical-blue-800 mr-2" />
                <span className="font-semibold text-medical-blue-800">🧠 Active Recall en 7 min</span>
              </div>
              <p className="text-medical-blue-700">
                ¿Cuáles son los 4 criterios principales del ACR/EULAR 2010 para AR?
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 mt-6">
              <Button className="bg-medical-blue-800 text-white hover:bg-medical-blue-700">
                ✅ Entendido, Continuar
              </Button>
              <Button variant="outline" className="border-gray-300 hover:bg-gray-50">
                📝 Tomar Notas
              </Button>
              <Button variant="outline" className="border-medical-green-300 text-medical-green-700 hover:bg-medical-green-50">
                🔄 Revisar Tema
              </Button>
            </div>
          </div>
        </div>

        {/* Sidebar - Notes */}
        <div className="w-80 bg-white border-l p-6">
          <h3 className="font-semibold mb-4">📝 Notas de la Sesión</h3>
          <Textarea
            className="w-full h-64 p-4 border rounded-lg resize-none"
            placeholder="Escribe tus notas aquí..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <div className="mt-6">
            <h4 className="font-semibold mb-3">📋 Puntos Clave</h4>
            <ul className="space-y-2 text-sm">
              <li>• TNF-α es clave en patogenia</li>
              <li>• Criterios ACR/EULAR 2010</li>
              <li>• MTX primera línea</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Study;
