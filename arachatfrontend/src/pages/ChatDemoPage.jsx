// src/pages/ChatDemoPage.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import DemoChatInterface from "../components/DemoChatInterface";
import LogoutButton from "../components/LogoutButton";

/**
 * ChatDemoPage: uses DemoChatInterface but now calls the real usage-based route
 */
export default function ChatDemoPage() {
  const navigate = useNavigate();

  // We assume you stored the chatbot ID in sessionStorage (or fetch from an API)
  const chatbotId = sessionStorage.getItem("chatbot_id");

  const handleIntegrateClick = () => {
    if (!chatbotId) {
      alert("No chatbot ID found. Please create a chatbot first.");
      return;
    }
    navigate("/integration");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Chat Demo</h1>
        <LogoutButton />
      </div>
      <p>
        Here is a demo interface that still consumes real usage tokens from your plan.
      </p>

      <DemoChatInterface chatbotId={chatbotId} />

      <div style={{ marginTop: "20px" }}>
        <button className="btn" onClick={handleIntegrateClick}>
          Integrate with your website
        </button>
      </div>
    </div>
  );
}