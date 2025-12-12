/**
 * Unit tests for Dashboard component
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import Dashboard from "../../src/components/Dashboard";
import {
  mockMaintenanceSummary,
  mockPeopleSummary,
  mockActivitiesSummary,
  mockSchoolStats,
  mockMaintenanceFrequency,
} from "../mocks";

// Mock axios
vi.mock("axios");

describe("Dashboard Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render loading state initially", () => {
    axios.get.mockImplementation(() => new Promise(() => {}));

    render(<Dashboard />);

    expect(screen.getByText(/loading dashboard data/i)).toBeInTheDocument();
  });

  it("should render dashboard with data after loading", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("maintenance-summary")) {
        return Promise.resolve({ data: mockMaintenanceSummary });
      }
      if (url.includes("people-summary")) {
        return Promise.resolve({ data: mockPeopleSummary });
      }
      if (url.includes("activities-summary")) {
        return Promise.resolve({ data: mockActivitiesSummary });
      }
      if (url.includes("school-stats")) {
        return Promise.resolve({ data: mockSchoolStats });
      }
      if (url.includes("maintenance-frequency")) {
        return Promise.resolve({ data: mockMaintenanceFrequency });
      }
      return Promise.reject(new Error("Unknown endpoint"));
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Executive Dashboard")).toBeInTheDocument();
    });

    expect(screen.getByText("Maintenance by Location")).toBeInTheDocument();
    expect(screen.getByText("People by Role")).toBeInTheDocument();
    expect(screen.getByText("Activities by Type")).toBeInTheDocument();
    expect(screen.getByText("School Statistics")).toBeInTheDocument();
    expect(screen.getByText("Maintenance Frequency")).toBeInTheDocument();
  });

  it("should render error state when API fails", async () => {
    axios.get.mockRejectedValue(new Error("Network Error"));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Connection Error")).toBeInTheDocument();
    });

    expect(screen.getByText(/Network Error/)).toBeInTheDocument();
  });

  it("should display frequency table data", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("maintenance-summary")) {
        return Promise.resolve({ data: mockMaintenanceSummary });
      }
      if (url.includes("people-summary")) {
        return Promise.resolve({ data: mockPeopleSummary });
      }
      if (url.includes("activities-summary")) {
        return Promise.resolve({ data: mockActivitiesSummary });
      }
      if (url.includes("school-stats")) {
        return Promise.resolve({ data: mockSchoolStats });
      }
      if (url.includes("maintenance-frequency")) {
        return Promise.resolve({ data: mockMaintenanceFrequency });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Daily")).toBeInTheDocument();
    });

    expect(screen.getByText("Weekly")).toBeInTheDocument();
  });

  it("should call all report endpoints on mount", async () => {
    axios.get.mockResolvedValue({ data: [] });

    render(<Dashboard />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(5);
    });

    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("maintenance-summary"),
    );
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("people-summary"),
    );
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("activities-summary"),
    );
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("school-stats"),
    );
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("maintenance-frequency"),
    );
  });
});
