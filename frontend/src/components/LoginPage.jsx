import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRole, ROLES } from "../context/RoleContext";
import { LogIn, LogOut, User, Shield, Briefcase, Users } from "lucide-react";

export default function LoginPage() {
  const { login, logout, isLoggedIn, role } = useRole();
  const [selectedRole, setSelectedRole] = useState(ROLES.STAFF);
  const navigate = useNavigate();

  const handleLogin = () => {
    if (login(selectedRole)) {
      navigate("/");
    }
  };

  const handleLogout = () => {
    logout();
  };

  const roleIcons = {
    [ROLES.ADMIN]: Shield,
    [ROLES.EXECUTIVE]: Briefcase,
    [ROLES.STAFF]: Users,
  };

  const roleDescriptions = {
    [ROLES.ADMIN]: "Full access to all features including Dev Console, CRUD operations, and reports.",
    [ROLES.EXECUTIVE]: "View dashboard, reports, and safety search. Read-only access to all entities.",
    [ROLES.STAFF]: "Limited access to safety search and view entities. No access to dashboard or reports.",
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>🏛️ PolyU CMMS</h1>
          <p>Campus Maintenance Management System</p>
        </div>

        {isLoggedIn() ? (
          <div className="login-logged-in">
            <div className="current-role">
              <User size={48} />
              <h2>Currently logged in as</h2>
              <span className={`role-badge role-${role.toLowerCase()}`}>{role}</span>
            </div>
            <p className="role-description">{roleDescriptions[role]}</p>
            <div className="login-actions">
              <button className="btn-primary" onClick={() => navigate("/")}>
                Continue to Dashboard
              </button>
              <button className="btn-secondary" onClick={handleLogout}>
                <LogOut size={18} /> Logout & Switch Role
              </button>
            </div>
          </div>
        ) : (
          <div className="login-form">
            <h2>Select your role to continue</h2>
            <div className="role-selector">
              {Object.values(ROLES).map((roleOption) => {
                const Icon = roleIcons[roleOption];
                return (
                  <div
                    key={roleOption}
                    className={`role-option ${selectedRole === roleOption ? "selected" : ""}`}
                    onClick={() => setSelectedRole(roleOption)}
                  >
                    <Icon size={32} />
                    <span className="role-name">{roleOption}</span>
                    <span className="role-desc">{roleDescriptions[roleOption]}</span>
                  </div>
                );
              })}
            </div>
            <button className="btn-primary btn-login" onClick={handleLogin}>
              <LogIn size={18} /> Login as {selectedRole}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

