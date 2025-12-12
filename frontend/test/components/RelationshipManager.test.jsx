/**
 * Unit tests for RelationshipManager component
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import RelationshipManager from "../../src/components/RelationshipManager";

// Mock axios
vi.mock("axios");

const mockParticipations = [
  {
    personal_id: "P001",
    name: "John Doe",
    activity_id: 1,
  },
];

// Props required by RelationshipManager
const defaultProps = {
  title: "Participations",
  endpoint: "participations",
  fields: [
    { name: "personal_id", label: "Person ID", required: true },
    { name: "activity_id", label: "Activity ID", required: true },
  ],
  displayColumns: [
    { key: "personal_id", label: "Person ID" },
    { key: "name", label: "Name" },
    { key: "activity_id", label: "Activity" },
  ],
};

describe("RelationshipManager Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axios.get.mockResolvedValue({ data: mockParticipations });
    axios.post.mockResolvedValue({ data: { message: "Created" } });
  });

  it("should render title", async () => {
    render(<RelationshipManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText("Participations")).toBeInTheDocument();
    });
  });

  it("should fetch data on mount", async () => {
    render(<RelationshipManager {...defaultProps} />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining("/participations"),
      );
    });
  });

  it("should display data in table", async () => {
    render(<RelationshipManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText("P001")).toBeInTheDocument();
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });
  });

  it("should render input fields for creating new entry", async () => {
    render(<RelationshipManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Person ID")).toBeInTheDocument();
      expect(screen.getByPlaceholderText("Activity ID")).toBeInTheDocument();
    });
  });

  it("should display error when fetch fails", async () => {
    axios.get.mockRejectedValue({
      response: { data: { error: "Connection failed" } },
    });

    render(<RelationshipManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch data/i)).toBeInTheDocument();
    });
  });

  it("should render export button", async () => {
    render(<RelationshipManager {...defaultProps} />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /export/i }),
      ).toBeInTheDocument();
    });
  });
});
