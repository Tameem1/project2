// src/pages/RegisterPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";

export default function RegisterPage() {
  const navigate = useNavigate();

  // Form state
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Construct the request body matching your FastAPI pydantic model
      await apiFetch("/auth/register", {
        method: "POST",
        body: {
          username,
          password,
          customer_name: customerName,
          contact_email: contactEmail
        }
      });

      alert("Registration successful! You can now log in.");
      navigate("/login");
    } catch (err) {
      console.error("Registration error:", err);
      alert(`Registration failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>Register</h1>
      <form onSubmit={handleRegister}>
        <div style={{ marginBottom: "10px" }}>
          <label>Username: </label><br/>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Password: </label><br/>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Customer Name: </label><br/>
          <input
            type="text"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Contact Email: </label><br/>
          <input
            type="email"
            value={contactEmail}
            onChange={(e) => setContactEmail(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      <div className="spacer"></div>
      <p>
        Already have an account? 
        <span style={{ color: "blue", cursor: "pointer" }} onClick={() => navigate("/login")}>
          Log In
        </span>
      </p>
    </div>
  );
}