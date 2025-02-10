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

  // If not okay, throw an error
  if (!res.ok) {
    // Attempt to parse error text/JSON
    const errorText = await res.text();
    throw new Error(errorText || `HTTP ${res.status} - ${res.statusText}`);
  }

  // Attempt to parse JSON; if none, return empty object
  try {
    return await res.json();
  } catch (err) {
    return {};
  }
}