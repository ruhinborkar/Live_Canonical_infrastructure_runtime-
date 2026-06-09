import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import ProtectedRoute from "./components/ProtectedRoute";
import AppShell from "./components/layout/AppShell";
import { RuntimeProvider } from "./hooks/RuntimeProvider";
import { ToastProvider } from "./hooks/useToast";
import { AuthProvider } from "./providers/AuthProvider";
import { QueryProvider } from "./providers/QueryProvider";
import Dashboard from "./pages/Dashboard";
import EventsPage from "./pages/EventsPage";
import Login from "./pages/Login";
import Reports from "./pages/Reports";
import RunsPage from "./pages/RunsPage";
import Settings from "./pages/Settings";
import VerifyPage from "./pages/VerifyPage";

export default function App() {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <AuthProvider>
          <ToastProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route element={<ProtectedRoute />}>
                  <Route
                    element={
                      <RuntimeProvider>
                        <AppShell />
                      </RuntimeProvider>
                    }
                  >
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/events" element={<EventsPage />} />
                    <Route path="/runs" element={<RunsPage />} />
                    <Route path="/verify" element={<VerifyPage />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/settings" element={<Settings />} />
                  </Route>
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </ToastProvider>
        </AuthProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
}
