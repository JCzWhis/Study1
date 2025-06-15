
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookOpen, Clock } from "lucide-react";

interface StudyPlanCardProps {
  title: string;
  progress: number;
  timeLeft: string;
  specialty: string;
}

const StudyPlanCard = ({ title, progress, timeLeft, specialty }: StudyPlanCardProps) => {
  return (
    <Card className="bg-white study-shadow hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-study-text mb-1">{title}</h3>
            <Badge variant="outline" className="text-xs border-medical-blue-200 text-medical-blue-700">
              {specialty}
            </Badge>
          </div>
          <Button variant="outline" size="sm" className="border-medical-blue-200 text-medical-blue-700 hover:bg-medical-blue-50">
            <BookOpen className="w-4 h-4 mr-1" />
            Continuar
          </Button>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Progreso</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
          
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="w-4 h-4 mr-1" />
            <span>Tiempo restante: {timeLeft}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StudyPlanCard;
