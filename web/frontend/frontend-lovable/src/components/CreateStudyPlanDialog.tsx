import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Upload, X, Sparkles, Clock, User, BookOpen, Target } from "lucide-react";

interface CreateStudyPlanDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreatePlan: (planData: StudyPlanData) => void;
}

interface StudyPlanData {
  mainTopic: string;
  specialty: string;
  level: string;
  duration: number;
  sessionsPerDay: number;
  description?: string;
  subtopics: string[];
  uploadedFiles: File[];
}

const CreateStudyPlanDialog = ({ open, onOpenChange, onCreatePlan }: CreateStudyPlanDialogProps) => {
  const [formData, setFormData] = useState<StudyPlanData>({
    mainTopic: "",
    specialty: "",
    level: "",
    duration: 30,
    sessionsPerDay: 2,
    description: "",
    subtopics: [],
    uploadedFiles: []
  });

  const [newSubtopic, setNewSubtopic] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const specialties = [
    "Medicina Interna", "Cardiología", "Neurología", "Gastroenterología",
    "Endocrinología", "Reumatología", "Neumología", "Nefrología",
    "Dermatología", "Psiquiatría", "Oncología", "Hematología",
    "Infectología", "Geriatría", "Medicina de Emergencia"
  ];

  const levels = [
    { value: "interno", label: "Interno", description: "Conocimiento básico y fundamentos" },
    { value: "becado", label: "Becado/Residente", description: "Conocimiento intermedio y casos clínicos" },
    { value: "especialista", label: "Especialista", description: "Conocimiento avanzado y casos complejos" }
  ];

  const handleAddSubtopic = () => {
    if (newSubtopic.trim() && !formData.subtopics.includes(newSubtopic.trim())) {
      setFormData(prev => ({
        ...prev,
        subtopics: [...prev.subtopics, newSubtopic.trim()]
      }));
      setNewSubtopic("");
    }
  };

  const handleRemoveSubtopic = (index: number) => {
    setFormData(prev => ({
      ...prev,
      subtopics: prev.subtopics.filter((_, i) => i !== index)
    }));
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setFormData(prev => ({
      ...prev,
      uploadedFiles: [...prev.uploadedFiles, ...files]
    }));
  };

  const handleRemoveFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      uploadedFiles: prev.uploadedFiles.filter((_, i) => i !== index)
    }));
  };

  const handleGeneratePlan = async () => {
    console.log("🚀 Iniciando generación de plan");
    console.log("📊 Datos del formulario:", formData);
    
    if (!formData.mainTopic || !formData.specialty || !formData.level) {
      alert("Por favor completa los campos obligatorios");
      return;
    }

    setIsGenerating(true);
    try {
      console.log("⏳ Simulando generación con IA...");
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log("✨ Enviando datos al padre:");
      console.log("- Tema principal:", formData.mainTopic);
      console.log("- Especialidad:", formData.specialty);
      console.log("- Nivel:", formData.level);
      console.log("- Subtemas:", formData.subtopics);
      console.log("- Archivos:", formData.uploadedFiles.map(f => f.name));
      
      onCreatePlan(formData);
      onOpenChange(false);
      
      // Resetear formulario
      setFormData({
        mainTopic: "",
        specialty: "",
        level: "",
        duration: 30,
        sessionsPerDay: 2,
        description: "",
        subtopics: [],
        uploadedFiles: []
      });
    } catch (error) {
      console.error("❌ Error generando plan:", error);
      alert("Error al generar el plan. Intenta de nuevo.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-medical-blue-600" />
            <span>Crear Nuevo Plan de Estudio con IA</span>
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 py-4">
          {/* Configuración Principal */}
          <div className="space-y-6">
            <Card>
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center space-x-2 mb-3">
                  <Target className="w-4 h-4 text-medical-blue-600" />
                  <h3 className="font-semibold">Configuración Principal</h3>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mainTopic">Tema Principal *</Label>
                  <Input
                    id="mainTopic"
                    placeholder="ej: Artritis Reumatoide, Insuficiencia Cardíaca..."
                    value={formData.mainTopic}
                    onChange={(e) => setFormData(prev => ({ ...prev, mainTopic: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="specialty">Especialidad *</Label>
                  <Select value={formData.specialty} onValueChange={(value) => setFormData(prev => ({ ...prev, specialty: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona una especialidad" />
                    </SelectTrigger>
                    <SelectContent>
                      {specialties.map((specialty) => (
                        <SelectItem key={specialty} value={specialty}>
                          {specialty}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="level">Nivel de Complejidad *</Label>
                  <Select value={formData.level} onValueChange={(value) => setFormData(prev => ({ ...prev, level: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona tu nivel" />
                    </SelectTrigger>
                    <SelectContent>
                      {levels.map((level) => (
                        <SelectItem key={level.value} value={level.value}>
                          <div className="flex flex-col">
                            <span className="font-medium">{level.label}</span>
                            <span className="text-xs text-gray-500">{level.description}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="duration">Duración (días) *</Label>
                    <Select value={formData.duration.toString()} onValueChange={(value) => setFormData(prev => ({ ...prev, duration: parseInt(value) }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="10">10 días</SelectItem>
                        <SelectItem value="15">15 días</SelectItem>
                        <SelectItem value="30">30 días</SelectItem>
                        <SelectItem value="45">45 días</SelectItem>
                        <SelectItem value="60">60 días</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sessionsPerDay">Sesiones/día *</Label>
                    <Select value={formData.sessionsPerDay.toString()} onValueChange={(value) => setFormData(prev => ({ ...prev, sessionsPerDay: parseInt(value) }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 sesión</SelectItem>
                        <SelectItem value="2">2 sesiones</SelectItem>
                        <SelectItem value="3">3 sesiones</SelectItem>
                        <SelectItem value="4">4 sesiones</SelectItem>
                        <SelectItem value="5">5 sesiones</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Descripción (opcional)</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe objetivos específicos, áreas de enfoque, etc..."
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Material y Subtemas */}
          <div className="space-y-6">
            <Card>
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center space-x-2 mb-3">
                  <BookOpen className="w-4 h-4 text-medical-green-600" />
                  <h3 className="font-semibold">Material y Subtemas</h3>
                </div>

                <div className="space-y-2">
                  <Label>Subir Material (PDFs)</Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                    <input
                      type="file"
                      multiple
                      accept=".pdf"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="fileUpload"
                    />
                    <label htmlFor="fileUpload" className="cursor-pointer">
                      <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-600">Arrastra PDFs aquí o haz clic para subir</p>
                    </label>
                  </div>

                  {formData.uploadedFiles.length > 0 && (
                    <div className="space-y-2">
                      {formData.uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                          <span className="text-sm truncate">{file.name}</span>
                          <Button variant="ghost" size="sm" onClick={() => handleRemoveFile(index)}>
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Subtemas Específicos (opcional)</Label>
                  <div className="flex space-x-2">
                    <Input
                      placeholder="ej: Patogenia, Diagnóstico, Tratamiento..."
                      value={newSubtopic}
                      onChange={(e) => setNewSubtopic(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddSubtopic()}
                    />
                    <Button type="button" onClick={handleAddSubtopic} size="sm">
                      Agregar
                    </Button>
                  </div>

                  {formData.subtopics.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {formData.subtopics.map((subtopic, index) => (
                        <Badge key={index} variant="secondary" className="flex items-center space-x-1">
                          <span>{subtopic}</span>
                          <X className="w-3 h-3 cursor-pointer" onClick={() => handleRemoveSubtopic(index)} />
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Preview del Plan */}
            <Card className="bg-gray-50">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <Clock className="w-4 h-4 text-medical-blue-600" />
                  <h3 className="font-semibold">Vista Previa del Plan</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <p><strong>Total de sesiones:</strong> {formData.duration * formData.sessionsPerDay}</p>
                  <p><strong>Tiempo estimado:</strong> {Math.round(formData.duration * formData.sessionsPerDay * 0.75)} horas</p>
                  <p><strong>Modalidad:</strong> {formData.sessionsPerDay} sesión(es) diaria(s) por {formData.duration} días</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            onClick={handleGeneratePlan}
            disabled={!formData.mainTopic || !formData.specialty || !formData.level || isGenerating}
            className="bg-medical-blue-600 hover:bg-medical-blue-700"
          >
            {isGenerating ? (
              <>
                <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                Generando Plan con IA...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generar Plan con IA
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateStudyPlanDialog;