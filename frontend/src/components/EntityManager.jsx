import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Plus, Trash2, Edit2, Save, X, Download, Upload } from "lucide-react";
import { useRole } from "../context/RoleContext";

const API_URL = "http://127.0.0.1:5050/api";

export default function EntityManager({
  title,
  endpoint,
  columns,
  idField,
  createFields,
}) {
  const { hasPermission } = useRole();
  const canCreate = hasPermission("canCreate");
  const canUpdate = hasPermission("canUpdate");
  const canDelete = hasPermission("canDelete");
  const canModify = canCreate || canUpdate || canDelete;

  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({});
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editFormData, setEditFormData] = useState({});
  const [error, setError] = useState(null);
  const [importFile, setImportFile] = useState(null);
  const [isImporting, setIsImporting] = useState(false);
  const [dynamicOptions, setDynamicOptions] = useState({});

  const fetchItems = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/${endpoint}`);
      setItems(res.data);
      setError(null);
    } catch (err) {
      setError(
        "Failed to fetch data: " + (err.response?.data?.error || err.message),
      );
    }
  }, [endpoint]);

  // Store raw data for cascading selects
  const [rawOptionsData, setRawOptionsData] = useState({});

  // Fetch dynamic options for select fields that have optionsEndpoint
  const fetchDynamicOptions = useCallback(async () => {
    const fieldsWithEndpoint = createFields.filter((f) => f.optionsEndpoint);
    const optionsMap = {};
    const rawDataMap = {};

    // Group fields by endpoint to avoid duplicate fetches
    const endpointFields = {};
    for (const field of fieldsWithEndpoint) {
      if (!endpointFields[field.optionsEndpoint]) {
        endpointFields[field.optionsEndpoint] = [];
      }
      endpointFields[field.optionsEndpoint].push(field);
    }

    for (const [endpointName, fields] of Object.entries(endpointFields)) {
      try {
        const res = await axios.get(`${API_URL}/${endpointName}`);
        rawDataMap[endpointName] = res.data;

        for (const field of fields) {
          if (field.type === "cascading-select" && field.unique) {
            // Get unique values for this field
            const uniqueValues = [
              ...new Set(res.data.map((item) => item[field.optionValue])),
            ];
            optionsMap[field.name] = uniqueValues.map((val) => ({
              value: val,
              label: field.optionLabel({
                [field.optionValue]: val,
                building: val,
              }),
            }));
          } else if (field.type !== "cascading-select" || !field.dependsOn) {
            optionsMap[field.name] = res.data.map((item) => ({
              value: item[field.optionValue],
              label: field.optionLabel(item),
            }));
          }
        }
      } catch (err) {
        console.error(`Failed to fetch options for ${endpointName}:`, err);
      }
    }

    setRawOptionsData(rawDataMap);
    setDynamicOptions(optionsMap);
  }, [createFields]);

  useEffect(() => {
    fetchItems();
    fetchDynamicOptions();
  }, [fetchItems, fetchDynamicOptions]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/${endpoint}`, newItem);
      fetchItems();
      setNewItem({});
      setIsCreating(false);
      setError(null);
    } catch (err) {
      setError(
        "Failed to create item: " + (err.response?.data?.error || err.message),
      );
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;
    try {
      await axios.delete(`${API_URL}/${endpoint}/${id}`);
      fetchItems();
      setError(null);
    } catch (err) {
      setError(
        "Failed to delete item: " + (err.response?.data?.error || err.message),
      );
    }
  };

  const startEdit = (item) => {
    setEditingId(item[idField]);
    setEditFormData({ ...item });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditFormData({});
  };

  const handleUpdate = async (id) => {
    try {
      await axios.put(`${API_URL}/${endpoint}/${id}`, editFormData);
      setEditingId(null);
      fetchItems();
      setError(null);
    } catch (err) {
      setError(
        "Failed to update item: " + (err.response?.data?.error || err.message),
      );
    }
  };

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importFile) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target.result;
      const lines = text.split("\n");
      const headers = lines[0].split(",").map((h) => h.trim());
      const items = [];

      for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const values = lines[i].split(",");
        const item = {};
        headers.forEach((h, idx) => {
          if (values[idx]) item[h] = values[idx].trim();
        });
        items.push(item);
      }

      try {
        await axios.post(`${API_URL}/import`, { entity: endpoint, items });
        fetchItems();
        setIsImporting(false);
        setImportFile(null);
        setError(null);
        alert(`Successfully imported ${items.length} items.`);
      } catch (err) {
        setError(
          "Failed to import: " + (err.response?.data?.error || err.message),
        );
      }
    };
    reader.readAsText(importFile);
  };

  const handleExport = () => {
    if (items.length === 0) {
      setError("No data to export");
      return;
    }

    // Get all unique keys from items (in case some items have different fields)
    const allKeys = [...new Set(items.flatMap((item) => Object.keys(item)))];

    // Use column keys if available, otherwise use all keys from data
    const exportKeys = columns.map((col) => col.key);
    const keysToExport = exportKeys.length > 0 ? exportKeys : allKeys;

    // Create CSV header
    const headerLabels = keysToExport.map((key) => {
      const col = columns.find((c) => c.key === key);
      return col ? col.label : key;
    });

    // Create CSV content
    const csvRows = [headerLabels.join(",")];

    items.forEach((item) => {
      const row = keysToExport.map((key) => {
        let value = item[key];

        // Handle null/undefined
        if (value === null || value === undefined) {
          return "";
        }

        // Convert to string
        value = String(value);

        // Escape quotes and wrap in quotes if contains comma, quote, or newline
        if (
          value.includes(",") ||
          value.includes('"') ||
          value.includes("\n")
        ) {
          value = `"${value.replace(/"/g, '""')}"`;
        }

        return value;
      });
      csvRows.push(row.join(","));
    });

    const csvContent = csvRows.join("\n");

    // Create and download the file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `${endpoint}_export_${new Date().toISOString().split("T")[0]}.csv`,
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
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h2>{title}</h2>
          <p className="subtitle">Manage {title.toLowerCase()} records</p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={handleExport}
            className="secondary-btn"
            disabled={items.length === 0}
          >
            <Download size={16} /> Export CSV
          </button>
          {canCreate && (
            <button
              onClick={() => setIsImporting(!isImporting)}
              className="secondary-btn"
            >
              <Upload size={16} /> Import CSV
            </button>
          )}
          {canCreate && (
            <button onClick={() => setIsCreating(!isCreating)}>
              {isCreating ? (
                <>
                  <X size={16} /> Cancel
                </>
              ) : (
                <>
                  <Plus size={16} /> Add New
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {isImporting && canCreate && (
        <div
          className="import-section"
          style={{
            padding: "20px",
            background: "#f8f9fa",
            marginBottom: "20px",
            borderRadius: "8px",
          }}
        >
          <h3>Bulk Import</h3>
          <p>Upload a CSV file with headers matching the field names.</p>
          <form
            onSubmit={handleImport}
            style={{ display: "flex", gap: "10px", alignItems: "center" }}
          >
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setImportFile(e.target.files[0])}
              required
            />
            <button type="submit">Upload</button>
            <button
              type="button"
              onClick={() => setIsImporting(false)}
              style={{ background: "transparent", color: "#666" }}
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {isCreating && canCreate && (
        <form onSubmit={handleCreate} className="data-form">
          {createFields.map((field) => {
            // Handle cascading select (e.g., Building -> Room)
            if (field.type === "cascading-select") {
              let options = [];
              if (field.dependsOn) {
                // This is a dependent field - filter based on parent value
                const parentValue = newItem[field.dependsOn];
                const rawData = rawOptionsData[field.optionsEndpoint] || [];
                const filtered = parentValue
                  ? rawData.filter(
                      (item) => item[field.filterBy] === parentValue,
                    )
                  : [];
                options = filtered.map((item) => ({
                  value: item[field.optionValue],
                  label: field.optionLabel(item),
                  _raw: item,
                }));
              } else {
                // This is a parent field - use pre-computed unique options
                options = dynamicOptions[field.name] || [];
              }

              // If allowNew is true, use input with datalist for autocomplete + new entries
              if (field.allowNew) {
                return (
                  <div key={field.name} style={{ flex: "1 1 200px" }}>
                    <input
                      type="text"
                      list={`${field.name}-list`}
                      value={newItem[field.name] || ""}
                      onChange={(e) =>
                        setNewItem({ ...newItem, [field.name]: e.target.value })
                      }
                      placeholder={field.label}
                      required={field.required}
                    />
                    <datalist id={`${field.name}-list`}>
                      {options.map((opt) => (
                        <option key={opt.value} value={opt.value} />
                      ))}
                    </datalist>
                  </div>
                );
              }

              return (
                <div key={field.name} style={{ flex: "1 1 200px" }}>
                  <select
                    value={newItem[field.name] || ""}
                    onChange={(e) => {
                      const val = e.target.value;
                      const updates = { ...newItem, [field.name]: val };

                      // If this is a dependent field with resolveTo, also set the resolved field
                      if (field.resolveTo && val) {
                        const selectedOpt = options.find(
                          (o) => String(o.value) === val,
                        );
                        if (selectedOpt?._raw) {
                          updates[field.resolveTo.field] =
                            selectedOpt._raw[field.resolveTo.key];
                        }
                      }

                      // If this is a parent field, clear dependent fields
                      if (!field.dependsOn) {
                        const dependentFields = createFields.filter(
                          (f) => f.dependsOn === field.name,
                        );
                        dependentFields.forEach((df) => {
                          updates[df.name] = "";
                          if (df.resolveTo) updates[df.resolveTo.field] = "";
                        });
                      }

                      setNewItem(updates);
                    }}
                    required={field.required}
                    disabled={field.dependsOn && !newItem[field.dependsOn]}
                  >
                    <option value="">Select {field.label}</option>
                    {options.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              );
            }

            // Regular select
            if (field.type === "select") {
              return (
                <div key={field.name} style={{ flex: "1 1 200px" }}>
                  <select
                    value={newItem[field.name] || ""}
                    onChange={(e) =>
                      setNewItem({ ...newItem, [field.name]: e.target.value })
                    }
                    required={field.required}
                  >
                    <option value="">Select {field.label}</option>
                    {field.options
                      ? field.options.map((opt) => (
                          <option
                            key={opt}
                            value={opt === "Yes" ? 1 : opt === "No" ? 0 : opt}
                          >
                            {opt}
                          </option>
                        ))
                      : (dynamicOptions[field.name] || []).map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                  </select>
                </div>
              );
            }

            // Regular input
            return (
              <div key={field.name} style={{ flex: "1 1 200px" }}>
                <input
                  type={field.type || "text"}
                  placeholder={field.label}
                  value={newItem[field.name] || ""}
                  onChange={(e) =>
                    setNewItem({ ...newItem, [field.name]: e.target.value })
                  }
                  required={field.required}
                />
              </div>
            );
          })}
          <button type="submit" style={{ flex: "0 0 auto" }}>
            <Save size={16} /> Save
          </button>
        </form>
      )}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key}>{col.label}</th>
              ))}
              {canModify && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={item[idField] || idx}>
                {columns.map((col) => {
                  const rawValue = item[col.key];
                  const displayValue = col.render
                    ? col.render(rawValue, item)
                    : rawValue;
                  // Find matching createField for this column to get field type/options
                  const fieldConfig = createFields.find(
                    (f) => f.name === col.key,
                  );
                  // Get options: either static options or dynamic options from API
                  const selectOptions = fieldConfig?.optionsEndpoint
                    ? dynamicOptions[fieldConfig.name] || []
                    : (fieldConfig?.options || []).map((opt) => ({
                        value: opt === "Yes" ? 1 : opt === "No" ? 0 : opt,
                        label: opt,
                      }));
                  return (
                    <td key={col.key}>
                      {editingId === item[idField] ? (
                        fieldConfig?.type === "select" ? (
                          <select
                            value={editFormData[col.key] ?? ""}
                            onChange={(e) =>
                              setEditFormData({
                                ...editFormData,
                                [col.key]: e.target.value,
                              })
                            }
                          >
                            <option value="">Select...</option>
                            {selectOptions.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            value={editFormData[col.key] || ""}
                            onChange={(e) =>
                              setEditFormData({
                                ...editFormData,
                                [col.key]: e.target.value,
                              })
                            }
                          />
                        )
                      ) : (
                        displayValue
                      )}
                    </td>
                  );
                })}
                {canModify && (
                  <td>
                    {editingId === item[idField] ? (
                      <>
                        <button
                          onClick={() => handleUpdate(item[idField])}
                          className="icon-btn success"
                        >
                          <Save size={16} />
                        </button>
                        <button onClick={cancelEdit} className="icon-btn">
                          <X size={16} />
                        </button>
                      </>
                    ) : (
                      <>
                        {canUpdate && (
                          <button
                            onClick={() => startEdit(item)}
                            className="icon-btn"
                          >
                            <Edit2 size={16} />
                          </button>
                        )}
                        {canDelete && (
                          <button
                            onClick={() => handleDelete(item[idField])}
                            className="icon-btn danger"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
