// src/pages/LandingPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
// If you want a logout button in the corner:
import LogoutButton from "../components/LogoutButton";

export default function LandingPage() {
  const navigate = useNavigate();

  // Local state for the new chatbot
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  // State to handle loading / disabled button
  const [creating, setCreating] = useState(false);

  const handleCreateClick = async () => {
    // 1. Ensure the user provided at least a name
    if (!name.trim()) {
      alert("Please provide a name for your chatbot.");
      return;
    }

    try {
      setCreating(true);

      // 2. Make the POST request to create the chatbot
      const body = { 
        name, 
        description // can be empty or optional 
      };
      const chatbot = await apiFetch("/api/chatbots", {
        method: "POST",
        body
      });

      // 3. Store the returned chatbot ID in sessionStorage
      sessionStorage.setItem("chatbot_id", chatbot.id);

      // 4. Go to the next page (e.g., Upload & Ingest)
      navigate("/upload-ingest");

    } catch (err) {
      console.error("Create chatbot error:", err);
      alert("Failed to create chatbot: " + err.message);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="page-container">
      {/* Optional: A row with Title + Logout button */}
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Create a New Chatbot</h1>
        <LogoutButton />
      </div>

      <p>Fill out the name and optional description for your chatbot.</p>

      <div style={{ margin: "20px 0" }}>
        <label>Chatbot Name:</label><br />
        <input
          type="text"
          placeholder="e.g. My Customer Support Bot"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={creating}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ margin: "20px 0" }}>
        <label>Description (optional):</label><br />
        <textarea
          placeholder="Describe your chatbot's purpose..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={creating}
          style={{ width: "100%", padding: "8px", height: "80px" }}
        />
      </div>

      <button className="btn" onClick={handleCreateClick} disabled={creating}>
        {creating ? "Creating..." : "Create Chatbot"}
      </button>
    </div>
  );
}