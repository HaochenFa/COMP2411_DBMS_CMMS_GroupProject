import React, { createContext, useContext, useState, useEffect } from "react";

// Define role permissions
export const ROLES = {
  ADMIN: "Admin",
  EXECUTIVE: "Executive",
  STAFF: "Staff",
};

// Define what each role can access
export const PERMISSIONS = {
  [ROLES.ADMIN]: {
    canViewDashboard: true,
    canViewReports: true,
    canViewSafetySearch: true,
    canViewDevConsole: true,
    canViewBuildingSupervision: true,
    canCreate: true,
    canUpdate: true,
    canDelete: true,
    canViewEntities: true,
  },
  [ROLES.EXECUTIVE]: {
    canViewDashboard: true,
    canViewReports: true,
    canViewSafetySearch: true,
    canViewDevConsole: false,
    canViewBuildingSupervision: true,
    canCreate: false,
    canUpdate: false,
    canDelete: false,
    canViewEntities: true,
  },
  [ROLES.STAFF]: {
    canViewDashboard: false,
    canViewReports: false,
    canViewSafetySearch: true,
    canViewDevConsole: false,
    canViewBuildingSupervision: false,
    canCreate: false,
    canUpdate: false,
    canDelete: false,
    canViewEntities: true,
  },
};

const RoleContext = createContext(null);

export function RoleProvider({ children }) {
  const [role, setRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load role from localStorage on mount
  useEffect(() => {
    const savedRole = localStorage.getItem("userRole");
    if (savedRole && Object.values(ROLES).includes(savedRole)) {
      setRole(savedRole);
    }
    setIsLoading(false);
  }, []);

  // Login function - set role and save to localStorage
  const login = (selectedRole) => {
    if (Object.values(ROLES).includes(selectedRole)) {
      setRole(selectedRole);
      localStorage.setItem("userRole", selectedRole);
      return true;
    }
    return false;
  };

  // Logout function - clear role and localStorage
  const logout = () => {
    setRole(null);
    localStorage.removeItem("userRole");
  };

  // Check if user has a specific permission
  const hasPermission = (permission) => {
    if (!role) return false;
    return PERMISSIONS[role]?.[permission] ?? false;
  };

  // Check if user is logged in
  const isLoggedIn = () => {
    return role !== null;
  };

  const value = {
    role,
    login,
    logout,
    hasPermission,
    isLoggedIn,
    isLoading,
    ROLES,
    PERMISSIONS,
  };

  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>;
}

// Custom hook to use the role context
export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error("useRole must be used within a RoleProvider");
  }
  return context;
}

export default RoleContext;

