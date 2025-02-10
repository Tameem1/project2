// src/components/DemoChatInterface.jsx
import React, { useState, useEffect } from "react";
import { apiFetch } from "../utils/api";

/**
 * DemoChatInterface:
 * - Calls /api/demo/query for a specific chatbotId
 * - Expects a 10-message limit
 */
export default function DemoChatInterface({ chatbotId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    if (!chatbotId) {
      alert("No chatbotId provided. Please ensure you created/stored a chatbot first.");
      return;
    }

    // Show user message
    const userMessage = { text: inputValue, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    try {
      // Call the demo endpoint
      const response = await apiFetch(`/api/demo/query`, {
        method: "POST",
        body: {
          chatbot_id: chatbotId, 
          question: userMessage.text
        }
      });
      // Suppose the backend returns { answer: "...", limit_reached: false }

      if (response.limit_reached) {
        // If user hits the 10-message limit
        const botMessage = {
          text: response.answer || "Demo limit reached. Please create a full chatbot to continue.",
          sender: "bot"
        };
        setMessages((prev) => [...prev, botMessage]);
        // Optionally disable the input, or show a special alert
        return;
      }

      // Otherwise, normal scenario
      const botMessage = {
        text: response.answer || "No answer found.",
        sender: "bot"
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Demo query error:", err);
      setMessages((prev) => [...prev, {
        text: "Error during demo query: " + err.message,
        sender: "bot"
      }]);
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
            <strong>{msg.sender.toUpperCase()}:</strong> {msg.text}
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