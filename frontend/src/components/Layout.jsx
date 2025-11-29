import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Database,
  FileText,
  Wrench,
  Activity,
  School,
  Link as LinkIcon,
  ShieldAlert,
  MapPin,
  LogOut,
  Building2,
} from "lucide-react";
import { useRole } from "../context/RoleContext";
import "../App.css";

function NavLink({ to, icon: Icon, children, permission }) {
  const location = useLocation();
  const { hasPermission } = useRole();
  const isActive = location.pathname === to;

  // If permission is specified and user doesn't have it, don't render
  if (permission && !hasPermission(permission)) {
    return null;
  }

  return (
    <Link to={to} className={isActive ? "active" : ""}>
      <Icon size={20} /> {children}
    </Link>
  );
}

export default function Layout({ children }) {
  const { role, logout } = useRole();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">PolyU CMMS</div>

        {/* Role indicator */}
        <div className="role-indicator">
          <span className={`role-badge role-${role?.toLowerCase()}`}>{role}</span>
        </div>

        <NavLink to="/" icon={LayoutDashboard} permission="canViewDashboard">
          Dashboard
        </NavLink>
        <NavLink to="/safety-search" icon={ShieldAlert} permission="canViewSafetySearch">
          Safety Search
        </NavLink>
        <NavLink to="/reports" icon={FileText} permission="canViewReports">
          Reports
        </NavLink>

        <div className="sidebar-section">Management</div>
        <NavLink to="/persons" icon={Users} permission="canViewEntities">
          People
        </NavLink>
        <NavLink to="/schools" icon={School} permission="canViewEntities">
          Schools
        </NavLink>
        <NavLink to="/locations" icon={MapPin} permission="canViewEntities">
          Locations
        </NavLink>
        <NavLink to="/activities" icon={Activity} permission="canViewEntities">
          Activities
        </NavLink>
        <NavLink to="/maintenance" icon={Wrench} permission="canViewEntities">
          Maintenance
        </NavLink>
        <NavLink
          to="/building-supervision"
          icon={Building2}
          permission="canViewBuildingSupervision"
        >
          Building Supervision
        </NavLink>

        <div className="sidebar-section">Relationships</div>
        <NavLink to="/participations" icon={LinkIcon} permission="canViewEntities">
          Participations
        </NavLink>
        <NavLink to="/affiliations" icon={LinkIcon} permission="canViewEntities">
          Affiliations
        </NavLink>

        <div style={{ marginTop: "auto", borderTop: "1px solid #eee", paddingTop: "10px" }}>
          <NavLink to="/dev-console" icon={Database} permission="canViewDevConsole">
            Dev Console
          </NavLink>
          <button className="sidebar-logout" onClick={handleLogout}>
            <LogOut size={20} /> Logout
          </button>
        </div>
      </nav>
      <main className="content">{children}</main>
    </div>
  );
}
