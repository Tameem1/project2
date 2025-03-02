// src/pages/UploadIngestPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { parseJwt } from "../utils/jwt";
import LogoutButton from "../components/LogoutButton";

export default function UploadIngestPage() {
  const navigate = useNavigate();

  // We store multiple files in an array:
  const [files, setFiles] = useState([]);

  // For progress/status:
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [processing, setProcessing] = useState(false);

  // ** New ** track if ingestion was successful
  const [ingestionSuccess, setIngestionSuccess] = useState(false);

  // Chatbot ID from sessionStorage
  const chatbotId = sessionStorage.getItem("chatbot_id");

  // We'll store the real customer ID
  const [customerId, setCustomerId] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
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

  /**
   * When new files are selected, append them to the existing array of files
   * instead of overwriting.
   */
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...newFiles]);
    }
  };

  /**
   * Removes a single file from the `files` array by index.
   */
  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  /**
   * Main "Process" flow:
   * 1) Upload each file (one-by-one).
   * 2) Then ingest.
   * 3) Show progress & status along the way.
   * 4) If success, set ingestionSuccess(true); if error, false.
   */
  const handleProcess = async () => {
    if (!files.length) {
      alert("Please select at least one file first!");
      return;
    }
    if (!customerId) {
      alert("Customer ID not available. Check that you're logged in with a valid token.");
      return;
    }
    if (!chatbotId) {
      alert("No chatbot ID found in session. Please create a chatbot first.");
      return;
    }

    try {
      setProcessing(true);
      setProgress(0);
      setStatusMessage("Starting upload...");
      setIngestionSuccess(false); // reset

      // We'll do N uploads + 1 ingest step
      const totalSteps = files.length + 1;
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
      await apiFetch(`/api/${customerId}/${chatbotId}/ingest`, { method: "POST" });

      currentStep++;
      setProgress(Math.round((currentStep / totalSteps) * 100));
      setStatusMessage("All done! Documents ingested successfully.");

      // If we reached here, everything was successful
      setIngestionSuccess(true);

    } catch (err) {
      console.error("Process error:", err);
      alert("Error during process: " + err.message);
      setStatusMessage("Error encountered. Please try again.");
      // Ensure ingestionSuccess is false
      setIngestionSuccess(false);
    } finally {
      setProcessing(false);
    }
  };

  // The Next button is disabled if ingestion not successful or still processing
  const handleNextPage = () => {
    navigate("/model-selection");
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Upload & Ingest</h1>
        <LogoutButton />
      </div>
      <p>
        Select one or more files to upload for your new chatbot, then click "Process" to
        automatically upload & ingest. You can only proceed once ingestion succeeds.
      </p>

      {/* File input (multiple) */}
      <div style={{ marginBottom: "10px" }}>
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          disabled={processing}
        />
      </div>

      {/* Render list of selected files + remove button */}
      {files.length > 0 && (
        <div style={{ textAlign: "left", marginBottom: "20px" }}>
          <p>Files to be uploaded:</p>
          <ul>
            {files.map((file, index) => (
              <li key={index}>
                <button onClick={() => handleRemoveFile(index)}>Remove</button>{" "}
                {file.name}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Progress Bar & status */}
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

      {/* Single "Process" button */}
      <div style={{ marginBottom: "20px" }}>
        <button className="btn" onClick={handleProcess} disabled={processing}>
          {processing ? "Processing..." : "Process"}
        </button>
      </div>

      {/* Next Button - disabled unless ingestion succeeded */}
      <button
        className="btn"
        onClick={handleNextPage}
        disabled={!ingestionSuccess || processing}
      >
        Next
      </button>
    </div>
  );
}