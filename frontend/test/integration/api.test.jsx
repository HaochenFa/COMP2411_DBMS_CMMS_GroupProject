/**
 * Frontend-Backend Integration Tests
 *
 * These tests verify the integration between frontend components and the backend API.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import Dashboard from "../../src/components/Dashboard";
import EntityManager from "../../src/components/EntityManager";

// Mock axios for controlled API simulation
vi.mock("axios");

describe("Frontend-Backend Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Dashboard API Integration", () => {
    it("should fetch and display dashboard title", async () => {
      // Simulate successful API responses
      axios.get.mockImplementation((url) => {
        if (url.includes("maintenance-summary")) {
          return Promise.resolve({
            data: [{ type: "Cleaning", building: "Block A", count: 5 }],
          });
        }
        if (url.includes("people-summary")) {
          return Promise.resolve({
            data: [{ job_role: "Manager", status: "Current", count: 10 }],
          });
        }
        if (url.includes("activities-summary")) {
          return Promise.resolve({
            data: [{ type: "Seminar", activity_count: 5 }],
          });
        }
        if (url.includes("school-stats")) {
          return Promise.resolve({
            data: [{ department: "COMP", affiliated_people: 25 }],
          });
        }
        if (url.includes("maintenance-frequency")) {
          return Promise.resolve({
            data: [{ frequency: "Daily", task_count: 20 }],
          });
        }
        return Promise.resolve({ data: [] });
      });

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText("Executive Dashboard")).toBeInTheDocument();
      });
    });

    it("should handle API errors gracefully", async () => {
      axios.get.mockRejectedValue(new Error("Network Error"));

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText("Connection Error")).toBeInTheDocument();
      });
    });
  });

  describe("EntityManager Integration", () => {
    const defaultProps = {
      title: "People",
      endpoint: "persons",
      columns: [
        { key: "personal_id", label: "ID" },
        { key: "name", label: "Name" },
      ],
      idField: "personal_id",
      createFields: [
        { name: "personal_id", label: "ID", required: true },
        { name: "name", label: "Name", required: true },
      ],
    };

    it("should fetch and display entity data", async () => {
      axios.get.mockResolvedValue({
        data: [{ personal_id: "P001", name: "John Doe" }],
      });

      render(<EntityManager {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText("P001")).toBeInTheDocument();
        expect(screen.getByText("John Doe")).toBeInTheDocument();
      });
    });

    it("should display error when fetch fails", async () => {
      axios.get.mockRejectedValue({
        response: { data: { error: "Connection failed" } },
      });

      render(<EntityManager {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/failed to fetch data/i)).toBeInTheDocument();
      });
    });

    it("should call GET endpoint on mount", async () => {
      axios.get.mockResolvedValue({ data: [] });

      render(<EntityManager {...defaultProps} />);

      await waitFor(() => {
        expect(axios.get).toHaveBeenCalledWith(
          expect.stringContaining("/persons"),
        );
      });
    });
  });
});
