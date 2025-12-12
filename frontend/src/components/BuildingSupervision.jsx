import { useState, useEffect } from "react";
import { useRole } from "../context/RoleContext";
import { Building2, UserCheck, Trash2, Plus, RefreshCw } from "lucide-react";

const API_BASE = "http://127.0.0.1:5050/api";

export default function BuildingSupervision() {
  const { hasPermission } = useRole();
  const [supervisions, setSupervisions] = useState([]);
  const [managers, setManagers] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ personal_id: "", building: "" });

  const canModify = hasPermission("canCreate");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [supRes, mgrRes, bldRes] = await Promise.all([
        fetch(`${API_BASE}/building-supervision`),
        fetch(`${API_BASE}/persons?role=Mid-level Manager`),
        fetch(`${API_BASE}/locations`),
      ]);

      const supData = await supRes.json();
      const mgrData = await mgrRes.json();
      const bldData = await bldRes.json();

      setSupervisions(supData.data || supData || []);
      setManagers(mgrData.data || mgrData || []);

      // Extract unique buildings
      const uniqueBuildings = [
        ...new Set((bldData.data || bldData || []).map((l) => l.building)),
      ];
      setBuildings(uniqueBuildings);
      setError(null);
    } catch (err) {
      setError("Failed to fetch data: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/building-supervision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to create supervision");
      }
      setFormData({ personal_id: "", building: "" });
      setShowForm(false);
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this supervision assignment?")) return;
    try {
      const res = await fetch(`${API_BASE}/building-supervision/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete");
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="building-supervision">
      <div className="page-header">
        <h1>
          <Building2 size={28} /> Building Supervision
        </h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={fetchData}>
            <RefreshCw size={16} /> Refresh
          </button>
          {canModify && (
            <button
              className="btn-primary"
              onClick={() => setShowForm(!showForm)}
            >
              <Plus size={16} /> Assign Manager
            </button>
          )}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && canModify && (
        <form className="supervision-form" onSubmit={handleSubmit}>
          <select
            value={formData.personal_id}
            onChange={(e) =>
              setFormData({ ...formData, personal_id: e.target.value })
            }
            required
          >
            <option value="">Select Manager</option>
            {managers.map((m) => (
              <option key={m.personal_id} value={m.personal_id}>
                {m.name} ({m.personal_id})
              </option>
            ))}
          </select>
          <select
            value={formData.building}
            onChange={(e) =>
              setFormData({ ...formData, building: e.target.value })
            }
            required
          >
            <option value="">Select Building</option>
            {buildings.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
          <button type="submit" className="btn-primary">
            Assign
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => setShowForm(false)}
          >
            Cancel
          </button>
        </form>
      )}

      <table className="data-table">
        <thead>
          <tr>
            <th>Manager</th>
            <th>Building</th>
            <th>Assigned Date</th>
            {canModify && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {supervisions.length === 0 ? (
            <tr>
              <td colSpan={canModify ? 4 : 3}>
                No supervision assignments found
              </td>
            </tr>
          ) : (
            supervisions.map((s) => (
              <tr key={s.supervision_id}>
                <td>
                  <UserCheck size={16} /> {s.manager_name} ({s.personal_id})
                </td>
                <td>
                  <Building2 size={16} /> {s.building}
                </td>
                <td>
                  {s.assigned_date
                    ? new Date(s.assigned_date).toLocaleDateString()
                    : "-"}
                </td>
                {canModify && (
                  <td>
                    <button
                      className="btn-danger btn-sm"
                      onClick={() => handleDelete(s.supervision_id)}
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
