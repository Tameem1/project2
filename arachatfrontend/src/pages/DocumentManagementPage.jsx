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

  // Multiple file selection
  const [files, setFiles] = useState([]);

  // Progress bar states
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [processing, setProcessing] = useState(false);

  // Customer ID from JWT
  const [customerId, setCustomerId] = useState("");

  useEffect(() => {
    fetchDocuments();

    const token = localStorage.getItem("token");
    if (token) {
      const claims = parseJwt(token);
      if (claims && claims.customer_id) {
        setCustomerId(claims.customer_id);
      }
    }
  }, [chatbotId]);

  // Fetch existing documents
  const fetchDocuments = async () => {
    try {
      setLoadingDocs(true);
      const data = await apiFetch(`/api/chatbots/${chatbotId}/documents`);
      setDocuments(data);
    } catch (err) {
      console.error("Error fetching documents:", err);
      alert(`Failed to fetch documents: ${err.message}`);
    } finally {
      setLoadingDocs(false);
    }
  };

  // Remove a document from the server
  const handleDelete = async (docId) => {
    try {
      await apiFetch(`/api/chatbots/${chatbotId}/documents/${docId}`, {
        method: "DELETE",
      });
      alert("Document deleted successfully.");
      fetchDocuments();
    } catch (err) {
      console.error("Error deleting document:", err);
      alert(`Failed to delete document: ${err.message}`);
    }
  };

  // File selection => append new files to existing
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...newFiles]);
    }
  };

  // Remove one file from the "to upload" list
  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  /**
   * Single "Process" button:
   * 1) Upload each file
   * 2) Ingest
   * 3) Update progress bar + messages
   * 4) Refresh the doc list
   */
  const handleProcess = async () => {
    if (!files.length) {
      alert("Select at least one file to process!");
      return;
    }
    if (!customerId) {
      alert("No customer ID found in token. Please log in again?");
      return;
    }

    try {
      setProcessing(true);
      setProgress(0);
      setStatusMessage("Starting upload...");

      const totalSteps = files.length + 1; // each file + 1 for ingestion
      let currentStep = 0;

      // 1) Upload each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setStatusMessage(`Uploading file ${i + 1} of ${files.length}: ${file.name}`);

        const formData = new FormData();
        formData.append("file", file);

        await apiFetch(`/api/upload/${chatbotId}`, {
          method: "POST",
          body: formData,
          isFormData: true,
        });

        currentStep++;
        setProgress(Math.round((currentStep / totalSteps) * 100));
      }

      // 2) Ingest
      setStatusMessage("All files uploaded. Ingesting documents...");
      await apiFetch(`/api/${customerId}/${chatbotId}/ingest`, {
        method: "POST",
      });

      currentStep++;
      setProgress(Math.round((currentStep / totalSteps) * 100));
      setStatusMessage("All done! Documents ingested successfully.");

      // Refresh doc list
      await fetchDocuments();
      setFiles([]); // Clear out the local file list
    } catch (err) {
      console.error("Process error:", err);
      alert("Error during process: " + err.message);
      setStatusMessage("Error encountered. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  // Return to ChatHistory or MyChatbots
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

      <h2>Add or Update Documents</h2>
      <p>Select multiple files, then click "Process" to upload and ingest in one go.</p>

      <input
        type="file"
        multiple
        onChange={handleFileChange}
        disabled={processing}
      />

      {/* Show selected files with remove buttons */}
      {files.length > 0 && (
        <div style={{ margin: "10px 0", textAlign: "left" }}>
          <p>Files selected for upload:</p>
          <ul>
            {files.map((file, idx) => (
              <li key={idx}>
                <button onClick={() => removeFile(idx)}>Remove</button>{" "}
                {file.name}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Progress + status */}
      {processing && (
        <div style={{ margin: "20px 0" }}>
          <div
            style={{
              width: "100%",
              height: "20px",
              backgroundColor: "#e0e0df",
              borderRadius: "10px",
              marginBottom: "10px",
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: "100%",
                backgroundColor: "#007bff",
                borderRadius: "10px",
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <p>{statusMessage}</p>
        </div>
      )}

      <button onClick={handleProcess} disabled={processing}>
        {processing ? "Processing..." : "Process"}
      </button>
    </div>
  );
}