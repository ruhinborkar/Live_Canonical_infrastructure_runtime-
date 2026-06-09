import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import { RuntimeProvider } from "./hooks/useRuntime";
import { ToastProvider } from "./hooks/useToast";
import Dashboard from "./pages/Dashboard";
import EventsPage from "./pages/EventsPage";
import RunsPage from "./pages/RunsPage";
import VerifyPage from "./pages/VerifyPage";
import "./App.css";

export default function App() {
  return (
    <ToastProvider>
      <RuntimeProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/runs" element={<RunsPage />} />
              <Route path="/verify" element={<VerifyPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </RuntimeProvider>
    </ToastProvider>
  );
}
