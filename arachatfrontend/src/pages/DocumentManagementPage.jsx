// src/pages/DocumentManagementPage.jsx

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";
import LogoutButton from "../components/LogoutButton";

export default function DocumentManagementPage() {
  const { chatbotId } = useParams();
  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [ingesting, setIngesting] = useState(false);

  // 1. On mount, fetch documents
  useEffect(() => {
    fetchDocuments();
  }, [chatbotId]);

  const fetchDocuments = async () => {
    try {
      setLoadingDocs(true);
      // GET /api/chatbots/{chatbotId}/documents (You’ll add this in your backend)
      const data = await apiFetch(`/api/chatbots/${chatbotId}/documents`);
      setDocuments(data);
    } catch (err) {
      console.error("Error fetching documents:", err);
      alert(`Failed to fetch documents: ${err.message}`);
    } finally {
      setLoadingDocs(false);
    }
  };

  // 2. Delete a document
  const handleDelete = async (docId) => {
    try {
      // DELETE /api/chatbots/{chatbotId}/documents/{docId}
      await apiFetch(`/api/chatbots/${chatbotId}/documents/${docId}`, {
        method: "DELETE",
      });
      alert("Document deleted successfully.");
      // Refresh list
      fetchDocuments();
    } catch (err) {
      console.error("Error deleting document:", err);
      alert(`Failed to delete document: ${err.message}`);
    }
  };

  // 3. Upload a file
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      // POST /api/upload/{chatbotId}
      const res = await apiFetch(`/api/upload/${chatbotId}`, {
        method: "POST",
        body: formData,
        isFormData: true
      });
      alert("Upload success: " + res.message);
      // Refresh document list
      fetchDocuments();
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  // 4. Re-ingest documents
  const handleIngest = async () => {
    try {
      setIngesting(true);
      // Need the customerId from token
      const token = localStorage.getItem("token");
      const claims = parseJwt(token);
      const customerId = claims.customer_id;

      // POST /api/{customerId}/{chatbotId}/ingest
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

  // 5. Return to ChatHistory or MyChatbots
  const handleBackToHistory = () => {
    navigate(`/chatbots/${chatbotId}`);
  };
  const handleBackToChatbots = () => {
    navigate("/");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Manage Documents</h1>
        <LogoutButton />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={handleBackToHistory} style={{ marginRight: "10px" }}>
          Back to Chat History
        </button>
        <button onClick={handleBackToChatbots}>
          Back to My Chatbots
        </button>
      </div>

      <h2>Existing Documents</h2>
      {loadingDocs ? (
        <p>Loading documents...</p>
      ) : (
        <ul>
          {documents.map((doc) => (
            <li key={doc.id}>
              {doc.filename}{" "}
              <button onClick={() => handleDelete(doc.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}

      <hr />

      <h2>Upload a New Document</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? "Uploading..." : "Upload"}
      </button>

      <hr />

      <h2>Re-Ingest Documents</h2>
      <button onClick={handleIngest} disabled={ingesting}>
        {ingesting ? "Ingesting..." : "Ingest"}
      </button>
    </div>
  );
}