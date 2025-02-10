import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import LogoutButton from "../components/LogoutButton";

export default function MyChatbotsPage() {
  const navigate = useNavigate();
  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchChatbots = async () => {
      try {
        setLoading(true);
        const data = await apiFetch("/api/chatbots");
        setChatbots(data);
      } catch (error) {
        console.error("Failed to fetch chatbots:", error);
        alert("Failed to load chatbots.");
      } finally {
        setLoading(false);
      }
    };
    fetchChatbots();
  }, []);

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>My Chatbots</h1>
        <LogoutButton />
      </div>
      <button
        className="btn"
        onClick={() => navigate("/create-chatbot")}
      >
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
              <div
                key={chatbot.id}
                className="chatbot-item"
                onClick={() => navigate(`/chatbots/${chatbot.id}`)}
              >
                <h3>{chatbot.name}</h3>
                <p>{chatbot.description}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}