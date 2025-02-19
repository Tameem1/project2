// src/pages/CancelPlanPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";
import LogoutButton from "../components/LogoutButton";

export default function CancelPlanPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleCancel = async () => {
    setLoading(true);
    setMessage("");

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Not logged in");
        navigate("/login");
        return;
      }
      const claims = parseJwt(token);
      const customer_id = claims.customer_id;

      const res = await apiFetch("/api/pricing/cancel", {
        method: "POST",
        body: { customer_id },
      });
      setMessage(res.message || "Cancellation initiated.");
    } catch (err) {
      console.error("Cancellation error:", err);
      setMessage(err.message || "Failed to cancel subscription.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Cancel Subscription</h1>
        <LogoutButton />
      </div>
      <p>
        If you wish to cancel your subscription, click the button below. Your subscription will be canceled at the end of your billing period.
      </p>
      {message && (
        <p style={{ color: "green", marginBottom: "10px" }}>{message}</p>
      )}
      <button className="btn" onClick={handleCancel} disabled={loading}>
        {loading ? "Processing..." : "Cancel Subscription"}
      </button>
      <div style={{ marginTop: "20px" }}>
        <button className="btn" onClick={() => navigate("/")}>
          Back to My Chatbots
        </button>
      </div>
    </div>
  );
}