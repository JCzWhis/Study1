
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookOpen, Clock, Star } from "lucide-react";

interface PlanCardProps {
  title: string;
  description: string;
  progress: number;
  specialty: string;
  studyTime: string;
}

const PlanCard = ({ title, description, progress, specialty, studyTime }: PlanCardProps) => {
  const getProgressColor = (progress: number) => {
    if (progress >= 80) return "from-medical-green-500 to-medical-green-600";
    if (progress >= 50) return "from-medical-turquoise-500 to-medical-turquoise-600";
    return "from-medical-blue-500 to-medical-blue-600";
  };

  const getProgressBadge = (progress: number) => {
    if (progress >= 80) return { text: "Casi completado", color: "bg-medical-green-100 text-medical-green-800" };
    if (progress >= 50) return { text: "En progreso", color: "bg-medical-turquoise-100 text-medical-turquoise-800" };
    return { text: "Comenzado", color: "bg-medical-blue-100 text-medical-blue-800" };
  };

  const progressBadge = getProgressBadge(progress);

  return (
    <Card className="bg-white border-0 shadow-lg hover:shadow-2xl transition-all duration-300 group overflow-hidden">
      <div className={`h-1 bg-gradient-to-r ${getProgressColor(progress)}`}></div>
      
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <CardTitle className="text-xl text-study-text mb-2 group-hover:text-medical-blue-800 transition-colors">
              {title}
            </CardTitle>
            <p className="text-sm text-gray-600 mb-3 leading-relaxed">{description}</p>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="border-medical-blue-200 text-medical-blue-700 bg-medical-blue-50">
                {specialty}
              </Badge>
              <Badge className={`text-xs ${progressBadge.color} border-0`}>
                {progressBadge.text}
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-5">
          <div>
            <div className="flex items-center justify-between text-sm mb-3">
              <span className="text-gray-600 font-medium">Progreso del plan</span>
              <span className="font-bold text-gray-900">{progress}%</span>
            </div>
            <div className="relative">
              <Progress value={progress} className="h-3 bg-gray-100" />
              <div 
                className={`absolute top-0 left-0 h-3 rounded-full bg-gradient-to-r ${getProgressColor(progress)} transition-all duration-500`}
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="w-4 h-4 mr-2" />
              <span className="font-medium">{studyTime}</span>
            </div>
            <div className="flex items-center text-sm text-medical-blue-600">
              <Star className="w-4 h-4 mr-1 fill-current" />
              <span className="font-medium">4.8</span>
            </div>
          </div>
          
          <Button 
            className="w-full bg-gradient-to-r from-medical-blue-700 to-medical-blue-800 hover:from-medical-blue-800 hover:to-medical-blue-900 text-white shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Iniciar Estudio
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PlanCard;
