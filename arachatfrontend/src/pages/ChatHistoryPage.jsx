import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { apiFetch } from "../utils/api";
import LogoutButton from "../components/LogoutButton";

export default function ChatHistoryPage() {
  const { chatbotId } = useParams();
  const [chatHistory, setChatHistory] = useState([]);
  const [tokensUsed, setTokensUsed] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await apiFetch(`/api/chatbots/${chatbotId}`);
        setChatHistory(data.history || []);
        setTokensUsed(data.tokens_used || 0);
      } catch (error) {
        console.error("Error fetching data:", error);
        alert("Failed to load chat history.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [chatbotId]);

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Chat History</h1>
        <LogoutButton />
      </div>
      <p>Tokens used: {tokensUsed}</p>
      {loading ? (
        <p>Loading chat history...</p>
      ) : (
        <div className="chat-history">
          {chatHistory.map((chat, index) => (
            <div key={index} className="chat-message">
              <p><strong>{chat.sender}:</strong> {chat.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}