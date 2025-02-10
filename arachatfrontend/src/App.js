// src/App.js

import React from "react";
import { Routes, Route } from "react-router-dom";

// Public pages
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";

// Protected pipeline pages
import MyChatbotsPage from "./pages/MyChatbotsPage";
import LandingPage from "./pages/LandingPage";
import UploadIngestPage from "./pages/UploadIngestPage";
import ModelSelectionPage from "./pages/ModelSelectionPage";
import ChatDemoPage from "./pages/ChatDemoPage";
import IntegrationPage from "./pages/IntegrationPage";
import ChatHistoryPage from "./pages/ChatHistoryPage";
import DocumentManagementPage from "./pages/DocumentManagementPage";

// Higher-order component to wrap protected routes
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <div className="app-container">
      <Routes>
        {/* Public routes (no auth required) */}
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes (user must be logged in) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MyChatbotsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/create-chatbot"
          element={
            <ProtectedRoute>
              <LandingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chatbots/:chatbotId"
          element={
            <ProtectedRoute>
              <ChatHistoryPage />
            </ProtectedRoute>
          }
        />
        {/* NEW ROUTE: Document management */}
        <Route
          path="/chatbots/:chatbotId/documents"
          element={
            <ProtectedRoute>
              <DocumentManagementPage />
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

        {/* Fallback: If no route matches, go to Login */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </div>
  );
}

export default App;