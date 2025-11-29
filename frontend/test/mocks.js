/**
 * Mock data and utilities for frontend testing
 */
import { vi } from "vitest";

// Mock API responses
export const mockPersons = [
  {
    personal_id: "P001",
    name: "John Doe",
    gender: "Male",
    date_of_birth: "1990-01-15",
    entry_date: "2020-01-01",
    supervisor_id: null,
    age: 34,
  },
  {
    personal_id: "P002",
    name: "Jane Smith",
    gender: "Female",
    date_of_birth: "1992-05-20",
    entry_date: "2021-03-01",
    supervisor_id: "P001",
    age: 32,
  },
];

export const mockSchools = [
  {
    department: "COMP",
    school_name: "Computing",
    faculty: "Engineering",
    hq_building: "Block Y",
  },
  {
    department: "EEE",
    school_name: "Electrical Engineering",
    faculty: "Engineering",
    hq_building: "Block S",
  },
];

export const mockLocations = [
  {
    location_id: 1,
    room: "101",
    floor: "1",
    building: "Block A",
    type: "Classroom",
    campus: "Main",
    department: "COMP",
  },
];

export const mockActivities = [
  {
    activity_id: "A001",
    type: "Seminar",
    time: "2024-03-15 14:00:00",
    organiser_name: "John Doe",
    building: "Block A",
    room: "101",
    floor: "1",
  },
];

export const mockMaintenance = [
  {
    maintenance_id: 1,
    type: "Cleaning",
    frequency: "Daily",
    location_id: 1,
    active_chemical: false,
    building: "Block A",
    room: "101",
    campus: "Main",
  },
];

export const mockMaintenanceSummary = [
  { type: "Cleaning", building: "Block A", campus: "Main", count: 5 },
  { type: "Repair", building: "Block B", campus: "Main", count: 3 },
];

export const mockPeopleSummary = [
  { job_role: "Manager", status: "Current", count: 10 },
  { job_role: "Worker", status: "Current", count: 50 },
];

export const mockActivitiesSummary = [
  { type: "Seminar", organiser_name: "John Doe", activity_count: 5 },
];

export const mockSchoolStats = [
  {
    department: "COMP",
    school_name: "Computing",
    faculty: "Engineering",
    affiliated_people: 25,
    locations_count: 10,
  },
];

export const mockMaintenanceFrequency = [
  { frequency: "Daily", type: "Cleaning", task_count: 20 },
  { frequency: "Weekly", type: "Repair", task_count: 10 },
];

export const mockSafetySearchResults = [
  {
    maintenance_id: 1,
    type: "Cleaning",
    frequency: "Daily",
    building: "Block A",
    room: "101",
    floor: "1",
    active_chemical: true,
    warning: "WARNING: Hazardous chemicals used!",
  },
];

// Create a mock axios instance
export const createMockAxios = () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
});

// Helper to setup axios mock for specific endpoints
export const setupAxiosMock = (axios, mocks = {}) => {
  axios.get.mockImplementation((url) => {
    const endpoint = url.split("/api/")[1];
    if (mocks[endpoint]) {
      return Promise.resolve({ data: mocks[endpoint] });
    }
    return Promise.reject(new Error(`No mock for ${url}`));
  });

  axios.post.mockResolvedValue({ data: { message: "Success" } });
  axios.put.mockResolvedValue({ data: { message: "Updated" } });
  axios.delete.mockResolvedValue({ data: { message: "Deleted" } });
};
