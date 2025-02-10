// src/utils/jwt.js

/**
 * parseJwt(token)
 * - Removes the "Bearer " prefix if present
 * - Splits the token by '.' 
 * - Decodes the base64-encoded middle part to JSON
 */
export function parseJwt(token) {
    if (!token) return null;
  
    // If the token has the "Bearer " prefix, remove it
    const cleanedToken = token.replace(/^Bearer\s+/, "");
  
    const parts = cleanedToken.split(".");
    if (parts.length !== 3) {
      // Not a valid JWT
      return null;
    }
  
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  
    try {
      const decodedPayload = atob(base64);
      return JSON.parse(decodedPayload);
    } catch (err) {
      console.error("Failed to parse JWT payload:", err);
      return null;
    }
  }