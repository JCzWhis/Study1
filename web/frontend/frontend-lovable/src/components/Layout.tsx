
import { Outlet } from "react-router-dom";
import Navigation from "./Navigation";

const Layout = () => {
  return (
    <div className="min-h-screen bg-study-bg">
      <Navigation />
      <main className="pt-16">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
