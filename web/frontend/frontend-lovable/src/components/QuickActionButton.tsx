
import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";

interface QuickActionButtonProps {
  icon: LucideIcon;
  text: string;
  onClick?: () => void;
}

const QuickActionButton = ({ icon: Icon, text, onClick }: QuickActionButtonProps) => {
  return (
    <Button
      variant="outline"
      className="w-full justify-start text-left p-6 h-auto border-0 bg-white hover:bg-gradient-to-r hover:from-medical-blue-50 hover:to-medical-turquoise-50 shadow-md hover:shadow-lg transition-all duration-300 group"
      onClick={onClick}
    >
      <div className="flex items-center w-full">
        <div className="p-2 rounded-lg bg-gradient-to-br from-medical-blue-100 to-medical-blue-200 group-hover:from-medical-blue-200 group-hover:to-medical-blue-300 transition-all duration-300">
          <Icon className="w-5 h-5 text-medical-blue-600" />
        </div>
        <span className="text-gray-700 ml-4 font-medium group-hover:text-medical-blue-800 transition-colors">
          {text}
        </span>
      </div>
    </Button>
  );
};

export default QuickActionButton;
