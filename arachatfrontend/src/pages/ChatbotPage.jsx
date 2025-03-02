// src/pages/ChatbotPage.jsx

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";
import LogoutButton from "../components/LogoutButton";

export default function ChatbotPage() {
  const { chatbotId } = useParams();
  const navigate = useNavigate();

  // Chatbot name for the page title
  const [chatbotName, setChatbotName] = useState("Chatbot");

  // Chat history
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Snippet modal
  const [snippetLoading, setSnippetLoading] = useState(false);
  const [snippet, setSnippet] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 1. Load the chatbot name, 2. Load chat history
  useEffect(() => {
    fetchChatbotName();
    fetchHistory();
    // eslint-disable-next-line
  }, [chatbotId]);

  /**
   * Fetch all chatbots, then find the one with this chatbotId.
   * Update the page title with that chatbot's name.
   */
  async function fetchChatbotName() {
    try {
      // GET /api/chatbots returns array of { id, name, description, ... }
      const chatbots = await apiFetch("/api/chatbots");
      const found = chatbots.find((cb) => cb.id === chatbotId);
      if (found) {
        setChatbotName(found.name || "Chatbot");
      } else {
        console.warn("Could not find chatbot with ID:", chatbotId);
      }
    } catch (err) {
      console.error("Failed to fetch chatbot name:", err);
    }
  }

  async function fetchHistory() {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token in localStorage.");

      const claims = parseJwt(token);
      if (!claims || !claims.customer_id) {
        throw new Error("No customer_id in token claims.");
      }
      const customerId = claims.customer_id;

      // GET /api/{customerId}/{chatbotId}/history
      const data = await apiFetch(`/api/${customerId}/${chatbotId}/history`);
      setChatHistory(data.chat_history || []);
    } catch (err) {
      console.error("Error fetching chat history:", err);
      alert(`Failed to load chat history: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  // Show snippet button
  const handleShowSnippet = async () => {
    try {
      setSnippetLoading(true);
      // GET /api/chatbots/{chatbotId}/snippet
      const data = await apiFetch(`/api/chatbots/${chatbotId}/snippet`);
      if (!data.snippet) {
        alert("No snippet returned from server.");
        return;
      }
      setSnippet(data.snippet);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error fetching snippet:", error);
      alert("Failed to load snippet: " + error.message);
    } finally {
      setSnippetLoading(false);
    }
  };

  // Copy snippet to clipboard
  const handleCopySnippet = async () => {
    if (!snippet) return;
    try {
      await navigator.clipboard.writeText(snippet);
      alert("Snippet copied to clipboard!");
    } catch (err) {
      alert("Failed to copy snippet: " + err.message);
    }
  };

  // Clear chat history
  const handleClearHistory = async () => {
    try {
      const token = localStorage.getItem("token");
      const claims = parseJwt(token);
      const customerId = claims.customer_id;

      await apiFetch(`/api/${customerId}/${chatbotId}/history`, { method: "DELETE" });
      setChatHistory([]);
      alert("Chat history cleared.");
    } catch (error) {
      console.error("Error clearing chat history:", error);
      alert(`Failed to clear chat history: ${error.message}`);
    }
  };

  // Modify Documents
  const handleModifyDocuments = () => {
    navigate(`/chatbots/${chatbotId}/documents`);
  };

  // Test Chatbot
  const handleTestChatbot = () => {
    sessionStorage.setItem("chatbot_id", chatbotId);
    navigate("/chat-demo");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {/* Title => e.g. "Support Bot Chatbot" */}
        <h1>{chatbotName} Chatbot</h1>
        <LogoutButton />
      </div>

      {loading ? (
        <p>Loading chat history...</p>
      ) : (
        <div className="chat-history">
          {chatHistory.map((entry) => (
            <div key={entry.id} className="chat-message">
              <p><strong>User:</strong> {entry.question}</p>
              <p><strong>Bot:</strong> {entry.answer}</p>
              <small>{entry.timestamp}</small>
            </div>
          ))}
        </div>
      )}

      <button onClick={handleClearHistory} style={{ margin: "10px" }}>
        Clear Chat History
      </button>
      <button onClick={handleShowSnippet} disabled={snippetLoading} style={{ margin: "10px" }}>
        {snippetLoading ? "Loading Snippet..." : "Show Snippet"}
      </button>
      <button onClick={handleModifyDocuments} style={{ margin: "10px" }}>
        Modify Documents
      </button>
      <button onClick={handleTestChatbot} style={{ margin: "10px" }}>
        Test This Chatbot
      </button>

      {/* Snippet Modal Overlay */}
      {isModalOpen && (
        <div
          style={{
            position: "fixed",
            top: 0, left: 0,
            width: "100%", height: "100%",
            background: "rgba(0, 0, 0, 0.4)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 9999
          }}
        >
          <div
            style={{
              background: "#fff",
              padding: "20px",
              borderRadius: "8px",
              width: "80%",
              maxWidth: "600px",
              position: "relative"
            }}
          >
            <h2>Integration Snippet</h2>
            <pre
              style={{
                background: "#f9f9f9",
                padding: "10px",
                whiteSpace: "pre-wrap",
                overflowX: "auto",
                marginBottom: "10px"
              }}
            >
              {snippet}
            </pre>
            <button onClick={handleCopySnippet} style={{ marginRight: "10px" }}>
              Copy Snippet
            </button>
            <button onClick={() => setIsModalOpen(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}