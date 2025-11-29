/**
 * Unit tests for EntityManager component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import EntityManager from '../../src/components/EntityManager';
import { mockPersons } from '../mocks';

// Mock axios
vi.mock('axios');

const defaultProps = {
  title: 'People',
  endpoint: 'persons',
  columns: [
    { key: 'personal_id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'gender', label: 'Gender' },
  ],
  idField: 'personal_id',
  createFields: [
    { name: 'personal_id', label: 'ID', required: true },
    { name: 'name', label: 'Name', required: true },
    { name: 'gender', label: 'Gender', type: 'select', options: ['Male', 'Female'] },
  ],
};

describe('EntityManager Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axios.get.mockResolvedValue({ data: mockPersons });
    axios.post.mockResolvedValue({ data: { message: 'Created' } });
    axios.put.mockResolvedValue({ data: { message: 'Updated' } });
    axios.delete.mockResolvedValue({ data: { message: 'Deleted' } });
  });

  it('should render title and subtitle', async () => {
    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('People')).toBeInTheDocument();
    });
    expect(screen.getByText(/manage people records/i)).toBeInTheDocument();
  });

  it('should fetch and display items on mount', async () => {
    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('should display table headers', async () => {
    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('ID')).toBeInTheDocument();
    });
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Gender')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('should toggle create form when Add New is clicked', async () => {
    const user = userEvent.setup();
    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const addButton = screen.getByRole('button', { name: /add new/i });
    await user.click(addButton);

    expect(screen.getByPlaceholderText('ID')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Name')).toBeInTheDocument();
  });

  it('should display error when fetch fails', async () => {
    axios.get.mockRejectedValue({ response: { data: { error: 'Connection failed' } } });

    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch data/i)).toBeInTheDocument();
    });
  });

  it('should have export and import buttons', async () => {
    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /export csv/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /import csv/i })).toBeInTheDocument();
  });

  it('should export data as CSV', async () => {
    const user = userEvent.setup();
    const createObjectURL = vi.fn();
    global.URL.createObjectURL = createObjectURL;

    render(<EntityManager {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const exportButton = screen.getByRole('button', { name: /export csv/i });
    await user.click(exportButton);

    expect(createObjectURL).toHaveBeenCalled();
  });
});

