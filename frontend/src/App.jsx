import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import EntityManager from "./components/EntityManager";
import RelationshipManager from "./components/RelationshipManager";
import SafetySearch from "./components/SafetySearch";
import ReportGenerator from "./components/ReportGenerator";
import DevConsole from "./components/DevConsole";
import "./App.css";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/safety-search" element={<SafetySearch />} />
          <Route path="/reports" element={<ReportGenerator />} />

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
                  {
                    key: "entry_date",
                    label: "Entry Date",
                    render: (value) =>
                      value
                        ? new Date(value).toLocaleDateString("en-HK", {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                            timeZone: "Asia/Hong_Kong",
                          })
                        : "-",
                  },
                  { key: "supervisor_id", label: "Supervisor" },
                ]}
                createFields={[
                  { name: "personal_id", label: "Personal ID", required: true },
                  { name: "name", label: "Name", required: true },
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
                idField="department"
                columns={[
                  { key: "department", label: "Dept Abbr" },
                  { key: "school_name", label: "Department Name" },
                  { key: "faculty", label: "Faculty/School" },
                  { key: "hq_building", label: "HQ Building" },
                ]}
                createFields={[
                  { name: "department", label: "Dept Abbr", required: true },
                  { name: "school_name", label: "Department Name", required: true },
                  {
                    name: "faculty",
                    label: "Faculty/School",
                    type: "cascading-select",
                    optionsEndpoint: "schools",
                    optionValue: "faculty",
                    optionLabel: (s) => s.faculty,
                    unique: true,
                    allowNew: true,
                  },
                  {
                    name: "hq_building",
                    label: "HQ Building",
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    optionValue: "building",
                    optionLabel: (loc) => loc.building,
                    unique: true,
                  },
                ]}
              />
            }
          />

          <Route
            path="/locations"
            element={
              <EntityManager
                title="Location Management"
                endpoint="locations"
                idField="location_id"
                columns={[
                  { key: "location_id", label: "ID" },
                  { key: "building", label: "Building" },
                  { key: "floor", label: "Floor" },
                  { key: "room", label: "Room" },
                  { key: "type", label: "Type" },
                  { key: "campus", label: "Campus" },
                  { key: "dept_name", label: "Department" },
                ]}
                createFields={[
                  {
                    name: "building",
                    label: "Building",
                    required: true,
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    optionValue: "building",
                    optionLabel: (loc) => loc.building,
                    unique: true,
                    allowNew: true,
                  },
                  {
                    name: "floor",
                    label: "Floor",
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    dependsOn: "building",
                    filterBy: "building",
                    optionValue: "floor",
                    optionLabel: (loc) => `Floor ${loc.floor}`,
                    unique: true,
                    allowNew: true,
                  },
                  {
                    name: "room",
                    label: "Room",
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    dependsOn: "floor",
                    filterBy: "floor",
                    optionValue: "room",
                    optionLabel: (loc) => `Room ${loc.room}`,
                    unique: true,
                    allowNew: true,
                  },
                  {
                    name: "type",
                    label: "Type",
                    type: "select",
                    options: ["Room", "Square", "Gate", "Level", "Hall", "Lab", "Office"],
                  },
                  {
                    name: "campus",
                    label: "Campus",
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    optionValue: "campus",
                    optionLabel: (loc) => loc.campus,
                    unique: true,
                    allowNew: true,
                  },
                  {
                    name: "department",
                    label: "Department",
                    type: "cascading-select",
                    optionsEndpoint: "schools",
                    optionValue: "department",
                    optionLabel: (s) => `${s.department} - ${s.dept_name || s.school_name}`,
                  },
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
                  {
                    key: "time",
                    label: "Time",
                    render: (value) =>
                      value
                        ? new Date(value).toLocaleString("en-HK", {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                            timeZone: "Asia/Hong_Kong",
                          })
                        : "-",
                  },
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
                  {
                    name: "building",
                    label: "Building",
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    optionValue: "building",
                    optionLabel: (loc) => loc.building,
                    unique: true,
                  },
                  {
                    name: "room",
                    label: "Room",
                    type: "cascading-select",
                    optionsEndpoint: "locations",
                    dependsOn: "building",
                    filterBy: "building",
                    optionValue: "room",
                    optionLabel: (loc) => `Room ${loc.room} (Floor ${loc.floor})`,
                    resolveTo: { field: "location_id", key: "location_id" },
                  },
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
                  {
                    name: "type",
                    label: "Type",
                    required: true,
                    type: "select",
                    options: ["Inspection", "Security", "Renovation", "Repair", "Cleaning"],
                  },
                  {
                    name: "frequency",
                    label: "Frequency",
                    type: "select",
                    options: ["Daily", "Weekly", "Monthly", "Yearly", "One-off"],
                  },
                  {
                    name: "building",
                    label: "Building",
                    type: "cascading-select",
                    required: true,
                    optionsEndpoint: "locations",
                    optionValue: "building",
                    optionLabel: (loc) => loc.building,
                    unique: true,
                  },
                  {
                    name: "room",
                    label: "Room",
                    type: "cascading-select",
                    required: true,
                    optionsEndpoint: "locations",
                    dependsOn: "building",
                    filterBy: "building",
                    optionValue: "room",
                    optionLabel: (loc) => `Room ${loc.room} (Floor ${loc.floor})`,
                    resolveTo: { field: "location_id", key: "location_id" },
                  },
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
                  { name: "department", label: "Department (Abbr)" },
                ]}
                displayColumns={[
                  { key: "person_name", label: "Person" },
                  { key: "department", label: "Dept Abbr" },
                  { key: "school_name", label: "Department Name" },
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
