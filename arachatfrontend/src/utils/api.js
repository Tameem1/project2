// src/utils/api.js

export const BASE_URL = "http://localhost:8000"; 
// Update to match where your FastAPI backend is hosted

/**
 * Save the JWT token to localStorage (or sessionStorage).
 */
export function setAuthToken(token) {
  localStorage.setItem("token", token);
}

/**
 * Read the JWT token from localStorage (or sessionStorage).
 */
export function getAuthToken() {
  const token = localStorage.getItem("token");
  return token ? `Bearer ${token}` : "";
}

/**
 * Unified fetch wrapper that sets Authorization header if a token exists.
 * 
 * @param {string} endpoint - The API endpoint (e.g. "/auth/register")
 * @param {object} options - { method, body, isFormData }
 */
export async function apiFetch(endpoint, { method = "GET", body, isFormData = false } = {}) {
  const headers = isFormData ? {} : { "Content-Type": "application/json" };

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers: {
      ...headers,
      Authorization: getAuthToken(),
    },
    body: isFormData ? body : body ? JSON.stringify(body) : null,
  });

  if (!res.ok) {
    const errorText = await res.text();
    if (errorText.includes("Token expired")) {
      alert("Your session has expired. Click OK to login.");
      window.location.href = "/login";
      return; // Prevent further processing after redirect
    }
    throw new Error(errorText || `HTTP ${res.status} - ${res.statusText}`);
  }

  try {
    return await res.json();
  } catch (err) {
    return {};
  }
}