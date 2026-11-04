import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DailyPage } from '../../../src/components/daily/DailyPage';

// Mock the planner API module
vi.mock('../../../src/api/planner', () => ({
  getDaily: vi.fn(),
  updateDaily: vi.fn(),
}));

import { getDaily } from '../../../src/api/planner';

const mockPage = {
  user_id: 'user-1',
  date: '2026-11-03',
  time_blocks: [
    { time: '07:00', text: '' },
    { time: '07:30', text: 'Breakfast' },
  ],
  notes: 'Some notes',
  study_topic: '',
  exercise_plan: '',
  goals_for_today: '',
  to_do_list: '',
};

describe('DailyPage', () => {
  beforeEach(() => {
    vi.mocked(getDaily).mockResolvedValue(mockPage);
  });

  it('shows loading state initially', () => {
    render(<DailyPage date="2026-11-03" />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders time blocks after loading', async () => {
    render(<DailyPage date="2026-11-03" />);
    await waitFor(() => {
      expect(screen.getByText('07:00')).toBeInTheDocument();
      expect(screen.getByText('07:30')).toBeInTheDocument();
    });
  });

  it('renders notes section', async () => {
    render(<DailyPage date="2026-11-03" />);
    await waitFor(() => {
      expect(screen.getByLabelText('Notes')).toBeInTheDocument();
    });
  });

  it('calls getDaily with the correct date', () => {
    render(<DailyPage date="2026-11-03" />);
    expect(getDaily).toHaveBeenCalledWith('2026-11-03');
  });
});
