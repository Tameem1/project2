// src/pages/LoginPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, setAuthToken, BASE_URL } from "../utils/api";

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 1) Prepare form data
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      // 2) POST /auth/token
      const response = await fetch(`${BASE_URL}/auth/token`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `HTTP ${response.status}`);
      }

      // 3) Parse token
      const data = await response.json();
      const token = data.access_token;
      if (!token) {
        throw new Error("No access_token returned from server.");
      }

      // 4) Set token in localStorage
      setAuthToken(token);

      // 5) Alert once, then navigate
      alert("Login successful!");
      navigate("/");
    } catch (err) {
      console.error("Login error:", err);
      alert(`Login failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>Login</h1>
      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: "10px" }}>
          <label>Username: </label><br/>
          <input
            type="text"
            required
            disabled={loading}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Password: </label><br/>
          <input
            type="password"
            required
            disabled={loading}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <div className="spacer"></div>
      <p>
        Don't have an account yet? 
        <span style={{ color: "blue", cursor: "pointer" }} onClick={() => navigate("/register")}>
          Register
        </span>
      </p>
    </div>
  );
}