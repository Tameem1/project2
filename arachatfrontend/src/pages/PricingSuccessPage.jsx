// src/pages/PricingSuccessPage.jsx
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { apiFetch } from "../utils/api";

export default function PricingSuccessPage() {
  const location = useLocation();
  const [verificationStatus, setVerificationStatus] = useState("loading"); 
  // "loading", "verified", or "failed"

  useEffect(() => {
    // Grab ?session_id=XYZ from the URL
    const queryParams = new URLSearchParams(location.search);
    const sessionId = queryParams.get("session_id");

    if (sessionId) {
      // Call our new verify endpoint
      apiFetch(`/api/pricing/verify_subscription?session_id=${sessionId}`)
        .then((response) => {
          // response might look like { subscriptionFound: true/false }
          if (response.subscriptionFound) {
            setVerificationStatus("verified");
          } else {
            setVerificationStatus("failed");
          }
        })
        .catch((err) => {
          console.error("Verification error:", err);
          setVerificationStatus("failed");
        });
    } else {
      // If no sessionId, we can't verify. Show fallback
      setVerificationStatus("failed");
    }
  }, [location.search]);

  if (verificationStatus === "loading") {
    return <div style={{ padding: "40px", textAlign: "center" }}>Verifying your subscription...</div>;
  }

  if (verificationStatus === "verified") {
    return (
      <div style={{ padding: "40px", textAlign: "center" }}>
        <h1>Payment Successful!</h1>
        <p>Your subscription is now active in our system. Thank you!</p>
      </div>
    );
  }

  // Otherwise, "failed"
  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h1>Payment Confirmed by Stripe</h1>
      <p>However, we haven't yet finalized your subscription in our system.</p>
      <p>
        Please <strong>contact support</strong> so we can fix this issue.
      </p>
    </div>
  );
}