
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Plans from "./pages/Plans";
import StudyPlanDetail from "./pages/StudyPlanDetail";
import Study from "./pages/Study";
import StudySession from "./pages/StudySession";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="plans" element={<Plans />} />
            <Route path="plan/:planId" element={<StudyPlanDetail />} />
            <Route path="study/:topicId" element={<StudySession />} />
            <Route path="study" element={<Study />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="settings" element={<Settings />} />
            {/* Rutas legacy en español */}
            <Route path="planes" element={<Plans />} />
            <Route path="estudio" element={<Study />} />
            <Route path="analiticas" element={<Analytics />} />
            <Route path="configuracion" element={<Settings />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
