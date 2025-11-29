/**
 * Unit tests for DevConsole component
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import DevConsole from "../../src/components/DevConsole";

// Mock axios
vi.mock("axios");

describe("DevConsole Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("should render title", () => {
    render(<DevConsole />);
    expect(screen.getByText(/Dev Mode.*SQL Console/i)).toBeInTheDocument();
  });

  it("should render danger zone warning", () => {
    render(<DevConsole />);
    expect(screen.getByText(/danger zone/i)).toBeInTheDocument();
  });

  it("should render query textarea with placeholder", () => {
    render(<DevConsole />);
    const textarea = screen.getByPlaceholderText(/SELECT \* FROM Person/i);
    expect(textarea).toBeInTheDocument();
  });

  it("should render run query button", () => {
    render(<DevConsole />);
    const button = screen.getByRole("button", { name: /run query/i });
    expect(button).toBeInTheDocument();
  });

  it("should render clear button", () => {
    render(<DevConsole />);
    const button = screen.getByRole("button", { name: /clear/i });
    expect(button).toBeInTheDocument();
  });

  it("should disable run query button when query is empty", () => {
    render(<DevConsole />);
    const executeButton = screen.getByRole("button", { name: /run query/i });
    expect(executeButton).toBeDisabled();
  });

  it("should render history section", () => {
    render(<DevConsole />);
    expect(screen.getByText("History")).toBeInTheDocument();
  });

  it("should show no history message initially", () => {
    render(<DevConsole />);
    expect(screen.getByText(/no history yet/i)).toBeInTheDocument();
  });

  it("should show results placeholder initially", () => {
    render(<DevConsole />);
    expect(screen.getByText(/results will appear here/i)).toBeInTheDocument();
  });
});
