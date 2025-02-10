// src/components/ChatInterface.jsx
import React, { useState, useEffect } from "react";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";  // The same helper we used for ingest

/**
 * ChatInterface
 * @param {string} chatbotId - The ID of the chatbot (UUID) 
 */
export default function ChatInterface({ chatbotId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  // We'll store the real customer ID in state
  const [customerId, setCustomerId] = useState("");

  // On mount, parse the JWT from localStorage to get the real customer_id
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
      console.warn("No token found in localStorage. User might not be logged in.");
    }
  }, []);

  // Handle sending a query to the chatbot
  const handleSend = async () => {
    if (!inputValue.trim()) return;
    if (!customerId) {
      alert("Customer ID not available. Are you logged in with a valid token?");
      return;
    }

    // Add user message to chat
    const userMessage = { text: inputValue, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);

    setInputValue("");
    setLoading(true);

    try {
      // POST /api/{customerId}/{chatbotId}/query
      const response = await apiFetch(`/api/${customerId}/${chatbotId}/query`, {
        method: "POST",
        body: { question: userMessage.text }
      });
      // e.g. response = { answer: "some text", sources: [...], ... }

      const botMessage = {
        text: response.answer || "No answer found.",
        sender: "bot"
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Query error:", err);
      const errorMsg = { text: "Error retrieving answer", sender: "bot" };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Chat display */}
      <div className="chat-container">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${msg.sender === "user" ? "user" : "bot"}`}
          >
            <strong>{msg.sender.toUpperCase()}: </strong>
            {msg.text}
          </div>
        ))}
      </div>

      {/* Input and send button */}
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