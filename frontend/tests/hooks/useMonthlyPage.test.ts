import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useMonthlyPage } from '../../src/hooks/useMonthlyPage';

vi.mock('../../src/api/planner', () => ({
  getMonthly: vi.fn(),
  updateMonthly: vi.fn(),
}));

import { getMonthly, updateMonthly } from '../../src/api/planner';

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

describe('useMonthlyPage', () => {
  beforeEach(() => {
    vi.mocked(getMonthly).mockResolvedValue(mockPage);
    vi.mocked(updateMonthly).mockResolvedValue({ ...mockPage, study_topic: 'saved' });
  });

  it('fetches the page on mount', async () => {
    const { result } = renderHook(() => useMonthlyPage(2026, 11));
    await waitFor(() => expect(result.current.page).not.toBeNull());
    expect(getMonthly).toHaveBeenCalledWith(2026, 11);
  });

  it('calls updateMonthly on save', async () => {
    const { result } = renderHook(() => useMonthlyPage(2026, 11));
    await waitFor(() => expect(result.current.page).not.toBeNull());

    await act(async () => {
      await result.current.save({ study_topic: 'TypeScript' });
    });

    expect(updateMonthly).toHaveBeenCalledWith(2026, 11, { study_topic: 'TypeScript' });
  });
});
