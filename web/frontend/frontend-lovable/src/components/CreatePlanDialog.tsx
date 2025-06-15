
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Upload, Plus, Timer, BookOpen, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface CreatePlanDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const CreatePlanDialog = ({ open, onOpenChange }: CreatePlanDialogProps) => {
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    title: "",
    specialty: "",
    duration: "",
    difficulty: "",
    description: "",
    focusAreas: [] as string[],
    files: [] as File[]
  });

  const specialties = [
    "Cardiología", "Neurología", "Reumatología", "Endocrinología", 
    "Neumología", "Gastroenterología", "Oncología", "Infectología",
    "Dermatología", "Psiquiatría", "Radiología", "Medicina Interna"
  ];

  const focusOptions = [
    "Diagnóstico", "Tratamiento", "Patogenia", "Epidemiología",
    "Complicaciones", "Prevención", "Pronóstico", "Farmacología"
  ];

  const durations = [
    { value: "30", label: "30 minutos" },
    { value: "45", label: "45 minutos" },
    { value: "60", label: "1 hora" },
    { value: "90", label: "1.5 horas" },
    { value: "120", label: "2 horas" }
  ];

  const difficulties = [
    { value: "basico", label: "Básico - Conceptos fundamentales" },
    { value: "intermedio", label: "Intermedio - Aplicación clínica" },
    { value: "avanzado", label: "Avanzado - Casos complejos" }
  ];

  const handleFocusAreaToggle = (area: string) => {
    setFormData(prev => ({
      ...prev,
      focusAreas: prev.focusAreas.includes(area)
        ? prev.focusAreas.filter(a => a !== area)
        : [...prev.focusAreas, area]
    }));
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setFormData(prev => ({
      ...prev,
      files: [...prev.files, ...files]
    }));
  };

  const removeFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index)
    }));
  };

  const handleGeneratePlan = async () => {
    setIsGenerating(true);
    
    // Simular generación con IA
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setIsGenerating(false);
    setStep(3);
    
    toast({
      title: "¡Plan creado exitosamente!",
      description: "Tu plan de estudio ha sido generado con IA y está listo para usar.",
    });
  };

  const handleSavePlan = () => {
    toast({
      title: "Plan guardado",
      description: "Tu plan ha sido guardado en tu biblioteca de estudios.",
    });
    onOpenChange(false);
    setStep(1);
    setFormData({
      title: "",
      specialty: "",
      duration: "",
      difficulty: "",
      description: "",
      focusAreas: [],
      files: []
    });
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="title">Título del Plan</Label>
        <Input
          id="title"
          placeholder="Ej: Artritis Reumatoide - Diagnóstico y Tratamiento"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="specialty">Especialidad Médica</Label>
        <Select 
          value={formData.specialty} 
          onValueChange={(value) => setFormData(prev => ({ ...prev, specialty: value }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Selecciona una especialidad" />
          </SelectTrigger>
          <SelectContent>
            {specialties.map((specialty) => (
              <SelectItem key={specialty} value={specialty.toLowerCase()}>
                {specialty}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="duration">Duración de Estudio</Label>
          <Select 
            value={formData.duration} 
            onValueChange={(value) => setFormData(prev => ({ ...prev, duration: value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Duración" />
            </SelectTrigger>
            <SelectContent>
              {durations.map((duration) => (
                <SelectItem key={duration.value} value={duration.value}>
                  {duration.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="difficulty">Nivel de Dificultad</Label>
          <Select 
            value={formData.difficulty} 
            onValueChange={(value) => setFormData(prev => ({ ...prev, difficulty: value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Nivel" />
            </SelectTrigger>
            <SelectContent>
              {difficulties.map((difficulty) => (
                <SelectItem key={difficulty.value} value={difficulty.value}>
                  {difficulty.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Áreas de Enfoque</Label>
        <div className="grid grid-cols-2 gap-2">
          {focusOptions.map((area) => (
            <div key={area} className="flex items-center space-x-2">
              <Checkbox
                id={area}
                checked={formData.focusAreas.includes(area)}
                onCheckedChange={() => handleFocusAreaToggle(area)}
              />
              <Label htmlFor={area} className="text-sm font-normal">{area}</Label>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Descripción (Opcional)</Label>
        <Textarea
          id="description"
          placeholder="Describe objetivos específicos o temas adicionales..."
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          rows={3}
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">Subir PDFs (Opcional)</h3>
        <p className="text-gray-600 text-sm mb-6">
          Sube documentos médicos para personalizar el contenido del plan
        </p>
      </div>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
        <div className="text-center">
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <Label htmlFor="file-upload" className="cursor-pointer">
            <span className="text-medical-blue-600 hover:text-medical-blue-700 font-medium">
              Haz clic para subir archivos
            </span>
            <span className="text-gray-600"> o arrastra y suelta</span>
          </Label>
          <Input
            id="file-upload"
            type="file"
            accept=".pdf"
            multiple
            className="hidden"
            onChange={handleFileUpload}
          />
          <p className="text-xs text-gray-500 mt-2">PDF hasta 10MB cada uno</p>
        </div>
      </div>

      {formData.files.length > 0 && (
        <div className="space-y-2">
          <Label>Archivos seleccionados:</Label>
          {formData.files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium">{file.name}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
                className="text-red-600 hover:text-red-700"
              >
                Eliminar
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6 text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
        <Check className="w-8 h-8 text-green-600" />
      </div>
      
      <div>
        <h3 className="text-xl font-semibold text-study-text mb-2">
          ¡Plan Creado Exitosamente!
        </h3>
        <p className="text-gray-600">
          Tu plan de estudio ha sido generado con IA y está listo para usar
        </p>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 text-left">
        <h4 className="font-semibold mb-2">{formData.title}</h4>
        <div className="space-y-1 text-sm text-gray-600">
          <p>📚 Especialidad: {formData.specialty}</p>
          <p>⏱️ Duración: {formData.duration} minutos</p>
          <p>🎯 Nivel: {formData.difficulty}</p>
          <p>📋 Áreas: {formData.focusAreas.join(", ")}</p>
        </div>
      </div>

      <div className="flex gap-3">
        <Button 
          variant="outline" 
          onClick={() => onOpenChange(false)}
          className="flex-1"
        >
          Crear Otro Plan
        </Button>
        <Button 
          onClick={handleSavePlan}
          className="flex-1 bg-medical-blue-700 hover:bg-medical-blue-800"
        >
          <BookOpen className="w-4 h-4 mr-2" />
          Ir a Estudiar
        </Button>
      </div>
    </div>
  );

  const renderGenerating = () => (
    <div className="space-y-6 text-center py-8">
      <div className="w-16 h-16 border-4 border-medical-blue-200 border-t-medical-blue-600 rounded-full animate-spin mx-auto"></div>
      
      <div>
        <h3 className="text-xl font-semibold text-study-text mb-2">
          Generando tu plan con IA...
        </h3>
        <p className="text-gray-600">
          Estamos creando contenido personalizado basado en tus preferencias
        </p>
      </div>

      <div className="bg-blue-50 rounded-lg p-4 text-left max-w-md mx-auto">
        <h4 className="font-semibold mb-2 text-medical-blue-800">Procesando:</h4>
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-green-600">
            <Check className="w-4 h-4 mr-2" />
            Analizando especialidad médica
          </div>
          <div className="flex items-center text-green-600">
            <Check className="w-4 h-4 mr-2" />
            Seleccionando contenido relevante
          </div>
          <div className="flex items-center text-medical-blue-600">
            <div className="w-4 h-4 border-2 border-medical-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
            Generando plan de estudio...
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-medical-blue-100 rounded-lg flex items-center justify-center">
              <Plus className="w-5 h-5 text-medical-blue-600" />
            </div>
            <span>🤖 Crear Plan de Estudio con IA</span>
          </DialogTitle>
        </DialogHeader>

        {/* Indicador de pasos */}
        {!isGenerating && step < 3 && (
          <div className="flex items-center justify-center space-x-4 mb-6">
            {[1, 2].map((stepNum) => (
              <div key={stepNum} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step >= stepNum 
                    ? 'bg-medical-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {stepNum}
                </div>
                {stepNum < 2 && (
                  <div className={`w-12 h-1 mx-2 ${
                    step > stepNum ? 'bg-medical-blue-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        )}

        {/* Contenido del paso */}
        <div className="space-y-6">
          {isGenerating ? renderGenerating() : 
           step === 1 ? renderStep1() :
           step === 2 ? renderStep2() :
           renderStep3()}
        </div>

        {/* Botones de navegación */}
        {!isGenerating && step < 3 && (
          <div className="flex justify-between pt-6">
            <Button
              variant="outline"
              onClick={() => step === 1 ? onOpenChange(false) : setStep(step - 1)}
            >
              {step === 1 ? "Cancelar" : "Anterior"}
            </Button>
            
            <Button
              onClick={() => {
                if (step === 1) {
                  setStep(2);
                } else {
                  handleGeneratePlan();
                }
              }}
              className="bg-medical-blue-700 hover:bg-medical-blue-800"
              disabled={step === 1 && (!formData.title || !formData.specialty)}
            >
              {step === 1 ? (
                <>
                  Siguiente
                  <Timer className="w-4 h-4 ml-2" />
                </>
              ) : (
                <>
                  🚀 Generar Plan con IA
                </>
              )}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default CreatePlanDialog;
