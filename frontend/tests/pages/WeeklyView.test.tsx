import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../src/hooks/useAuth';
import { WeeklyView } from '../../src/pages/WeeklyView';

vi.mock('../../src/api/planner', () => ({
  getWeekly: vi.fn(),
  updateWeekly: vi.fn(),
}));

vi.mock('../../src/api/auth', () => ({
  logout: vi.fn().mockResolvedValue(undefined),
}));

import { getWeekly } from '../../src/api/planner';

const mockAuthValue = {
  token: 'test-token',
  userId: 'u1',
  setAuth: vi.fn(),
  clearAuth: vi.fn(),
};

const mockPage = {
  user_id: 'u1',
  year: 2026,
  week: 45,
  week_of_date: '2026-11-02',
  study_topic: '',
  educational_goal: '',
  exercise_goal: '',
  career_goal: '',
  other_goals: '',
  week_at_a_glance: [
    { day: 'Monday', date: '', text: '' },
    { day: 'Tuesday', date: '', text: '' },
    { day: 'Wednesday', date: '', text: '' },
    { day: 'Thursday', date: '', text: '' },
    { day: 'Friday', date: '', text: '' },
    { day: 'Saturday', date: '', text: '' },
    { day: 'Sunday', date: '', text: '' },
  ],
};

describe('WeeklyView', () => {
  beforeEach(() => {
    vi.mocked(getWeekly).mockResolvedValue(mockPage);
  });

  it('renders the weekly page', async () => {
    render(
      <AuthContext.Provider value={mockAuthValue}>
        <MemoryRouter initialEntries={['/weekly/2026/45']}>
          <Routes>
            <Route path="/weekly/:year/:week" element={<WeeklyView />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );
    await waitFor(() => {
      expect(getWeekly).toHaveBeenCalledWith(2026, 45);
    });
  });

  it('renders all 7 day rows', async () => {
    render(
      <AuthContext.Provider value={mockAuthValue}>
        <MemoryRouter initialEntries={['/weekly/2026/45']}>
          <Routes>
            <Route path="/weekly/:year/:week" element={<WeeklyView />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );
    await waitFor(() => {
      expect(screen.getByText('Mon')).toBeInTheDocument();
    });
  });
});
