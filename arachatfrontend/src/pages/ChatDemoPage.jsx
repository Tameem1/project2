// src/pages/ChatDemoPage.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import DemoChatInterface from "../components/DemoChatInterface";
import LogoutButton from "../components/LogoutButton";

export default function ChatDemoPage() {
  const navigate = useNavigate();

  // We assume chatbot_id was stored in sessionStorage
  const chatbotId = sessionStorage.getItem("chatbot_id");

  const handleIntegrateClick = () => {
    // Make sure we have a chatbot ID
    if (!chatbotId) {
      alert("No chatbot ID found. Please create a chatbot first.");
      return;
    }
    // Navigate to /integration
    navigate("/integration");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Chat Demo (10-message limit)</h1>
        <LogoutButton />
      </div>
      <p>Test your chatbot in this limited demo environment (10 messages).</p>

      <DemoChatInterface chatbotId={chatbotId} />

      <div style={{ marginTop: "20px" }}>
        <button className="btn" onClick={handleIntegrateClick}>
          Integrate with your website
        </button>
      </div>
    </div>
  );
}