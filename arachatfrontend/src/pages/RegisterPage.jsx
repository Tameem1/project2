// src/pages/RegisterPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";

export default function RegisterPage() {
  const navigate = useNavigate();
  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [loading, setLoading] = useState(false);

  // New state for error display:
  const [errorMessage, setErrorMessage] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(""); // clear any previous error

    try {
      // POST /auth/register with the proper field names
      await apiFetch("/auth/register", {
        method: "POST",
        body: {
          username,
          password,
          business_name: businessName,
          contact_email: contactEmail,
        },
      });

      alert("Registration successful! You can now log in.");
      navigate("/login");
    } catch (err) {
      console.error("Registration error:", err);
      // Display the error message returned from the backend
      setErrorMessage(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>Register</h1>

      {/* Display error message if present */}
      {errorMessage && (
        <p style={{ color: "red", marginBottom: "10px" }}>
          {errorMessage}
        </p>
      )}

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
          <label>Business Name: </label><br/>
          <input
            type="text"
            value={businessName}
            onChange={(e) => setBusinessName(e.target.value)}
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
        Already have an account?{" "}
        <span
          style={{ color: "blue", cursor: "pointer" }}
          onClick={() => navigate("/login")}
        >
          Log In
        </span>
      </p>
    </div>
  );
}