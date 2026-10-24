import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import Navigation from "./components/shared/Navigation";

// Auth components
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import ProfilePage from "./pages/auth/ProfilePage";

// Interview components
import InterviewSetup from "./pages/interview/InterviewSetup";
import InterviewSession from "./pages/interview/InterviewSession";
import InterviewReport from "./pages/interview/InterviewReport";

// Resume components
import Home from "./pages/resume/Home";
import Upload from "./pages/resume/Upload";
import Dashboard from "./pages/resume/Dashboard";
import Recommendations from "./pages/resume/Recommendations";
import Simulation from "./pages/resume/Simulation";

// Providers
import { AuthProvider, useAuth } from "./context/AuthContext";
import { InterviewProvider } from "./context/InterviewContext";
import { ResultProvider } from "./context/ResultContext";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function AppContent() {
  return (
    <InterviewProvider>
      <ResultProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <Navigation />
            <Routes>
              {/* Auth Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

              {/* Resume Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/resume" element={<Navigate to="/" />} />
              <Route path="/resume/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
              <Route path="/resume/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/resume/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
              <Route path="/resume/simulation" element={<ProtectedRoute><Simulation /></ProtectedRoute>} />

              {/* Interview Routes */}
              <Route path="/interview" element={<ProtectedRoute><InterviewSetup /></ProtectedRoute>} />
              <Route path="/interview/session" element={<ProtectedRoute><InterviewSession /></ProtectedRoute>} />
              <Route path="/interview/report" element={<ProtectedRoute><InterviewReport /></ProtectedRoute>} />

              {/* Dashboard Route */}
              <Route path="/dashboard" element={<ProtectedRoute><Home /></ProtectedRoute>} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>

            <Toaster
              position="top-right"
              richColors
              theme="light"
              toastOptions={{
                classNames: {
                  toast: "bg-white shadow-lg rounded-lg",
                  success: "bg-green-50 border border-green-200",
                  error: "bg-red-50 border border-red-200",
                  info: "bg-blue-50 border border-blue-200",
                },
              }}
            />
          </div>
        </BrowserRouter>
      </ResultProvider>
    </InterviewProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
