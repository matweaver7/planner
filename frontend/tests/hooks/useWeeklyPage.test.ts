import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useWeeklyPage } from '../../src/hooks/useWeeklyPage';

vi.mock('../../src/api/planner', () => ({
  getWeekly: vi.fn(),
  updateWeekly: vi.fn(),
}));

import { getWeekly, updateWeekly } from '../../src/api/planner';

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
  week_at_a_glance: [],
};

describe('useWeeklyPage', () => {
  beforeEach(() => {
    vi.mocked(getWeekly).mockResolvedValue(mockPage);
    vi.mocked(updateWeekly).mockResolvedValue({ ...mockPage, study_topic: 'saved' });
  });

  it('fetches the page on mount', async () => {
    const { result } = renderHook(() => useWeeklyPage(2026, 45));
    await waitFor(() => expect(result.current.page).not.toBeNull());
    expect(getWeekly).toHaveBeenCalledWith(2026, 45);
  });

  it('calls updateWeekly on save', async () => {
    const { result } = renderHook(() => useWeeklyPage(2026, 45));
    await waitFor(() => expect(result.current.page).not.toBeNull());

    await act(async () => {
      await result.current.save({ study_topic: 'TypeScript' });
    });

    expect(updateWeekly).toHaveBeenCalledWith(2026, 45, { study_topic: 'TypeScript' });
  });
});
