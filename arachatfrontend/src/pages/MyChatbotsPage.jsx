// src/pages/MyChatbotsPage.jsx

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import LogoutButton from "../components/LogoutButton";
import { parseJwt } from "../utils/jwt";

export default function MyChatbotsPage() {
  const navigate = useNavigate();
  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);

      // 1) Grab JWT from localStorage
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No token found, user not logged in.");
      }
      const claims = parseJwt(token);
      if (!claims || !claims.customer_id) {
        throw new Error("No customer_id in token claims.");
      }
      const customerId = claims.customer_id;

      // 2) Fetch the user's chatbots
      const botsData = await apiFetch("/api/chatbots");
      setChatbots(botsData);

      // 3) Also fetch usage info
      const usageData = await apiFetch(`/api/${customerId}/usage`);
      setUsage(usageData);

    } catch (error) {
      console.error("Failed to fetch chatbots or usage:", error);
      alert("Failed to load chatbots or usage. " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChatbot = async (chatbotId) => {
    if (!window.confirm("Are you sure you want to delete this chatbot?")) return;
    try {
      // DELETE /api/chatbots/{chatbotId}
      await apiFetch(`/api/chatbots/${chatbotId}`, {
        method: "DELETE",
      });
      alert("Chatbot deleted successfully!");
      // Re-fetch the chatbots list
      fetchAllData();
    } catch (err) {
      console.error("Error deleting chatbot:", err);
      alert("Failed to delete chatbot: " + err.message);
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>My Chatbots</h1>
        <LogoutButton />
      </div>

      {/* Show usage info if we have it */}
      {usage && (
        <div style={{ margin: "10px 0", textAlign: "left" }}>
          <p><strong>Total Tokens Used:</strong> {usage.tokens_used_total}</p>
          <p><strong>Tokens Remaining:</strong> {usage.tokens_remaining}</p>
          <p>Input Tokens: {usage.tokens_used_input}, Output Tokens: {usage.tokens_used_output}</p>
        </div>
      )}

      <button className="btn" onClick={() => navigate("/create-chatbot")}>
        Create New Chatbot
      </button>

      {loading ? (
        <p>Loading chatbots...</p>
      ) : (
        <div>
          {chatbots.length === 0 ? (
            <p>No chatbots found. Create one!</p>
          ) : (
            chatbots.map((chatbot) => (
              <div key={chatbot.id} className="chatbot-item">
                {/* Clicking name goes to ChatHistoryPage */}
                <h3
                  style={{ cursor: "pointer", marginBottom: "5px" }}
                  onClick={() => navigate(`/chatbots/${chatbot.id}`)}
                >
                  {chatbot.name}
                </h3>
                <p>{chatbot.description}</p>
                <button
                  className="btn"
                  style={{ backgroundColor: "red" }}
                  onClick={() => handleDeleteChatbot(chatbot.id)}
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}