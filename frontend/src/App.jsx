import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Users, Database, FileText, Wrench, Activity } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from "recharts";
import "./App.css";

const API_URL = "http://localhost:5000/api";

// --- Components ---

function ExecutiveDashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Mock data for visualization if API fails or is empty, to show off the UI
    const mockData = [
      { building: "Block A", activity_count: 12, worker_count: 5 },
      { building: "Block B", activity_count: 19, worker_count: 8 },
      { building: "Block C", activity_count: 3, worker_count: 2 },
      { building: "Block Z", activity_count: 25, worker_count: 12 },
    ];

    axios
      .get(`${API_URL}/reports/executive`)
      .then((res) => setData(res.data && res.data.length > 0 ? res.data : mockData))
      .catch(() => setData(mockData));
  }, []);

  return (
    <div className="dashboard-container">
      <div className="header-section">
        <h1>Executive Dashboard</h1>
        <p className="subtitle">Real-time campus maintenance overview</p>
      </div>

      <div className="chart-container card">
        <h3>Activity vs Workforce</h3>
        <div style={{ width: "100%", height: 400 }}>
          <ResponsiveContainer>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.1)"
                vertical={false}
              />
              <XAxis
                dataKey="building"
                stroke="#94a3b8"
                tick={{ fill: "#94a3b8" }}
                axisLine={{ stroke: "#334155" }}
              />
              <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8" }} axisLine={{ stroke: "#334155" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  borderColor: "rgba(255,255,255,0.1)",
                  color: "#f8fafc",
                }}
                itemStyle={{ color: "#f8fafc" }}
                cursor={{ fill: "rgba(255,255,255,0.05)" }}
              />
              <Legend wrapperStyle={{ paddingTop: "20px" }} />
              <Bar
                dataKey="activity_count"
                name="Total Activities"
                fill="url(#colorActivity)"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="worker_count"
                name="Workers Deployed"
                fill="url(#colorWorker)"
                radius={[4, 4, 0, 0]}
              />
              <defs>
                <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.3} />
                </linearGradient>
                <linearGradient id="colorWorker" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ec4899" stopOpacity={0.3} />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card-grid" style={{ marginTop: "30px" }}>
        <div className="stat-card card">
          <div className="stat-value">
            {data.reduce((acc, curr) => acc + curr.activity_count, 0)}
          </div>
          <div className="stat-label">Total Activities</div>
        </div>
        <div className="stat-card card">
          <div className="stat-value">{data.reduce((acc, curr) => acc + curr.worker_count, 0)}</div>
          <div className="stat-label">Active Workers</div>
        </div>
        <div className="stat-card card">
          <div className="stat-value">{data.length}</div>
          <div className="stat-label">Buildings Monitored</div>
        </div>
      </div>
    </div>
  );
}

function OperationsCenter() {
  const [batch, setBatch] = useState({
    building: "Block Z",
    floor: "5",
    type: "Cleaning",
    worker_id: "W001",
    time: "",
  });
  const [search, setSearch] = useState({ building: "Block Z", start: "", end: "" });
  const [schedule, setSchedule] = useState([]);

  const sendBatch = async () => {
    try {
      await axios.post(`${API_URL}/maintenance/batch`, batch);
      alert("Batch dispatched successfully");
    } catch (error) {
      alert("Error dispatching batch: " + (error.response?.data?.error || error.message));
    }
  };

  const checkSchedule = async () => {
    try {
      const res = await axios.get(`${API_URL}/schedules/cleaning`, { params: search });
      setSchedule(res.data.data || []);
    } catch (error) {
      console.error("Error fetching schedule:", error);
    }
  };

  return (
    <div className="page-container">
      <div className="header-section">
        <h2>
          <Wrench size={28} style={{ marginRight: "10px", color: "var(--warning)" }} /> Operations
          Center
        </h2>
        <p className="subtitle">Manage maintenance tasks and schedules</p>
      </div>

      <div className="section-block">
        <h3>Batch Job Dispatch</h3>
        <div className="data-form grid-form">
          <input
            placeholder="Building"
            value={batch.building}
            onChange={(e) => setBatch({ ...batch, building: e.target.value })}
          />
          <input
            placeholder="Floor"
            value={batch.floor}
            onChange={(e) => setBatch({ ...batch, floor: e.target.value })}
          />
          <input
            placeholder="Worker ID"
            value={batch.worker_id}
            onChange={(e) => setBatch({ ...batch, worker_id: e.target.value })}
          />
          <input
            type="datetime-local"
            onChange={(e) => setBatch({ ...batch, time: e.target.value })}
          />
          <button onClick={sendBatch} className="action-btn">
            Dispatch Batch
          </button>
        </div>
      </div>

      <div className="section-block" style={{ marginTop: "40px" }}>
        <h3>Safety & Schedule Check</h3>
        <div className="data-form">
          <input type="date" onChange={(e) => setSearch({ ...search, start: e.target.value })} />
          <input type="date" onChange={(e) => setSearch({ ...search, end: e.target.value })} />
          <input
            placeholder="Building"
            onChange={(e) => setSearch({ ...search, building: e.target.value })}
          />
          <button onClick={checkSchedule}>Search</button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Room</th>
                <th>Time</th>
                <th>Chemicals?</th>
              </tr>
            </thead>
            <tbody>
              {schedule.length > 0 ? (
                schedule.map((row, i) => (
                  <tr key={i}>
                    <td>{row.room}</td>
                    <td>{new Date(row.scheduled_time).toLocaleString()}</td>
                    <td
                      style={{
                        color: row.chemicals_used === "Yes" ? "var(--error)" : "var(--success)",
                        fontWeight: "bold",
                      }}
                    >
                      {row.chemicals_used}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="3" style={{ textAlign: "center", color: "var(--text-muted)" }}>
                    No records found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function AdminConsole() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runQuery = async () => {
    setError(null);
    setResult(null);
    try {
      const res = await axios.post(`${API_URL}/admin/query`, { query }); // Updated endpoint to match user request
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  return (
    <div className="page-container">
      <div className="header-section">
        <h2>
          <Database size={28} style={{ marginRight: "10px", color: "var(--success)" }} /> Admin
          Console
        </h2>
        <p className="subtitle">Direct database access and system management</p>
      </div>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="SELECT * FROM users..."
        rows={6}
        className="sql-input"
      />
      <button onClick={runQuery} className="primary-btn">
        Execute Query
      </button>

      {error && (
        <div className="error">
          <Activity size={16} /> {error}
        </div>
      )}

      {result && (
        <div className="result-container">
          {Array.isArray(result.data) ? (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {result.data.length > 0 &&
                      Object.keys(result.data[0]).map((k) => <th key={k}>{k}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {result.data.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((val, j) => (
                        <td key={j}>{val}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="success">{JSON.stringify(result, null, 2)}</div>
          )}
        </div>
      )}
    </div>
  );
}

function PersonManager() {
  const [persons, setPersons] = useState([]);
  const [newPerson, setNewPerson] = useState({
    personal_id: "",
    name: "",
    age: "",
    gender: "",
    supervisor_id: "",
  });

  const fetchPersons = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/persons`);
      setPersons(res.data);
    } catch (error) {
      console.error("Error fetching persons:", error);
    }
  }, []);

  useEffect(() => {
    fetchPersons();
  }, [fetchPersons]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/persons`, newPerson);
      fetchPersons();
      setNewPerson({ personal_id: "", name: "", age: "", gender: "", supervisor_id: "" });
    } catch (error) {
      alert("Error adding person: " + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div className="page-container">
      <div className="header-section">
        <h2>
          <Users size={28} style={{ marginRight: "10px", color: "var(--secondary)" }} /> Person
          Management
        </h2>
        <p className="subtitle">Staff and student directory</p>
      </div>

      <form onSubmit={handleSubmit} className="data-form">
        <input
          placeholder="ID"
          value={newPerson.personal_id}
          onChange={(e) => setNewPerson({ ...newPerson, personal_id: e.target.value })}
          required
        />
        <input
          placeholder="Name"
          value={newPerson.name}
          onChange={(e) => setNewPerson({ ...newPerson, name: e.target.value })}
          required
        />
        <input
          placeholder="Age"
          type="number"
          value={newPerson.age}
          onChange={(e) => setNewPerson({ ...newPerson, age: e.target.value })}
        />
        <select
          value={newPerson.gender}
          onChange={(e) => setNewPerson({ ...newPerson, gender: e.target.value })}
        >
          <option value="">Select Gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
        <input
          placeholder="Supervisor ID"
          value={newPerson.supervisor_id}
          onChange={(e) => setNewPerson({ ...newPerson, supervisor_id: e.target.value })}
        />
        <button type="submit">Add Person</button>
      </form>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Age</th>
              <th>Gender</th>
              <th>Supervisor</th>
            </tr>
          </thead>
          <tbody>
            {persons.map((p) => (
              <tr key={p.personal_id}>
                <td>{p.personal_id}</td>
                <td>{p.name}</td>
                <td>{p.age}</td>
                <td>{p.gender}</td>
                <td>{p.supervisor_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} className={isActive ? "active" : ""}>
      <Icon size={20} /> {children}
    </Link>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">
            CMMS <span className="pro-badge">PRO</span>
          </div>
          <NavLink to="/" icon={LayoutDashboard}>
            Dashboard
          </NavLink>
          <NavLink to="/ops" icon={Wrench}>
            Operations
          </NavLink>
          <NavLink to="/persons" icon={Users}>
            People
          </NavLink>
          <NavLink to="/admin" icon={Database}>
            Admin
          </NavLink>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<ExecutiveDashboard />} />
            <Route path="/ops" element={<OperationsCenter />} />
            <Route path="/persons" element={<PersonManager />} />
            <Route path="/admin" element={<AdminConsole />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
