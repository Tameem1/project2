import React from "react";
import { useNavigate } from "react-router-dom";

export default function LogoutButton() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear token from localStorage
    localStorage.removeItem("token");
    // Optionally, clear any other user data
    // Redirect to /login
    navigate("/login");
  };

  return (
    <button className="btn" onClick={handleLogout}>
      Logout
    </button>
  );
}