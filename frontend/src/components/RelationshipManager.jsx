import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Plus, Link as LinkIcon } from 'lucide-react';

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

  return (
    <div className="page-container">
      <div className="header-section">
        <h2>{title}</h2>
        <p className="subtitle">Manage relationships</p>
      </div>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleCreate} className="data-form">
        {fields.map(field => (
          <input
            key={field.name}
            placeholder={field.label}
            value={newItem[field.name] || ''}
            onChange={e => setNewItem({ ...newItem, [field.name]: e.target.value })}
            required
          />
        ))}
        <button type="submit"><LinkIcon size={16} /> Link</button>
      </form>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {displayColumns.map(col => <th key={col.key}>{col.label}</th>)}
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={idx}>
                {displayColumns.map(col => (
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
