import { useEffect } from "react";
import "@/App.css";
import "@/os/os.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Experience from "@/pages/Experience";
import Admin from "@/pages/Admin";
import RouteTransition from "@/components/RouteTransition";
import { Toaster } from "sonner";

function App() {
  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <RouteTransition />
        <Routes>
          <Route path="/" element={<Experience />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </BrowserRouter>
      <Toaster
        theme="dark"
        position="top-center"
        toastOptions={{
          style: {
            background: "rgba(10,10,12,0.85)",
            color: "#fff",
            border: "1px solid rgba(255,255,255,0.08)",
            backdropFilter: "blur(20px)",
          },
        }}
      />
    </div>
  );
}

export default App;
