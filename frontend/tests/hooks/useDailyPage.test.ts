import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useDailyPage } from '../../src/hooks/useDailyPage';

vi.mock('../../src/api/planner', () => ({
  getDaily: vi.fn(),
  updateDaily: vi.fn(),
}));

import { getDaily, updateDaily } from '../../src/api/planner';

const mockPage = {
  user_id: 'u1',
  date: '2026-11-03',
  time_blocks: [{ time: '07:00', text: '' }],
  notes: '',
  study_topic: '',
  exercise_plan: '',
  goals_for_today: '',
  to_do_list: '',
};

describe('useDailyPage', () => {
  beforeEach(() => {
    vi.mocked(getDaily).mockResolvedValue(mockPage);
    vi.mocked(updateDaily).mockResolvedValue({ ...mockPage, notes: 'saved' });
  });

  it('fetches the page on mount', async () => {
    const { result } = renderHook(() => useDailyPage('2026-11-03'));
    await waitFor(() => {
      expect(result.current.page).toEqual(mockPage);
    });
    expect(getDaily).toHaveBeenCalledWith('2026-11-03');
  });

  it('starts with page = null', () => {
    const { result } = renderHook(() => useDailyPage('2026-11-03'));
    expect(result.current.page).toBeNull();
  });

  it('calls updateDaily on save', async () => {
    const { result } = renderHook(() => useDailyPage('2026-11-03'));
    await waitFor(() => expect(result.current.page).not.toBeNull());

    await act(async () => {
      await result.current.save({ notes: 'hello' });
    });

    expect(updateDaily).toHaveBeenCalledWith('2026-11-03', { notes: 'hello' });
  });

  it('sets saved=true after a successful save', async () => {
    const { result } = renderHook(() => useDailyPage('2026-11-03'));
    await waitFor(() => expect(result.current.page).not.toBeNull());

    await act(async () => {
      await result.current.save({ notes: 'hello' });
    });

    expect(result.current.saved).toBe(true);
  });

  it('refetches when date changes', async () => {
    const { result, rerender } = renderHook(({ date }) => useDailyPage(date), {
      initialProps: { date: '2026-11-03' },
    });
    await waitFor(() => expect(result.current.page).not.toBeNull());

    rerender({ date: '2026-11-04' });

    await waitFor(() => {
      expect(getDaily).toHaveBeenCalledWith('2026-11-04');
    });
  });
});
