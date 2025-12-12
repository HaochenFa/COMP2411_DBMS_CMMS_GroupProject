import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const API_URL = "http://127.0.0.1:5050/api";
const COLORS = [
  "#A6192E",
  "#B08E55",
  "#8C1526",
  "#5D5D5D",
  "#A0A0A0",
  "#D4D4D4",
  "#E8D4A0",
  "#6B3A3A",
  "#4A7C59",
  "#7B68EE",
];

export default function Dashboard() {
  const [maintenanceSummary, setMaintenanceSummary] = useState([]);
  const [peopleSummary, setPeopleSummary] = useState([]);
  const [activitiesSummary, setActivitiesSummary] = useState([]);
  const [schoolStats, setSchoolStats] = useState([]);
  const [maintenanceFreq, setMaintenanceFreq] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [mSum, pSum, aSum, sStats, mFreq] = await Promise.all([
          axios
            .get(`${API_URL}/reports/maintenance-summary`)
            .then((res) => res.data),
          axios
            .get(`${API_URL}/reports/people-summary`)
            .then((res) => res.data),
          axios
            .get(`${API_URL}/reports/activities-summary`)
            .then((res) => res.data),
          axios.get(`${API_URL}/reports/school-stats`).then((res) => res.data),
          axios
            .get(`${API_URL}/reports/maintenance-frequency`)
            .then((res) => res.data),
        ]);
        setMaintenanceSummary(mSum);
        setPeopleSummary(pSum);
        setActivitiesSummary(aSum);
        setSchoolStats(sStats);
        setMaintenanceFreq(mFreq);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setError(
          `Error: ${error.message || "Unknown error"}. ${error.code ? `Code: ${error.code}` : ""}`,
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div
        className="dashboard-container"
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
        }}
      >
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div
          className="error-message"
          style={{
            padding: "20px",
            color: "#ef4444",
            background: "#fee2e2",
            borderRadius: "8px",
          }}
        >
          <h3>Connection Error</h3>
          <p>{error}</p>
          <p>Backend URL: {API_URL}</p>
          <p>Please ensure the backend is running on port 5050.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="header-section">
        <h1>Executive Dashboard</h1>
        <p className="subtitle">Real-time campus management overview</p>
      </div>

      <div className="card-grid">
        {/* Maintenance Summary */}
        <div className="card full-row">
          <h3>Maintenance by Location</h3>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <BarChart
                data={maintenanceSummary}
                margin={{ top: 5, right: 20, left: 0, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis
                  dataKey="building"
                  stroke="#666"
                  fontSize={11}
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  height={60}
                  tick={{ dy: 5 }}
                />
                <YAxis stroke="#666" fontSize={12} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    borderColor: "#ccc",
                    color: "#333",
                  }}
                  formatter={(value, name) => [`${value} tasks`, "Maintenance"]}
                  labelFormatter={(label) => `Location: ${label}`}
                />
                <Bar
                  dataKey="count"
                  fill="#A6192E"
                  name="Tasks"
                  radius={[3, 3, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* People Summary */}
        <div className="card">
          <h3>People by Role</h3>
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={peopleSummary}
                  dataKey="count"
                  nameKey="job_role"
                  cx="35%"
                  cy="45%"
                  outerRadius={70}
                  label={({ count }) => count}
                  labelLine={{ stroke: "#666", strokeWidth: 1 }}
                >
                  {peopleSummary.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    borderColor: "#ccc",
                    color: "#333",
                  }}
                  formatter={(value, name) => [`${value} people`, name]}
                />
                <Legend
                  layout="vertical"
                  align="right"
                  verticalAlign="middle"
                  wrapperStyle={{
                    fontSize: "11px",
                    right: 0,
                    lineHeight: "18px",
                  }}
                  iconSize={10}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activities Summary */}
        <div className="card">
          <h3>Activities by Type</h3>
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer>
              <BarChart data={activitiesSummary} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis
                  type="number"
                  stroke="#666"
                  fontSize={12}
                  allowDecimals={false}
                  tickFormatter={(value) => Math.floor(value)}
                />
                <YAxis
                  dataKey="type"
                  type="category"
                  stroke="#666"
                  width={80}
                  fontSize={12}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    borderColor: "#ccc",
                    color: "#333",
                  }}
                  formatter={(value) => [`${value} activities`, "Count"]}
                />
                <Bar
                  dataKey="activity_count"
                  fill="#B08E55"
                  name="Count"
                  radius={[0, 3, 3, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* School Stats */}
        <div className="card">
          <h3>School Statistics</h3>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <BarChart data={schoolStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis dataKey="school_name" stroke="#666" fontSize={12} />
                <YAxis stroke="#666" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    borderColor: "#ccc",
                    color: "#333",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Bar dataKey="affiliated_people" fill="#8C1526" name="People" />
                <Bar
                  dataKey="locations_count"
                  fill="#5D5D5D"
                  name="Locations"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Maintenance Frequency */}
        <div className="card">
          <h3>Maintenance Frequency</h3>
          <div
            className="table-wrapper"
            style={{ maxHeight: "200px", overflowY: "auto" }}
          >
            <table style={{ fontSize: "0.85rem" }}>
              <thead>
                <tr>
                  <th style={{ padding: "8px" }}>Freq</th>
                  <th style={{ padding: "8px" }}>Type</th>
                  <th style={{ padding: "8px" }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {maintenanceFreq.map((item, i) => (
                  <tr key={i}>
                    <td style={{ padding: "8px" }}>{item.frequency}</td>
                    <td style={{ padding: "8px" }}>{item.type}</td>
                    <td style={{ padding: "8px" }}>{item.task_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
