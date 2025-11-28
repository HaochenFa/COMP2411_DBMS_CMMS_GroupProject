import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Plus, Trash2, Edit2, Save, X } from 'lucide-react';

const API_URL = "http://127.0.0.1:5050/api";

export default function EntityManager({ title, endpoint, columns, idField, createFields }) {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({});
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editFormData, setEditFormData] = useState({});
  const [error, setError] = useState(null);
  const [importFile, setImportFile] = useState(null);
  const [isImporting, setIsImporting] = useState(false);

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
      setIsCreating(false);
      setError(null);
    } catch (err) {
      setError("Failed to create item: " + (err.response?.data?.error || err.message));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;
    try {
      await axios.delete(`${API_URL}/${endpoint}/${id}`);
      fetchItems();
      setError(null);
    } catch (err) {
      setError("Failed to delete item: " + (err.response?.data?.error || err.message));
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
      setError("Failed to update item: " + (err.response?.data?.error || err.message));
    }
  };

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importFile) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target.result;
      const lines = text.split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      const items = [];

      for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const values = lines[i].split(',');
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
        setError("Failed to import: " + (err.response?.data?.error || err.message));
      }
    };
    reader.readAsText(importFile);
  };

  return (
    <div className="page-container">
      <div className="header-section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>{title}</h2>
          <p className="subtitle">Manage {title.toLowerCase()} records</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setIsImporting(!isImporting)} className="secondary-btn">
            Import CSV
          </button>
          <button onClick={() => setIsCreating(!isCreating)}>
            {isCreating ? <><X size={16} /> Cancel</> : <><Plus size={16} /> Add New</>}
          </button>
        </div>
      </div>

      {isImporting && (
        <div className="import-section" style={{ padding: '20px', background: '#f8f9fa', marginBottom: '20px', borderRadius: '8px' }}>
          <h3>Bulk Import</h3>
          <p>Upload a CSV file with headers matching the field names.</p>
          <form onSubmit={handleImport} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <input type="file" accept=".csv" onChange={e => setImportFile(e.target.files[0])} required />
            <button type="submit">Upload</button>
            <button type="button" onClick={() => setIsImporting(false)} style={{ background: 'transparent', color: '#666' }}>Cancel</button>
          </form>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {isCreating && (
        <form onSubmit={handleCreate} className="data-form">
          {createFields.map(field => (
            <div key={field.name} style={{ flex: '1 1 200px' }}>
              {field.type === 'select' ? (
                <select
                  value={newItem[field.name] || ''}
                  onChange={e => setNewItem({ ...newItem, [field.name]: e.target.value })}
                  required={field.required}
                >
                  <option value="">Select {field.label}</option>
                  {field.options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={field.type || 'text'}
                  placeholder={field.label}
                  value={newItem[field.name] || ''}
                  onChange={e => setNewItem({ ...newItem, [field.name]: e.target.value })}
                  required={field.required}
                />
              )}
            </div>
          ))}
          <button type="submit" style={{ flex: '0 0 auto' }}><Save size={16} /> Save</button>
        </form>
      )}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {columns.map(col => <th key={col.key}>{col.label}</th>)}
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={item[idField] || idx}>
                {columns.map(col => (
                  <td key={col.key}>
                    {editingId === item[idField] ? (
                      <input 
                        value={editFormData[col.key] || ''} 
                        onChange={e => setEditFormData({...editFormData, [col.key]: e.target.value})}
                      />
                    ) : (
                      item[col.key]
                    )}
                  </td>
                ))}
                <td>
                  {editingId === item[idField] ? (
                    <>
                      <button onClick={() => handleUpdate(item[idField])} className="icon-btn success"><Save size={16} /></button>
                      <button onClick={cancelEdit} className="icon-btn"><X size={16} /></button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => startEdit(item)} className="icon-btn"><Edit2 size={16} /></button>
                      <button onClick={() => handleDelete(item[idField])} className="icon-btn danger"><Trash2 size={16} /></button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
