
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Brain } from "lucide-react";

const Navigation = () => {
  const location = useLocation();

  const navigationItems = [
    { name: "📊 Tablero", href: "/" },
    { name: "📋 Planes", href: "/planes" },
    { name: "📖 Estudio", href: "/estudio" },
    { name: "📈 Analíticas", href: "/analiticas" },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-medical-blue-800" />
          <h1 className="text-xl font-bold text-gray-900">MedStudy Pro</h1>
        </div>
        <div className="flex space-x-6">
          {navigationItems.map((item) => {
            const isActive = location.pathname === item.href;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-medical-blue-50 text-medical-blue-700 shadow-sm"
                    : "text-gray-600 hover:text-medical-blue-700 hover:bg-gray-50"
                )}
              >
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
