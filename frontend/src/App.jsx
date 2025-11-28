import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import EntityManager from "./components/EntityManager";
import RelationshipManager from "./components/RelationshipManager";
import SafetySearch from "./components/SafetySearch";
import DevConsole from "./components/DevConsole";
import "./App.css";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/safety-search" element={<SafetySearch />} />

          <Route
            path="/persons"
            element={
              <EntityManager
                title="Person Management"
                endpoint="persons"
                idField="personal_id"
                columns={[
                  { key: "personal_id", label: "ID" },
                  { key: "name", label: "Name" },
                  { key: "age", label: "Age" },
                  { key: "gender", label: "Gender" },
                  { key: "supervisor_id", label: "Supervisor" },
                ]}
                createFields={[
                  { name: "personal_id", label: "Personal ID", required: true },
                  { name: "name", label: "Name", required: true },
                  { name: "age", label: "Age", type: "number" },
                  {
                    name: "gender",
                    label: "Gender",
                    type: "select",
                    options: ["Male", "Female", "Other"],
                  },
                  { name: "date_of_birth", label: "Date of Birth", type: "date" },
                  { name: "supervisor_id", label: "Supervisor ID" },
                ]}
              />
            }
          />

          <Route
            path="/schools"
            element={
              <EntityManager
                title="School Management"
                endpoint="schools"
                idField="school_name"
                columns={[
                  { key: "school_name", label: "School Name" },
                  { key: "department", label: "Department" },
                  { key: "faculty", label: "Faculty" },
                  { key: "building", label: "HQ Building" },
                  { key: "room", label: "HQ Room" },
                ]}
                createFields={[
                  { name: "school_name", label: "School Name", required: true },
                  { name: "department", label: "Department", required: true },
                  { name: "faculty", label: "Faculty" },
                  { name: "hq_location_id", label: "HQ Location ID" },
                ]}
              />
            }
          />

          <Route
            path="/activities"
            element={
              <EntityManager
                title="Activity Management"
                endpoint="activities"
                idField="activity_id"
                columns={[
                  { key: "activity_id", label: "ID" },
                  { key: "type", label: "Type" },
                  { key: "time", label: "Time" },
                  { key: "organiser_name", label: "Organiser" },
                  { key: "building", label: "Building" },
                  { key: "room", label: "Room" },
                  { key: "floor", label: "Floor" },
                ]}
                createFields={[
                  { name: "activity_id", label: "Activity ID", required: true },
                  { name: "type", label: "Type" },
                  { name: "time", label: "Time", type: "datetime-local" },
                  { name: "organiser_id", label: "Organiser ID", required: true },
                  { name: "location_id", label: "Location ID" },
                ]}
              />
            }
          />

          <Route
            path="/maintenance"
            element={
              <EntityManager
                title="Maintenance Management"
                endpoint="maintenance"
                idField="maintenance_id"
                columns={[
                  { key: "type", label: "Type" },
                  { key: "frequency", label: "Frequency" },
                  { key: "building", label: "Building" },
                  { key: "room", label: "Room" },
                  {
                    key: "active_chemical",
                    label: "Active Chemical",
                    render: (value) => (value ? "Yes" : "No"),
                  },
                ]}
                createFields={[
                  { name: "type", label: "Type", required: true },
                  { name: "frequency", label: "Frequency" },
                  { name: "location_id", label: "Location ID", required: true },
                  {
                    name: "active_chemical",
                    label: "Active Chemical",
                    type: "select",
                    options: ["Yes", "No"],
                  },
                ]}
              />
            }
          />

          <Route
            path="/participations"
            element={
              <RelationshipManager
                title="Participations"
                endpoint="participations"
                fields={[
                  { name: "personal_id", label: "Personal ID" },
                  { name: "activity_id", label: "Activity ID" },
                ]}
                displayColumns={[
                  { key: "person_name", label: "Person" },
                  { key: "activity_type", label: "Activity" },
                  { key: "activity_time", label: "Time" },
                  { key: "building", label: "Building" },
                  { key: "room", label: "Room" },
                ]}
              />
            }
          />

          <Route
            path="/affiliations"
            element={
              <RelationshipManager
                title="Affiliations"
                endpoint="affiliations"
                fields={[
                  { name: "personal_id", label: "Personal ID" },
                  { name: "school_name", label: "School Name" },
                ]}
                displayColumns={[
                  { key: "person_name", label: "Person" },
                  { key: "school_name", label: "School" },
                  { key: "department", label: "Department" },
                ]}
              />
            }
          />

          <Route path="/dev-console" element={<DevConsole />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
