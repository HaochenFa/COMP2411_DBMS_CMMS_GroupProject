import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Plus, Link as LinkIcon, Download } from "lucide-react";

const API_URL = "http://127.0.0.1:5050/api";

export default function RelationshipManager({ title, endpoint, fields, displayColumns }) {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({});
  const [error, setError] = useState(null);

  const fetchItems = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/${endpoint}`);
      setItems(res.data);
      setError(null);
    } catch (err) {
      setError("Failed to fetch data: " + (err.response?.data?.error || err.message));
    }
  }, [endpoint]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/${endpoint}`, newItem);
      fetchItems();
      setNewItem({});
      setError(null);
    } catch (err) {
      setError("Failed to create link: " + (err.response?.data?.error || err.message));
    }
  };

  const handleExport = () => {
    if (items.length === 0) {
      setError("No data to export");
      return;
    }

    const keysToExport = displayColumns.map((col) => col.key);
    const headerLabels = displayColumns.map((col) => col.label);

    const csvRows = [headerLabels.join(",")];

    items.forEach((item) => {
      const row = keysToExport.map((key) => {
        let value = item[key];
        if (value === null || value === undefined) return "";
        value = String(value);
        if (value.includes(",") || value.includes('"') || value.includes("\n")) {
          value = `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      });
      csvRows.push(row.join(","));
    });

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `${endpoint}_export_${new Date().toISOString().split("T")[0]}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-container">
      <div
        className="header-section"
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
      >
        <div>
          <h2>{title}</h2>
          <p className="subtitle">Manage relationships</p>
        </div>
        <button onClick={handleExport} className="secondary-btn" disabled={items.length === 0}>
          <Download size={16} /> Export CSV
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleCreate} className="data-form">
        {fields.map((field) => (
          <input
            key={field.name}
            placeholder={field.label}
            value={newItem[field.name] || ""}
            onChange={(e) => setNewItem({ ...newItem, [field.name]: e.target.value })}
            required
          />
        ))}
        <button type="submit">
          <LinkIcon size={16} /> Link
        </button>
      </form>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {displayColumns.map((col) => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={idx}>
                {displayColumns.map((col) => (
                  <td key={col.key}>{item[col.key]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
