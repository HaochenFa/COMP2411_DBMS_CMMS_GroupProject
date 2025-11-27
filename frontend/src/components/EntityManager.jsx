import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Plus, Trash2, Edit2, Save, X } from 'lucide-react';

const API_URL = "http://127.0.0.1:5050/api";

export default function EntityManager({ title, endpoint, columns, idField, createFields }) {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({});
  const [isCreating, setIsCreating] = useState(false);
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
      setIsCreating(false);
      setError(null);
    } catch (err) {
      setError("Failed to create item: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="page-container">
      <div className="header-section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>{title}</h2>
          <p className="subtitle">Manage {title.toLowerCase()} records</p>
        </div>
        <button onClick={() => setIsCreating(!isCreating)}>
          {isCreating ? <><X size={16} /> Cancel</> : <><Plus size={16} /> Add New</>}
        </button>
      </div>

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
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={item[idField] || idx}>
                {columns.map(col => (
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
