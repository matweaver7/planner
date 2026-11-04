import { render, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../src/hooks/useAuth';
import { MonthlyView } from '../../src/pages/MonthlyView';

vi.mock('../../src/api/planner', () => ({
  getMonthly: vi.fn(),
  updateMonthly: vi.fn(),
}));

vi.mock('../../src/api/auth', () => ({
  logout: vi.fn().mockResolvedValue(undefined),
}));

import { getMonthly } from '../../src/api/planner';

const mockAuthValue = {
  token: 'test-token',
  userId: 'u1',
  setAuth: vi.fn(),
  clearAuth: vi.fn(),
};

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

describe('MonthlyView', () => {
  beforeEach(() => {
    vi.mocked(getMonthly).mockResolvedValue(mockPage);
  });

  it('renders the monthly page', async () => {
    render(
      <AuthContext.Provider value={mockAuthValue}>
        <MemoryRouter initialEntries={['/monthly/2026/11']}>
          <Routes>
            <Route path="/monthly/:year/:month" element={<MonthlyView />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );
    await waitFor(() => {
      expect(getMonthly).toHaveBeenCalledWith(2026, 11);
    });
  });
});
