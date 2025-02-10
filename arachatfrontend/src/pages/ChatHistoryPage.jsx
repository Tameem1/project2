// src/pages/ChatHistoryPage.jsx


import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";
import LogoutButton from "../components/LogoutButton";

export default function ChatHistoryPage() {
  const { chatbotId } = useParams();
  const navigate = useNavigate();

  // States for chat history
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // States for snippet modal
  const [snippetLoading, setSnippetLoading] = useState(false);
  const [snippet, setSnippet] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Load the chat history on mount
  useEffect(() => {
    const fetchHistory = async () => {
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
    };
    fetchHistory();
  }, [chatbotId]);

  // Show snippet button handler
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
      setIsModalOpen(true); // Open the modal
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

  // (Optional) Clear chat history
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
  const handleModifyDocuments = () => {
    navigate(`/chatbots/${chatbotId}/documents`);
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Chat History</h1>
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

      {/* Clear History Button (optional) */}
      <button onClick={handleClearHistory} style={{ margin: "10px" }}>
        Clear Chat History
      </button>

      {/* Show Snippet Button -> opens modal */}
      <button onClick={handleShowSnippet} disabled={snippetLoading} style={{ margin: "10px" }}>
        {snippetLoading ? "Loading Snippet..." : "Show Snippet"}
      </button>
      {/* Button to modify documents */}
      <button onClick={handleModifyDocuments}>
        Modify Documents
      </button>
      {/* MODAL OVERLAY (only if isModalOpen) */}
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
          {/* Modal content box */}
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
            {/* Close Button */}
            <button onClick={() => setIsModalOpen(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}