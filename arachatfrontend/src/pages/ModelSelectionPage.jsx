// src/pages/ModelSelectionPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import LogoutButton from "../components/LogoutButton"; // optional

export default function ModelSelectionPage() {
  const navigate = useNavigate();
  const [selectedModel, setSelectedModel] = useState("");

  // If your backend has an endpoint to store the chosen model, 
  // you could call it inside handleContinue:
  //   await apiFetch(`/api/chatbots/${chatbotId}/set-model`, { method: "PATCH", body: { model: selectedModel } });

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };

  const handleContinue = async () => {
    if (!selectedModel) {
      alert("Please select a model first!");
      return;
    }
    alert(`Selected model: ${selectedModel}`);
    navigate("/chat-demo");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Model Selection</h1>
        <LogoutButton />
      </div>
      <p>Select the model you want to use for your chatbot.</p>

      <select value={selectedModel} onChange={handleModelChange}>
        <option value="">-- Select a Model --</option>
        <option value="gpt-3.5-turbo">OpenAI GPT-3.5 Turbo</option>
        <option value="bard">Google Bard</option>
        <option value="fireworks-32b-qwen">Fireworks 32B Qwen</option>
        {/* Add more model options as needed */}
      </select>

      <div style={{ marginTop: "20px" }}>
        <button className="btn" onClick={handleContinue}>
          Continue
        </button>
      </div>
    </div>
  );
}