/**
 * Unit tests for SafetySearch component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import SafetySearch from '../../src/components/SafetySearch';
import { mockLocations, mockSafetySearchResults } from '../mocks';

// Mock axios
vi.mock('axios');

describe('SafetySearch Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axios.get.mockImplementation((url) => {
      if (url.includes('/locations')) {
        return Promise.resolve({ data: mockLocations });
      }
      if (url.includes('/search/safety')) {
        return Promise.resolve({ data: mockSafetySearchResults });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });
  });

  it('should render title and subtitle', async () => {
    render(<SafetySearch />);

    expect(screen.getByText('Safety Search')).toBeInTheDocument();
    expect(screen.getByText(/find cleaning activities/i)).toBeInTheDocument();
  });

  it('should fetch and display buildings in dropdown', async () => {
    render(<SafetySearch />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/locations'));
    });

    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
  });

  it('should display placeholder when no results', () => {
    axios.get.mockImplementation((url) => {
      if (url.includes('/locations')) {
        return Promise.resolve({ data: mockLocations });
      }
      return Promise.resolve({ data: [] });
    });

    render(<SafetySearch />);

    expect(screen.getByText(/no results found/i)).toBeInTheDocument();
  });

  it('should perform search when form is submitted', async () => {
    const user = userEvent.setup();
    render(<SafetySearch />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'Block A');

    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/search/safety'),
        expect.objectContaining({
          params: { building: 'Block A' },
        })
      );
    });
  });

  it('should display search results with warning', async () => {
    const user = userEvent.setup();
    render(<SafetySearch />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'Block A');

    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('Cleaning')).toBeInTheDocument();
    });

    expect(screen.getByText(/hazardous/i)).toBeInTheDocument();
  });

  it('should display error when search fails', async () => {
    const user = userEvent.setup();
    axios.get.mockImplementation((url) => {
      if (url.includes('/locations')) {
        return Promise.resolve({ data: mockLocations });
      }
      if (url.includes('/search/safety')) {
        return Promise.reject({ response: { data: { error: 'Search failed' } } });
      }
      return Promise.reject(new Error('Unknown'));
    });

    render(<SafetySearch />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'Block A');

    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText(/search failed/i)).toBeInTheDocument();
    });
  });

  it('should show table headers when results exist', async () => {
    const user = userEvent.setup();
    render(<SafetySearch />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'Block A');

    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('Type')).toBeInTheDocument();
    });

    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Frequency')).toBeInTheDocument();
    expect(screen.getByText('Safety Status')).toBeInTheDocument();
  });
});

