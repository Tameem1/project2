// src/pages/UserProfilePage.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LogoutButton from "../components/LogoutButton";
import { parseJwt } from "../utils/jwt";
import { apiFetch } from "../utils/api";

export default function UserProfilePage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  // Data from /api/user/profile
  const [username, setUsername] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [businessName, setBusinessName] = useState("");

  // Data from /api/{customer_id}/usage
  const [planName, setPlanName] = useState("N/A");

  // For error display
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    const claims = parseJwt(token);
    if (!claims?.customer_id) {
      alert("Invalid token: no customer_id");
      navigate("/login");
      return;
    }
    const customerId = claims.customer_id;

    // 1) Fetch user profile
    apiFetch("/api/user/profile")
      .then((profileData) => {
        setUsername(profileData.username);
        setContactEmail(profileData.contact_email);
        setBusinessName(profileData.business_name);
      })
      .catch((err) => {
        console.error("Profile error:", err);
        setError(err.message || "Failed to load profile");
      });

    // 2) Fetch usage & plan name
    apiFetch(`/api/${customerId}/usage`)
      .then((usageData) => {
        if (usageData.plan_name) {
          setPlanName(usageData.plan_name);
        }
      })
      .catch((err) => {
        console.error("Usage error:", err);
        setError(err.message || "Failed to load usage info");
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  const handleUpgrade = () => {
    // The Pricing page is where the user chooses or upgrades plans
    navigate("/pricing");
  };

  const handleCancel = () => {
    // We already have an existing route: "/cancel-plan" page
    // or you can do it from here with a direct call if you want:
    navigate("/cancel-plan");
  };

  if (loading) {
    return <div className="page-container"><p>Loading...</p></div>;
  }

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>User Profile</h1>
        <LogoutButton />
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ textAlign: "left", marginTop: "20px" }}>
        <p><strong>Username:</strong> {username}</p>
        <p><strong>Business Name:</strong> {businessName}</p>
        <p><strong>Contact Email:</strong> {contactEmail}</p>
        <p><strong>Current Plan:</strong> {planName}</p>
      </div>

      <div style={{ marginTop: "20px" }}>
        {planName && planName !== "N/A" ? (
          <>
            <button className="btn" onClick={handleCancel}>
              Cancel Current Plan
            </button>
            <button className="btn" onClick={handleUpgrade}>
              Upgrade / Change Plan
            </button>
          </>
        ) : (
          <button className="btn" onClick={handleUpgrade}>
            Subscribe Now
          </button>
        )}
      </div>
    </div>
  );
}