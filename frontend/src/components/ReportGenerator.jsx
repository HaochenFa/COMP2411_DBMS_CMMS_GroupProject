import React, { useState } from "react";
import axios from "axios";
import { FileText, Download, Loader2, CheckSquare, Square, AlertCircle } from "lucide-react";

const API_URL = "http://127.0.0.1:5050/api";

const AVAILABLE_SECTIONS = [
  { id: "executive_summary", label: "Executive Summary", description: "KPIs and overview metrics" },
  { id: "maintenance", label: "Maintenance Analysis", description: "Tasks by location and type" },
  { id: "personnel", label: "Personnel Overview", description: "Staff by role and status" },
  {
    id: "activities",
    label: "Activities Statistics",
    description: "Events and activities summary",
  },
  { id: "schools", label: "Department Statistics", description: "School and faculty data" },
  { id: "safety", label: "Safety Report", description: "Chemical hazard analysis" },
];

export default function ReportGenerator() {
  const [selectedSections, setSelectedSections] = useState(AVAILABLE_SECTIONS.map((s) => s.id));
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const toggleSection = (sectionId) => {
    setSelectedSections((prev) =>
      prev.includes(sectionId) ? prev.filter((id) => id !== sectionId) : [...prev, sectionId]
    );
  };

  const selectAll = () => {
    setSelectedSections(AVAILABLE_SECTIONS.map((s) => s.id));
  };

  const selectNone = () => {
    setSelectedSections([]);
  };

  const handleGenerateReport = async () => {
    if (selectedSections.length === 0) {
      setError("Please select at least one section to include in the report.");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(
        `${API_URL}/reports/generate-pdf`,
        { sections: selectedSections },
        { responseType: "blob" }
      );

      // Create download link
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Extract filename from header or use default
      const contentDisposition = response.headers["content-disposition"];
      let filename = `CMMS_Report_${new Date().toISOString().split("T")[0]}.pdf`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error("Report generation failed:", err);
      if (err.response?.data instanceof Blob) {
        const text = await err.response.data.text();
        try {
          const json = JSON.parse(text);
          setError(json.error || "Failed to generate report");
        } catch {
          setError("Failed to generate report. Please try again.");
        }
      } else {
        setError(err.response?.data?.error || "Failed to generate report. Please try again.");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="page-container">
      <div className="header-section">
        <h2>
          <FileText size={24} style={{ marginRight: "10px", verticalAlign: "middle" }} />
          Report Generation
        </h2>
        <p className="subtitle">Generate comprehensive PDF reports with data analysis</p>
      </div>

      <div className="card" style={{ maxWidth: "700px" }}>
        <h3 style={{ marginBottom: "15px", color: "#A6192E" }}>Report Sections</h3>
        <p style={{ fontSize: "0.9rem", color: "#666", marginBottom: "15px" }}>
          Select the sections to include in your report. Each section will appear on its own page
          with relevant charts and data tables.
        </p>

        <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
          <button onClick={selectAll} className="secondary-btn" style={{ fontSize: "0.85rem" }}>
            Select All
          </button>
          <button onClick={selectNone} className="secondary-btn" style={{ fontSize: "0.85rem" }}>
            Clear All
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {AVAILABLE_SECTIONS.map((section) => (
            <div
              key={section.id}
              onClick={() => toggleSection(section.id)}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "12px 15px",
                borderRadius: "8px",
                cursor: "pointer",
                background: selectedSections.includes(section.id) ? "#fef2f2" : "#f9fafb",
                border: selectedSections.includes(section.id)
                  ? "1px solid #A6192E"
                  : "1px solid #e5e7eb",
                transition: "all 0.2s ease",
              }}
            >
              {selectedSections.includes(section.id) ? (
                <CheckSquare size={20} color="#A6192E" style={{ marginRight: "12px" }} />
              ) : (
                <Square size={20} color="#9ca3af" style={{ marginRight: "12px" }} />
              )}
              <div>
                <div style={{ fontWeight: 500, color: "#1f2937" }}>{section.label}</div>
                <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>{section.description}</div>
              </div>
            </div>
          ))}
        </div>

        {error && (
          <div
            style={{
              marginTop: "20px",
              padding: "12px 15px",
              background: "#fee2e2",
              borderRadius: "8px",
              color: "#dc2626",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {success && (
          <div
            style={{
              marginTop: "20px",
              padding: "12px 15px",
              background: "#dcfce7",
              borderRadius: "8px",
              color: "#16a34a",
            }}
          >
            ✓ Report generated and downloaded successfully!
          </div>
        )}

        <div style={{ marginTop: "25px", paddingTop: "20px", borderTop: "1px solid #e5e7eb" }}>
          <button
            onClick={handleGenerateReport}
            disabled={isGenerating || selectedSections.length === 0}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "10px",
              width: "100%",
              padding: "14px 20px",
              fontSize: "1rem",
              fontWeight: 600,
              background: isGenerating || selectedSections.length === 0 ? "#d1d5db" : "#A6192E",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: isGenerating || selectedSections.length === 0 ? "not-allowed" : "pointer",
              transition: "background 0.2s ease",
            }}
          >
            {isGenerating ? (
              <>
                <Loader2
                  size={20}
                  className="animate-spin"
                  style={{ animation: "spin 1s linear infinite" }}
                />
                Generating Report...
              </>
            ) : (
              <>
                <Download size={20} />
                Generate PDF Report
              </>
            )}
          </button>

          <p
            style={{
              marginTop: "12px",
              fontSize: "0.8rem",
              color: "#9ca3af",
              textAlign: "center",
            }}
          >
            {selectedSections.length} of {AVAILABLE_SECTIONS.length} sections selected
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
