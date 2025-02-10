import React from "react";
import { Routes, Route } from "react-router-dom";

import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";

// Protected pipeline pages
import LandingPage from "./pages/LandingPage";
import UploadIngestPage from "./pages/UploadIngestPage";
import ModelSelectionPage from "./pages/ModelSelectionPage";
import ChatDemoPage from "./pages/ChatDemoPage";
import IntegrationPage from "./pages/IntegrationPage";

import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <div className="app-container">
      <Routes>
        {/* Public routes (no auth required) */}
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes (require login) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <LandingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upload-ingest"
          element={
            <ProtectedRoute>
              <UploadIngestPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/model-selection"
          element={
            <ProtectedRoute>
              <ModelSelectionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat-demo"
          element={
            <ProtectedRoute>
              <ChatDemoPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/integration"
          element={
            <ProtectedRoute>
              <IntegrationPage />
            </ProtectedRoute>
          }
        />

        {/* Optionally, redirect unknown routes to /login or 404 */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </div>
  );
}

export default App;