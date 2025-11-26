import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Layout, Database, Users, Activity, FileText } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function Dashboard() {
  return (
    <div className="dashboard">
      <h1>Campus Maintenance & Management System</h1>
      <div className="card-grid">
        <Link to="/persons" className="card">
          <Users size={48} />
          <h3>Manage People</h3>
          <p>Add, edit, and view staff and students.</p>
        </Link>
        <Link to="/query" className="card">
          <Database size={48} />
          <h3>SQL Interface</h3>
          <p>Run custom SQL queries directly.</p>
        </Link>
        <Link to="/reports" className="card">
          <FileText size={48} />
          <h3>Reports</h3>
          <p>View maintenance and activity reports.</p>
        </Link>
      </div>
    </div>
  );
}

function PersonManager() {
  const [persons, setPersons] = useState([]);
  const [newPerson, setNewPerson] = useState({ personal_id: '', name: '', age: '', gender: '', supervisor_id: '' });

  useEffect(() => {
    fetchPersons();
  }, []);

  const fetchPersons = async () => {
    try {
      const res = await axios.get(`${API_URL}/persons`);
      setPersons(res.data);
    } catch (error) {
      console.error("Error fetching persons:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/persons`, newPerson);
      fetchPersons();
      setNewPerson({ personal_id: '', name: '', age: '', gender: '', supervisor_id: '' });
    } catch (error) {
      alert("Error adding person: " + error.response?.data?.error || error.message);
    }
  };

  return (
    <div className="page-container">
      <h2>Person Management</h2>
      <form onSubmit={handleSubmit} className="data-form">
        <input placeholder="ID" value={newPerson.personal_id} onChange={e => setNewPerson({...newPerson, personal_id: e.target.value})} required />
        <input placeholder="Name" value={newPerson.name} onChange={e => setNewPerson({...newPerson, name: e.target.value})} required />
        <input placeholder="Age" type="number" value={newPerson.age} onChange={e => setNewPerson({...newPerson, age: e.target.value})} />
        <select value={newPerson.gender} onChange={e => setNewPerson({...newPerson, gender: e.target.value})}>
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
        </select>
        <input placeholder="Supervisor ID" value={newPerson.supervisor_id} onChange={e => setNewPerson({...newPerson, supervisor_id: e.target.value})} />
        <button type="submit">Add Person</button>
      </form>

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
          {persons.map(p => (
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
  );
}

function SQLInterface() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runQuery = async () => {
    setError(null);
    setResult(null);
    try {
      const res = await axios.post(`${API_URL}/query`, { query });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  return (
    <div className="page-container">
      <h2>SQL Interface</h2>
      <textarea 
        value={query} 
        onChange={e => setQuery(e.target.value)} 
        placeholder="Enter SQL query here..." 
        rows={5}
        className="sql-input"
      />
      <button onClick={runQuery}>Execute</button>
      
      {error && <div className="error">{error}</div>}
      
      {result && Array.isArray(result) && (
        <div className="table-wrapper">
            <table>
            <thead>
                <tr>{result.length > 0 && Object.keys(result[0]).map(k => <th key={k}>{k}</th>)}</tr>
            </thead>
            <tbody>
                {result.map((row, i) => (
                <tr key={i}>{Object.values(row).map((val, j) => <td key={j}>{val}</td>)}</tr>
                ))}
            </tbody>
            </table>
        </div>
      )}
      {result && !Array.isArray(result) && <div className="success">{JSON.stringify(result)}</div>}
    </div>
  );
}

function Reports() {
    const [report, setReport] = useState([]);

    useEffect(() => {
        axios.get(`${API_URL}/reports/maintenance-summary`)
            .then(res => setReport(res.data))
            .catch(err => console.error(err));
    }, []);

    return (
        <div className="page-container">
            <h2>Maintenance Report</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Building</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
                    {report.map((row, i) => (
                        <tr key={i}>
                            <td>{row.type}</td>
                            <td>{row.building}</td>
                            <td>{row.count}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">CMMS</div>
          <Link to="/"><Layout /> Dashboard</Link>
          <Link to="/persons"><Users /> People</Link>
          <Link to="/query"><Database /> SQL</Link>
          <Link to="/reports"><FileText /> Reports</Link>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/persons" element={<PersonManager />} />
            <Route path="/query" element={<SQLInterface />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
