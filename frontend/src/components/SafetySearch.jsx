import React, { useState, useEffect } from "react";
import axios from "axios";
import { AlertTriangle, Search } from "lucide-react";

const API_URL = "http://127.0.0.1:5050/api";

export default function SafetySearch() {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBuildings();
  }, []);

  const fetchBuildings = async () => {
    try {
      // Fetch unique buildings from locations
      const res = await axios.get(`${API_URL}/locations`);
      const uniqueBuildings = [...new Set(res.data.map((l) => l.building).filter(Boolean))];
      setBuildings(uniqueBuildings);
    } catch (err) {
      console.error("Failed to fetch buildings", err);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_URL}/search/safety`, {
        params: { building: selectedBuilding },
      });
      setResults(res.data);
    } catch (err) {
      setError("Search failed: " + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="header-section">
        <h2>Safety Search</h2>
        <p className="subtitle">Find cleaning activities and check for chemical hazards</p>
      </div>

      <div
        className="search-section"
        style={{
          background: "#fff",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "20px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
        }}
      >
        <form onSubmit={handleSearch} style={{ display: "flex", gap: "15px", alignItems: "end" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}>
              Building
            </label>
            <select
              value={selectedBuilding}
              onChange={(e) => setSelectedBuilding(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ddd",
              }}
            >
              <option value="">Select Building</option>
              {buildings.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{ display: "flex", alignItems: "center", gap: "8px" }}
          >
            <Search size={18} /> Search
          </button>
        </form>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="results-section">
        {results.length > 0 ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Location</th>
                  <th>Frequency</th>
                  <th>Safety Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((item, idx) => (
                  <tr key={idx} style={item.warning ? { backgroundColor: "#fff5f5" } : {}}>
                    <td>{item.type}</td>
                    <td>
                      {item.building} - {item.room} (Floor {item.floor})
                    </td>
                    <td>{item.frequency}</td>
                    <td>
                      {item.warning ? (
                        <span
                          style={{
                            color: "#e53e3e",
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            fontWeight: "bold",
                          }}
                        >
                          <AlertTriangle size={16} /> {item.warning}
                        </span>
                      ) : (
                        <span style={{ color: "#38a169" }}>Safe</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !loading && (
            <p style={{ textAlign: "center", color: "#666", marginTop: "40px" }}>
              No results found. Select a building to search.
            </p>
          )
        )}
      </div>
    </div>
  );
}
