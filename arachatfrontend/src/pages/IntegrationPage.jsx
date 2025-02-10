// src/pages/IntegrationPage.jsx

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import LogoutButton from "../components/LogoutButton";

export default function IntegrationPage() {
  const navigate = useNavigate();
  const [snippet, setSnippet] = useState("");
  const [loading, setLoading] = useState(false);

  // Retrieve the chatbotId from sessionStorage
  const chatbotId = sessionStorage.getItem("chatbot_id");

  // On component mount, fetch the snippet automatically
  useEffect(() => {
    const fetchSnippet = async () => {
      if (!chatbotId) {
        alert("No chatbot ID found in session. Please create a chatbot first.");
        // Navigate to "/" which loads MyChatbotsPage
        navigate("/");
        return;
      }
      setLoading(true);
      try {
        // GET /api/chatbots/{chatbotId}/snippet
        const data = await apiFetch(`/api/chatbots/${chatbotId}/snippet`, {
          method: "GET",
        });
        if (!data.snippet) {
          alert("No snippet returned from server.");
          return;
        }
        setSnippet(data.snippet);
      } catch (err) {
        console.error("Error fetching snippet:", err);
        alert(`Error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchSnippet();
  }, [chatbotId, navigate]);

  // Copy snippet to clipboard
  const handleCopySnippet = () => {
    if (!snippet) return;
    navigator.clipboard
      .writeText(snippet)
      .then(() => alert("Snippet copied to clipboard!"))
      .catch((err) => alert("Failed to copy snippet: " + err.message));
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Integration Snippet</h1>
        <LogoutButton />
      </div>

      {loading ? (
        <p>Loading snippet...</p>
      ) : (
        <>
          {snippet ? (
            <>
              <p>Copy and paste this code into your website's HTML:</p>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  background: "#f9f9f9",
                  padding: "10px",
                }}
              >
                {snippet}
              </pre>
              <button className="btn" onClick={handleCopySnippet}>
                Copy Snippet
              </button>
            </>
          ) : (
            <p>No snippet available yet.</p>
          )}
        </>
      )}

      <div style={{ marginTop: "30px" }}>
        <button className="btn" onClick={() => navigate("/chat-demo")}>
          Back to Demo
        </button>
        
        {/* New button to go back to the main page (MyChatbots) */}
        <button className="btn" onClick={() => navigate("/")}>
          Back to My Chatbots
        </button>
      </div>
    </div>
  );
}