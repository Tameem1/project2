// src/components/DemoChatInterface.jsx
import React, { useState, useEffect } from "react";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";

/**
 * DemoChatInterface:
 * - Previously used /api/demo/query with a 10-message limit
 * - NOW calls the same usage-based route as the normal ChatInterface: /api/{customerId}/{chatbotId}/query
 * - This way it consumes tokens from usage_token in the backend.
 */
export default function DemoChatInterface({ chatbotId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  // We'll store the real customer ID from the JWT
  const [customerId, setCustomerId] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      const claims = parseJwt(token);
      if (claims && claims.customer_id) {
        setCustomerId(claims.customer_id);
      } else {
        console.warn("No customer_id found in token claims!");
      }
    } else {
      console.warn("No token found in localStorage. Are you logged in?");
    }
  }, []);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    if (!chatbotId) {
      alert("No chatbot ID provided. Please create a chatbot first.");
      return;
    }
    if (!customerId) {
      alert("No customer ID found in JWT. Please log in first.");
      return;
    }

    // Show user message
    const userMessage = { text: inputValue, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    try {
      // Call the real usage-based endpoint:
      // POST /api/{customerId}/{chatbotId}/query
      const response = await apiFetch(`/api/${customerId}/${chatbotId}/query`, {
        method: "POST",
        body: { question: userMessage.text },
      });

      // e.g. response = { answer: "...", sources: [...] }
      const botMessage = {
        text: response.answer || "No answer found.",
        sender: "bot",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Query error:", err);
      setMessages((prev) => [
        ...prev,
        { text: "Error: " + err.message, sender: "bot" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="chat-container">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${msg.sender === "user" ? "user" : "bot"}`}
          >
            <strong>{msg.sender.toUpperCase()}:</strong> {msg.text}
          </div>
        ))}
      </div>

      <div style={{ marginTop: "10px" }}>
        <input
          type="text"
          value={inputValue}
          placeholder="Ask a question..."
          onChange={(e) => setInputValue(e.target.value)}
          disabled={loading}
        />
        <button className="btn" onClick={handleSend} disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}