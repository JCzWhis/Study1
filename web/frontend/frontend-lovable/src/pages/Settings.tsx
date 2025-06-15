
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Clock, 
  BookOpen,
  Shield,
  Download,
  Upload
} from "lucide-react";

const Settings = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-study-text mb-2">⚙️ Configuración</h1>
        <p className="text-gray-600">
          Personaliza tu experiencia de estudio médico
        </p>
      </div>

      <div className="space-y-8">
        {/* Perfil */}
        <Card className="bg-white study-shadow">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="w-5 h-5 text-medical-blue-600" />
              <span>Perfil de Usuario</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Nombre completo</Label>
                <Input id="name" placeholder="Dr. Juan Pérez" />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email">Correo electrónico</Label>
                <Input id="email" type="email" placeholder="doctor@email.com" />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="specialty">Especialidad principal</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar especialidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="medicina-interna">Medicina Interna</SelectItem>
                    <SelectItem value="cardiologia">Cardiología</SelectItem>
                    <SelectItem value="neurologia">Neurología</SelectItem>
                    <SelectItem value="reumatologia">Reumatología</SelectItem>
                    <SelectItem value="endocrinologia">Endocrinología</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="level">Nivel de experiencia</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar nivel" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="estudiante">Estudiante de Medicina</SelectItem>
                    <SelectItem value="residente">Médico Residente</SelectItem>
                    <SelectItem value="especialista">Médico Especialista</SelectItem>
                    <SelectItem value="consultor">Médico Consultor</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="flex justify-end">
              <Button className="bg-medical-blue-700 hover:bg-medical-blue-800">
                Guardar Cambios
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Preferencias de estudio */}
        <Card className="bg-white study-shadow">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-medical-green-600" />
              <span>Preferencias de Estudio</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="daily-goal">Meta diaria (minutos)</Label>
                <Input id="daily-goal" type="number" placeholder="180" />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="session-length">Duración de sesión predeterminada</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="45 minutos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">30 minutos</SelectItem>
                    <SelectItem value="45">45 minutos</SelectItem>
                    <SelectItem value="60">60 minutos</SelectItem>
                    <SelectItem value="90">90 minutos</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="recall-interval">Intervalo de Active Recall</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Cada 10 minutos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5">Cada 5 minutos</SelectItem>
                    <SelectItem value="10">Cada 10 minutos</SelectItem>
                    <SelectItem value="15">Cada 15 minutos</SelectItem>
                    <SelectItem value="20">Cada 20 minutos</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="difficulty">Nivel de dificultad preferido</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Intermedio" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basico">Básico</SelectItem>
                    <SelectItem value="intermedio">Intermedio</SelectItem>
                    <SelectItem value="avanzado">Avanzado</SelectItem>
                    <SelectItem value="mixto">Mixto</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Opciones de Aprendizaje</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="auto-advance">Avance automático entre temas</Label>
                    <p className="text-sm text-gray-600">Pasar automáticamente al siguiente tema al completar uno</p>
                  </div>
                  <Switch id="auto-advance" />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="spaced-repetition">Repetición espaciada activa</Label>
                    <p className="text-sm text-gray-600">Programar revisiones basadas en tu confianza</p>
                  </div>
                  <Switch id="spaced-repetition" defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="adaptive-difficulty">Dificultad adaptativa</Label>
                    <p className="text-sm text-gray-600">Ajustar automáticamente la dificultad según tu rendimiento</p>
                  </div>
                  <Switch id="adaptive-difficulty" defaultChecked />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notificaciones */}
        <Card className="bg-white study-shadow">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bell className="w-5 h-5 text-medical-turquoise-600" />
              <span>Notificaciones</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="study-reminders">Recordatorios de estudio</Label>
                  <p className="text-sm text-gray-600">Recibir notificaciones para sesiones programadas</p>
                </div>
                <Switch id="study-reminders" defaultChecked />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="review-alerts">Alertas de revisión</Label>
                  <p className="text-sm text-gray-600">Notificar cuando es momento de revisar temas</p>
                </div>
                <Switch id="review-alerts" defaultChecked />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="goal-progress">Progreso de metas</Label>
                  <p className="text-sm text-gray-600">Actualizaciones sobre el progreso de tus metas diarias</p>
                </div>
                <Switch id="goal-progress" />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="achievements">Logros y celebraciones</Label>
                  <p className="text-sm text-gray-600">Notificar cuando alcances nuevos logros</p>
                </div>
                <Switch id="achievements" defaultChecked />
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Horarios de Notificación</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="morning-time">Recordatorio matutino</Label>
                  <Input id="morning-time" type="time" defaultValue="08:00" />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="evening-time">Recordatorio vespertino</Label>
                  <Input id="evening-time" type="time" defaultValue="19:00" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Datos y privacidad */}
        <Card className="bg-white study-shadow">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-purple-600" />
              <span>Datos y Privacidad</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="analytics">Analíticas de uso</Label>
                  <p className="text-sm text-gray-600">Permitir recopilación de datos para mejorar la experiencia</p>
                </div>
                <Switch id="analytics" defaultChecked />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="sync">Sincronización en la nube</Label>
                  <p className="text-sm text-gray-600">Sincronizar datos entre dispositivos</p>
                </div>
                <Switch id="sync" defaultChecked />
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Gestión de Datos</h3>
              
              <div className="flex flex-col sm:flex-row gap-3">
                <Button variant="outline" className="flex items-center space-x-2">
                  <Download className="w-4 h-4" />
                  <span>Exportar mis datos</span>
                </Button>
                
                <Button variant="outline" className="flex items-center space-x-2">
                  <Upload className="w-4 h-4" />
                  <span>Importar datos</span>
                </Button>
                
                <Button variant="destructive" className="sm:ml-auto">
                  Eliminar todos los datos
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Botón de guardar global */}
        <div className="flex justify-end space-x-4">
          <Button variant="outline">
            Restablecer valores por defecto
          </Button>
          <Button className="bg-medical-blue-700 hover:bg-medical-blue-800">
            Guardar toda la configuración
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
