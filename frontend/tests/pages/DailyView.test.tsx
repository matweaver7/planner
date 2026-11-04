import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../src/hooks/useAuth';
import { DailyView } from '../../src/pages/DailyView';

vi.mock('../../src/api/planner', () => ({
  getDaily: vi.fn(),
  updateDaily: vi.fn(),
}));

vi.mock('../../src/api/auth', () => ({
  logout: vi.fn().mockResolvedValue(undefined),
}));

import { getDaily } from '../../src/api/planner';

const mockAuthValue = {
  token: 'test-token',
  userId: 'u1',
  setAuth: vi.fn(),
  clearAuth: vi.fn(),
};

const mockPage = {
  user_id: 'u1',
  date: '2026-11-03',
  time_blocks: [
    { time: '07:00', text: '' },
    { time: '07:30', text: '' },
  ],
  notes: '',
  study_topic: '',
  exercise_plan: '',
  goals_for_today: '',
  to_do_list: '',
};

function renderDailyView(date = '2026-11-03') {
  return render(
    <AuthContext.Provider value={mockAuthValue}>
      <MemoryRouter initialEntries={[`/daily/${date}`]}>
        <Routes>
          <Route path="/daily/:date" element={<DailyView />} />
          <Route path="/daily/:date2" element={<DailyView />} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('DailyView', () => {
  beforeEach(() => {
    vi.mocked(getDaily).mockResolvedValue(mockPage);
  });

  it('renders the daily page for the date in the URL', async () => {
    renderDailyView('2026-11-03');
    await waitFor(() => {
      expect(getDaily).toHaveBeenCalledWith('2026-11-03');
    });
  });

  it('renders time block rows after loading', async () => {
    renderDailyView('2026-11-03');
    await waitFor(() => {
      expect(screen.getByText('07:00')).toBeInTheDocument();
    });
  });
});
