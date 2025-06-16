
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface StatCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  color: "blue" | "green" | "turquoise" | "purple";
}

const StatCard = ({ title, value, icon: Icon, color }: StatCardProps) => {
  const colorClasses = {
    blue: "text-medical-blue-600 bg-gradient-to-br from-medical-blue-50 to-medical-blue-100",
    green: "text-medical-green-600 bg-gradient-to-br from-medical-green-50 to-medical-green-100",
    turquoise: "text-medical-turquoise-600 bg-gradient-to-br from-medical-turquoise-50 to-medical-turquoise-100",
    purple: "text-purple-600 bg-gradient-to-br from-purple-50 to-purple-100"
  };

  const shadowClasses = {
    blue: "shadow-medical-blue-100",
    green: "shadow-medical-green-100",
    turquoise: "shadow-medical-turquoise-100",
    purple: "shadow-purple-100"
  };

  return (
    <Card className={`bg-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 ${shadowClasses[color]}`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
            <p className="text-3xl font-bold text-gray-900 tracking-tight">{value}</p>
          </div>
          <div className={`p-4 rounded-xl ${colorClasses[color]} shadow-inner`}>
            <Icon className="w-7 h-7" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StatCard;
