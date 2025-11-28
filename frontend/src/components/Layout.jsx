import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Database,
  FileText,
  Wrench,
  Activity,
  School,
  MapPin,
  Link as LinkIcon,
} from "lucide-react";
import "../App.css";

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} className={isActive ? "active" : ""}>
      <Icon size={20} /> {children}
    </Link>
  );
}

export default function Layout({ children }) {
  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">
          PolyU CMMS
        </div>
        <NavLink to="/" icon={LayoutDashboard}>
          Dashboard
        </NavLink>
        <div className="sidebar-section">Management</div>
        <NavLink to="/persons" icon={Users}>
          People
        </NavLink>
        <NavLink to="/schools" icon={School}>
          Schools
        </NavLink>
        <NavLink to="/locations" icon={MapPin}>
          Locations
        </NavLink>
        <NavLink to="/activities" icon={Activity}>
          Activities
        </NavLink>
        <NavLink to="/maintenance" icon={Wrench}>
          Maintenance
        </NavLink>
        <div className="sidebar-section">Relationships</div>
        <NavLink to="/participations" icon={LinkIcon}>
          Participations
        </NavLink>
        <NavLink to="/affiliations" icon={LinkIcon}>
          Affiliations
        </NavLink>
        
        <div style={{ marginTop: 'auto', borderTop: '1px solid #eee', paddingTop: '10px' }}>
          <NavLink to="/dev-console" icon={Database}>
            Dev Console
          </NavLink>
        </div>
      </nav>
      <main className="content">{children}</main>
    </div>
  );
}
