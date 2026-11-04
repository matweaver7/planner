import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { WeeklyPage } from '../../../src/components/weekly/WeeklyPage';

vi.mock('../../../src/api/planner', () => ({
  getWeekly: vi.fn(),
  updateWeekly: vi.fn(),
}));

import { getWeekly } from '../../../src/api/planner';

const mockPage = {
  user_id: 'u1',
  year: 2026,
  week: 45,
  week_of_date: '2026-11-02',
  study_topic: 'TypeScript',
  educational_goal: '',
  exercise_goal: '',
  career_goal: '',
  other_goals: '',
  week_at_a_glance: [
    { day: 'Monday', date: '2026-11-02', text: '' },
    { day: 'Tuesday', date: '2026-11-03', text: '' },
    { day: 'Wednesday', date: '2026-11-04', text: '' },
    { day: 'Thursday', date: '2026-11-05', text: '' },
    { day: 'Friday', date: '2026-11-06', text: '' },
    { day: 'Saturday', date: '2026-11-07', text: '' },
    { day: 'Sunday', date: '2026-11-08', text: '' },
  ],
};

describe('WeeklyPage', () => {
  beforeEach(() => {
    vi.mocked(getWeekly).mockResolvedValue(mockPage);
  });

  it('shows loading initially', () => {
    render(<WeeklyPage year={2026} week={45} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders goal sections after loading', async () => {
    render(<WeeklyPage year={2026} week={45} />);
    await waitFor(() => {
      expect(screen.getByLabelText('Study Topic')).toBeInTheDocument();
      expect(screen.getByLabelText('Educational Goal')).toBeInTheDocument();
      expect(screen.getByLabelText('Exercise Goal')).toBeInTheDocument();
      expect(screen.getByLabelText('Career Goal')).toBeInTheDocument();
      expect(screen.getByLabelText('Other Goals')).toBeInTheDocument();
    });
  });

  it('renders 7 day rows in week at a glance', async () => {
    render(<WeeklyPage year={2026} week={45} />);
    await waitFor(() => {
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      days.forEach((day) => {
        expect(screen.getByText(day)).toBeInTheDocument();
      });
    });
  });

  it('calls getWeekly with year and week', () => {
    render(<WeeklyPage year={2026} week={45} />);
    expect(getWeekly).toHaveBeenCalledWith(2026, 45);
  });
});
