// arachatfrontend/src/App.js
import React from "react";
import { Routes, Route } from "react-router-dom";

// Import your pages
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import MyChatbotsPage from "./pages/MyChatbotsPage";
import LandingPage from "./pages/LandingPage";
import ChatHistoryPage from "./pages/ChatHistoryPage";
import DocumentManagementPage from "./pages/DocumentManagementPage";
import UploadIngestPage from "./pages/UploadIngestPage";
import ModelSelectionPage from "./pages/ModelSelectionPage";
import ChatDemoPage from "./pages/ChatDemoPage";
import IntegrationPage from "./pages/IntegrationPage";
import PricingPage from "./pages/PricingPage"; // pricing page import
import ProtectedRoute from "./components/ProtectedRoute";
import NavBar from "./components/NavBar"; // new NavBar import
import PricingSuccessPage from "./pages/PricingSuccessPage";
import CancelPlanPage from "./pages/CancelPlanPage";
import UserProfilePage from "./pages/UserProfilePage"; 

function App() {
  return (
    <div className="app-container">
      <NavBar />
      <Routes>
        {/* Public routes */}
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes */}
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
        <Route
          path="/pricing"
          element={
            <ProtectedRoute>
              <PricingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <UserProfilePage />
            </ProtectedRoute>
          }
        />
        {/* Fallback */}
        <Route path="*" element={<LoginPage />} />
        <Route
          path="/pricing/success"
          element={
            <ProtectedRoute>
              <PricingSuccessPage />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/cancel-plan" 
          element={
            <ProtectedRoute>
              <CancelPlanPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;