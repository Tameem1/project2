// src/pages/PricingSuccessPage.jsx
import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

export default function PricingSuccessPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // Optionally, read the session_id:
  // const queryParams = new URLSearchParams(location.search);
  // const sessionId = queryParams.get("session_id");

  function handleGoBack() {
    navigate("/");
  }

  return (
    <div className="page-container">
      <h1>Payment Successful</h1>
      <p>Your subscription has been processed. Thank you!</p>
      <p>
        We’re applying your new plan in the background. You can click below
        to return to your chatbots. (The webhook will handle your token update.)
      </p>
      <button className="btn" onClick={handleGoBack}>
        Go to My Chatbots
      </button>
    </div>
  );
}