import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * A small helper that checks if we have a token in localStorage.
 * 
 * You could also import from your `api.js` if you already have a similar function.
 */
function isUserLoggedIn() {
  return !!localStorage.getItem("token");
}

/**
 * ProtectedRoute:
 * - Renders children if user is logged in
 * - Otherwise redirects to /login
 */
export default function ProtectedRoute({ children }) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isUserLoggedIn()) {
      navigate("/login");
    }
  }, [navigate]);

  return <>{children}</>;
}