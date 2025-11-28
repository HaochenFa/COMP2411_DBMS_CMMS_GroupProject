import React, { useState, useEffect } from "react";
import axios from "axios";
import { Play, Trash2, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

const API_URL = "http://127.0.0.1:5050/api";

// Simple Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("DevConsole Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "20px", color: "red" }}>
          <h2>Something went wrong.</h2>
          <pre>{this.state.error && this.state.error.toString()}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function DevConsoleContent() {
  // Initialize state from localStorage
  const [query, setQuery] = useState(() => {
    return localStorage.getItem("devConsole_query") || "";
  });
  const [results, setResults] = useState(() => {
    const saved = localStorage.getItem("devConsole_results");
    return saved ? JSON.parse(saved) : null;
  });
  const [error, setError] = useState(() => {
    return localStorage.getItem("devConsole_error") || null;
  });
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("devConsole_history");
    return saved ? JSON.parse(saved) : [];
  });

  // Persist query to localStorage
  useEffect(() => {
    localStorage.setItem("devConsole_query", query);
  }, [query]);

  // Persist results to localStorage
  useEffect(() => {
    if (results) {
      localStorage.setItem("devConsole_results", JSON.stringify(results));
    } else {
      localStorage.removeItem("devConsole_results");
    }
  }, [results]);

  // Persist error to localStorage
  useEffect(() => {
    if (error) {
      localStorage.setItem("devConsole_error", error);
    } else {
      localStorage.removeItem("devConsole_error");
    }
  }, [error]);

  // Persist history to localStorage
  useEffect(() => {
    localStorage.setItem("devConsole_history", JSON.stringify(history));
  }, [history]);

  const executeQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await axios.post(`${API_URL}/query`, { query });
      setResults(res.data);
      addToHistory(query, "success");
    } catch (err) {
      console.error("Query failed:", err);
      setError(err.response?.data?.error || err.message);
      addToHistory(query, "error");
    } finally {
      setLoading(false);
    }
  };

  const addToHistory = (sql, status) => {
    setHistory((prev) => [{ sql, status, timestamp: new Date() }, ...prev].slice(0, 10));
  };

  const loadFromHistory = (sql) => {
    setQuery(sql);
  };

  return (
    <div
      className="dashboard-container"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "calc(100vh - 100px)",
        gap: "20px",
      }}
    >
      <div className="header-section">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <h1>Dev Mode: SQL Console</h1>
          <span
            style={{
              background: "#fef3c7",
              color: "#d97706",
              padding: "4px 8px",
              borderRadius: "4px",
              fontSize: "0.75rem",
              fontWeight: "bold",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <AlertTriangle size={14} /> DANGER ZONE
          </span>
        </div>
        <p className="subtitle">Execute raw SQL queries directly against the database.</p>
      </div>

      <div style={{ display: "flex", gap: "20px", flex: 1, minHeight: 0 }}>
        {/* Left Panel: Editor & Results */}
        <div
          style={{ flex: 3, display: "flex", flexDirection: "column", gap: "15px", minWidth: 0 }}
        >
          {/* Editor Container */}
          <div
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: "6px",
              display: "flex",
              flexDirection: "column",
              background: "#fff",
              boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
              flex: "0 0 200px", // Fixed height for editor
            }}
          >
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="SELECT * FROM Person;"
              style={{
                flex: 1,
                padding: "15px",
                fontFamily: '"Fira code", "Fira Mono", Consolas, monospace',
                fontSize: 14,
                border: "none",
                outline: "none",
                resize: "none",
                background: "#fafafa",
                borderRadius: "6px 6px 0 0",
              }}
            />
            <div
              style={{
                padding: "10px",
                borderTop: "1px solid #f0f0f0",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                background: "#fafafa",
                borderBottomLeftRadius: "6px",
                borderBottomRightRadius: "6px",
              }}
            >
              <button
                onClick={() => setQuery("")}
                style={{
                  background: "transparent",
                  color: "#666",
                  border: "1px solid #e0e0e0",
                  height: "32px",
                }}
              >
                <Trash2 size={14} /> Clear
              </button>
              <button
                onClick={executeQuery}
                disabled={loading || !query.trim()}
                style={{ height: "32px", padding: "0 20px" }}
              >
                {loading ? (
                  "Running..."
                ) : (
                  <>
                    <Play size={16} /> Run Query
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Area */}
          <div
            style={{
              flex: 1,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              border: "1px solid #e0e0e0",
              borderRadius: "6px",
              background: "white",
              boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
            }}
          >
            {error && (
              <div
                style={{
                  padding: "15px",
                  color: "#dc2626",
                  background: "#fef2f2",
                  borderBottom: "1px solid #fee2e2",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontWeight: "bold",
                    marginBottom: "5px",
                  }}
                >
                  <XCircle size={16} /> Query Failed
                </div>
                <pre
                  style={{
                    margin: 0,
                    whiteSpace: "pre-wrap",
                    fontFamily: "monospace",
                    fontSize: "13px",
                  }}
                >
                  {error}
                </pre>
              </div>
            )}

            <div style={{ flex: 1, overflow: "auto" }}>
              {results ? (
                Array.isArray(results) ? (
                  results.length > 0 ? (
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead style={{ position: "sticky", top: 0, zIndex: 1 }}>
                        <tr>
                          {Object.keys(results[0]).map((key) => (
                            <th
                              key={key}
                              style={{
                                background: "#f8f9fa",
                                padding: "10px",
                                textAlign: "left",
                                borderBottom: "2px solid #e0e0e0",
                                fontSize: "12px",
                                color: "#666",
                                whiteSpace: "nowrap",
                              }}
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {results.map((row, i) => (
                          <tr key={i} style={{ borderBottom: "1px solid #f0f0f0" }}>
                            {Object.values(row).map((val, j) => (
                              <td
                                key={j}
                                style={{ padding: "8px 10px", fontSize: "13px", color: "#333" }}
                              >
                                {val === null ? (
                                  <span style={{ color: "#999", fontStyle: "italic" }}>NULL</span>
                                ) : (
                                  String(val)
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div
                      style={{
                        padding: "20px",
                        color: "#666",
                        fontStyle: "italic",
                        textAlign: "center",
                      }}
                    >
                      Query returned 0 rows.
                    </div>
                  )
                ) : (
                  <div
                    style={{
                      padding: "20px",
                      color: "#059669",
                      background: "#ecfdf5",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <CheckCircle size={18} />
                    {results.message || "Operation successful"}
                    {results.rows_affected !== undefined &&
                      ` (${results.rows_affected} rows affected)`}
                  </div>
                )
              ) : (
                !error && (
                  <div style={{ padding: "40px", textAlign: "center", color: "#ccc" }}>
                    <div style={{ marginBottom: "10px" }}>Results will appear here</div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: History */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            border: "1px solid #e0e0e0",
            borderRadius: "6px",
            background: "#fafafa",
            maxWidth: "300px",
          }}
        >
          <div
            style={{
              padding: "10px 15px",
              borderBottom: "1px solid #e0e0e0",
              fontWeight: "600",
              color: "#666",
              fontSize: "0.9rem",
            }}
          >
            History
          </div>
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "10px",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            {history.map((item, i) => (
              <div
                key={i}
                onClick={() => loadFromHistory(item.sql)}
                style={{
                  padding: "10px",
                  borderRadius: "4px",
                  background: item.status === "success" ? "#fff" : "#fff1f2",
                  border: `1px solid ${item.status === "success" ? "#e5e7eb" : "#fecdd3"}`,
                  cursor: "pointer",
                  fontSize: "12px",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
                }}
              >
                <div
                  style={{
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    fontFamily: "monospace",
                    marginBottom: "4px",
                    fontWeight: "600",
                    color: "#333",
                  }}
                >
                  {item.sql}
                </div>
                <div
                  style={{
                    color: "#999",
                    fontSize: "10px",
                    display: "flex",
                    justifyContent: "space-between",
                  }}
                >
                  <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                  <span style={{ color: item.status === "success" ? "#10b981" : "#ef4444" }}>
                    {item.status === "success" ? "Success" : "Failed"}
                  </span>
                </div>
              </div>
            ))}
            {history.length === 0 && (
              <div
                style={{
                  color: "#999",
                  fontSize: "12px",
                  fontStyle: "italic",
                  textAlign: "center",
                  marginTop: "20px",
                }}
              >
                No history yet
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DevConsole() {
  return (
    <ErrorBoundary>
      <DevConsoleContent />
    </ErrorBoundary>
  );
}
