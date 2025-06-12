import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Brain, 
  BarChart3, 
  BookOpen, 
  Calendar,
  Settings,
  User,
  Bell,
  Search
} from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3, current: location.pathname === '/dashboard' || location.pathname === '/' },
    { name: 'Planes', href: '/plans', icon: Calendar, current: location.pathname === '/plans' },
    { name: 'Estudiar', href: '/study', icon: BookOpen, current: location.pathname === '/study' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, current: location.pathname === '/analytics' },
  ];

  return (
    <div className="min-h-screen bg-medical-bg">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 medical-sidebar">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center px-6 border-b border-gray-200">
            <Brain className="h-8 w-8 text-primary-900" />
            <span className="ml-3 text-xl font-bold text-gray-900">MedStudy</span>
          </div>
          
          {/* Navigation */}
          <nav className="flex flex-1 flex-col p-4">
            <ul role="list" className="flex flex-1 flex-col gap-y-2">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`group flex gap-x-3 rounded-lg p-3 text-sm font-medium transition-all duration-200 ${
                      item.current
                        ? 'bg-primary-50 text-primary-900 shadow-sm'
                        : 'text-gray-600 hover:text-primary-900 hover:bg-gray-50'
                    }`}
                  >
                    <item.icon
                      className={`h-5 w-5 shrink-0 ${
                        item.current ? 'text-primary-900' : 'text-gray-400 group-hover:text-primary-900'
                      }`}
                    />
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
            
            {/* User section */}
            <div className="mt-auto">
              <div className="flex items-center gap-x-4 px-3 py-3 text-sm font-medium text-gray-900 hover:bg-gray-50 rounded-lg transition-colors duration-200">
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <User className="h-4 w-4 text-primary-900" />
                </div>
                <span className="sr-only">Tu perfil</span>
                <span className="truncate">Dr. Cruz Migueles</span>
              </div>
            </div>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Top header */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="relative flex flex-1 items-center">
              <Search className="pointer-events-none absolute left-3 h-5 w-5 text-gray-400" />
              <input
                type="search"
                placeholder="Buscar temas, planes..."
                className="block h-full w-full border-0 py-0 pl-10 pr-0 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm bg-transparent"
              />
            </div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 transition-colors duration-200"
              >
                <span className="sr-only">Ver notificaciones</span>
                <Bell className="h-6 w-6" />
              </button>
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 transition-colors duration-200"
              >
                <span className="sr-only">Configuración</span>
                <Settings className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-8">
          <div className="px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
