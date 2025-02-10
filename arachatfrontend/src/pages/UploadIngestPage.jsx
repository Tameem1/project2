// src/pages/UploadIngestPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";  // <-- our helper
import LogoutButton from "../components/LogoutButton";

export default function UploadIngestPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [ingesting, setIngesting] = useState(false);

  // Chatbot ID from sessionStorage (assuming you stored it there 
  // after creation in LandingPage)
  const chatbotId = sessionStorage.getItem("chatbot_id");

  // We'll store the real customer ID in state
  const [customerId, setCustomerId] = useState("");

  useEffect(() => {
    // 1. Grab the token from localStorage
    const token = localStorage.getItem("token");
    if (token) {
      // 2. Parse JWT to retrieve the 'customer_id' claim
      const claims = parseJwt(token);
      if (claims && claims.customer_id) {
        setCustomerId(claims.customer_id);
      } else {
        console.warn("No customer_id found in token claims!");
      }
    } else {
      console.warn("No token found in localStorage. User might not be logged in.");
    }
  }, []);

  // File selection handler
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // Upload file => POST /api/upload/{chatbot_id}
  const handleUploadClick = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      const res = await apiFetch(`/api/upload/${chatbotId}`, {
        method: "POST",
        body: formData,
        isFormData: true
      });

      alert("Upload success: " + res.message);
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  // Ingest => POST /api/{customerId}/{chatbotId}/ingest (real ID instead of 'YOUR_CUSTOMER_ID')
  const handleIngestClick = async () => {
    if (!customerId) {
      alert("Customer ID not available. Make sure you're logged in and token claims are correct.");
      return;
    }
    try {
      setIngesting(true);
      const res = await apiFetch(`/api/${customerId}/${chatbotId}/ingest`, {
        method: "POST"
      });
      alert("Ingest success: " + res.message);
    } catch (err) {
      console.error(err);
      alert("Ingest failed: " + err.message);
    } finally {
      setIngesting(false);
    }
  };

  const handleNextPage = () => {
    navigate("/model-selection");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Upload & Ingest</h1>
        <LogoutButton />
      </div>
      <p>Upload documents for your chatbot and then ingest them for training.</p>

      <div style={{ marginBottom: "20px" }}>
        <input type="file" onChange={handleFileChange} />
        <button
          className="btn"
          onClick={handleUploadClick}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Upload Documents"}
        </button>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <button
          className="btn"
          onClick={handleIngestClick}
          disabled={ingesting}
        >
          {ingesting ? "Ingesting..." : "Ingest"}
        </button>
      </div>

      <button className="btn" onClick={handleNextPage}>
        Next
      </button>
    </div>
  );
}