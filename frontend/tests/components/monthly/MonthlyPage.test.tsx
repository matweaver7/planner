import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MonthlyPage } from '../../../src/components/monthly/MonthlyPage';

vi.mock('../../../src/api/planner', () => ({
  getMonthly: vi.fn(),
  updateMonthly: vi.fn(),
}));

import { getMonthly } from '../../../src/api/planner';

const mockPage = {
  user_id: 'u1',
  year: 2026,
  month: 11,
  study_topic: '',
  educational_goal: '',
  exercise_goal: '',
  career_goal: '',
  other_goals: '',
};

describe('MonthlyPage', () => {
  beforeEach(() => {
    vi.mocked(getMonthly).mockResolvedValue(mockPage);
  });

  it('shows loading initially', () => {
    render(<MonthlyPage year={2026} month={11} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders all goal sections after loading', async () => {
    render(<MonthlyPage year={2026} month={11} />);
    await waitFor(() => {
      expect(screen.getByLabelText('Study Topic')).toBeInTheDocument();
      expect(screen.getByLabelText('Educational Goal')).toBeInTheDocument();
      expect(screen.getByLabelText('Exercise Goal')).toBeInTheDocument();
      expect(screen.getByLabelText('Career Goal')).toBeInTheDocument();
      expect(screen.getByLabelText('Other Goals')).toBeInTheDocument();
    });
  });

  it('renders the month name in the header', async () => {
    render(<MonthlyPage year={2026} month={11} />);
    await waitFor(() => {
      expect(screen.getAllByText(/november/i).length).toBeGreaterThan(0);
    });
  });

  it('calls getMonthly with year and month', () => {
    render(<MonthlyPage year={2026} month={11} />);
    expect(getMonthly).toHaveBeenCalledWith(2026, 11);
  });
});
